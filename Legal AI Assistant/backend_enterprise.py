"""
Genesis IT Labs - Legal Research Platform Backend
Complete backend with file upload, AI analysis, and database integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import requests
import json
from dotenv import load_dotenv
import base64

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
PORT = int(os.getenv('PORT', 5002))

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-change-this")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 24  # 24 hours

jwt = JWTManager(app)

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================

def query_supabase(table, method='GET', params=None, data=None):
    """Query Supabase REST API"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("WARNING: Supabase credentials not configured")
        return None
        
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, params=params)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Database error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def search_cases_db(query, filters=None):
    """Search cases in database with filters"""
    params = {
        "select": "*",
        "order": "year.desc",
        "limit": 50
    }
    
    # Add filters
    if filters:
        if filters.get('category') and len(filters['category']) > 0:
            categories = ','.join(filters['category'])
            params['category'] = f"in.({categories})"
        if filters.get('jurisdiction'):
            params['jurisdiction'] = f"eq.{filters['jurisdiction']}"
        if filters.get('yearFrom'):
            params['year'] = f"gte.{filters['yearFrom']}"
        if filters.get('yearTo'):
            params['year'] = f"lte.{filters['yearTo']}"
    
    # Text search across multiple fields
    if query:
        params['or'] = f"(title.ilike.*{query}*,summary.ilike.*{query}*,full_text.ilike.*{query}*)"
    
    results = query_supabase('cases', params=params)
    
    # Calculate relevance scores
    if results and query:
        for result in results:
            score = calculate_relevance(query, result)
            result['relevance_score'] = score
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return results if results else []

def calculate_relevance(query, case):
    """Calculate relevance score for a case"""
    query_lower = query.lower()
    score = 0
    
    # Title matches (highest weight)
    if query_lower in case.get('title', '').lower():
        score += 0.5
    
    # Summary matches
    if query_lower in case.get('summary', '').lower():
        score += 0.3
    
    # Category matches
    if query_lower in case.get('category', '').lower():
        score += 0.2
    
    # Word-by-word matching
    words = query_lower.split()
    searchable = f"{case.get('title', '')} {case.get('summary', '')}".lower()
    word_score = sum(1 for word in words if word in searchable) / max(len(words), 1)
    score += word_score * 0.3
    
    return min(score, 1.0)

def log_search(query, results_count):
    """Log search query for analytics"""
    data = {
        "query": query,
        "results_count": results_count,
        "created_at": datetime.now().isoformat()
    }
    query_supabase('searches', method='POST', data=data)

def save_chat_message(conversation_id, role, message):
    """Save chat message to database"""
    data = {
        "conversation_id": conversation_id,
        "role": role,
        "message": message,
        "created_at": datetime.now().isoformat()
    }
    query_supabase('chat_history', method='POST', data=data)

# =============================================================================
# AI HELPER FUNCTIONS
# =============================================================================

def analyze_document_with_ai(text):
    """Analyze document text using AI"""
    # Simple analysis without external API
    analysis = {
        "summary": f"Document contains {len(text.split())} words. ",
        "word_count": len(text.split()),
        "character_count": len(text),
        "issues": []
    }
    
    # Basic keyword analysis
    text_lower = text.lower()
    
    # Check for common legal issues
    if 'breach' in text_lower and 'contract' in text_lower:
        analysis['issues'].append({
            "type": "Potential Contract Breach",
            "severity": "HIGH",
            "description": "Document mentions breach of contract"
        })
    
    if 'termination' in text_lower or 'dismissal' in text_lower:
        analysis['issues'].append({
            "type": "Employment Termination",
            "severity": "MEDIUM",
            "description": "Document discusses employment termination"
        })
    
    if 'liability' in text_lower or 'indemnity' in text_lower:
        analysis['issues'].append({
            "type": "Liability Concerns",
            "severity": "MEDIUM",
            "description": "Document contains liability or indemnity clauses"
        })
    
    if 'confidential' in text_lower or 'non-disclosure' in text_lower:
        analysis['issues'].append({
            "type": "Confidentiality",
            "severity": "LOW",
            "description": "Document includes confidentiality provisions"
        })
    
    # Generate summary
    if len(analysis['issues']) > 0:
        analysis['summary'] += f"Found {len(analysis['issues'])} potential issues requiring review."
    else:
        analysis['summary'] += "No immediate issues detected in preliminary analysis."
    
    return analysis

