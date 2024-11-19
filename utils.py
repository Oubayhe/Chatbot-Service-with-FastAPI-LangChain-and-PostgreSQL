import os
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline
from connection import get_connection

def process_pdf(file) -> int:
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    loader = PyPDFLoader(temp_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_documents(documents)

    
    embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')  
    doc_id = None

    with get_connection() as conn:
        with conn.cursor() as cur:
            for chunk in chunks:
                chunk_text = chunk.page_content  
                embedding = embeddings_model.encode([chunk_text])  

                cur.execute("INSERT INTO documents (content) VALUES (%s) RETURNING id;", (chunk_text,))
                doc_id = cur.fetchone()[0]

                
                cur.execute("INSERT INTO vectors (document_id, embedding) VALUES (%s, %s);",
                            (doc_id, embedding[0].tolist()))  
            conn.commit()

    os.remove(temp_path)
    return doc_id

def generate_embeddings(text: str) -> list:
    embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    return embeddings_model.encode([text])[0].tolist()

def query_similar_documents(question: str) -> str:
    question_embedding = generate_embeddings(question)

    similar_docs = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT content FROM documents
                JOIN vectors ON documents.id = vectors.document_id
                ORDER BY embedding <-> %s::vector LIMIT 5;
            """, (question_embedding,))

            similar_docs = [row[0] for row in cur.fetchall()]

    context = "\n\n".join(similar_docs)

    
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")  
    answer = qa_pipeline(question=question, context=context)

    return answer['answer']
