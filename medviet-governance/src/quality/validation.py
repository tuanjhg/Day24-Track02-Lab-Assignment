# src/quality/validation.py
import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    TODO: Tạo expectation suite cho anonymized patient data.
    """
    context = gx.get_context()
    suite = context.add_expectation_suite("patient_data_suite")

    # Lấy validator
    df = pd.read_csv("data/raw/patients_raw.csv")
    validator = context.sources.pandas_default.read_dataframe(df)

    # --- TASK: Thêm các expectations ---

    # 1. patient_id không được null
    validator.expect_column_values_to_not_be_null("patient_id")

    validator.expect_column_value_lengths_to_equal(
        column="cccd",
        value=12
    )

    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50
    )

    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions
    )

    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    TODO: Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    if "cccd" in df and not df["cccd"].astype(str).str.match(r"^\d{12}$").all():
        results["success"] = False
        results["failed_checks"].append("cccd must contain 12-digit replacement values")

    required_columns = ["patient_id", "cccd", "so_dien_thoai", "email", "benh", "ket_qua_xet_nghiem"]
    null_columns = [col for col in required_columns if col in df and df[col].isna().any()]
    if null_columns:
        results["success"] = False
        results["failed_checks"].append(f"null values found in: {', '.join(null_columns)}")

    try:
        original_rows = len(pd.read_csv("data/raw/patients_raw.csv"))
        results["stats"]["original_rows"] = original_rows
        if len(df) != original_rows:
            results["success"] = False
            results["failed_checks"].append("row count differs from raw dataset")
    except FileNotFoundError:
        results["failed_checks"].append("raw dataset not found; skipped row-count comparison")

    return results
