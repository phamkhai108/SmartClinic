import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from smartclinic.api.dependencies import get_elasticsearch_client, get_embedding_model
from smartclinic.core.files.file_dto import FileResponseDTO
from smartclinic.core.files.file_service import FileProcessingService
from smartclinic.vectordb.elasticsearch.es_service import Chunker

UPLOAD_DIR = "./uploaded_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


es_client = get_elasticsearch_client()
embeding_model = get_embedding_model()
chunker = Chunker(es_client)
# Initialize the file processing service with the chunker
file_service = FileProcessingService(chunker, embeding_model)


@router.post("/upload_file", tags=["File Upload"])
async def upload_file(user_id: str, file: UploadFile = File(...)) -> FileResponseDTO:
    if file.filename.lower().endswith((".pdf", ".docx")):
        file_id = str(uuid.uuid4())

        try:
            success = await file_service.process_and_store_file(file)

            return FileResponseDTO(
                id=file_id,
                user_id=user_id,
                status="success" if success else "error",
                file_name=file.filename,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing file: {str(e)}"
            )
    else:
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX")
