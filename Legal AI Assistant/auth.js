document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = "http://127.0.0.1:5002/api/auth";

    // Select Elements
    const authForm = document.getElementById('auth-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMsg = document.getElementById('error-msg');
    const appHeader = document.getElementById('app-header');
    const loginContainer = document.getElementById('login-container');
    const userEmailSpan = document.getElementById('user-email');
    const btnSubmit = document.getElementById('btn-submit');
    const toggleTextContainer = document.getElementById('toggle-text');
    const logoutBtn = document.getElementById('btn-logout');
    const workspace = document.getElementById('workspace');

    let isLoginMode = true;

    /**
     * Helper: Formats the email prefix into a clean Display Name
     * e.g., "john.doe@email.com" -> "John Doe"
     */
    function formatDisplayName(email) {
        if (!email) return "User";
        const namePart = email.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
        return namePart.replace(/\b\w/g, char => char.toUpperCase());
    }

    /**
     * UI Transition: Handles the switch from Login Screen to Dashboard
     */
    function enterApp(email) {
        // 1. Switch body from 'flex' (centering) to 'block' (dashboard scrolling)
        document.body.style.display = "block"; 
        document.body.classList.add('logged-in');

        // 2. Hide Login Interface
        if (loginContainer) loginContainer.style.display = 'none';
        
        // 3. Reveal Header and Workspace
        if (appHeader) appHeader.style.display = 'flex';
        if (workspace) workspace.style.display = 'block'; 
        
        // 4. Personalize the Header
        if (userEmailSpan) userEmailSpan.innerText = formatDisplayName(email);
    }

    // Toggle logic for Login vs Signup
    function setupToggle() {
        const toggleBtn = document.getElementById('btn-toggle');
        if (!toggleBtn) return;
        toggleBtn.onclick = (e) => {
            e.preventDefault();
            isLoginMode = !isLoginMode;
            document.getElementById('form-title').innerText = isLoginMode ? "Unlock Legal Insights" : "Create Account";
            btnSubmit.innerText = isLoginMode ? "Log In" : "Sign Up";
            toggleTextContainer.innerHTML = isLoginMode 
                ? 'Don\'t have an account? <a href="#" id="btn-toggle" class="signup-link">Sign up</a>'
                : 'Already have an account? <a href="#" id="btn-toggle" class="signup-link">Log In</a>';
            setupToggle(); 
        };
    }
    setupToggle();

    // Form Submission Logic
    if (authForm) {
        authForm.onsubmit = async (e) => {
            e.preventDefault();
            errorMsg.style.display = 'none';
            btnSubmit.disabled = true;
            const endpoint = isLoginMode ? "/login" : "/register";
            
            try {
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        email: emailInput.value, 
                        password: passwordInput.value 
                    })
                });

                const result = await response.json();
                if (!response.ok) throw new Error(result.error || "Authentication failed");

                if (isLoginMode) {
                    localStorage.setItem('token', result.access_token);
                    localStorage.setItem('email', result.user.email);
                    enterApp(result.user.email);
                } else {
                    alert("Registration successful! Please log in.");
                    location.reload();
                }
            } catch (err) {
                errorMsg.innerText = err.message;
                errorMsg.style.display = 'block';
            } finally {
                btnSubmit.disabled = false;
            }
        };
    }

    // Logout Logic
    if (logoutBtn) {
        logoutBtn.onclick = () => {
            localStorage.clear();
            location.reload();
        };
    }

    // Session Check: Auto-login if token exists
    const token = localStorage.getItem('token');
    const email = localStorage.getItem('email');
    if (token && email) {
        enterApp(email);
    } else {
        // Ensure body remains flex for login screen centering if no session exists
        document.body.style.display = "flex";
    }
});

// =============================================================================
// GLOBAL MODAL LOGIC (Accessible by onclick in HTML)
// =============================================================================

const roleData = {
    legal: { 
        title: "Legal Professionals", 
        icon: "⚖️", 
        desc: "Harness AI-driven research to analyze case law, statutes, and legal precedents with pinpoint accuracy." 
    },
    tax: { 
        title: "Tax Professionals", 
        icon: "📜", 
        desc: "Stay ahead of regulatory changes with specialized tools for tax compliance and cross-border analysis." 
    },
    audit: { 
        title: "Audit Professionals", 
        icon: "🔍", 
        desc: "Enhance risk detection and verification workflows using intelligent data auditing and reporting modules." 
    },
    accounting: { 
        title: "Accounting Professionals", 
        icon: "📊", 
        desc: "Optimize financial accuracy with advanced forensic accounting and automated reporting tools." 
    }
};

function openModal(role) {
    const data = roleData[role];
    if (!data) return;

    document.getElementById('modal-title').innerText = data.title;
    document.getElementById('modal-icon').innerText = data.icon;
    document.getElementById('modal-description').innerText = data.desc;
    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

// Close modal if user clicks on the blurred background
window.onclick = function(event) {
    const overlay = document.getElementById('modal-overlay');
    if (event.target == overlay) {
        closeModal();
    }
}