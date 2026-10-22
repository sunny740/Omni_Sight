# Headless Navigator — Python & Playwright

A simple browser automation project using Python and Playwright to navigate a website, interact with form elements, submit a form, and capture screenshots at every step.

## Features

- Launch Chromium in visible browser mode.
- Navigate to the Selenium demo web form.
- Enter text into an input field.
- Select an option from a dropdown.
- Submit the form.
- Capture full-page screenshots after each action.
- Print the final URL and form submission result.
- Save screenshots in a dedicated folder.

## Project Structure

```text
playwright-browser-automation/
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
    ├── 01_browser_started.png
    ├── 02_website_opened.png
    ├── 03_text_entered.png
    ├── 04_dropdown_selected.png
    ├── 05_form_submitted.png
    └── 06_final_result.png
```

The `screenshots/` directory is created automatically when the script runs.

## Prerequisites

- Python 3.9 or later recommended.
- pip package manager.
- Chromium browser installed through Playwright.
- Internet connection to access the Selenium demo website.

## Installation

### 1. Clone or create the project directory

Open a terminal in your project directory.

### 2. Create a virtual environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Playwright Chromium browser

```bash
python -m playwright install chromium
```

## Run the Automation

Save your Python script as `navigator.py`, then execute:

```bash
python navigator.py
```

The script launches a visible browser, opens the demo form, enters the text `Hello from Playwright`, selects dropdown option `2`, submits the form, and captures screenshots along the way.

## Screenshot Output

All screenshots are saved in the `screenshots/` folder.

| Screenshot | Description |
|---|---|
| `01_browser_started.png` | Initial browser page |
| `02_website_opened.png` | Demo form loaded |
| `03_text_entered.png` | Text entered in the input field |
| `04_dropdown_selected.png` | Dropdown option selected |
| `05_form_submitted.png` | Form submitted |
| `06_final_result.png` | Final result displayed |

Screenshots use full-page capture to include the entire page where supported.

## Expected Output

The terminal should display messages similar to:

```text
Screenshot saved: .../screenshots/01_browser_started.png
Screenshot saved: .../screenshots/02_website_opened.png
Screenshot saved: .../screenshots/03_text_entered.png
Screenshot saved: .../screenshots/04_dropdown_selected.png
Screenshot saved: .../screenshots/05_form_submitted.png
Final URL: https://www.selenium.dev/selenium/web/form.html
Result: Received!
Screenshot saved: .../screenshots/06_final_result.png
Automation completed!
```

The final URL shown above is illustrative; the actual URL depends on the website's response after submission.

## Configuration

The browser is currently launched in visible mode:

```python
browser = p.chromium.launch(headless=False)
```

To run without a visible browser window, change it to:

```python
browser = p.chromium.launch(headless=True)
```

## Troubleshooting

**Playwright module not found**

```bash
pip install -r requirements.txt
```

**Chromium executable not found**

```bash
python -m playwright install chromium
```

**Element not found or timeout**

Verify the website is available and the selectors match its current HTML.

**Screenshots not appearing**

Check the terminal output for the absolute screenshot path and confirm the project directory is writable.

## Notes

- This is a basic browser automation example, not a comprehensive test suite.
- The script currently prints the submission result but does not assert that it matches an expected value.
- The browser is closed at the end of the script.
- Run automated tests only on websites you own or are authorized to test.

## License

This project is provided for educational and testing purposes. Add a license file if you intend to distribute it publicly.
