from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from utils import process_pdf, query_similar_documents

app = FastAPI()

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    doc_id = process_pdf(file)
    return {"status": "success", "document_id": doc_id}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/")
async def ask_question(request: QuestionRequest):
    answer = query_similar_documents(request.question)
    return {"answer": answer}
