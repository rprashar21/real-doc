import typer
from rich import print

from app.ingestion.pipeline import process_book

app = typer.Typer()

@app.command()
def ingest_book(blob_name: str, title: str = "", author: str = ""):
    book = process_book(blob_name=blob_name,
                        title=title or None, author=author or None)
    print(f"Pages: {book.metadata.num_pages}, Chapters: {len(book.chapters)}")


if __name__ == "__main__":
    process_book("")
    app()