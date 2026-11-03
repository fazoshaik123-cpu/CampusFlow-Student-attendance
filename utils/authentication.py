"""
=============================================================================
CampusFlow – Authentication Module
Supports Supabase Cloud Authentication with Graceful Missing-Secret Handling
and Explicit Local Academic Demo Mode.
=============================================================================
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Try importing supabase without crashing if library is absent
try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False


def safe_get_credential(key_names):
    """
    Safely retrieves a configuration value from environment variables (.env)
    or st.secrets without raising StreamlitSecretNotFoundError or crashing.
    """
    if isinstance(key_names, str):
        key_names = [key_names]

    # 1. Check OS environment variables
    for k in key_names:
        val = os.getenv(k)
        if val and str(val).strip():
            return str(val).strip()

    # 2. Safely attempt reading from st.secrets without triggering unhandled exceptions
    try:
        secrets_obj = getattr(st, "secrets", None)
        if secrets_obj is not None:
            for k in key_names:
                try:
                    if k in secrets_obj:
                        val = secrets_obj[k]
                        if val and str(val).strip():
                            return str(val).strip()
                except Exception:
                    # Catches StreamlitSecretNotFoundError, FileNotFoundError, KeyError
                    pass
    except Exception:
        pass

    return None


def is_valid_supabase_url(url):
    """Validates if the provided URL looks like a real Supabase endpoint."""
    if not url:
        return False
    u = url.strip().lower()
    if not (u.startswith("https://") or u.startswith("http://")):
        return False
    # Check for placeholder strings
    placeholders = ["your-project-id", "your-project", "example.supabase.co", "<", ">", "placeholder"]
    return not any(p in u for p in placeholders)


def is_valid_supabase_key(key):
    """Validates if the provided key is non-empty and not a placeholder."""
    if not key:
        return False
    k = key.strip()
    placeholders = ["your-anon-public-key", "your-anon-key", "your-key", "<", ">", "placeholder"]
    return not any(p in k.lower() for p in placeholders) and len(k) > 10


def get_supabase_client():
    """
    Retrieves or initializes the Supabase client safely.
    Never hardcodes fake credentials and never crashes if secrets are missing.
    Returns (client, is_connected: bool, status_message: str)
    """
    if "supabase_client" in st.session_state and st.session_state.supabase_client is not None:
        return st.session_state.supabase_client, True, "Connected to Supabase Cloud"

    url = safe_get_credential(["SUPABASE_URL"])
    key = safe_get_credential(["SUPABASE_ANON_KEY", "SUPABASE_KEY"])

    # If credentials are not supplied or are placeholders, do not attempt network call
    if not url or not key:
        return None, False, "Supabase credentials (SUPABASE_URL and SUPABASE_ANON_KEY) are not configured."

    if not is_valid_supabase_url(url) or not is_valid_supabase_key(key):
        return None, False, "Supabase credentials contain template placeholders. Valid production keys required."

    if not HAS_SUPABASE_LIB:
        return None, False, "The 'supabase' Python library is not installed in the active environment."

    try:
        client: Client = create_client(url, key)
        st.session_state.supabase_client = client
        return client, True, "Connected to Supabase Cloud Authentication"
    except Exception as e:
        return None, False, f"Supabase Connection Failed: {str(e)}"


def init_auth_state():
    """Initializes session state keys for authentication."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "demo_mode_enabled" not in st.session_state:
        st.session_state.demo_mode_enabled = False
    if "mock_users" not in st.session_state:
        # Default academic test accounts for simulated local demo
        st.session_state.mock_users = {
            "admin@campusflow.edu": {
                "password": "admin123",
                "name": "Prof. Administrator",
                "role": "Lead Faculty / Admin",
                "verified": True
            },
            "evaluator@college.edu": {
                "password": "college2026",
                "name": "Project Evaluator",
                "role": "Academic Examiner",
                "verified": True
            },
            "student@campusflow.edu": {
                "password": "student123",
                "name": "Student Researcher",
                "role": "Data Analyst",
                "verified": True
            }
        }