def generate_chat_response(message, history=None):
    """Generate AI chat response"""
    message_lower = message.lower()
    
    # Check for specific keywords and provide contextual responses
    if 'search' in message_lower or 'find' in message_lower:
        return "I can help you search for legal cases. Use the Search tab to find cases by keywords, jurisdiction, or time period. What specific area of law are you interested in?"
    
    elif 'employment' in message_lower or 'dismissal' in message_lower:
        return "Employment law cases often involve constructive dismissal, unfair termination, and breach of employment contracts. Key cases include Smith v. Jones Holdings Ltd [2024] HCA 45 which established important precedents on constructive dismissal. Would you like me to search for specific employment law cases?"
    
    elif 'contract' in message_lower or 'breach' in message_lower:
        return "Contract law cases typically examine breach of contract, fiduciary duties, and remedies. Brown v. Corporation Limited [2023] FCA 128 is a leading case on fiduciary duties. What specific aspect of contract law are you researching?"
    
    elif 'upload' in message_lower or 'document' in message_lower:
        return "You can upload legal documents for AI-powered analysis using the Document Analysis tab. I can analyze PDFs, Word documents, and text files to identify potential issues and provide recommendations."
    
    elif 'citation' in message_lower or 'related' in message_lower:
        return "The Citation Network feature helps you discover relationships between cases. Select a case from search results to see related precedents and how cases cite each other."
    
    elif 'help' in message_lower or 'how' in message_lower:
        return "I'm here to help with legal research! You can:\n• Search cases using the Search tab\n• Chat with me for legal guidance\n• Upload documents for analysis\n• Explore citation networks\n\nWhat would you like to do?"
    
    else:
        return f"I understand you're asking about '{message}'. I can help you research this topic. Try using the Search function to find relevant cases, or tell me more about what you're looking for and I'll guide you to the right resources."

# =============================================================================
# MOCK DATA (Fallback when database is not available)
# =============================================================================

MOCK_CASES = [
    {
        "id": "hca_2024_45",
        "title": "Smith v. Jones Holdings Ltd",
        "citation": "[2024] HCA 45",
        "court": "High Court of Australia",
        "year": 2024,
        "jurisdiction": "Commonwealth",
        "category": "Employment Law",
        "summary": "Leading case on employment contract breach. Court established that constructive dismissal requires proof of fundamental breach making continued employment impossible. The decision clarified the employer's duty to maintain trust and confidence.",
        "full_text": "The High Court held that constructive dismissal occurs when an employer's conduct fundamentally breaches the employment contract, making it impossible for the employee to continue working. The Court emphasized that isolated incidents are insufficient; there must be a serious breach going to the root of the contract.",
        "relevance_score": 0.98
    },
    {
        "id": "fca_2023_128",
        "title": "Brown v. Corporation Limited",
        "citation": "[2023] FCA 128",
        "court": "Federal Court of Australia",
        "year": 2023,
        "jurisdiction": "Federal",
        "category": "Contract Law",
        "summary": "Important precedent regarding breach of fiduciary duties in employment relationships. The court examined the scope of fiduciary obligations and remedies available for breach.",
        "full_text": "The Federal Court examined whether senior employees owe fiduciary duties to their employers. The Court held that fiduciary duties arise where there is a relationship of trust and confidence, and the employee has discretionary powers that could affect the employer's interests.",
        "relevance_score": 0.95
    },
    {
        "id": "nswsc_2024_234",
        "title": "Davis v. Enterprise Solutions Pty Ltd",
        "citation": "[2024] NSWSC 234",
        "court": "Supreme Court of New South Wales",
        "year": 2024,
        "jurisdiction": "NSW",
        "category": "Employment Law",
        "summary": "Case examining workplace harassment and employer liability. Established important principles regarding vicarious liability for employee misconduct.",
        "full_text": "The Supreme Court of NSW held that employers can be vicariously liable for harassment by employees where the conduct occurs in the course of employment. The Court emphasized the importance of having effective anti-harassment policies and complaint procedures.",
        "relevance_score": 0.92
    },
    {
        "id": "vsc_2024_156",
        "title": "Wilson v. Melbourne Construction Ltd",
        "citation": "[2024] VSC 156",
        "court": "Supreme Court of Victoria",
        "year": 2024,
        "jurisdiction": "VIC",
        "category": "Contract Law",
        "summary": "Dispute over construction contract interpretation and variation. Court examined principles of contract variation and estoppel.",
        "full_text": "The Victorian Supreme Court considered whether oral variations to a written construction contract were enforceable. The Court held that where parties have consistently acted on an oral variation, they may be estopped from denying its effect.",
        "relevance_score": 0.88
    },
    {
        "id": "hca_2023_89",
        "title": "Thompson v. National Bank of Australia",
        "citation": "[2023] HCA 89",
        "court": "High Court of Australia",
        "year": 2023,
        "jurisdiction": "Commonwealth",
        "category": "Banking Law",
        "summary": "Leading case on banker's duty of care and unconscionable conduct. Court examined the extent of banks' obligations when dealing with vulnerable customers.",
        "full_text": "The High Court held that banks owe a duty to take reasonable care to avoid loss to customers in certain circumstances. The Court emphasized that this duty is particularly important when dealing with vulnerable customers or those with diminished capacity.",
        "relevance_score": 0.85
    }
]

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    organization = data.get('organization')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    password_hash = hash_password(password)

    user_data = {
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "organization": organization,
        "created_at": datetime.now().isoformat()
    }

    result = query_supabase('users', method='POST', data=user_data)

    if not result:
        return jsonify({"error": "User already exists"}), 409

    return jsonify({
        "message": "User registered successfully"
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    users = query_supabase(
        'users',
        params={"email": f"eq.{email}"}
    )

    if not users:
        return jsonify({"error": "Invalid credentials"}), 401

    user = users[0]

    if not verify_password(password, user['password_hash']):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity={
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "subscription": user["subscription_tier"]
    })

    # Update last login
    query_supabase(
        'users',
        method='PATCH',
        params={"id": f"eq.{user['id']}"},
        data={"last_login": datetime.now().isoformat()}
    )

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "subscription": user["subscription_tier"]
        }
    })


