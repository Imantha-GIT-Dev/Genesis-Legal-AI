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
    const appFooter = document.querySelector('.app-footer'); 

    let isLoginMode = true;

    /**
     * Helper: Formats the email prefix into a clean Display Name
     */
    function formatDisplayName(email) {
        if (!email) return "User";
        const namePart = email.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
        return namePart.replace(/\b\w/g, char => char.toUpperCase());
    }

    /**
     * Large Sidebar Welcome Card logic
     */
    function showWelcomeToast() {
        const toast = document.getElementById('welcome-toast');
        const workspace = document.getElementById('workspace');
        const header = document.getElementById('app-header');
        const arrow = document.querySelector('.next-page-arrow'); 
        
        if (!toast) return;

        toast.style.opacity = '1';
        setTimeout(() => {
            toast.classList.add('show');
            if (workspace) workspace.classList.add('blur-active');
            if (header) header.classList.add('blur-active');
            if (arrow) arrow.classList.add('blur-active'); 
        }, 600);

        setTimeout(() => {
            toast.style.opacity = '0'; 
            toast.classList.remove('show'); 
            
            if (workspace) workspace.classList.remove('blur-active');
            if (header) header.classList.remove('blur-active');
            if (arrow) arrow.classList.remove('blur-active'); 
            
            setTimeout(() => { 
                toast.style.opacity = '1'; 
            }, 1000);
        }, 10000); 
    }

    /**
     * UI Transition: Handles the switch from Login Screen to Dashboard
     */
    function enterApp(email) {
        document.body.style.display = "flex"; 
        document.body.classList.add('logged-in');

        if (loginContainer) loginContainer.style.display = 'none';
        if (appHeader) appHeader.style.display = 'flex';
        if (workspace) workspace.style.display = 'block'; 
        if (appFooter) appFooter.style.display = 'block'; 

        const displayName = formatDisplayName(email);
        if (userEmailSpan) userEmailSpan.innerText = displayName;

        const toastAlreadyShown = sessionStorage.getItem('welcomeShown');
        if (!toastAlreadyShown) {
            showWelcomeToast();
            sessionStorage.setItem('welcomeShown', 'true');
        }
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
                    const displayName = formatDisplayName(result.user.email);
                    localStorage.setItem('username', displayName);
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

    if (logoutBtn) {
        logoutBtn.onclick = () => {
            localStorage.clear();
            sessionStorage.removeItem('welcomeShown');
            if (appFooter) appFooter.style.display = 'none'; 
            location.reload();
        };
    }

    const token = localStorage.getItem('token');
    const email = localStorage.getItem('email');
    if (token && email) {
        enterApp(email);
    } else {
        document.body.style.display = "flex";
        if (appFooter) appFooter.style.display = 'none'; 
    }
});

// =============================================================================
// GLOBAL MODAL LOGIC
// =============================================================================

const roleData = {
    legal: { title: "Legal Professionals", icon: "⚖️", desc: "Harness AI-driven research to analyze case law, statutes, and legal precedents." },
    tax: { title: "Tax Professionals", icon: "📜", desc: "Stay ahead of regulatory changes with specialized tools for tax compliance." },
    audit: { title: "Audit Professionals", icon: "🔍", desc: "Enhance risk detection and verification workflows using intelligent data auditing." },
    accounting: { title: "Accounting Professionals", icon: "📊", desc: "Optimize financial accuracy with advanced forensic accounting tools." }
};

function openModal(role) {
    const data = roleData[role];
    if (!data) return;

    document.getElementById('modal-title').innerText = data.title;
    document.getElementById('modal-icon').innerText = data.icon;
    document.getElementById('modal-description').innerText = data.desc;
    document.getElementById('modal-overlay').style.display = 'flex';

    const portalBtn = document.querySelector('.portal-btn');
    if (portalBtn) {
        portalBtn.onclick = () => window.location.href = 'Genesis.html';
    }
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

window.onclick = function(event) {
    const overlay = document.getElementById('modal-overlay');
    if (event.target == overlay) { closeModal(); }
}

function closeToast() {
    const toast = document.getElementById('welcome-toast');
    const workspace = document.getElementById('workspace');
    const header = document.getElementById('app-header');
    const arrow = document.querySelector('.next-page-arrow'); 

    if (toast) {
        toast.style.opacity = '0';
        toast.classList.remove('show');
    }

    if (workspace) workspace.classList.remove('blur-active');
    if (header) header.classList.remove('blur-active');
    if (arrow) arrow.classList.remove('blur-active'); 
}