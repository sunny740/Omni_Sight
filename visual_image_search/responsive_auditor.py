
import os
import json
import base64
import argparse

from pathlib import Path
from playwright.sync_api import sync_playwright
from groq import Groq
from dotenv import load_dotenv


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

if not API_KEY:
    raise ValueError("GROQ_API_KEY missing from .env")

client = Groq(api_key=API_KEY)

SCREENSHOT_DIR = Path("screenshots")
REPORT_DIR = Path("reports")

SCREENSHOT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# Use common viewport sizes rather than assuming
# one specific phone/tablet represents every device.
VIEWPORTS = {
    "mobile": {"width": 390, "height": 844},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1440, "height": 900},
}


# =========================================================
# STEP 1: CAPTURE SCREENSHOTS AND INSPECT DOM
# =========================================================

DOM_AUDIT_JS = """
() => {
    const vw = document.documentElement.clientWidth;
    const vh = document.documentElement.clientHeight;

    const elements = Array.from(
        document.querySelectorAll(
            'button, input, select, textarea, a, [role="button"]'
        )
    );

    const interactive = elements.map((el) => {
        const r = el.getBoundingClientRect();
        const style = getComputedStyle(el);

        const visible =
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            Number(style.opacity) > 0 &&
            r.width > 0 &&
            r.height > 0;

        const fullyInsideViewport =
            r.left >= 0 &&
            r.right <= vw &&
            r.top >= 0 &&
            r.bottom <= vh;

        return {
            tag: el.tagName,
            text: (el.innerText || el.value || el.getAttribute('aria-label') || '')
                .trim().slice(0, 100),
            type: el.getAttribute('type'),
            visible: visible,
            fully_inside_viewport: fullyInsideViewport,
            x: Math.round(r.x),
            y: Math.round(r.y),
            width: Math.round(r.width),
            height: Math.round(r.height),
            right: Math.round(r.right),
            bottom: Math.round(r.bottom),
            position: style.position,
            display: style.display,
            overflow: style.overflow
        };
    });

    const overflowElements = Array.from(
        document.querySelectorAll('body *')
    ).map(el => {
        const r = el.getBoundingClientRect();
        const style = getComputedStyle(el);

        return {
            tag: el.tagName,
            id: el.id,
            className: String(el.className || '').slice(0, 100),
            left: Math.round(r.left),
            right: Math.round(r.right),
            width: Math.round(r.width),
            overflowX: style.overflowX
        };
    }).filter(el =>
        el.right > vw + 1 || el.left < -1
    ).slice(0, 30);

    return {
        viewport: { width: vw, height: vh },
        document_width: document.documentElement.scrollWidth,
        document_height: document.documentElement.scrollHeight,
        horizontal_overflow:
            document.documentElement.scrollWidth > vw,
        interactive_elements: interactive,
        elements_outside_viewport: overflowElements
    };
}
"""


def capture_screenshots(url, extra_css=None):
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for device, viewport in VIEWPORTS.items():

            context = browser.new_context(
                viewport=viewport,
                device_scale_factor=1,
                is_mobile=(device == "mobile"),
                has_touch=(device != "desktop"),
            )

            page = context.new_page()

            try:
                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=60000
                )

                page.wait_for_timeout(1500)

                # Optional: inject the AI-generated CSS
                # to preview the proposed correction.
                if extra_css and extra_css.exists():
                    css_text = extra_css.read_text(
                        encoding="utf-8"
                    )
                    page.add_style_tag(content=css_text)

                # Capture the complete webpage.
                screenshot_path = (
                    SCREENSHOT_DIR / f"{device}.png"
                )

                page.screenshot(
                    path=str(screenshot_path),
                    full_page=True,
                )

                # Capture DOM-level diagnostics.
                audit = page.evaluate(DOM_AUDIT_JS)

                results[device] = {
                    "screenshot": str(screenshot_path),
                    "audit": audit,
                }

                print(f"[OK] Captured {device}: {viewport}")

            except Exception as e:
                results[device] = {
                    "error": str(e)
                }
                print(f"[ERROR] {device}: {e}")

            finally:
                context.close()

        browser.close()

    return results


# =========================================================
# STEP 2: ENCODE SCREENSHOTS
# =========================================================

def image_to_data_url(path):

    data = Path(path).read_bytes()

    encoded = base64.b64encode(data).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


