
import streamlit as st
import json
import zipfile
import tempfile
import shutil

from pathlib import Path

import responsive_auditor as auditor


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Visual QA Studio",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.metric-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
}

.metric-label {
    color: #64748b;
    font-size: 14px;
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
}

.issue-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
}

.small-muted {
    color: #64748b;
    font-size: 13px;
}

.stButton button {
    border-radius: 8px;
    min-height: 42px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "audit_results" not in st.session_state:
    st.session_state.audit_results = None

if "audit_report" not in st.session_state:
    st.session_state.audit_report = None

if "fixed_code" not in st.session_state:
    st.session_state.fixed_code = None

if "source_directory" not in st.session_state:
    st.session_state.source_directory = None

if "temp_directory" not in st.session_state:
    st.session_state.temp_directory = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def extract_source_zip(uploaded_file):

    temp_dir = tempfile.mkdtemp(
        prefix="responsive_audit_"
    )

    destination = Path(temp_dir).resolve()

    try:
        with zipfile.ZipFile(uploaded_file) as archive:

            for member in archive.infolist():

                target = (
                    destination / member.filename
                ).resolve()

                if not target.is_relative_to(destination):
                    raise ValueError(
                        "Unsafe ZIP archive path detected."
                    )

                if member.is_dir():
                    target.mkdir(
                        parents=True,
                        exist_ok=True
                    )
                    continue

                # Only extract frontend source files.
                allowed = {
                    ".html",
                    ".htm",
                    ".css"
                }

                if Path(member.filename).suffix.lower() not in allowed:
                    continue

                target.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                with archive.open(member) as src:
                    with target.open("wb") as dst:
                        shutil.copyfileobj(src, dst)

        html_files = list(destination.rglob("index.html"))

        if html_files:
            source_root = html_files[0].parent

        else:
            source_root = destination

        if not list(source_root.rglob("*.html")) and not list(
            source_root.rglob("*.htm")
        ):
            raise ValueError(
                "No HTML files found in the uploaded ZIP."
            )

        return temp_dir, source_root

    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def run_audit(url, source_directory):

    # 1. Capture all device screenshots.
    with st.status(
        "Capturing website screenshots...",
        expanded=True
    ) as status:

        results = auditor.capture_screenshots(url)

        status.update(
            label="Screenshots captured.",
            state="complete"
        )

    # 2. Analyze screenshots with Qwen.
    with st.status(
        "Analyzing responsive layouts with Qwen...",
        expanded=True
    ) as status:

        audit = auditor.analyze_screenshots(results)

        status.update(
            label="Visual analysis completed.",
            state="complete"
        )

    # 3. Read HTML/CSS.
    with st.status(
        "Reading original HTML and CSS...",
        expanded=True
    ) as status:

        source_code = auditor.read_source_code(
            str(source_directory)
        )

        status.update(
            label="Source code loaded.",
            state="complete"
        )

    # 4. Generate corrected code.
    with st.status(
        "Generating responsive HTML/CSS corrections...",
        expanded=True
    ) as status:

        fixed_code = auditor.generate_fixed_code(
            audit,
            source_code
        )

        status.update(
            label="Code generation completed.",
            state="complete"
        )

    return results, audit, fixed_code


def get_severity_counts(audit):

    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for issue in audit.get("issues", []):
        severity = issue.get(
            "severity", "low"
        ).lower()

        if severity in counts:
            counts[severity] += 1

    return counts


def severity_badge(severity):

    colors = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵"
    }

    severity = severity.lower()

    return colors.get(severity, "⚪")


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🔍 Visual QA Studio")

    st.caption(
        "AI-powered responsive website testing"
    )

    st.divider()

    st.subheader("Testing configuration")

    st.markdown(
        "**Enabled devices**"
    )

    st.checkbox(
        "Mobile (390 × 844)",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Tablet (768 × 1024)",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Desktop (1440 × 900)",
        value=True,
        disabled=True
    )

    st.divider()

    st.markdown("**AI configuration**")

    st.write(
        f"Vision model: `{auditor.MODEL}`"
    )

    st.write(
        "Embedding: Not required for this module"
    )

    st.write(
        "Browser: Playwright Chromium"
    )

    st.divider()

    if st.button(
        "Clear previous results",
        use_container_width=True
    ):

        st.session_state.audit_results = None
        st.session_state.audit_report = None
        st.session_state.fixed_code = None

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.title("Visual QA Studio")

st.markdown(
    "Test your webpage across different devices, "
    "detect responsive design issues, and generate "
    "AI-powered HTML/CSS corrections."
)

st.divider()


# =========================================================
# INPUT SECTION
# =========================================================

st.subheader("1. Website configuration")

url = st.text_input(
    "Website URL",
    placeholder="http://127.0.0.1:5500",
    help="Enter the running webpage URL."
)

uploaded_zip = st.file_uploader(
    "Upload original HTML/CSS project (ZIP)",
    type=["zip"],
    help="Upload your webpage source files."
)

with st.expander("Testing information"):

    st.write(
        "The webpage must be accessible from the "
        "machine running this Streamlit application."
    )

    st.write(
        "Upload the original source code so the "
        "AI can generate accurate corrections."
    )

    st.write(
        "JavaScript and backend files are not extracted "
        "by this basic version."
    )


# =========================================================
# RUN AUDIT BUTTON
# =========================================================

run_button = st.button(
    "🚀 Run Responsive Audit",
    type="primary",
    use_container_width=True
)


