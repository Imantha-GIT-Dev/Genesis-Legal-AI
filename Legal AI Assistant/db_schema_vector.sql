-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE cases
ADD COLUMN embedding VECTOR(384);

ALTER TABLE legislation
ADD COLUMN embedding VECTOR(384);

ALTER TABLE document_analysis
ADD COLUMN embedding VECTOR(384);


CREATE INDEX cases_embedding_idx
ON cases
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX legislation_embedding_idx
ON legislation
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX document_analysis_embedding_idx
ON document_analysis
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

ANALYZE cases;
ANALYZE legislation;
ANALYZE document_analysis;

ALTER TABLE cases
ADD COLUMN search_vector tsvector;

ALTER TABLE legislation
ADD COLUMN search_vector tsvector;

UPDATE cases
SET search_vector =
    to_tsvector(
        'english',
        coalesce(title,'') || ' ' ||
        coalesce(summary,'') || ' ' ||
        coalesce(full_text,'')
    );

UPDATE legislation
SET search_vector =
    to_tsvector(
        'english',
        coalesce(title,'') || ' ' ||
        coalesce(summary,'') || ' ' ||
        coalesce(full_text,'')
    );

-- SELECT column_name
-- FROM information_schema.columns
-- WHERE table_name = 'cases';

CREATE INDEX cases_search_idx
ON cases
USING GIN (search_vector);

CREATE INDEX legislation_search_idx
ON legislation
USING GIN (search_vector);