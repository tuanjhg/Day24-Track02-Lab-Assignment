from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException

from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "patients_raw.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "patients_anonymized.csv"

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()


def load_raw_patients() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Missing data/raw/patients_raw.csv. Run scripts/generate_data.py first.",
        )
    return pd.read_csv(
        RAW_DATA_PATH,
        dtype={"cccd": str, "so_dien_thoai": str, "patient_id": str},
    )


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(current_user: dict = Depends(get_current_user)):
    df = load_raw_patients()
    return df.head(10).to_dict(orient="records")


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(current_user: dict = Depends(get_current_user)):
    df = load_raw_patients()
    df_anon = anonymizer.anonymize_dataframe(df)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_anon.to_csv(PROCESSED_DATA_PATH, index=False)
    return df_anon.head(10).to_dict(orient="records")


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(current_user: dict = Depends(get_current_user)):
    df = load_raw_patients()
    disease_counts = df["benh"].value_counts().to_dict()
    return {
        "total_patients": int(len(df)),
        "patients_by_disease": {str(key): int(value) for key, value in disease_counts.items()},
        "average_test_result": float(df["ket_qua_xet_nghiem"].mean()),
    }


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    df = load_raw_patients()
    if patient_id not in set(df["patient_id"].astype(str)):
        raise HTTPException(status_code=404, detail="Patient not found")

    df = df[df["patient_id"].astype(str) != patient_id]
    df.to_csv(RAW_DATA_PATH, index=False)
    return {"status": "deleted", "patient_id": patient_id}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
