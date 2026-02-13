document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = "http://127.0.0.1:5002/api/auth";

    // 1. Select HTML Elements
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
    // NEW: Select the Workspace div
    const workspace = document.getElementById('workspace');

    let isLoginMode = true;

    // 2. Helper Function: Formats name for the UI
    function formatDisplayName(email) {
        if (!email) return "User";
        const namePart = email.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
        return namePart.replace(/\b\w/g, char => char.toUpperCase());
    }

    // 3. UI Transition: Enter the Workspace
    function enterApp(email) {
        // RESET BODY: This ensures the dashboard doesn't stay centered in the middle of the screen
        document.body.style.display = "block"; 

        if (loginContainer) loginContainer.style.display = 'none';
        if (appHeader) appHeader.style.display = 'flex';
        
        // NEW: Make the Welcome Dashboard visible
        if (workspace) workspace.style.display = 'block'; 
        
        if (userEmailSpan) userEmailSpan.innerText = formatDisplayName(email);
    }

    // 4. Setup Toggle Listener (Login <-> Signup)
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

    // 5. Form Submission Logic
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
                
                if (!response.ok) {
                    throw new Error(result.error || "Authentication failed");
                }

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
                console.error("Auth Error:", err);
            } finally {
                btnSubmit.disabled = false;
            }
        };
    }

    // 6. Logout Logic
    if (logoutBtn) {
        logoutBtn.onclick = () => {
            localStorage.clear();
            location.reload();
        };
    }

    // 7. Session Check (Persist login on refresh)
    const token = localStorage.getItem('token');
    const email = localStorage.getItem('email');
    if (token && email) {
        enterApp(email);
    }
});