
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL
);

CREATE TABLE vectors (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    embedding VECTOR(384) NOT NULL
);
