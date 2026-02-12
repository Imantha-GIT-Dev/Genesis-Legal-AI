// 1. Initialize Supabase Client
const SUPABASE_URL = 'https://bcsmolpvmbhqqanpmiqt.supabase.co'; 
const SUPABASE_KEY = 'sb_publishable_C3uuuKWkT8ik_IqrAa0RRw_l8jKWIkB';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 2. Select HTML Elements
const authForm = document.getElementById('auth-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const submitBtn = document.getElementById('btn-submit');
const formTitle = document.getElementById('form-title');
const errorMsg = document.getElementById('error-msg');
const appHeader = document.getElementById('app-header');
const loginContainer = document.getElementById('login-container');
const userEmailSpan = document.getElementById('user-email');
const logoutBtn = document.getElementById('btn-logout');
const toggleTextContainer = document.getElementById('toggle-text');

// Helper Function: Formats email prefix into a Clean Name
function formatDisplayName(email) {
    // 1. Get part before @ 
    // 2. Replace dots, numbers, or dashes with spaces
    const namePart = email.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
    // 3. Capitalize first letter of each word
    return namePart.replace(/\b\w/g, char => char.toUpperCase());
}

// 3. Handle Form Toggle (Login <-> Signup)
function setupToggleListener() {
    const toggleBtn = document.getElementById('btn-toggle');
    if (!toggleBtn) return;

    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        isLoginMode = !isLoginMode;
        
        if (isLoginMode) {
            formTitle.innerText = "Unlock Legal Insights";
            submitBtn.innerText = "Log In";
            toggleTextContainer.innerHTML = 'Don\'t have an account? <a href="#" id="btn-toggle" class="signup-link">Sign up</a>';
        } else {
            formTitle.innerText = "Create Account";
            submitBtn.innerText = "Sign Up";
            toggleTextContainer.innerHTML = 'Already have an account? <a href="#" id="btn-toggle" class="signup-link">Log In</a>';
        }
        setupToggleListener(); 
    });
}

let isLoginMode = true;
setupToggleListener();

// 4. Handle Form Submit
authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorMsg.style.display = 'none';
    submitBtn.disabled = true;

    const email = emailInput.value;
    const password = passwordInput.value;

    try {
        let data, error;
        if (isLoginMode) {
            const result = await supabaseClient.auth.signInWithPassword({ email, password });
            data = result.data;
            error = result.error;
        } else {
            const result = await supabaseClient.auth.signUp({ email, password });
            data = result.data;
            error = result.error;
            if (!error && data.user) {
                alert("Signup successful! You can now log in.");
            }
        }
        if (error) throw error;
    } catch (err) {
        errorMsg.innerText = err.message;
        errorMsg.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
    }
});

// 5. Handle Logout
logoutBtn.addEventListener('click', async () => {
    await supabaseClient.auth.signOut();
});

// 6. Listen for Auth State Changes (UPDATED TO SHOW NAME)
supabaseClient.auth.onAuthStateChange((event, session) => {
    if (session) {
        console.log("User Logged In:", session.user);
        appHeader.style.display = 'flex'; // Changed to flex for better header layout
        loginContainer.style.display = 'none';
        
        // Use our helper function to show the name
        userEmailSpan.innerText = formatDisplayName(session.user.email);
    } else {
        console.log("User Logged Out");
        appHeader.style.display = 'none';
        loginContainer.style.display = 'block';
    }
});

// 7. Check session on page load (UPDATED TO SHOW NAME)
async function checkSession() {
    const { data: { session } } = await supabaseClient.auth.getSession();
    if (session) {
        appHeader.style.display = 'flex';
        loginContainer.style.display = 'none';
        userEmailSpan.innerText = formatDisplayName(session.user.email);
    }
}
checkSession();