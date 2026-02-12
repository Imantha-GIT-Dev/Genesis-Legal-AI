"""
Database Connection and ORM Setup
SQLAlchemy models for LexAI Research Platform
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Boolean, ARRAY, Float, JSON, ForeignKey, Table, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Base class for all models
Base = declarative_base()

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv('DATABASE_URL', 'postgresql://localhost:5432/lexai_research')

def create_db_engine():
    """Create database engine"""
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL logging
        pool_size=10,
        max_overflow=20
    )
    return engine

def get_session():
    """Create database session"""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    """Initialize database - create all tables"""
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")

# ============================================================
# ASSOCIATION TABLES (Many-to-Many)
# ============================================================

case_categories = Table('case_categories', Base.metadata,
    Column('case_id', Integer, ForeignKey('cases.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

legislation_categories = Table('legislation_categories', Base.metadata,
    Column('legislation_id', Integer, ForeignKey('legislation.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

article_categories = Table('article_categories', Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

# ============================================================
# ORM MODELS
# ============================================================

class Case(Base):
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    citation = Column(String(200), nullable=False)
    court = Column(String(200), nullable=False)
    jurisdiction = Column(String(100))
    decision_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    judges = Column(ARRAY(Text))
    summary = Column(Text)
    facts = Column(Text)
    holding = Column(Text)
    reasoning = Column(Text)
    outcome = Column(String(100))
    full_text = Column(Text)
    pdf_url = Column(String(500))
    neutral_citation = Column(String(200))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = relationship('Category', secondary=case_categories, back_populates='cases')
    keywords = relationship('CaseKeyword', back_populates='case')
    citations_made = relationship('CaseCitation', foreign_keys='CaseCitation.citing_case_id', back_populates='citing_case')
    citations_received = relationship('CaseCitation', foreign_keys='CaseCitation.cited_case_id', back_populates='cited_case')
    
    def __repr__(self):
        return f"<Case {self.citation}: {self.title[:50]}>"

class Legislation(Base):
    __tablename__ = 'legislation'
    
    id = Column(Integer, primary_key=True)
    leg_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    jurisdiction = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    act_number = Column(String(50))
    section = Column(String(50))
    subsection = Column(String(50))
    summary = Column(Text)
    full_text = Column(Text)
    commencement_date = Column(Date)
    repeal_date = Column(Date)
    current_version = Column(Boolean, default=True)
    pdf_url = Column(String(500))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = relationship('Category', secondary=legislation_categories, back_populates='legislation')
    
    def __repr__(self):
        return f"<Legislation {self.title}>"

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(ARRAY(Text))
    publication = Column(String(300))
    publication_date = Column(Date)
    year = Column(Integer)
    volume = Column(String(50))
    issue = Column(String(50))
    pages = Column(String(50))
    abstract = Column(Text)
    full_text = Column(Text)
    pdf_url = Column(String(500))
    doi = Column(String(200))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = relationship('Category', secondary=article_categories, back_populates='articles')
    
    def __repr__(self):
        return f"<Article {self.title[:50]}>"

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    cases = relationship('Case', secondary=case_categories, back_populates='categories')
    legislation = relationship('Legislation', secondary=legislation_categories, back_populates='categories')
    articles = relationship('Article', secondary=article_categories, back_populates='categories')
    
    def __repr__(self):
        return f"<Category {self.name}>"

class Keyword(Base):
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(200), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Keyword {self.keyword}>"

class CaseKeyword(Base):
    __tablename__ = 'case_keywords'
    
    case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id', ondelete='CASCADE'), primary_key=True)
    relevance_score = Column(Float, default=1.0)
    
    # Relationships
    case = relationship('Case', back_populates='keywords')
    keyword = relationship('Keyword')

class CaseCitation(Base):
    __tablename__ = 'case_citations'
    
    id = Column(Integer, primary_key=True)
    citing_case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'))
    cited_case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'))
    citation_type = Column(String(50))  # 'followed', 'distinguished', 'overruled', etc.
    citation_context = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    citing_case = relationship('Case', foreign_keys=[citing_case_id], back_populates='citations_made')
    cited_case = relationship('Case', foreign_keys=[cited_case_id], back_populates='citations_received')
    
    def __repr__(self):
        return f"<Citation {self.citing_case_id} -> {self.cited_case_id}>"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    organization = Column(String(200))
    role = Column(String(50), default='user')
    subscription_tier = Column(String(50), default='basic')
    is_active = Column(Boolean, default=True)
    last_login = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    search_history = relationship('SearchHistory', back_populates='user')
    saved_searches = relationship('SavedSearch', back_populates='user')
    research_folders = relationship('ResearchFolder', back_populates='user')
    conversations = relationship('Conversation', back_populates='user')
    
    def __repr__(self):
        return f"<User {self.email}>"

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    query = Column(Text, nullable=False)
    filters = Column(JSON)
    results_count = Column(Integer)
    search_timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='search_history')

class SavedSearch(Base):
    __tablename__ = 'saved_searches'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(200), nullable=False)
    query = Column(Text, nullable=False)
    filters = Column(JSON)
    alert_enabled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='saved_searches')

class ResearchFolder(Base):
    __tablename__ = 'research_folders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_shared = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='research_folders')
    saved_items = relationship('SavedItem', back_populates='folder')

class SavedItem(Base):
    __tablename__ = 'saved_items'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    folder_id = Column(Integer, ForeignKey('research_folders.id', ondelete='SET NULL'))
    item_type = Column(String(50), nullable=False)  # 'case', 'legislation', 'article'
    item_id = Column(Integer, nullable=False)
    notes = Column(Text)
    tags = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    folder = relationship('ResearchFolder', back_populates='saved_items')

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    conversation_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(300))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='conversations')
    messages = relationship('ChatMessage', back_populates='conversation')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSON)  # Citations/sources used
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship('Conversation', back_populates='messages')

class UploadedDocument(Base):
    __tablename__ = 'uploaded_documents'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    file_url = Column(String(500))
    document_type = Column(String(50))
    upload_timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    analyses = relationship('DocumentAnalysis', back_populates='document')

class DocumentAnalysis(Base):
    __tablename__ = 'document_analyses'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('uploaded_documents.id', ondelete='CASCADE'))
    analysis_type = Column(String(50), nullable=False)
    results = Column(JSON)
    confidence_score = Column(Float)
    analyzed_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    document = relationship('UploadedDocument', back_populates='analyses')
    issues = relationship('DocumentIssue', back_populates='analysis')

class DocumentIssue(Base):
    __tablename__ = 'document_issues'
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('document_analyses.id', ondelete='CASCADE'))
    issue_type = Column(String(100), nullable=False)
    severity = Column(String(20))
    description = Column(Text)
    location = Column(Text)
    recommendation = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship('DocumentAnalysis', back_populates='issues')

class UsageAnalytics(Base):
    __tablename__ = 'usage_analytics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    action_type = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    metadata = Column(JSON)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def insert_sample_data():
    """Insert sample data for testing"""
    session = get_session()
    
    try:
        # Add categories
        categories_data = [
            'Contract Law', 'Employment Law', 'Tort Law', 'Criminal Law',
            'Property Law', 'Corporate Law', 'Family Law', 'Intellectual Property'
        ]
        
        for cat_name in categories_data:
            if not session.query(Category).filter_by(name=cat_name).first():
                category = Category(name=cat_name, description=f'{cat_name} matters')
                session.add(category)
        
        session.commit()
        print("Sample categories added!")
        
        # Add keywords
        keywords_data = [
            'employment contract', 'breach', 'constructive dismissal',
            'material breach', 'damages', 'remedies', 'wrongful dismissal'
        ]
        
        for kw in keywords_data:
            if not session.query(Keyword).filter_by(keyword=kw).first():
                keyword = Keyword(keyword=kw)
                session.add(keyword)
        
        session.commit()
        print("Sample keywords added!")
        
        # Add a sample case
        if not session.query(Case).filter_by(case_id='hca_2024_45').first():
            case = Case(
                case_id='hca_2024_45',
                title='Smith v. Jones Holdings Ltd',
                citation='[2024] HCA 45',
                court='High Court of Australia',
                jurisdiction='Commonwealth',
                decision_date=datetime(2024, 3, 15).date(),
                year=2024,
                judges=['Kiefel CJ', 'Gageler J', 'Gordon J'],
                summary='Material breach of employment contract case',
                holding='Employer failure to provide agreed benefits constitutes material breach'
            )
            session.add(case)
            session.commit()
            print("Sample case added!")
        
    except Exception as e:
        session.rollback()
        print(f"Error inserting sample data: {e}")
    finally:
        session.close()

# ============================================================
# QUERY HELPERS
# ============================================================

class DatabaseQueries:
    """Helper class for common database queries"""
    
    @staticmethod
    def search_cases(query_text, limit=10):
        """Search cases by text"""
        session = get_session()
        results = session.query(Case).filter(
            Case.title.ilike(f'%{query_text}%') | 
            Case.summary.ilike(f'%{query_text}%')
        ).limit(limit).all()
        session.close()
        return results
    
    @staticmethod
    def get_case_by_citation(citation):
        """Get case by citation"""
        session = get_session()
        case = session.query(Case).filter_by(citation=citation).first()
        session.close()
        return case
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        session = get_session()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        return user
    
    @staticmethod
    def add_search_to_history(user_id, query, results_count):
        """Add search to user's history"""
        session = get_session()
        search = SearchHistory(
            user_id=user_id,
            query=query,
            results_count=results_count
        )
        session.add(search)
        session.commit()
        session.close()
    
    @staticmethod
    def get_citation_network(case_id, depth=2):
        """Get citation network for a case"""
        session = get_session()
        case = session.query(Case).get(case_id)
        
        if not case:
            return None
        
        network = {
            'case': case,
            'cites': [c.cited_case for c in case.citations_made],
            'cited_by': [c.citing_case for c in case.citations_received]
        }
        
        session.close()
        return network

# ============================================================
# MAIN - FOR TESTING
# ============================================================

if __name__ == '__main__':
    print("Initializing LexAI Research Database...")
    
    # Create all tables
    init_database()
    
    # Insert sample data
    insert_sample_data()
    
    # Test query
    print("\nTesting database queries...")
    cases = DatabaseQueries.search_cases('employment')
    print(f"Found {len(cases)} cases matching 'employment'")
    
    for case in cases:
        print(f"  - {case.citation}: {case.title}")
    
    print("\nDatabase setup complete!")