# =========================================================
# STEP 3: VISION MODEL ANALYSIS
# =========================================================

VISUAL_AUDIT_PROMPT = """
You are a senior frontend engineer and responsive UI auditor.

You will receive screenshots of the SAME webpage rendered at:

1. Mobile: 390 x 844
2. Tablet: 768 x 1024
3. Desktop: 1440 x 900

Your task is to perform a detailed responsive design audit.

Inspect the screenshots carefully.

Look specifically for:

- Submit buttons that are clipped, hidden or partially visible.
- Input fields exceeding the viewport width.
- Horizontal scrolling.
- Navigation menu overflow.
- Text overlapping other elements.
- Headings wrapping incorrectly.
- Cards extending outside their containers.
- Images stretching or overflowing.
- Poor padding and margins.
- Elements overlapping.
- Inconsistent alignment.
- Unreadable text.
- Buttons that are too small for touch interaction.
- Important content missing from mobile.
- Layouts that do not adapt to the screen width.

IMPORTANT:

A desktop layout does not automatically mean a mobile layout
is correct.

Compare all three screenshots.

Use the accompanying DOM diagnostics as additional evidence.

Do not report a problem merely because an element is below
the initial viewport in a full-page screenshot. Distinguish
between normal scrolling and actual clipping or hiding.

Do not invent elements or problems.

Return a structured JSON object with this schema:

{
  "overall_status": "PASS or NEEDS_FIX",
  "summary": "Short explanation",
  "issues": [
    {
      "device": "mobile/tablet/desktop",
      "element": "Element name or description",
      "severity": "critical/high/medium/low",
      "problem": "What is wrong",
      "evidence": "What is visible in the screenshot",
      "recommended_fix": "Specific frontend correction"
    }
  ],
  "device_assessment": {
    "mobile": "Assessment",
    "tablet": "Assessment",
    "desktop": "Assessment"
  }
}

Return valid JSON only.
"""


def analyze_screenshots(results):

    content = [
        {
            "type": "text",
            "text": VISUAL_AUDIT_PROMPT
        }
    ]

    for device in ["mobile", "tablet", "desktop"]:

        result = results.get(device, {})

        if "error" in result:
            content.append({
                "type": "text",
                "text": f"{device} screenshot failed: "
                        f"{result['error']}"
            })
            continue

        content.append({
            "type": "text",
            "text": (
                f"{device.upper()} DOM DIAGNOSTICS:\n"
                + json.dumps(result["audit"], indent=2)
            )
        })

        content.append({
            "type": "text",
            "text": f"{device.upper()} SCREENSHOT:"
        })

        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_to_data_url(
                    result["screenshot"]
                )
            }
        })

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0.1,
        max_completion_tokens=3000,
    )

    raw = response.choices[0].message.content

    # Parse the model's JSON response.
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # Preserve the original output if the model
        # fails to return valid JSON.
        return {
            "overall_status": "REVIEW_REQUIRED",
            "summary": "Could not parse the visual audit JSON.",
            "raw_response": raw,
            "issues": []
        }


# =========================================================
# STEP 4: READ ORIGINAL HTML AND CSS
# =========================================================

def read_source_code(source_dir):

    source_dir = Path(source_dir)

    if not source_dir.exists():
        raise FileNotFoundError(
            f"Source folder not found: {source_dir}"
        )

    extensions = {".html", ".htm", ".css"}

    files = [
        f for f in source_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in extensions
        and not any(
            part in {"node_modules", ".venv", ".git", "dist", "build"}
            for part in f.parts
        )
    ]

    source = []

    total_chars = 0
    max_chars = 45000

    for file in files:

        try:
            code = file.read_text(
                encoding="utf-8",
                errors="replace"
            )

            remaining = max_chars - total_chars

            if remaining <= 0:
                break

            code = code[:remaining]

            source.append(
                f"\n\n--- FILE: {file} ---\n{code}"
            )

            total_chars += len(code)

        except Exception as e:
            print(f"Cannot read {file}: {e}")

    if not source:
        raise ValueError("No HTML/CSS source files found.")

    return "\n".join(source)


# =========================================================
# STEP 5: GENERATE CORRECTED HTML AND CSS
# =========================================================

