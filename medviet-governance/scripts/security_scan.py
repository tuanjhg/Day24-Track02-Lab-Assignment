import re
import sys
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{30,}"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
]

SKIP_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "data",
    "reports",
}


def should_scan(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    return path.is_file() and path.suffix.lower() in {
        ".env",
        ".ini",
        ".json",
        ".md",
        ".py",
        ".txt",
        ".yml",
        ".yaml",
        ".csv",
        ".conf",
    }


def iter_files(paths: list[str]) -> list[Path]:
    if not paths:
        paths = ["."]

    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(child for child in path.rglob("*") if should_scan(child))
        elif should_scan(path):
            files.append(path)
    return files


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path}:{line_no}: possible credential")
                    break
    except OSError as exc:
        findings.append(f"{path}: unable to scan: {exc}")
    return findings


def main() -> int:
    findings: list[str] = []
    for path in iter_files(sys.argv[1:]):
        findings.extend(scan_file(path))

    if findings:
        print("Credential scan failed:")
        for finding in findings:
            print(f"  {finding}")
        return 1

    print("Credential scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
