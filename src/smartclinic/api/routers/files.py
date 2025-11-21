import os

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from smartclinic.api.dependencies import (
    get_db,
    get_elasticsearch_client,
    get_embedding_model,
)
from smartclinic.core.files.file_dto import FileResponseDTO
from smartclinic.core.files.file_service import UploadFileNProcessChunk
from smartclinic.vectordb.elasticsearch.es_service import Chunker

UPLOAD_DIR = "./uploaded_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/files", tags=["File Management"])


es_client = get_elasticsearch_client()
embeding_model = get_embedding_model()
db_session = get_db()
chunker = Chunker(es_client)
file_service = UploadFileNProcessChunk(chunker, embeding_model, db_session)


@router.post("/upload_flow")
async def upload_file(user_id: str, file: UploadFile = File(...)) -> FileResponseDTO:
    if file.filename.lower().endswith((".pdf", ".docx")):
        try:
            file_obj = await file_service.process_and_store_file(file, user_id=user_id)

            return FileResponseDTO(
                id=file_obj.id,
                user_id=file_obj.user_id,
                status="success",
                file_name=file_obj.file_name,
                created_at=file_obj.created_at,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing file: {str(e)}"
            )
    else:
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX")


@router.get("/get_info_files", response_model=list[FileResponseDTO])
def list_files_by_user(user_id: str = Query(..., description='User ID or "all"')):
    try:
        files = file_service.list_files_by_user(user_id)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_file/{file_name}")
async def delete_file(file_name: str) -> dict:
    try:
        file_service.delete_file_by_filename(file_name)
        return {
            "detail": f"File {file_name} deleted successfully.",
            "status": "success",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
