from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token
import requests
import bcrypt  # Native bcrypt library

# Load environment variables
load_dotenv()

app = Flask(__name__)

# robust CORS settings to allow frontend communication
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "genesis-super-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 hours

jwt = JWTManager(app)

# =============================================================================
# SECURE PASSWORD HELPERS (Native Bcrypt)
# =============================================================================

def hash_password(password):
    """Securely hash a password. Fixes the 72-byte truncation error."""
    # Convert string to bytes
    pwd_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a plain text password against a stored hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Verification error: {e}")
        return False

# =============================================================================
# DATABASE HELPER
# =============================================================================

def query_supabase(table, method='GET', params=None, data=None):
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
        
        if res.status_code in [200, 201]:
            return res.json()
        else:
            print(f"Supabase Error ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        print(f"\n--- REGISTER ATTEMPT: {email} ---")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # Native bcrypt handles the length correctly
        hashed = hash_password(password)
        
        user_data = {
            "email": email,
            "password_hash": hashed,
            "created_at": datetime.now().isoformat()
        }
        
        result = query_supabase('users', method='POST', data=user_data)
        
        if not result:
            return jsonify({"error": "User already exists or DB connection failed"}), 409
            
        print("✅ Registration successful!")
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        print(f"🔥 Register Crash: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        print(f"\n--- LOGIN ATTEMPT: {email} ---")

        users = query_supabase('users', params={"email": f"eq.{email}"})
        
        if not users:
            return jsonify({"error": "Invalid credentials"}), 401

        user = users[0]
        
        # Verify using native bcrypt helper
        if not verify_password(password, user['password_hash']):
            print("❌ Password mismatch.")
            return jsonify({"error": "Invalid credentials"}), 401

        print("✅ Login successful!")
        token = create_access_token(identity=str(user.get('id')))
        
        return jsonify({
            "access_token": token,
            "user": {
                "email": user['email'],
                "id": user.get('id')
            }
        })
    except Exception as e:
        print(f"🔥 Login Crash: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Server starting on http://127.0.0.1:5002")
    app.run(debug=True, host='127.0.0.1', port=5002)