# NĐ13/2023 Compliance Checklist - MedViet AI Platform

## A. Data Localization

- [x] Patient data được lưu trong storage nội bộ đặt tại Việt Nam cho môi trường production.
- [x] Backup production phải dùng bucket/volume trong lãnh thổ Việt Nam, bật encryption at rest.
- [x] Mọi lần export hoặc transfer dữ liệu ra ngoài hệ thống phải ghi audit log gồm user, timestamp, mục đích, loại dữ liệu và nơi nhận.

## B. Explicit Consent

- [x] Thu thập consent trước khi dùng patient data cho AI training.
- [x] Lưu consent record gồm `patient_id`, version điều khoản, timestamp, kênh thu thập và trạng thái consent.
- [x] Có cơ chế rút consent/right to erasure qua API admin `DELETE /api/patients/{patient_id}` và quy trình xóa khỏi training dataset kế tiếp.
- [x] Chỉ dùng anonymized training data cho ML engineer; raw PII chỉ admin được đọc.

## C. Breach Notification 72h

- [x] Có incident response plan: detect, triage, contain, eradicate, recover, notify.
- [x] Prometheus/Grafana dùng để giám sát service, HTTP error rate, request spike và bất thường truy cập.
- [x] Khi xác nhận breach, DPO và Security Team phải được thông báo trong 24h nội bộ để còn thời gian báo cáo cơ quan có thẩm quyền trong 72h.
- [x] Audit evidence gồm API access log, RBAC policy, Bandit report, pip-audit report và commit hook result.

## D. DPO Appointment

- [x] Đã bổ nhiệm Data Protection Officer cho dự án lab.
- [x] DPO liên hệ: `dpo@medviet.example`.
- [x] DPO chịu trách nhiệm phê duyệt data export, breach notification và yêu cầu xóa dữ liệu cá nhân.

## E. Technical Controls Mapping

| NĐ13 requirement | Technical control | Status | Owner |
| --- | --- | --- | --- |
| Data minimization | PII detection/anonymization pipeline cho `ho_ten`, `cccd`, `so_dien_thoai`, `email`, `dia_chi`, `bac_si_phu_trach`, `ngay_sinh` | Done | AI Team |
| Purpose limitation | ML endpoint chỉ trả anonymized dataset; raw endpoint giới hạn admin | Done | AI Team |
| Access control | Casbin RBAC với admin, ml_engineer, data_analyst, intern; endpoint trái quyền trả 403 | Done | Platform Team |
| Encryption at rest | Envelope encryption AES-256-GCM; DEK được encrypt bởi KEK; payload không chứa plaintext key | Done | Infra Team |
| Consent management | Consent record schema và right-to-erasure workflow gắn với `patient_id` | Done | Product + Legal |
| Audit logging | Production cần log mọi request gồm `username`, `role`, `resource`, `action`, `decision`, `timestamp`, `request_id` | Designed | Platform Team |
| Security audit | Pre-commit hook chạy credential scan, Bandit SAST, pip-audit dependency scan | Done | Security Team |
| Breach detection | Prometheus/Grafana monitoring stack trong `docker-compose.yml`; alert rules cần triển khai trong production | Designed | Security Team |
| Data quality | Validation checks cho null, unique `patient_id`, valid bệnh, email format, row-count consistency | Done | Data Team |
| Data retention | Raw patient data giữ theo hợp đồng/consent; anonymized derived data rebuild khi consent bị rút | Designed | Data Governance |

## F. Evidence Trong Repo

- PII tests: `tests/test_pii.py`.
- RBAC API tests: `tests/test_rbac_api.py`.
- Encryption tests: `tests/test_encryption.py`.
- Security hook: `.github/hooks/pre-commit`.
- Credential scanner fallback: `scripts/security_scan.py`.
- Bandit report: `reports/bandit_report.txt`.
