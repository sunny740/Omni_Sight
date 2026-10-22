# Playwright Python Website Automation

A beginner-friendly Python example that automates a public demo web form using Playwright and saves a screenshot after each major step.

## Features

- Launches Chromium in visible mode.
- Opens a demo form.
- Enters text into a text field.
- Selects an option from a dropdown.
- Submits the form.
- Saves screenshots in a `screenshots/` folder.
- Prints the final URL and result message.

## Project structure

```text
playwright_demo/
├── automation.py
├── requirements.txt
└── screenshots/          # Created automatically when the script runs
```

## Requirements

- Python 3.9 or newer
- Internet connection for the first browser installation and demo website

## Setup on Windows (PowerShell)

Open PowerShell in your project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell blocks virtual-environment activation, you can run the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Run

Place `automation.py` in this folder, then run:

```powershell
python automation.py
```

The browser opens visibly and the script writes screenshots to `screenshots/`. Screenshot filenames are numbered to reflect the automation sequence.

## Website used

The sample targets the Selenium project's public demo form:

https://www.selenium.dev/selenium/web/web-form.html

The page's structure can change, so if the script fails, inspect the current page and update the selectors in `automation.py`.

## Dependencies

`requirements.txt` contains the Python package dependency. The Chromium browser itself is installed separately with:

```powershell
python -m playwright install chromium
```

## Notes

- Run automation only on websites you own or are authorized to test.
- Do not store passwords, API keys, or other secrets directly in source code.
- This example takes screenshots after each major action. It does not automatically capture screenshots after every individual browser event.
- If an action fails, Playwright normally raises an exception and stops the script. For production use, add exception handling and save a failure screenshot.

## Troubleshooting

### `playwright` is not installed

Activate your virtual environment and run:

```powershell
pip install -r requirements.txt
```

### Browser executable is missing

Install Chromium:

```powershell
python -m playwright install chromium
```

### A locator times out or cannot be found

Check that the demo page loads and verify the selector in `automation.py`. Prefer accessible locators such as `get_by_role()` when practical.