if run_button:

    if not url.strip():
        st.error("Please enter a website URL.")

    elif not uploaded_zip:
        st.error("Please upload your HTML/CSS project ZIP.")

    else:

        try:

            # Validate URL format.
            from urllib.parse import urlparse

            parsed = urlparse(url.strip())

            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(
                    "Enter a valid HTTP or HTTPS URL."
                )

            # Extract project files.
            with st.spinner(
                "Extracting project files..."
            ):

                temp_dir, source_root = extract_source_zip(
                    uploaded_zip
                )

            # Preserve directory for later review.
            if st.session_state.temp_directory:
                shutil.rmtree(
                    st.session_state.temp_directory,
                    ignore_errors=True
                )

            st.session_state.temp_directory = temp_dir
            st.session_state.source_directory = str(source_root)

            # Execute audit pipeline.
            results, audit, fixed_code = run_audit(
                url.strip(),
                source_root
            )

            st.session_state.audit_results = results
            st.session_state.audit_report = audit
            st.session_state.fixed_code = fixed_code

            st.success(
                "Responsive audit completed successfully!"
            )

        except Exception as e:

            st.error(
                f"Audit failed: {str(e)}"
            )


# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state.audit_report is not None:

    audit = st.session_state.audit_report
    results = st.session_state.audit_results
    fixed_code = st.session_state.fixed_code

    st.divider()

    st.subheader("2. Audit overview")

    issues = audit.get("issues", [])

    severity_counts = get_severity_counts(audit)

    total_issues = len(issues)

    successful_devices = sum(
        1 for result in results.values()
        if "error" not in result
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Devices tested",
            f"{successful_devices}/3"
        )

    with col2:
        st.metric(
            "Total issues",
            total_issues
        )

    with col3:
        st.metric(
            "Critical / High",
            severity_counts["critical"]
            + severity_counts["high"]
        )

    with col4:
        st.metric(
            "Overall status",
            audit.get(
                "overall_status",
                "UNKNOWN"
            )
        )

    st.info(
        audit.get(
            "summary",
            "No summary available."
        )
    )

    # -----------------------------------------------------
    # SCREENSHOT TABS
    # -----------------------------------------------------

    st.divider()

    st.subheader("3. Device screenshots")

    tabs = st.tabs([
        "📱 Mobile",
        "📟 Tablet",
        "🖥️ Desktop"
    ])

    devices = ["mobile", "tablet", "desktop"]

    for tab, device in zip(tabs, devices):

        with tab:

            result = results.get(device, {})

            if "error" in result:
                st.error(result["error"])

            elif result:

                st.image(
                    result["screenshot"],
                    caption=f"{device.title()} screenshot",
                    use_container_width=True
                )

                with st.expander(
                    "View DOM diagnostics"
                ):

                    st.json(
                        result["audit"]
                    )

    # -----------------------------------------------------
    # DEVICE ASSESSMENT
    # -----------------------------------------------------

    st.divider()

    st.subheader("4. Device assessment")

    assessments = audit.get(
        "device_assessment", {}
    )

    col1, col2, col3 = st.columns(3)

    for col, device in zip(
        [col1, col2, col3],
        devices
    ):

        with col:

            st.markdown(
                f"**{device.title()}**"
            )

            st.write(
                assessments.get(
                    device,
                    "No assessment available."
                )
            )

    # -----------------------------------------------------
    # ISSUE DETAILS
    # -----------------------------------------------------

    st.divider()

    st.subheader("5. Detected UI problems")

    if not issues:

        st.success(
            "No visual issues were reported by the AI."
        )

    else:

        for index, issue in enumerate(
            issues,
            start=1
        ):

            severity = issue.get(
                "severity", "low"
            )

            with st.expander(
                f"{severity_badge(severity)} "
                f"{index}. {issue.get('element', 'UI issue')} "
                f"— {issue.get('device', 'Unknown device')}",
                expanded=(severity.lower() in ["critical", "high"])
            ):

                st.markdown(
                    f"**Severity:** {severity.upper()}"
                )

                st.markdown(
                    f"**Problem:** {issue.get('problem', '')}"
                )

                st.markdown(
                    f"**Evidence:** {issue.get('evidence', '')}"
                )

                st.markdown(
                    f"**Recommended fix:** "
                    f"{issue.get('recommended_fix', '')}"
                )

    # -----------------------------------------------------
    # GENERATED CODE
    # -----------------------------------------------------

    st.divider()

    st.subheader("6. AI-generated HTML/CSS corrections")

    st.markdown(
        "Review the generated changes before applying "
        "them to your original project."
    )

    st.download_button(
        "⬇ Download complete fix proposal",
        data=fixed_code,
        file_name="responsive_fix_proposal.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.markdown(
        "### Generated code proposal"
    )

    st.markdown(fixed_code)

    with st.expander("View raw Markdown source"):

        st.code(
            fixed_code,
            language="markdown"
        )

    # -----------------------------------------------------
    # DOWNLOAD AUDIT JSON
    # -----------------------------------------------------

    st.divider()

    st.subheader("7. Export reports")

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "⬇ Download audit JSON",
            data=json.dumps(
                audit,
                indent=4
            ),
            file_name="responsive_audit.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "⬇ Download mobile screenshot",
            data=Path(
                results["mobile"]["screenshot"]
            ).read_bytes(),
            file_name="mobile_screenshot.png",
            mime="image/png",
            use_container_width=True
        )

else:

    st.divider()

    st.subheader("Ready to test?")

    st.write(
        "Upload your webpage source code, provide its running URL, "
        "and start your first responsive design audit."
    )

    st.caption(
        "Your original source files will not be modified."
    )
