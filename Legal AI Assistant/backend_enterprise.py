from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
import requests
import bcrypt
from dotenv import load_dotenv
from flask_jwt_extended import (
    JWTManager, 
    create_access_token, 
    jwt_required, 
    get_jwt_identity
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Robust CORS for frontend-backend communication
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "genesis-production-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 hours

jwt = JWTManager(app)

# =============================================================================
# SECURE PASSWORD HELPERS
# =============================================================================

def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(password, hashed_password):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# =============================================================================
# UNIFIED DATABASE HELPER
# =============================================================================

def query_supabase(table, method='GET', params=None, data=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Supabase credentials missing!")
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
            res = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            res = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            res = requests.patch(url, headers=headers, json=data, params=params)
        
        if res.status_code in [200, 201]:
            return res.json()
        print(f"⚠️ Supabase {res.status_code}: {res.text}")
        return None
    except Exception as e:
        print(f"🔥 DB Connection Error: {e}")
        return None

# =============================================================================
# LEGAL AI LOGIC (From Version 1)
# =============================================================================

def calculate_relevance(query, case):
    query_lower = query.lower()
    score = 0
    title = case.get('title', '').lower()
    summary = case.get('summary', '').lower()
    
    if query_lower in title: score += 0.5
    if query_lower in summary: score += 0.3
    
    words = query_lower.split()
    word_count = sum(1 for w in words if w in title or w in summary)
    score += (word_count / max(len(words), 1)) * 0.2
    return min(score, 1.0)

def analyze_document_text(text):
    text_lower = text.lower()
    issues = []
    if 'breach' in text_lower: issues.append({"type": "Contractual Breach", "severity": "HIGH"})
    if 'liability' in text_lower: issues.append({"type": "Liability Risk", "severity": "MEDIUM"})
    
    return {
        "summary": f"Analysis of {len(text.split())} words completed.",
        "issues": issues,
        "word_count": len(text.split())
    }

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    hashed = hash_password(password)
    user_data = {"email": email, "password_hash": hashed, "created_at": datetime.now().isoformat()}
    
    result = query_supabase('users', method='POST', data=user_data)
    if not result:
        return jsonify({"error": "User already exists or DB error"}), 409
    return jsonify({"message": "User created"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    
    users = query_supabase('users', params={"email": f"eq.{email}"})
    if not users or not verify_password(password, users[0]['password_hash']):
        return jsonify({"error": "Invalid credentials"}), 401

    user = users[0]
    token = create_access_token(identity=str(user.get('id')))
    return jsonify({"access_token": token, "user": {"email": user['email'], "id": user['id']}})

@app.route('/api/search', methods=['POST'])
@jwt_required()
def search():
    data = request.get_json()
    query = data.get('query', '')
    
    # In a real app, you'd query the 'cases' table. 
    # If it's empty, this returns an empty list.
    results = query_supabase('cases', params={"select": "*"}) or []
    
    # Filter and Score
    filtered = [r for r in results if query.lower() in r.get('title', '').lower()]
    for r in filtered:
        r['relevance_score'] = calculate_relevance(query, r)
        
    return jsonify({"results": sorted(filtered, key=lambda x: x['relevance_score'], reverse=True)})

@app.route('/api/analyze-document', methods=['POST'])
@jwt_required()
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    # Basic text extraction for .txt
    content = file.read().decode('utf-8', errors='ignore')
    analysis = analyze_document_text(content)
    
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)