from fastapi import APIRouter, File, HTTPException, UploadFile

from smartclinic.core.brain.brain_dto import PredictBrainResponse
from smartclinic.core.brain.brain_service import predict_image_class

router = APIRouter(tags=["Brain"], prefix="/brain")


@router.post("/predict_tumor", response_model=PredictBrainResponse)
async def predict(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(
            status_code=400, detail="File must be an image (jpg, jpeg, png)"
        )

    return await predict_image_class(file)
