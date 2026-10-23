# Omni_Sight

**Omni_Sight** is a multi-purpose Generative AI and web automation suite developed by **Mobashshir Taj**. The repository combines multimodal Generative AI capabilities—such as conversational assistants and document analysis—with programmatic, headless browser automation and visual verification workflows.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Modules & Features](#modules--features)
  - [1. Simple Chatbot (`simple_chatbot/`)](#1-simple-chatbot-simple_chatbot)
  - [2. Headless Navigator (`headless_navigator/`)](#2-headless-navigator-headless_navigator)
- [Tech Stack & Dependencies](#tech-stack--dependencies)
- [Getting Started & Installation](#getting-started--installation)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
- [Execution & Usage](#execution--usage)
  - [Running the Streamlit Chatbot](#running-the-streamlit-chatbot)
  - [Running the Headless Navigator](#running-the-headless-navigator)
- [Visual Workflow & Screenshots](#visual-workflow--screenshots)
- [Roadmap & Enhancements](#roadmap--enhancements)
- [Author & Credits](#author--credits)

---

## 🌟 Overview

The `Omni_Sight` project serves as an exploratory and practical playground for building GenAI-driven applications and browser automation scripts:
- **Conversational Intelligence**: An interactive chat interface powered by modern LLM APIs (Google GenAI) with document/PDF understanding via PyMuPDF (`fitz`).
- **Headless Web Automation**: Robust browser execution and testing pipelines using Playwright, capturing end-to-end visual step-by-step verification artifacts.

---

## 📂 Repository Structure

```plaintext
Omni_Sight-Taj_omnisight/
├── README.md                          # Root project documentation
├── requirements.txt                   # Top-level dependencies
├── prompt.txt                         # System/engineering prompt templates
│
├── simple_chatbot/                    # Multimodal GenAI Chatbot module
│   ├── chatbot.py                     # Streamlit-based interactive web UI & chat logic
│   ├── requirements.txt               # Module dependencies (streamlit, google-genai, etc.)
│   └── readme.md                      # Module-specific instructions
│
└── headless_navigator/                # Playwright automation module
    ├── main.py                        # Automated browser interactions & navigation logic
    ├── requirements.txt               # Module dependencies (playwright>=1.50.0)
    ├── readme.md                      # Automation workflow documentation
    └── screenshots/                   # Step-by-step action artifacts
        ├── 01_browser_started.png
        ├── 02_website_opened.png
        ├── 03_text_entered.png
        ├── 04_dropdown_selected.png
        ├── 05_form_submitted.png
        └── 06_final_result.png
```

---

## 🧩 Modules & Features

### 1. Simple Chatbot (`simple_chatbot/`)
- **Interactive UI**: Clean, responsive frontend built with [Streamlit](https://streamlit.io/).
- **Google GenAI Integration**: Direct integration with Google's Gemini models using the modern `google-genai` SDK.
- **Document Ingestion**: Seamless PDF parsing using `pymupdf` to support grounding, Q&A, and document summarization.
- **Configuration Management**: Protected API keys and environment configurations managed via `python-dotenv`.

### 2. Headless Navigator (`headless_navigator/`)
- **High-Performance Automation**: Driven by [Playwright](https://playwright.dev/) for reliable, modern browser automation.
- **Visual Evidence Pipeline**: Captures sequential screenshots at every critical step of an interaction flow:
  1. Browser initialization
  2. Page load & target URL resolution
  3. Form element population & input handling
  4. Dynamic dropdown selections
  5. Submission triggers
  6. Final state and output validation

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.9+
- **GenAI / LLM**: `google-genai`
- **Frontend / UI**: `streamlit`
- **Web Automation**: `playwright >= 1.50.0`
- **Document Processing**: `pymupdf`
- **Environment Handling**: `python-dotenv`

---

## 🚀 Getting Started & Installation

### Prerequisites
- Python 3.9 or higher installed on your system.
- A valid Google Gemini API Key (obtained from [Google AI Studio](https://aistudio.google.com/)).

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Omni_Sight.git
   cd Omni_Sight
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   You can install from the project root or install specific module requirements:
   ```bash
   pip install -r simple_chatbot/requirements.txt
   pip install -r headless_navigator/requirements.txt
   ```

4. **Install Playwright browser binaries:**
   ```bash
   playwright install
   ```

5. **Set up API keys:**
   Create a `.env` file in the root or inside `simple_chatbot/`:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

---

## 💻 Execution & Usage

### Running the Streamlit Chatbot
Launch the chat interface from the terminal:
```bash
cd simple_chatbot
streamlit run chatbot.py
```
Open your browser and navigate to `http://localhost:8501`.

### Running the Headless Navigator
Execute the automated browser script:
```bash
cd headless_navigator
python main.py
```
Check the `headless_navigator/screenshots/` folder to view the generated stage-by-stage screenshots of your automated session.

---

## 📸 Visual Workflow & Screenshots

The `headless_navigator` pipeline exports visual artifacts verifying each action:

| Step | Action | Output File |
| :--: | :----- | :---------- |
| **01** | Browser Launch | `01_browser_started.png` |
| **02** | Target Webpage Navigation | `02_website_opened.png` |
| **03** | Form Filling / Input | `03_text_entered.png` |
| **04** | Dropdown / Menu Select | `04_dropdown_selected.png` |
| **05** | Form Submission Trigger | `05_form_submitted.png` |
| **06** | Final State Extraction | `06_final_result.png` |

---

## 🔮 Roadmap & Enhancements

- [ ] Combine `headless_navigator` with `simple_chatbot` to allow autonomous web browsing via natural language commands (Agentic Web Browsing).
- [ ] Add support for multi-document comparisons in the chat UI.
- [ ] Implement headless trace recording for advanced debugging in Playwright.
- [ ] Containerize the application with Docker and Docker Compose.

---

## 👤 Author & Credits

- **Author**: Mobashshir Taj
- **Project**: Omni_Sight