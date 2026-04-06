import os
import sys
import time
from datetime import datetime

import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from backend.backup_manager import run_backup
from backend.performance_monitor import load_metrics, compute_derived_metrics
from backend.logger import LOG_FILE

DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")


st.set_page_config(page_title="Multi-Cloud Hybrid Backup", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Space Grotesk', sans-serif;
        }

        .stApp {
            background: radial-gradient(1200px 800px at 20% -10%, #3f2b50 0%, rgba(63,43,80,0) 55%),
                        radial-gradient(1000px 600px at 110% 10%, #134e4a 0%, rgba(19,78,74,0) 55%),
                        linear-gradient(180deg, #111827 0%, #0b1220 100%);
        }

        .block-container {
            padding-top: 0.35rem;
        }

        .top-brand {
            color: #e8f1fb;
            font-size: 38px;
            font-weight: 700;
            letter-spacing: -0.2px;
            line-height: 1;
            margin-top: 2px;
        }

        .top-brand-dot {
            color: #ffd95a;
        }

        .nav-divider {
            height: 2px;
            margin: 8px 0 14px 0;
            background: linear-gradient(90deg, rgba(255, 217, 90, 0.9) 0%, rgba(255, 217, 90, 0.2) 100%);
            border-radius: 999px;
        }

        .hero {
            padding: 18px 22px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(18,25,38,0.9) 0%, rgba(20,45,58,0.85) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 40px rgba(0,0,0,0.35);
        }

        .hero-title {
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #eaf0ff;
        }

        .hero-subtitle {
            color: #a8b3c7;
            font-size: 15px;
            margin-top: 4px;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(77, 205, 123, 0.15);
            color: #6be18f;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(107, 225, 143, 0.35);
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #e6ecf8;
            margin: 6px 0 10px 0;
        }

        .card {
            padding: 16px;
            border-radius: 16px;
            background: rgba(17, 25, 40, 0.85);
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow: 0 12px 24px rgba(0,0,0,0.25);
        }

        .kpi {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }

        .kpi .label {
            color: #a9b7d0;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .kpi .value {
            color: #eaf0ff;
            font-size: 24px;
            font-weight: 700;
        }

        .kpi .delta {
            color: #6be18f;
            font-size: 12px;
            font-weight: 600;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 8px;
            background: rgba(110, 170, 255, 0.15);
            color: #8dbbff;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(110, 170, 255, 0.35);
        }

        .panel {
            padding: 18px;
            border-radius: 14px;
            background: rgba(10, 16, 26, 0.9);
            border: 1px solid rgba(255,255,255,0.06);
        }

        .muted {
            color: #8c99b2;
            font-size: 13px;
        }

        .glow {
            animation: pulse 3.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 rgba(107, 225, 143, 0.0); }
            50% { box-shadow: 0 0 24px rgba(107, 225, 143, 0.25); }
            100% { box-shadow: 0 0 0 rgba(107, 225, 143, 0.0); }
        }

        .file-table {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
        }

        .stButton>button {
            background: linear-gradient(120deg, #3a7bd5, #00d2ff);
            color: #0b111a;
            font-weight: 700;
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
        }

        .stButton>button:hover {
            filter: brightness(1.05);
        }

        .stTextInput>div>div>input {
            border-radius: 10px;
        }

        /* Hide browser-native password reveal controls to avoid duplicate eye icon */
        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear {
            display: none;
        }

        .stFileUploader>div>div {
            border-radius: 12px;
            border: 1px dashed rgba(255,255,255,0.2);
            background: rgba(12, 20, 32, 0.6);
        }

        .stTextArea textarea {
            border-radius: 12px;
            background: rgba(12, 20, 32, 0.6);
        }

        .stSidebar {
            background: linear-gradient(180deg, #0b111a 0%, #0d1622 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        .stSidebar .block-container {
            padding-top: 28px;
        }

        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #e6ecf8;
            font-weight: 700;
            letter-spacing: 0.2px;
        }

        .stSidebar [data-testid=\"stRadio\"] label {
            font-weight: 600;
            color: #d7e2f7;
        }

        .stSidebar [data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label {
            padding: 8px 12px;
            border-radius: 10px;
            margin-bottom: 6px;
            background: rgba(17, 25, 40, 0.5);
            border: 1px solid rgba(255,255,255,0.06);
        }

        .stSidebar [data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label:hover {
            background: rgba(35, 52, 82, 0.65);
            border: 1px solid rgba(110, 170, 255, 0.35);
        }

        .stSidebar [data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label span {
            color: #e6ecf8;
        }

        /* Hide Streamlit top bar/header */
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {
            display: none;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label {
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(17, 25, 40, 0.65);
            border: 1px solid rgba(255,255,255,0.08);
            transition: all 0.2s ease;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label:hover {
            background: rgba(58, 123, 213, 0.2);
            border-color: rgba(58, 123, 213, 0.5);
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label span {
            color: #e6ecf8;
            font-weight: 600;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] {
            gap: 10px;
            justify-content: flex-end;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label {
            padding: 4px 8px;
            background: transparent;
            border: none;
            border-radius: 4px;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label:hover {
            background: rgba(255, 255, 255, 0.08);
            border: none;
        }

        div[data-testid=\"stRadio\"] div[role=\"radiogroup\"] > label span {
            font-size: 11px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #eaf0ff;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "Home Dashboard"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "users" not in st.session_state:
    st.session_state.users = {}


def render_auth_gateway() -> None:
    st.markdown(
        """
        <style>
            .auth-shell {
                padding-top: 28px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                max-width: 560px;
                margin: 0 auto;
                padding: 18px 18px 14px 18px;
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid rgba(255,255,255,0.08);
                box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTabs"],
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stForm"] {
                max-width: 100%;
                margin: 0 auto;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stForm"] .stButton {
                display: flex;
                justify-content: center;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stForm"] .stButton > button {
                margin: 0 auto;
                display: block;
                width: 220px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="input"] {
                background: #0b1220;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 10px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="input"] input {
                color: #e2e8f0;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="input"]:focus-within {
                border-color: rgba(59, 130, 246, 0.85);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stForm"] label {
                font-weight: 600;
                color: #cfd8ea;
                letter-spacing: 0.15px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTabs"] > div[role="tablist"] {
                display: flex;
                justify-content: center;
                gap: 8px;
                border-bottom: 1px solid rgba(255,255,255,0.08);
                padding-bottom: 8px;
                margin-bottom: 14px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTabs"] button[role="tab"] {
                background: transparent;
                border: none;
                color: #9fb0cc;
                padding: 6px 10px;
                font-weight: 600;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                color: #e6f0ff;
                border-bottom: 2px solid #3b82f6;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stForm"] button {
                min-width: 180px;
                border-radius: 10px;
            }

            .auth-title {
                text-align: center;
                font-size: 26px;
                font-weight: 700;
                color: #e6f0ff;
                margin-bottom: 6px;
            }

            .auth-subtitle {
                text-align: center;
                color: #9fb0cc;
                font-size: 14px;
                margin-bottom: 14px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1.2, 1.5, 1.2])
    with center_col:
        st.markdown("<div class='auth-shell'></div>", unsafe_allow_html=True)
        auth_container = st.container(border=True)
        with auth_container:
            st.markdown("<div class='auth-title'>Welcome Back</div>", unsafe_allow_html=True)
            st.markdown("<div class='auth-subtitle'>Please sign in or login first.</div>", unsafe_allow_html=True)
            login_tab, register_tab = st.tabs(["Login", "Register"])

            with login_tab:
                with st.form("login_form", enter_to_submit=False):
                    username = st.text_input("User Name", placeholder="e.g. username")
                    password = st.text_input("Password", type="password", placeholder="Your password")
                    submitted = st.form_submit_button("Login")

                if submitted:
                    user_record = st.session_state.users.get(username)
                    if not user_record:
                        st.error("Account not found. Please register first.")
                    elif user_record != password:
                        st.error("Incorrect password. Please try again.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.page = "Home Dashboard"
                        st.success("Login successful. Redirecting to the dashboard...")
                        st.rerun()

            with register_tab:
                with st.form("register_form", enter_to_submit=False):
                    new_username = st.text_input("Choose a User Name")
                    new_password = st.text_input("Create a Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    submitted = st.form_submit_button("Register")

                if submitted:
                    if not new_username or not new_password:
                        st.error("Please fill in all fields.")
                    elif new_username in st.session_state.users:
                        st.error("That username is already taken.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        st.session_state.users[new_username] = new_password
                        st.success("Registration complete. Please login to continue.")
                        st.toast("Registration successful.", icon="✅")


if not st.session_state.authenticated:
    render_auth_gateway()
    st.stop()

NAV_OPTIONS = {
    "Home Dashboard": "Home Dashboard",
    "Upload Chain Files": "Upload Supply Chain Files",
    "Start Backup": "Start Backup",
    "Backup Logs": "Backup Logs",
    "Performance Metrics": "Performance Metrics",
}

selected_label = next(
    (label for label, value in NAV_OPTIONS.items() if value == st.session_state.page),
    "Home Dashboard",
)
if "navbar_selection" not in st.session_state:
    st.session_state.navbar_selection = selected_label

brand_col, nav_col, profile_col = st.columns([1.1, 5.0, 0.7], vertical_alignment="center")
with brand_col:
    st.markdown("<div class='top-brand'>MCHBS<span class='top-brand-dot'>.</span></div>", unsafe_allow_html=True)
with nav_col:
    selected_nav = st.radio(
        "Top Navigation",
        list(NAV_OPTIONS.keys()),
        horizontal=True,
        index=list(NAV_OPTIONS.keys()).index(st.session_state.navbar_selection),
        key="navbar_selection",
        label_visibility="collapsed",
    )
with profile_col:
    with st.popover("👤"):
        st.markdown(f"**Signed in as** `{st.session_state.current_user}`")
        if st.button("Logout", key="logout_in_profile"):
            st.session_state.authenticated = False
            st.session_state.current_user = ""
            st.session_state.page = "Home Dashboard"
            st.rerun()

page = NAV_OPTIONS[selected_nav]
st.session_state.page = page
st.markdown("<div class='nav-divider'></div>", unsafe_allow_html=True)

def set_page(target_page: str) -> None:
    st.session_state.page = target_page
    nav_label = next(
        (label for label, value in NAV_OPTIONS.items() if value == target_page),
        "Home Dashboard",
    )
    st.session_state.navbar_selection = nav_label


def list_dataset_files() -> list:
    os.makedirs(DATASET_DIR, exist_ok=True)
    files = []
    for filename in os.listdir(DATASET_DIR):
        path = os.path.join(DATASET_DIR, filename)
        if os.path.isfile(path):
            files.append(
                {
                    "file": filename,
                    "size_kb": round(os.path.getsize(path) / 1024, 2),
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M"),
                }
            )
    return files


def kpi_card(title: str, value: str, delta: str = "", badge: str = "") -> None:
    st.markdown(
        f"""
        <div class="card">
            <div class="kpi">
                <div>
                    <div class="label">{title}</div>
                    <div class="value">{value}</div>
                </div>
                <div>
                    <div class="delta">{delta}</div>
                    <div class="badge">{badge}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if page == "Home Dashboard":
    metrics = load_metrics()
    derived = compute_derived_metrics(metrics)

    total_files = len([f for f in os.listdir(DATASET_DIR) if os.path.isfile(os.path.join(DATASET_DIR, f))])
    total_size_mb = sum(
        os.path.getsize(os.path.join(DATASET_DIR, f))
        for f in os.listdir(DATASET_DIR)
        if os.path.isfile(os.path.join(DATASET_DIR, f))
    ) / (1024 * 1024)

    last_backup_time = metrics.get("last_backup_time") or "No backups yet"

    st.markdown(
        f"""
        <div class="hero glow">
            <div class="pill">SYSTEM ONLINE</div>
            <div class="hero-title">Multi-Cloud Hybrid Backup Strategy</div>
            <div class="hero-subtitle"></div>
            <div class="muted" style="margin-top:8px;">Last backup: {last_backup_time}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Backups", str(metrics.get("total_backups", 0)), badge="Lifecycle")
    with col2:
        kpi_card("Success Rate", f"{derived['success_rate']}%", badge="Reliability")
    with col3:
        kpi_card("Failover Count", str(metrics.get("failover_count", 0)), badge="Continuity")
    with col4:
        kpi_card("Dataset Volume", f"{round(total_size_mb, 2)} MB", badge=f"{total_files} files")

    st.write("")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("<div class='section-title'>Operational Overview</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel">
                <div class="muted">Local backup runs first for speed. Cloud backup ensures redundancy and off-site resilience.</div>
                <div style="margin-top:12px;">
                    <span class="badge">Local Storage</span>
                    <span class="badge" style="margin-left:6px;">AWS S3</span>
                    <span class="badge" style="margin-left:6px;">Failover Ready</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown("<div class='section-title'>Dataset Snapshot</div>", unsafe_allow_html=True)
        files = list_dataset_files()
        if files:
            st.dataframe(files, use_container_width=True, hide_index=True)
        else:
            st.info("No dataset files found. Upload files to get started.")

    with col_right:
        st.markdown("<div class='section-title'>Quick Actions</div>", unsafe_allow_html=True)
        action_col = st.container()
        with action_col:
            st.button("Go to Start Backup", on_click=set_page, args=("Start Backup",))
            st.button("Upload New Files", on_click=set_page, args=("Upload Supply Chain Files",))

        st.write("")
        st.markdown("<div class='section-title'>Health Monitor</div>", unsafe_allow_html=True)
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write("Local Backup Readiness")
        st.progress(95)
        st.write("Cloud Connectivity")
        st.progress(90)
        st.write("Failover Preparedness")
        st.progress(92)
        st.markdown("</div>", unsafe_allow_html=True)


elif page == "Upload Supply Chain Files":
    st.markdown("<div class='hero'><div class='hero-title'>Upload Supply Chain Files</div><div class='hero-subtitle'>Ingest new inventory, shipments, suppliers, and warehouse records.</div></div>", unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Drop CSV or Excel files here",
            type=["csv", "xlsx"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            os.makedirs(DATASET_DIR, exist_ok=True)
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATASET_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded {len(uploaded_files)} file(s) to dataset.")

    with col2:
        st.markdown("<div class='section-title'>Upload Tips</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel">
                <div class="muted">Recommended file types: CSV or XLSX.</div>
                <div class="muted">Keep filenames unique to avoid overwrites.</div>
                <div class="muted">Uploads are stored in the local dataset directory.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("<div class='section-title'>Current Dataset</div>", unsafe_allow_html=True)
    files = list_dataset_files()
    if files:
        st.dataframe(files, use_container_width=True, hide_index=True)
    else:
        st.info("No dataset files found yet.")


elif page == "Start Backup":
    st.markdown("<div class='hero'><div class='hero-title'>Start Backup</div><div class='hero-subtitle'>Run local backup first, then cloud backup for redundancy.</div></div>", unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("backup_form", enter_to_submit=False):
            bucket_name = st.text_input("AWS S3 Bucket Name", placeholder="your-s3-bucket-name")
            s3_prefix = st.text_input("S3 Prefix (Optional)", value="supply-chain-backups")
            submitted = st.form_submit_button("Start Backup")

        if submitted:
            if not bucket_name:
                st.error("Please provide an S3 bucket name.")
            else:
                with st.spinner("Running backup..."):
                    result = run_backup(cloud_bucket=bucket_name, s3_prefix=s3_prefix)
                    time.sleep(0.5)

                local = result["result"]["local"]
                cloud = result["result"]["cloud"]
                overall_success = local["success"] or cloud["success"]

                st.markdown("<div class='section-title'>Results</div>", unsafe_allow_html=True)
                st.markdown("<div class='panel'>", unsafe_allow_html=True)
                if overall_success:
                    st.success("Backup completed successfully.")
                else:
                    st.error("Backup failed. Please review the errors below.")
                st.write(f"Local Backup: {'Success' if local['success'] else 'Failed'}")
                st.write(f"Cloud Backup: {'Success' if cloud['success'] else 'Failed'}")
                if cloud["error"]:
                    st.write(f"Cloud Error: {cloud['error']}")
                st.write(f"Files Processed: {result['files_processed']}")
                st.write(f"Backup Time: {result['duration']} seconds")
                st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>Execution Summary</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel">
                <div class="muted">Sequence:</div>
                <div class="muted">1. Local backup to `backup/local_backup`</div>
                <div class="muted">2. Cloud backup to AWS S3</div>
                <div class="muted">3. Failover to cloud if local fails</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown("<div class='section-title'>Credentials</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel">
                <div class="muted">Set AWS credentials via environment variables:</div>
                <div class="muted">AWS_ACCESS_KEY_ID</div>
                <div class="muted">AWS_SECRET_ACCESS_KEY</div>
                <div class="muted">AWS_DEFAULT_REGION</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


elif page == "Backup Logs":
    st.markdown("<div class='hero'><div class='hero-title'>Backup Logs</div><div class='hero-subtitle'>Operational history and events.</div></div>", unsafe_allow_html=True)

    st.write("")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
        st.text_area("Logs", logs, height=420)
    else:
        st.info("No logs found yet.")


elif page == "Performance Metrics":
    st.markdown("<div class='hero'><div class='hero-title'>Performance Metrics</div><div class='hero-subtitle'>Monitoring backup efficiency and reliability.</div></div>", unsafe_allow_html=True)

    st.write("")
    metrics = load_metrics()
    derived = compute_derived_metrics(metrics)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Total Backups", str(metrics.get("total_backups", 0)), badge="Lifecycle")
    with col2:
        kpi_card("Failover Count", str(metrics.get("failover_count", 0)), badge="Continuity")
    with col3:
        kpi_card("Success Rate", f"{derived['success_rate']}%", badge="Reliability")

    st.write("")
    st.markdown("<div class='section-title'>Operational Timing</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.write("Average Backup Time (seconds):", derived["average_backup_time"])
    st.write("Total Files Processed:", metrics.get("total_files", 0))
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='section-title'>Raw Metrics</div>", unsafe_allow_html=True)
    st.json(metrics)
