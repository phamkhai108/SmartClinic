import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from smartclinic.core.files.file_dto import FileResponseDTO

UPLOAD_DIR = "./uploaded_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.post("/upload_file", tags=["File Upload"])
async def upload_file(user_id: str, file: UploadFile = File(...)) -> FileResponseDTO:
    if file.filename.lower().endswith((".pdf", ".docx")):
        file_id = str(uuid.uuid4())

        file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            return FileResponseDTO(
                id=file_id,
                user_id=user_id,
                status="success",
                file_name=file.filename,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error while saving file: {str(e)}"
            )

    else:
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX")