def sign_in_user(email, password, is_demo=False):
    """
    Authenticates a user via Supabase Cloud or explicitly enabled Demo Mode.
    Returns (success: bool, message: str, user_data: dict)
    """
    init_auth_state()
    email = email.strip().lower()

    # 1. Explicit Demo Mode Authentication
    if is_demo or st.session_state.demo_mode_enabled:
        if email in st.session_state.mock_users:
            record = st.session_state.mock_users[email]
            if record["password"] == password:
                user_info = {
                    "email": email,
                    "id": f"demo_{email.split('@')[0]}",
                    "name": record["name"],
                    "role": record["role"],
                    "is_demo": True,
                    "provider": "Simulated Academic Demo Mode"
                }
                st.session_state.authenticated = True
                st.session_state.user = user_info
                return True, "Authenticated in Demo Mode (Simulated Auth).", user_info
            return False, "Invalid password for demo account.", None
        return False, "Demo account not found. Please register or use a preset demo account.", None

    # 2. Real Supabase Cloud Authentication
    client, is_connected, err_msg = get_supabase_client()
    if is_connected and client:
        try:
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if response.user:
                user_info = {
                    "email": response.user.email,
                    "id": response.user.id,
                    "name": response.user.user_metadata.get("full_name", email.split("@")[0]),
                    "role": response.user.user_metadata.get("role", "Authenticated Researcher"),
                    "is_demo": False,
                    "provider": "Supabase Cloud"
                }
                st.session_state.authenticated = True
                st.session_state.user = user_info
                return True, "Successfully logged in via Supabase Cloud!", user_info
        except Exception as e:
            return False, f"Supabase Authentication Error: {str(e)}", None

    return False, f"Supabase is not configured ({err_msg}). Enable Demo Mode for local testing.", None


def sign_up_user(email, password, full_name, role="Student Analyst", is_demo=False):
    """
    Registers a new user in Supabase or in local demo store.
    Returns (success: bool, message: str)
    """
    init_auth_state()
    email = email.strip().lower()

    if is_demo or st.session_state.demo_mode_enabled:
        if email in st.session_state.mock_users:
            return False, "A demo account with this email already exists."
        st.session_state.mock_users[email] = {
            "password": password,
            "name": full_name,
            "role": role,
            "verified": True
        }
        return True, f"Simulated demo account registered for {full_name}! You may now sign in."

    client, is_connected, err_msg = get_supabase_client()
    if is_connected and client:
        try:
            response = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": role
                    }
                }
            })
            if response.user:
                return True, "Registration successful via Supabase! Verification instructions sent to email."
        except Exception as e:
            return False, f"Supabase Registration Error: {str(e)}"

    return False, f"Supabase is not configured ({err_msg}). Enable Demo Mode for local testing."


def reset_user_password(email, is_demo=False):
    """
    Handles password recovery.
    Returns (success: bool, message: str)
    """
    init_auth_state()
    email = email.strip().lower()

    if is_demo or st.session_state.demo_mode_enabled:
        if email in st.session_state.mock_users:
            rec = st.session_state.mock_users[email]
            return True, f"[Demo Simulation] Password for {email} is: '{rec['password']}'."
        return False, "Email address not found in demo records."

    client, is_connected, err_msg = get_supabase_client()
    if is_connected and client:
        try:
            client.auth.reset_password_for_email(email)
            return True, "Password reset link sent to your registered email via Supabase."
        except Exception as e:
            return False, f"Supabase Reset Error: {str(e)}"

    return False, f"Supabase is not configured. Enable Demo Mode for local testing."


def logout_user():
    """Logs out current user and clears session state."""
    init_auth_state()
    client, is_connected, _ = get_supabase_client()
    if is_connected and client:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    st.session_state.authenticated = False
    st.session_state.user = None


