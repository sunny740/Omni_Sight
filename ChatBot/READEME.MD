# 🤖 Gemini AI Chatbot

A free-to-start AI chatbot built with **Python, Streamlit, and the Google Gemini API**. It supports conversational AI, chat history during a session, and PDF document question answering.

## ✨ Features

- 💬 Interactive AI conversations powered by Google Gemini
- 📄 Upload PDF documents and ask questions about their contents
- 🧠 Maintains recent conversation context
- 🔄 Clear conversation history
- 🔐 Loads API credentials from a local `.env` file
- 💻 Runs locally on your computer
- ☁️ Can be deployed online using Streamlit Community Cloud

## 🛠️ Tech Stack

- Python
- Streamlit
- Google GenAI SDK
- PyMuPDF
- python-dotenv

## 📁 Project Structure

```text
gemini-chatbot/
├── app.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Prerequisites

- Python 3.10 or a compatible newer version supported by your dependencies
- A Google account
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- An internet connection

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd gemini-chatbot
```

Alternatively, download the project files and open the project directory in your terminal.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a file named `.env` in the project root:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Replace the API key placeholder with your own key. Select a model that is currently available to your account.

**Security:** Never commit your `.env` file or share your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal. It is normally:

[http://localhost:8501](http://localhost:8501)

## 📄 How to Use the PDF Assistant

1. Open the chatbot in your browser.
2. Expand the sidebar if necessary.
3. Upload a PDF document.
4. Ask questions about the document in the chat box.
5. Ask follow-up questions while the document remains loaded.

Text-based PDFs work best. Scanned PDFs may require OCR. Very large documents may need a retrieval-based approach for better results.

## ☁️ Online Deployment

You can deploy the application using [Streamlit Community Cloud](https://share.streamlit.io/).

1. Push your project to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Connect your GitHub account.
4. Select your repository and `app.py`.
5. Add the following variables in the deployment's Secrets settings:

```toml
GEMINI_API_KEY = "your_actual_gemini_api_key"
GEMINI_MODEL = "gemini-2.5-flash"
```

6. Deploy the application.

Do not upload your local `.env` file to GitHub. Cloud secrets provide the credentials needed by the deployed application.

## 💰 Cost

This project can be free to run within the applicable free-tier limits of the Gemini API and hosting provider.

- Python and the listed libraries are open source.
- Streamlit Community Cloud offers a free hosting option.
- Gemini API availability and quotas depend on the selected model and current Google policies.

Check the [Gemini API pricing page](https://ai.google.dev/gemini-api/docs/pricing) for current rates and free-tier eligibility.

## 🔒 Security and Privacy

- Keep API keys private.
- Exclude `.env` from version control.
- Avoid uploading confidential documents to a public deployment.
- Apply authentication and usage limits before sharing the application widely.

## 🔮 Future Improvements

- Persistent conversation history
- PDF page citations
- OCR for scanned documents
- Semantic search and retrieval-augmented generation (RAG)
- User authentication
- Improved error handling and rate limiting

## 📜 License

This project is available for personal learning and modification. Add a specific open-source license if you intend to distribute it under defined license terms.