CODE_GENERATION_PROMPT = """
You are a senior frontend developer specializing in
responsive HTML5, CSS3 and mobile-first web design.

You will receive:

1. Original HTML and CSS source code.
2. A visual audit report generated from screenshots.
3. DOM diagnostics for mobile, tablet and desktop.

Your job is to generate corrected frontend code.

REQUIREMENTS:

1. Fix every verified responsive design problem.
2. Preserve the original page structure and functionality.
3. Do not unnecessarily redesign the webpage.
4. Preserve form fields, labels, buttons and links.
5. Make the submit button visible and accessible.
6. Prevent horizontal overflow.
7. Use appropriate CSS media queries.
8. Use flexible layouts, CSS Grid or Flexbox where appropriate.
9. Ensure images scale proportionally.
10. Use readable typography and suitable spacing.
11. Preserve existing colors and visual identity.
12. Avoid fixed widths that break smaller viewports.
13. Do not remove content simply to hide layout problems.
14. Do not invent external dependencies.
15. Do not claim that the generated code has been tested.

OUTPUT FORMAT:

Return a Markdown document with these sections:

# Responsive Fix Summary
Explain each problem and how it is fixed.

# Corrected HTML
Provide the complete corrected HTML if an HTML change is
necessary. Otherwise explicitly say that the original HTML
can remain unchanged.

# Corrected CSS
Provide the complete replacement CSS for the supplied
stylesheet(s), or a clearly identified additional CSS
override if a complete replacement is not safe.

# Integration Instructions
Explain exactly which files need to be replaced or updated.

IMPORTANT:
- Include actual working HTML/CSS, not pseudocode.
- Identify the original filenames.
- Do not omit relevant existing styles.
- If the supplied source is incomplete, clearly identify
  the missing files instead of fabricating their contents.
"""


def generate_fixed_code(audit, source_code):

    prompt = f"""
VISUAL AUDIT REPORT:

{json.dumps(audit, indent=2)}

ORIGINAL HTML AND CSS SOURCE:

{source_code}

Generate the corrected responsive HTML/CSS.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": CODE_GENERATION_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.15,
        max_completion_tokens=10000,
    )

    return response.choices[0].message.content


# =========================================================
# STEP 6: SAVE AUDIT AND FIX PROPOSAL
# =========================================================

def save_results(audit, fixed_code):

    audit_file = REPORT_DIR / "responsive_audit.json"

    audit_file.write_text(
        json.dumps(audit, indent=4),
        encoding="utf-8"
    )

    fix_file = REPORT_DIR / "responsive_fix_proposal.md"

    fix_file.write_text(
        fixed_code,
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("RESPONSIVE AUDIT COMPLETE")
    print("=" * 60)

    print(f"Audit report: {audit_file.resolve()}")
    print(f"Fix proposal: {fix_file.resolve()}")

    print("\nOverall status:")
    print(audit.get("overall_status", "UNKNOWN"))

    print("\nSummary:")
    print(audit.get("summary", "No summary available."))

    print("\nDetected issues:")

    for issue in audit.get("issues", []):
        print(
            f"\n[{issue.get('severity', 'unknown').upper()}] "
            f"{issue.get('device', 'unknown')} - "
            f"{issue.get('element', 'unknown')}"
        )
        print("Problem:", issue.get("problem", ""))
        print("Fix:", issue.get("recommended_fix", ""))


# =========================================================
# STEP 7: MAIN PIPELINE
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description="AI Responsive Webpage Auditor"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Running webpage URL"
    )

    parser.add_argument(
        "--source",
        default="source",
        help="Directory containing original HTML/CSS"
    )

    parser.add_argument(
        "--extra-css",
        default=None,
        help="Optional CSS file to inject during testing"
    )

    args = parser.parse_args()

    print("\nSTEP 1: Capturing device screenshots...")

    extra_css = (
        Path(args.extra_css) if args.extra_css else None
    )

    results = capture_screenshots(
        args.url,
        extra_css=extra_css
    )

    print("\nSTEP 2: Analyzing screenshots with Qwen...")

    audit = analyze_screenshots(results)

    print("\nSTEP 3: Reading original source files...")

    source_code = read_source_code(args.source)

    print("\nSTEP 4: Generating corrected HTML/CSS...")

    fixed_code = generate_fixed_code(
        audit,
        source_code
    )

    print("\nSTEP 5: Saving reports...")

    save_results(audit, fixed_code)


if __name__ == "__main__":
    main()