def render_auth_interface():
    """
    Renders the authentication interface.
    Handles missing Supabase credentials gracefully without throwing StreamlitSecretNotFoundError.
    Offers an explicit Local Demo Mode for academic coursework evaluation.
    Returns True if user is authenticated, False otherwise.
    """
    init_auth_state()
    if st.session_state.authenticated:
        return True

    client, is_connected, conn_status = get_supabase_client()

    col_l, col_center, col_r = st.columns([1, 2.2, 1])
    with col_center:
        # CampusFlow Header
        st.markdown("""
            <div style="text-align: center; margin-bottom: 22px;">
                <div style="font-size: 3.2rem; margin-bottom: 4px;">🎓</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">CampusFlow</div>
                <div style="font-size: 0.95rem; color: #6366F1; font-weight: 700;">Multi-Format Data Wrangling & Preprocessing System</div>
                <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">College Academic Project • Data Wrangling and Preprocessing</div>
            </div>
        """, unsafe_allow_html=True)

        # SCENARIO 1: SUPABASE CREDENTIALS ARE CONFIGURED & CONNECTED
        if is_connected:
            st.markdown("""
                <div style="background-color: #17233B; border: 1px solid #10B981; border-radius: 8px; padding: 10px 14px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem;">
                    <span style="color: #CBD5E1;">Auth Status:</span>
                    <span style="color: #10B981; font-weight: 700;">🟢 Supabase Cloud Active</span>
                </div>
            """, unsafe_allow_html=True)

            tab_login, tab_signup, tab_forgot = st.tabs(["🔑 Cloud Sign In", "📝 Create Account", "🔄 Password Reset"])

            with tab_login:
                st.markdown("<p style='color:#CBD5E1; font-size:0.88rem;'>Sign in with your verified Supabase Cloud credentials:</p>", unsafe_allow_html=True)
                with st.form("supabase_login_form"):
                    email = st.text_input("Email Address", placeholder="name@college.edu")
                    show_pw = st.checkbox("Show password", key="sb_show_pw")
                    password = st.text_input("Password", type="text" if show_pw else "password", placeholder="Password")
                    submit = st.form_submit_button("🚀 Sign In via Supabase Cloud", use_container_width=True)

                if submit:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        success, msg, _ = sign_in_user(email, password, is_demo=False)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            with tab_signup:
                st.markdown("<p style='color:#CBD5E1; font-size:0.88rem;'>Register a new user in Supabase Auth:</p>", unsafe_allow_html=True)
                with st.form("supabase_signup_form"):
                    name = st.text_input("Full Name", placeholder="Dr. Priya Sharma")
                    reg_email = st.text_input("Email", placeholder="name@college.edu")
                    reg_role = st.selectbox("Role", ["Student Analyst", "Faculty Researcher", "Department Head", "External Auditor"])
                    show_reg_pw = st.checkbox("Show password", key="sb_reg_show_pw")
                    reg_pw = st.text_input("Password", type="text" if show_reg_pw else "password", placeholder="Min 6 characters")
                    submit_reg = st.form_submit_button("✨ Register in Supabase", use_container_width=True)

                if submit_reg:
                    if not name or not reg_email or not reg_pw:
                        st.error("Please fill in all registration fields.")
                    else:
                        success, msg = sign_up_user(reg_email, reg_pw, name, reg_role, is_demo=False)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

            with tab_forgot:
                st.markdown("<p style='color:#CBD5E1; font-size:0.88rem;'>Request password recovery via Supabase:</p>", unsafe_allow_html=True)
                with st.form("supabase_reset_form"):
                    rec_email = st.text_input("Registered Email", placeholder="name@college.edu")
                    submit_rec = st.form_submit_button("📧 Send Password Recovery Link", use_container_width=True)

                if submit_rec:
                    if not rec_email:
                        st.error("Please enter an email address.")
                    else:
                        success, msg = reset_user_password(rec_email, is_demo=False)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

        # SCENARIO 2: SUPABASE CREDENTIALS MISSING -> DISPLAY CLEAR CONFIG SCREEN & EXPLICIT DEMO MODE
        else:
            # Notice box explaining missing configuration gracefully
            st.markdown(f"""
                <div style="background-color: #17233B; border: 1px solid #F59E0B; border-left: 5px solid #F59E0B; border-radius: 8px; padding: 16px 18px; margin-bottom: 20px;">
                    <div style="font-weight: 700; color: #F59E0B; font-size: 1.05rem; margin-bottom: 4px;">
                        ⚠️ Supabase Authentication Not Configured
                    </div>
                    <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                        No valid Supabase project credentials were found in <code>.streamlit/secrets.toml</code> or <code>.env</code>.<br>
                        The application has caught this gracefully and prevented a system crash.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Option A: Explicit Demo Mode for Academic Evaluation
            st.markdown("""
                <div style="background-color: #111A2E; border: 1px solid #2A3B5C; border-radius: 8px; padding: 16px 18px; margin-bottom: 20px;">
                    <div style="font-weight: 700; color: #6366F1; font-size: 1.0rem; margin-bottom: 4px;">
                        🚀 Local Academic Demo Mode (Offline Testing)
                    </div>
                    <div style="color: #94A3B8; font-size: 0.84rem; margin-bottom: 12px;">
                        Enable local simulated authentication to test all Data Wrangling & Preprocessing features without an external cloud connection.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            enable_demo = st.checkbox(
                "✅ Explicitly Enable Local Academic Demo Mode (Simulated Auth)",
                value=st.session_state.demo_mode_enabled,
                key="chk_enable_demo"
            )
            st.session_state.demo_mode_enabled = enable_demo

            if enable_demo:
                # Prominent Simulated Auth Disclaimer
                st.markdown("""
                    <div style="background-color: rgba(245, 158, 11, 0.12); border: 1px solid #F59E0B; border-radius: 8px; padding: 12px 14px; margin-bottom: 16px;">
                        <div style="color: #FCD34D; font-weight: 700; font-size: 0.86rem; margin-bottom: 2px;">
                            ⚠️ SIMULATED AUTHENTICATION NOTICE
                        </div>
                        <div style="color: #FDE68A; font-size: 0.80rem; line-height: 1.4;">
                            Authentication is simulated locally in session memory for academic evaluation.
                            <b>This is NOT connected to Supabase Cloud and must NOT be treated as real secure authentication.</b>
                            Do not use real, sensitive, or production passwords.
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                demo_tab_in, demo_tab_up, demo_tab_rec = st.tabs(["🔑 Demo Sign In", "📝 Create Demo Account", "🔄 Password Help"])

                with demo_tab_in:
                    with st.form("demo_login_form"):
                        demo_email = st.text_input("Demo Email Address", placeholder="e.g. admin@campusflow.edu")
                        show_d_pw = st.checkbox("Show password", key="demo_show_pw")
                        demo_pw = st.text_input("Demo Password", type="text" if show_d_pw else "password", placeholder="Enter demo password")
                        submit_demo = st.form_submit_button("🚀 Enter CampusFlow Dashboard (Demo)", use_container_width=True)

                    if submit_demo:
                        if not demo_email or not demo_pw:
                            st.error("Please provide both email and password.")
                        else:
                            success, msg, _ = sign_in_user(demo_email, demo_pw, is_demo=True)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                    # Quick 1-click test credentials for evaluators
                    st.markdown("<p style='color:#94A3B8; font-size:0.80rem; margin-top:10px; margin-bottom:4px;'>Quick-fill preset academic accounts:</p>", unsafe_allow_html=True)
                    qc1, qc2, qc3 = st.columns(3)
                    if qc1.button("Fill Admin", use_container_width=True):
                        sign_in_user("admin@campusflow.edu", "admin123", is_demo=True)
                        st.rerun()
                    if qc2.button("Fill Evaluator", use_container_width=True):
                        sign_in_user("evaluator@college.edu", "college2026", is_demo=True)
                        st.rerun()
                    if qc3.button("Fill Student", use_container_width=True):
                        sign_in_user("student@campusflow.edu", "student123", is_demo=True)
                        st.rerun()

                with demo_tab_up:
                    with st.form("demo_reg_form"):
                        d_name = st.text_input("Full Name", placeholder="e.g. Alex Johnson")
                        d_email = st.text_input("Academic Email", placeholder="e.g. alex@college.edu")
                        d_role = st.selectbox("Designation", ["Student Analyst", "Faculty Researcher", "Department Head", "External Auditor"])
                        d_pw = st.text_input("Create Password", type="password")
                        submit_d_reg = st.form_submit_button("✨ Register Demo User", use_container_width=True)

                    if submit_d_reg:
                        if not d_name or not d_email or not d_pw:
                            st.error("Please fill in all fields.")
                        else:
                            success, msg = sign_up_user(d_email, d_pw, d_name, d_role, is_demo=True)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)

                with demo_tab_rec:
                    st.markdown("<p style='color:#CBD5E1; font-size:0.85rem;'>Preset demo accounts available:</p>", unsafe_allow_html=True)
                    st.code("""
admin@campusflow.edu      -> admin123
evaluator@college.edu     -> college2026
student@campusflow.edu    -> student123
                    """)

            # Option B: Expandable Instructions to configure .streamlit/secrets.toml
            with st.expander("📖 Instructions to Configure Real Supabase Authentication (.streamlit/secrets.toml & .env)", expanded=not enable_demo):
                st.markdown("""
                ### How to Configure Real Supabase Cloud Authentication:

                #### Method 1: Using `.streamlit/secrets.toml` (Recommended for Streamlit)
                1. Create a folder named `.streamlit` in your project root if it does not exist:
                2. Inside `.streamlit`, create a file named `secrets.toml`:
                3. Add your actual Supabase Project URL and Anon Public Key:

                ```toml
                # .streamlit/secrets.toml
                SUPABASE_URL = "https://your-project-id.supabase.co"
                SUPABASE_ANON_KEY = "your-actual-anon-public-key"
                ```

                ---

                #### Method 2: Using `.env` (Environment Variables)
                Create a `.env` file in the project root:

                ```ini
                # .env
                SUPABASE_URL=https://your-project-id.supabase.co
                SUPABASE_ANON_KEY=your-actual-anon-public-key
                ```

                ---

                #### Where to find these keys in Supabase:
                1. Log in to [supabase.com](https://supabase.com) and select your project.
                2. Navigate to **Project Settings** (gear icon) $\\rightarrow$ **API**.
                3. Copy the **Project URL** and the **`anon` `public` API Key**.
                4. Restart Streamlit or refresh the browser. CampusFlow will automatically detect the credentials and activate live cloud authentication.
                """)

    return False
