from fastapi import APIRouter, UploadFile, File
from app.analytics.service import summarize_csv

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/analytics/csv-summary")
async def csv_summary(file: UploadFile = File(...)):
    content = await file.read()
    tmp = f"./tmp_{file.filename}"
    with open(tmp, "wb") as f:
        f.write(content)
    return summarize_csv(tmp)
