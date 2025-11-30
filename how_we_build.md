# Step1
## Ui --> where user can upload a document and store in azure blob storage
## U upload a file and then we upload the file in azure blob storage



# Step2
Now we want a small service that can:
	1.	Given a book_id and a blob path
	2.	Download the PDF from Blob
	3.	Extract clean text
	4.	Structure it into chapters/sections (simple for now)
	5.	Save the structured text back (e.g., as JSON) for later steps (distillation, embeddings, etc.)


# what we have achived here is 
What have we achieved here?
	•	For each book (already uploaded as PDF in Blob):
	•	We extract text.
	•	Represent it as BookText.
	•	Store it as book_id.json in a processed container.
	•	This JSON file is now the canonical source for downstream:
	•	Summaries
	•	Study notes
	•	Embeddings
	•	Q&A generation
                    ALREADY DONE ✅                    NEXT STEP 🆕
                    ──────────────                    ───────────

PDF (in Blob)                                   
     │                                          
     ↓                                          
Download PDF bytes              ✅ Done          
     │                                          
     ↓                                          
Extract text (per page)         ✅ Done          
     │                                          
     ↓                                          
Chunk & clean text              ✅ Done (stored as BookText JSON)
     │                                          
     ↓                                          
Store book.json in Blob         ✅ Done (in "processed-books")
     │                                          
     │                                          
     ├────────────────────────────────────────► LLM Summary Generator  🆕
                                                     │
                                                     ↓
                                               Store summary.json      🆕
                                               (in "processed-books")

