from pydantic import BaseModel
from typing import Optional,List


class BookMetadata(BaseModel):
    book_id: str
    title: str = "Untitled"  # Default value
    author: str = "Unknown"   # Default value
    source_blob: str # blob path url
    num_pages: Optional[int] = None



class Chapter(BaseModel):
    index: int
    title: Optional[str] = None
    text: str


class BookText(BaseModel):
    metadata: BookMetadata
    chapters: List[Chapter]


"""
This is your canonical representation of a processed book’s text.
	•	Very easy to:
	•	json() it and store
	•	later feed chapter text into summarization, embeddings, Q&A, etc.
"""
