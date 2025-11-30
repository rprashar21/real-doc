from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.book import BookText
from app.ingestion.pipeline import process_book

router = APIRouter()


class ProcessBookRequest(BaseModel):
    blob_name: str
    title: str = None
    author: str = None


@router.post("/book", response_model=BookText)
async def process_book_endpoint(request: ProcessBookRequest) -> BookText:
    """
    Process a book from blob storage:
    1. Download PDF from raw container
    2. Extract text
    3. Build BookText model
    4. Upload JSON to processed container
    """
    try:
        book = process_book(
            blob_name=request.blob_name,
            title=request.title,
            author=request.author
        )
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process book {request.blob_name}: {str(e)}")
