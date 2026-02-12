-- ============================================================================
-- 1. CASES TABLE - Stores all legal cases
-- ============================================================================
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    citation TEXT NOT NULL,
    court TEXT,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    jurisdiction TEXT,
    category TEXT,
    summary TEXT,
    full_text TEXT,
    judges TEXT[],
    parties_plaintiff TEXT,
    parties_defendant TEXT,
    outcome TEXT,
    key_principles TEXT[],
    legislation_cited TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast searching
CREATE INDEX idx_cases_title ON cases USING GIN(to_tsvector('english', title));
CREATE INDEX idx_cases_summary ON cases USING GIN(to_tsvector('english', summary));
CREATE INDEX idx_cases_full_text ON cases USING GIN(to_tsvector('english', full_text));
CREATE INDEX idx_cases_year ON cases(year);
CREATE INDEX idx_cases_category ON cases(category);
CREATE INDEX idx_cases_jurisdiction ON cases(jurisdiction);

-- ============================================================================
-- 2. LEGISLATION TABLE - Stores statutes and regulations
-- ============================================================================
CREATE TABLE IF NOT EXISTS legislation (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    jurisdiction TEXT,
    year INTEGER,
    act_number TEXT,
    summary TEXT,
    full_text TEXT,
    sections JSONB,
    status TEXT, -- 'current', 'repealed', 'amended'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_legislation_title ON legislation USING GIN(to_tsvector('english', title));
CREATE INDEX idx_legislation_jurisdiction ON legislation(jurisdiction);
CREATE INDEX idx_legislation_status ON legislation(status);

-- ============================================================================
-- 3. CITATIONS TABLE - Tracks case-to-case citations
-- ============================================================================
CREATE TABLE IF NOT EXISTS citations (
    id SERIAL PRIMARY KEY,
    citing_case_id TEXT REFERENCES cases(id) ON DELETE CASCADE,
    cited_case_id TEXT REFERENCES cases(id) ON DELETE CASCADE,
    citation_type TEXT, -- 'followed', 'distinguished', 'applied', 'overruled'
    context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(citing_case_id, cited_case_id)
);

CREATE INDEX idx_citations_citing ON citations(citing_case_id);
CREATE INDEX idx_citations_cited ON citations(cited_case_id);

-- ============================================================================
-- 4. USERS TABLE - User accounts
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    organization TEXT,
    role TEXT DEFAULT 'user', -- 'user', 'admin', 'researcher'
    subscription_tier TEXT DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- 5. SEARCHES TABLE - Track user searches (analytics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS searches (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    filters JSONB,
    results_count INTEGER,
    clicked_results TEXT[], -- Array of case IDs clicked
    search_duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_searches_user ON searches(user_id);
CREATE INDEX idx_searches_created ON searches(created_at);
CREATE INDEX idx_searches_query ON searches USING GIN(to_tsvector('english', query));

-- ============================================================================
-- 6. SAVED_RESEARCH TABLE - Users' saved searches and cases
-- ============================================================================
CREATE TABLE IF NOT EXISTS saved_research (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    case_ids TEXT[],
    notes TEXT,
    tags TEXT[],
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_saved_research_user ON saved_research(user_id);
CREATE INDEX idx_saved_research_tags ON saved_research USING GIN(tags);

-- ============================================================================
-- 7. CHAT_HISTORY TABLE - AI chat conversations
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    sources JSONB, -- Referenced cases/legislation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_conversation ON chat_history(conversation_id);
CREATE INDEX idx_chat_user ON chat_history(user_id);
CREATE INDEX idx_chat_created ON chat_history(created_at);

-- ============================================================================
-- 8. DOCUMENT_ANALYSIS TABLE - Analyzed documents
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_analysis (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_name TEXT NOT NULL,
    document_type TEXT, -- 'contract', 'brief', 'agreement', etc.
    document_text TEXT,
    analysis_result JSONB, -- JSON with issues, risks, suggestions
    risk_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_doc_analysis_user ON document_analysis(user_id);
CREATE INDEX idx_doc_analysis_type ON document_analysis(document_type);

-- ============================================================================
-- 9. LEGAL_CONCEPTS TABLE - Legal principles and concepts
-- ============================================================================
CREATE TABLE IF NOT EXISTS legal_concepts (
    id SERIAL PRIMARY KEY,
    concept_name TEXT UNIQUE NOT NULL,
    description TEXT,
    related_cases TEXT[],
    related_legislation TEXT[],
    category TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_concepts_name ON legal_concepts(concept_name);
CREATE INDEX idx_concepts_category ON legal_concepts(category);

-- ============================================================================
-- 10. CASE_EMBEDDINGS TABLE - Vector embeddings for semantic search
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS case_embeddings (
    id SERIAL PRIMARY KEY,
    case_id TEXT REFERENCES cases(id) ON DELETE CASCADE,
    embedding vector(384), -- Using sentence-transformers
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ON case_embeddings USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- SAMPLE DATA - Australian Legal Cases
-- ============================================================================

INSERT INTO cases (id, title, citation, court, year, jurisdiction, category, summary, full_text) VALUES
('hca_2024_45', 
 'Smith v. Jones Holdings Ltd', 
 '[2024] HCA 45', 
 'High Court of Australia', 
 2024, 
 'Commonwealth', 
 'Employment Law',
 'Leading case on employment contract breach. Court established that constructive dismissal requires proof of fundamental breach making continued employment impossible. The court held that mere dissatisfaction or disagreement with management decisions does not constitute constructive dismissal.',
 'SMITH v JONES HOLDINGS LTD [2024] HCA 45

EMPLOYMENT LAW – Constructive dismissal – Requirements for establishing fundamental breach – Whether employee''s resignation was forced by employer''s conduct – High Court unanimously held that constructive dismissal requires proof of fundamental breach making continued employment impossible.

The appellant, Smith, was employed by Jones Holdings Ltd as a senior manager. Following a restructure, his reporting lines changed and he alleged his responsibilities were diminished. He resigned and claimed constructive dismissal.

HELD: Appeal dismissed. For constructive dismissal to be established, the employee must prove: (1) The employer committed a fundamental breach of contract; (2) The breach was sufficiently serious to entitle the employee to terminate; (3) The employee resigned in response to the breach; (4) The employee did not delay unreasonably or affirm the contract.

Damages: Appellant ordered to pay costs. No damages awarded as constructive dismissal not established.'
),

('fca_2023_128', 
 'Brown v. Corporation Limited', 
 '[2023] FCA 128', 
 'Federal Court of Australia', 
 2023, 
 'Federal', 
 'Contract Law',
 'Important precedent regarding breach of fiduciary duties in employment relationships. Court held that employees in positions of trust owe heightened duties of loyalty and must disclose conflicts of interest.',
 'BROWN v CORPORATION LIMITED [2023] FCA 128

CONTRACT LAW – Fiduciary duties – Employee in position of trust – Requirement to disclose conflicts of interest – Whether breach occurred.

The respondent, Brown, was employed as Chief Financial Officer. During employment, he invested in a competitor company without disclosure. Corporation Ltd discovered this and terminated his employment.

HELD: The court found that Brown breached his fiduciary duties. As CFO, he held a position of significant trust and his investment in a competitor created a clear conflict of interest. The failure to disclose this investment constituted a fundamental breach of his employment obligations.

The court emphasized that employees in senior positions, particularly those with access to confidential information, owe enhanced duties of loyalty to their employers. These duties include: (1) Duty of loyalty and fidelity; (2) Duty to avoid conflicts of interest; (3) Duty to disclose potential conflicts; (4) Duty not to compete during employment.

Damages: $150,000 awarded to Corporation Limited for breach of fiduciary duty.'
),

('nswsc_2024_234',
 'Davis v. Enterprise Solutions Pty Ltd',
 '[2024] NSWSC 234',
 'Supreme Court of New South Wales',
 2024,
 'NSW',
 'Employment Law',
 'Clarifies requirements for valid employment termination procedures. Court emphasized importance of procedural fairness and adequate notice periods under common law.',
 'DAVIS v ENTERPRISE SOLUTIONS PTY LTD [2024] NSWSC 234

EMPLOYMENT LAW – Termination of employment – Procedural fairness – Reasonable notice period – Whether termination was lawful.

Davis was employed for 8 years as a software developer. Employer terminated employment with 2 weeks notice, citing restructure. Davis argued inadequate notice period given length of service.

HELD: Termination was unlawful due to inadequate notice. The court held that for an employee with 8 years service in a professional role, reasonable notice would be at least 3 months. The court considered factors including: (1) Length of service; (2) Seniority of position; (3) Industry standards; (4) Age and prospects of re-employment; (5) Remuneration package.

The court also emphasized that employers must follow procedural fairness in termination: (1) Provide clear reasons for termination; (2) Give employee opportunity to respond; (3) Consider employee''s response; (4) Provide adequate notice or payment in lieu.

Damages: 3 months salary awarded as payment in lieu of notice ($45,000).'
),

('hca_2023_89',
 'Thompson v. National Bank Australia',
 '[2023] HCA 89',
 'High Court of Australia',
 2023,
 'Commonwealth',
 'Contract Law',
 'Landmark decision on interpretation of exclusion clauses in commercial contracts. Sets out principles for determining when exclusion clauses are unconscionable.',
 'THOMPSON v NATIONAL BANK AUSTRALIA [2023] HCA 89

CONTRACT LAW – Exclusion clauses – Unconscionability – Interpretation of contractual terms – Whether exclusion clause valid.

Business loan agreement contained broad exclusion clause purporting to exclude all liability for negligent advice. Thompson, a small business owner, alleged bank''s negligent financial advice caused substantial losses.

HELD (4:3): Exclusion clause was unconscionable and unenforceable. The majority held that exclusion clauses in consumer and small business contracts must be assessed for unconscionability considering: (1) Inequality of bargaining power; (2) Whether clause was specifically drawn to attention; (3) Reasonableness of the clause; (4) Industry practices.

The court emphasized that mere inclusion of exclusion clause in contract is insufficient - there must be genuine consent and the clause must not be unconscionable in the circumstances.

Damages: Matter remitted for assessment of damages for negligent advice.'
),

('vicsc_2024_156',
 'Wilson v. Melbourne Construction Ltd',
 '[2024] VSC 156',
 'Supreme Court of Victoria',
 2024,
 'Victoria',
 'Tort Law',
 'Important case on employer liability for workplace injuries. Establishes enhanced duty of care for employers in high-risk industries.',
 'WILSON v MELBOURNE CONSTRUCTION LTD [2024] VSC 156

TORT LAW – Negligence – Employer''s duty of care – Workplace safety – Whether adequate safety measures in place.

Wilson suffered serious injuries when scaffold collapsed at construction site. Alleged employer failed to: (1) Provide adequate safety equipment; (2) Conduct proper risk assessments; (3) Enforce safety protocols; (4) Provide adequate training.

HELD: Employer found negligent. The court held that employers in high-risk industries owe enhanced duty of care including: (1) Regular safety inspections; (2) Proper equipment maintenance; (3) Comprehensive safety training; (4) Adequate supervision; (5) Documented safety procedures.

The court noted that compliance with minimum regulatory standards is not sufficient - employers must take all reasonable steps to ensure worker safety.

Damages: $850,000 awarded comprising: Economic loss $450,000, Non-economic loss $300,000, Medical expenses $100,000.'
);

-- Insert legislation examples
INSERT INTO legislation (id, title, jurisdiction, year, act_number, summary, status) VALUES
('fair_work_act_2009',
 'Fair Work Act 2009',
 'Commonwealth',
 2009,
 'Act No. 28 of 2009',
 'The principal workplace relations legislation in Australia. Establishes the Fair Work Commission, sets minimum employment standards, regulates industrial action, and provides framework for enterprise bargaining.',
 'current'
),

('competition_consumer_act_2010',
 'Competition and Consumer Act 2010',
 'Commonwealth',
 2010,
 'Act No. 51 of 1974 (as amended)',
 'Promotes competition and fair trading, protects consumers. Includes Australian Consumer Law provisions.',
 'current'
);

-- Insert sample legal concepts
INSERT INTO legal_concepts (concept_name, description, category) VALUES
('Constructive Dismissal', 
 'Occurs when an employee resigns due to employer''s conduct that fundamentally breaches the employment contract, making continued employment intolerable. Requires proof of fundamental breach.',
 'Employment Law'
),

('Fiduciary Duty',
 'Obligation to act in the best interests of another party. In employment, senior employees and directors owe fiduciary duties including loyalty, good faith, and avoiding conflicts of interest.',
 'Contract Law'
),

('Procedural Fairness',
 'Principle requiring fair process in decision-making, including right to be heard, unbiased decision-maker, and disclosure of relevant information.',
 'Administrative Law'
);

-- ============================================================================
-- FUNCTIONS - Helpful PostgreSQL functions
-- ============================================================================

-- Function to search cases by text
CREATE OR REPLACE FUNCTION search_cases(search_query TEXT)
RETURNS TABLE (
    case_id TEXT,
    case_title TEXT,
    case_citation TEXT,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        title,
        citation,
        ts_rank(
            to_tsvector('english', title || ' ' || COALESCE(summary, '') || ' ' || COALESCE(full_text, '')),
            plainto_tsquery('english', search_query)
        ) as relevance
    FROM cases
    WHERE to_tsvector('english', title || ' ' || COALESCE(summary, '') || ' ' || COALESCE(full_text, ''))
          @@ plainto_tsquery('english', search_query)
    ORDER BY relevance DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Function to get related cases by citations
CREATE OR REPLACE FUNCTION get_related_cases(input_case_id TEXT)
RETURNS TABLE (
    related_case_id TEXT,
    related_case_title TEXT,
    relationship_type TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        'cites' as relationship_type
    FROM cases c
    INNER JOIN citations ct ON ct.cited_case_id = c.id
    WHERE ct.citing_case_id = input_case_id
    
    UNION
    
    SELECT 
        c.id,
        c.title,
        'cited_by' as relationship_type
    FROM cases c
    INNER JOIN citations ct ON ct.citing_case_id = c.id
    WHERE ct.cited_case_id = input_case_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Optional but recommended
-- ============================================================================

-- Enable RLS on user-specific tables
ALTER TABLE saved_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_analysis ENABLE ROW LEVEL SECURITY;

-- Policies - users can only see their own data
CREATE POLICY "Users can view own research" ON saved_research
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own chats" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own documents" ON document_analysis
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- VIEWS - Useful pre-built queries
-- ============================================================================

-- View: Recent cases with citation count
CREATE OR REPLACE VIEW recent_cases_with_citations AS
SELECT 
    c.id,
    c.title,
    c.citation,
    c.year,
    c.category,
    COUNT(DISTINCT ct1.id) as times_cited,
    COUNT(DISTINCT ct2.id) as cases_cited
FROM cases c
LEFT JOIN citations ct1 ON c.id = ct1.cited_case_id
LEFT JOIN citations ct2 ON c.id = ct2.citing_case_id
WHERE c.year >= EXTRACT(YEAR FROM CURRENT_DATE) - 5
GROUP BY c.id, c.title, c.citation, c.year, c.category
ORDER BY c.year DESC, times_cited DESC;

-- View: Popular searches
CREATE OR REPLACE VIEW popular_searches AS
SELECT 
    query,
    COUNT(*) as search_count,
    AVG(results_count) as avg_results,
    MAX(created_at) as last_searched
FROM searches
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY query
ORDER BY search_count DESC
LIMIT 50;

-- ============================================================================
-- COMMENTS - Documentation
-- ============================================================================

COMMENT ON TABLE cases IS 'Stores all legal cases with full text and metadata';
COMMENT ON TABLE legislation IS 'Stores statutes, regulations and legislative instruments';
COMMENT ON TABLE citations IS 'Tracks citations between cases for network analysis';
COMMENT ON TABLE users IS 'User accounts and authentication';
COMMENT ON TABLE searches IS 'Analytics - tracks all user searches';
COMMENT ON TABLE saved_research IS 'User-saved research collections';
COMMENT ON TABLE chat_history IS 'AI assistant conversation history';
COMMENT ON TABLE document_analysis IS 'Results from document analysis AI';

-- ============================================================================
-- GRANTS - Set permissions (adjust based on your setup)
-- ============================================================================

-- Grant read access to anonymous users for public tables
GRANT SELECT ON cases TO anon;
GRANT SELECT ON legislation TO anon;
GRANT SELECT ON citations TO anon;
GRANT SELECT ON legal_concepts TO anon;

-- Grant full access to authenticated users
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;


