"""
Genesis IT Labs - Legal Research Platform Backend (WITH DATABASE)
Complete backend with Supabase PostgreSQL integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')

# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================

def query_supabase(table, method='GET', params=None, data=None):
    """Query Supabase REST API"""
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
    """Search cases in database"""
    # Build query parameters
    params = {
        "select": "*",
        "order": "year.desc",
        "limit": 20
    }
    
    # Add filters
    if filters:
        if 'category' in filters and filters['category']:
            params['category'] = f"in.({','.join(filters['category'])})"
        if 'jurisdiction' in filters:
            params['jurisdiction'] = f"eq.{filters['jurisdiction']}"
        if 'year_from' in filters:
            params['year'] = f"gte.{filters['year_from']}"
        if 'year_to' in filters:
            params['year'] = f"lte.{filters['year_to']}"
    
    # For text search, use the search function
    if query:
        # Use PostgreSQL full-text search
        params['or'] = f"(title.ilike.%{query}%,summary.ilike.%{query}%,full_text.ilike.%{query}%)"
    
    results = query_supabase('cases', params=params)
    return results if results else []

def get_case_by_id(case_id):
    """Get single case by ID"""
    params = {"id": f"eq.{case_id}"}
    result = query_supabase('cases', params=params)
    return result[0] if result and len(result) > 0 else None

def get_citations(case_id):
    """Get citation network for a case"""
    params = {
        "select": "*, citing_case:cases!citing_case_id(*), cited_case:cases!cited_case_id(*)",
        "or": f"(citing_case_id.eq.{case_id},cited_case_id.eq.{case_id})"
    }
    return query_supabase('citations', params=params) or []

def save_search(query, user_id=None, results_count=0):
    """Save search to analytics"""
    data = {
        "query": query,
        "user_id": user_id,
        "results_count": results_count,
        "created_at": datetime.now().isoformat()
    }
    query_supabase('searches', method='POST', data=data)

def save_chat_message(user_id, conversation_id, role, message, sources=None):
    """Save chat message to history"""
    data = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "role": role,
        "message": message,
        "sources": sources,
        "created_at": datetime.now().isoformat()
    }
    query_supabase('chat_history', method='POST', data=data)

def save_document_analysis(user_id, doc_name, doc_type, analysis_result, risk_score):
    """Save document analysis result"""
    data = {
        "user_id": user_id,
        "document_name": doc_name,
        "document_type": doc_type,
        "analysis_result": analysis_result,
        "risk_score": risk_score,
        "created_at": datetime.now().isoformat()
    }
    return query_supabase('document_analysis', method='POST', data=data)

# =============================================================================
# AI HELPER FUNCTIONS
# =============================================================================

def query_ai(prompt, max_length=500):
    """Query AI using HuggingFace (free tier)"""
    if not HUGGINGFACE_API_KEY:
        return "AI service not configured. Please add HUGGINGFACE_API_KEY to environment."
    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_length,
            "temperature": 0.7,
            "top_p": 0.95,
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
        return f"AI temporarily unavailable (Status: {response.status_code})"
    except Exception as e:
        return f"AI error: {str(e)}"

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/')
def home():
    """API home"""
    return jsonify({
        "name": "Genesis IT Labs - Legal Research API",
        "version": "2.0.0",
        "status": "operational",
        "database": "connected" if SUPABASE_URL else "not configured",
        "ai": "configured" if HUGGINGFACE_API_KEY else "not configured"
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    db_status = "ok" if SUPABASE_URL and query_supabase('cases', params={"limit": "1"}) else "error"
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Search legal database"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        categories = data.get('categories', [])
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Build filters
        db_filters = {}
        if categories:
            db_filters['category'] = categories
        if 'jurisdiction' in filters:
            db_filters['jurisdiction'] = filters['jurisdiction']
        if 'year_from' in filters:
            db_filters['year_from'] = filters['year_from']
        if 'year_to' in filters:
            db_filters['year_to'] = filters['year_to']
        
        # Search database
        results = search_cases_db(query, db_filters)
        
        # Save search for analytics
        save_search(query, results_count=len(results))
        
        # Format results
        formatted_results = []
        for case in results:
            formatted_results.append({
                "id": case['id'],
                "title": case['title'],
                "citation": case['citation'],
                "court": case.get('court', 'Unknown Court'),
                "year": case.get('year'),
                "category": case.get('category'),
                "summary": case.get('summary', ''),
                "jurisdiction": case.get('jurisdiction'),
                "relevance_score": 0.95  # You can implement actual scoring
            })
        
        return jsonify({
            "query": query,
            "results": formatted_results,
            "total": len(formatted_results),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/case/<case_id>')
def get_case(case_id):
    """Get single case details"""
    try:
        case = get_case_by_id(case_id)
        if not case:
            return jsonify({"error": "Case not found"}), 404
        
        return jsonify({
            "case": case,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/citations/<case_id>')
def get_case_citations(case_id):
    """Get citation network for a case"""
    try:
        citations = get_citations(case_id)
        
        # Format related cases
        related = []
        for citation in citations:
            if citation.get('citing_case_id') == case_id:
                # This case cites another
                related.append({
                    "case": citation.get('cited_case'),
                    "relationship": "cites",
                    "type": citation.get('citation_type')
                })
            else:
                # Another case cites this one
                related.append({
                    "case": citation.get('citing_case'),
                    "relationship": "cited_by",
                    "type": citation.get('citation_type')
                })
        
        return jsonify({
            "case_id": case_id,
            "related_cases": related,
            "total": len(related),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-research', methods=['POST'])
def ai_research():
    """AI-assisted research"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # Search relevant cases
        relevant_cases = search_cases_db(question)[:3]
        
        # Build context
        context = "\n\n".join([
            f"Case: {case['title']} {case['citation']}\nSummary: {case.get('summary', '')}"
            for case in relevant_cases
        ])
        
        # Create AI prompt
        prompt = f"""You are a legal research assistant. Answer this question based on the provided cases:

Question: {question}

Relevant Cases:
{context}

Provide a detailed answer with citations:"""
        
        # Query AI
        ai_answer = query_ai(prompt, max_length=800)
        
        return jsonify({
            "question": question,
            "answer": ai_answer,
            "sources": [
                {
                    "title": case['title'],
                    "citation": case['citation'],
                    "id": case['id']
                }
                for case in relevant_cases
            ],
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    """Analyze legal document"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        doc_type = data.get('type', 'contract')
        doc_name = data.get('name', 'Untitled')
        user_id = data.get('user_id')
        
        if not text:
            return jsonify({"error": "Document text is required"}), 400
        
        # Simple analysis (you can enhance with AI)
        issues = []
        risk_score = 0
        
        # Check for common issues
        text_lower = text.lower()
        
        if 'force majeure' not in text_lower:
            issues.append({
                "type": "missing_clause",
                "severity": "high",
                "description": "No force majeure provisions found",
                "recommendation": "Add force majeure clause to protect against unforeseen circumstances",
                "location": "N/A"
            })
            risk_score += 2
        
        if 'indemnif' not in text_lower:
            issues.append({
                "type": "missing_clause",
                "severity": "medium",
                "description": "Indemnification provisions may be insufficient",
                "recommendation": "Review and strengthen indemnification clauses",
                "location": "N/A"
            })
            risk_score += 1.5
        
        if 'termination' not in text_lower:
            issues.append({
                "type": "unclear_terms",
                "severity": "high",
                "description": "Termination conditions not clearly specified",
                "recommendation": "Add clear termination provisions with notice periods",
                "location": "N/A"
            })
            risk_score += 2
        
        if 'dispute resolution' not in text_lower and 'arbitration' not in text_lower:
            issues.append({
                "type": "missing_clause",
                "severity": "medium",
                "description": "No dispute resolution mechanism specified",
                "recommendation": "Add arbitration or mediation clause",
                "location": "N/A"
            })
            risk_score += 1
        
        # Calculate final risk score (0-10)
        risk_score = min(risk_score, 10)
        
        analysis_result = {
            "issues": issues,
            "risk_assessment": {
                "high": [i['description'] for i in issues if i['severity'] == 'high'],
                "medium": [i['description'] for i in issues if i['severity'] == 'medium'],
                "low": [i['description'] for i in issues if i['severity'] == 'low']
            },
            "suggestions": [issue['recommendation'] for issue in issues],
            "risk_score": risk_score
        }
        
        # Save to database
        if user_id:
            save_document_analysis(user_id, doc_name, doc_type, analysis_result, risk_score)
        
        return jsonify({
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        user_id = data.get('user_id')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Search for relevant cases based on message
        relevant_cases = search_cases_db(message)[:2]
        
        # Build context
        context = ""
        if relevant_cases:
            context = "Relevant cases:\n" + "\n".join([
                f"- {case['title']} {case['citation']}"
                for case in relevant_cases
            ])
        
        # Create AI response
        prompt = f"""You are a helpful legal research assistant. Respond to: "{message}"

{context}

Provide a helpful, conversational response:"""
        
        ai_response = query_ai(prompt, max_length=500)
        
        # Save chat history
        if user_id:
            save_chat_message(user_id, conversation_id, 'user', message)
            save_chat_message(user_id, conversation_id, 'assistant', ai_response, 
                            sources=[c['id'] for c in relevant_cases])
        
        return jsonify({
            "message": ai_response,
            "conversation_id": conversation_id,
            "sources": [
                {"title": c['title'], "citation": c['citation'], "id": c['id']}
                for c in relevant_cases
            ],
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get platform statistics"""
    try:
        # Get counts from database
        cases_count = len(query_supabase('cases', params={"select": "id"}) or [])
        searches_count = len(query_supabase('searches', params={"select": "id"}) or [])
        
        return jsonify({
            "total_cases": cases_count,
            "total_searches": searches_count,
            "categories": ["Employment Law", "Contract Law", "Tort Law", "Property Law"],
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
