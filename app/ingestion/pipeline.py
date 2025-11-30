# here weill do all the steps
# download the file from storage account and then extact pdf and upload in a separate conatiner
import uuid

from app.schemas.book import BookText, BookMetadata, Chapter
from app.services.storage_service import StorageService
from app.ingestion.text_extractor import extract_text
from app.core.config import settings

storage_Service = StorageService()

def process_book(blob_name: str, title: str = None, author: str = None) -> BookText:
    """
        Light extraction pipeline:
        - Download PDF from raw container
        - Extract text page-by-page
        - Wrap into BookText model
        - Store JSON in processed container
        """

    """download the book from storage account -- can we use a google drive that would be cheaper as well??"""
    raw_pdf = storage_Service.download_blob(blob_name)

    """extract text from pdf file"""
    all_pages = extract_text(raw_pdf)
    number_pages = len(all_pages)

    # Generate book_id
    book_id = f'{uuid.uuid4()}_{blob_name}'
    
    # Extract filename for default title if not provided
    default_title = blob_name.split('/')[-1].replace('.pdf', '').replace('_', ' ')
    
    """Build metadata ie BookText object"""
    metadata = BookMetadata(
        book_id=book_id,
        title=title or default_title,
        author=author or "Unknown",
        source_blob=blob_name,
        num_pages=number_pages
    )
    """# 4. For now, treat each page as a "chapter" placeholder"""
    chapters=[]
    for index, page in enumerate(all_pages):
        if page.strip():
            chapter = Chapter(index=index,title=None,text=page.strip())
            chapters.append(chapter)

    book_text = BookText(metadata=metadata, chapters=chapters)

    """# 5 upload json in another processed container  """
    storage_Service.upload_json(
        container_name=settings.AZURE_PROCESSED_BOOK_CONTAINER,
        blob_name=f"{book_id}.json",
        data=book_text.model_dump()  # Convert Pydantic model to dict
    )
    
    return book_text





