from typing import List
from pypdf import PdfReader
def extract_text(pdf_bytes: bytes) -> List[str]:

    from io import BytesIO

  #creates an in-memory file object this is similar to byteStream
    reader = PdfReader(BytesIO(pdf_bytes))
    pages_text: List[str] = []

    for page in reader.pages:
        if page.extract_text() is not None:   # or we can write in one line       text = page.extract_text() or ""
            text = page.extract_text()
        else:
            text = ""
        cleaned = "".join(text.split()) # text.split() → splits into list of words and joins them without words
        pages_text.append(cleaned)

    return pages_text


if __name__ == "__main__":
   with open("az-305.pdf", "rb") as f:
       pdf_bytes = f.read()

   pages = extract_text(pdf_bytes)
   print(pages)