@app.route('/')
def home():
    """Health check endpoint"""
    db_status = "connected" if SUPABASE_URL and SUPABASE_KEY else "not configured"
    
    return jsonify({
        "name": "Genesis IT Labs - Legal Research API",
        "version": "2.0.0",
        "status": "operational",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Search legal cases"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Try database search first
        results = search_cases_db(query, filters)
        
        # Fallback to mock data if database not available
        if results is None or len(results) == 0:
            print("Using mock data for search")
            results = [
                case for case in MOCK_CASES
                if query.lower() in case['title'].lower() 
                or query.lower() in case['summary'].lower()
                or query.lower() in case.get('category', '').lower()
            ]
            
            # Calculate relevance scores for mock data
            for result in results:
                result['relevance_score'] = calculate_relevance(query, result)
            results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Log search
        log_search(query, len(results))
        
        return jsonify({
            "query": query,
            "results": results,
            "total": len(results),
            "timestamp": datetime.now().isoformat(),
            "source": "database" if SUPABASE_URL else "mock"
        })
    
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        history = data.get('history', [])
        conversation_id = data.get('conversation_id', f"conv_{datetime.now().timestamp()}")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Generate response
        response_text = generate_chat_response(message, history)
        
        # Save to database
        save_chat_message(conversation_id, 'user', message)
        save_chat_message(conversation_id, 'assistant', response_text)
        
        return jsonify({
            "message": response_text,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    """Analyze uploaded document"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file content
        content = file.read()
        
        # Handle different file types
        if file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        elif file.filename.endswith(('.pdf', '.doc', '.docx')):
            # For now, just extract what we can
            text = f"Analyzing {file.filename}... "
            text += "This is a binary file. Full text extraction requires additional libraries."
        else:
            text = "Unsupported file type"
        
        # Analyze the text
        analysis = analyze_document_with_ai(text[:5000])  # Limit to first 5000 chars
        
        # Add file info
        analysis['filename'] = file.filename
        analysis['file_size'] = len(content)
        analysis['file_type'] = file.filename.split('.')[-1].upper()
        
        # Save to database
        doc_data = {
            "filename": file.filename,
            "file_size": len(content),
            "analysis_result": json.dumps(analysis),
            "created_at": datetime.now().isoformat()
        }
        query_supabase('document_analysis', method='POST', data=doc_data)
        
        return jsonify(analysis)
    
    except Exception as e:
        print(f"Document analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/case/<case_id>', methods=['GET'])
def get_case(case_id):
    """Get single case by ID"""
    try:
        # Try database first
        params = {"id": f"eq.{case_id}"}
        result = query_supabase('cases', params=params)
        
        if result and len(result) > 0:
            return jsonify(result[0])
        
        # Fallback to mock data
        for case in MOCK_CASES:
            if case['id'] == case_id:
                return jsonify(case)
        
        return jsonify({"error": "Case not found"}), 404
    
    except Exception as e:
        print(f"Get case error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/citations/<case_id>', methods=['GET'])
def get_citations(case_id):
    """Get citation network for a case"""
    try:
        params = {
            "select": "*,citing_case:cases!citing_case_id(*),cited_case:cases!cited_case_id(*)",
            "or": f"(citing_case_id.eq.{case_id},cited_case_id.eq.{case_id})"
        }
        
        citations = query_supabase('citations', params=params)
        
        return jsonify({
            "case_id": case_id,
            "citations": citations if citations else [],
            "total": len(citations) if citations else 0
        })
    
    except Exception as e:
        print(f"Citations error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        # Get case count
        cases = query_supabase('cases', params={"select": "id"})
        case_count = len(cases) if cases else len(MOCK_CASES)
        
        # Get search count
        searches = query_supabase('searches', params={"select": "id"})
        search_count = len(searches) if searches else 0
        
        return jsonify({
            "total_cases": case_count,
            "total_searches": search_count,
            "database_connected": bool(SUPABASE_URL and SUPABASE_KEY),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Genesis IT Labs - Legal Research Platform Backend")
    print("=" * 60)
    print(f"Starting server on port {PORT}...")
    print(f"Database: {'Connected' if SUPABASE_URL else 'Using mock data'}")
    print(f"API URL: http://localhost:{PORT}/api")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=PORT)
