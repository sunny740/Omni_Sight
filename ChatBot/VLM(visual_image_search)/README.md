# Omni Sight — Visual Image Search & Question Answering

A Python-based visual search and question-answering system that retrieves relevant images from a local folder using semantic embeddings, stores them in ChromaDB, and uses a Qwen vision model through the Groq API to answer questions about the retrieved images.

## Features

- **Semantic image search:** Search images using natural-language queries.
- **Image embeddings:** Generate image vectors locally using CLIP.
- **Vector database:** Store and retrieve embeddings using ChromaDB.
- **Similarity search:** Support cosine distance and Euclidean distance.
- **Visual question answering:** Use Qwen vision through Groq to analyze retrieved images.
- **Image previews:** Display matching images with their retrieval scores.
- **Persistent storage:** Save embeddings locally so the index survives application restarts.
- **Incremental indexing:** Update existing records and index newly added images.

## Architecture

```text
Local Image Folder
       |
       v
CLIP Image Encoder
       |
       v
Image Embeddings
       |
       v
ChromaDB Vector Store
       |
       v
Natural-Language Query
       |
       v
CLIP Text Encoder
       |
       v
Similarity Search
       |
       v
Top Matching Images
       |
       v
Qwen Vision API via Groq
       |
       v
Answer + Matching Image Previews
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Image-text embedding model | `sentence-transformers/clip-ViT-B-32` |
| Vector database | ChromaDB |
| Vision LLM | Qwen via Groq |
| Image processing | Pillow |
| Numerical operations | NumPy |
| Visualization | Matplotlib |
| Environment configuration | python-dotenv |

## Project Structure

```text
visual_image_search/
├── images/                  # Input images and screenshots
├── chroma_db/               # Persistent vector database
├── venv/                    # Python virtual environment
├── .env                     # Groq API key and configuration
├── .gitignore
├── app.py                   # Main application
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

The `chroma_db/` directory is created automatically when the application initializes the database.

## Prerequisites

- Python 3.10 or newer is recommended.
- pip and a virtual environment.
- An internet connection for installing dependencies and downloading the embedding model.
- A Groq API key for Qwen-based question answering.
- Sufficient local disk space and RAM to load the embedding model.

Image embedding and vector search run locally after the model weights are downloaded. Qwen inference requires an internet connection and a working Groq API account.

## Installation

### 1. Clone or open the project

Navigate to the project directory:

```bash
cd /path/to/visual_image_search
```

If you already have the project, skip cloning.

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it on Linux:

```bash
source venv/bin/activate
```

Your terminal should show `(venv)` when the environment is active.

### 3. Create `requirements.txt`

Add the following dependencies:

```text
chromadb
sentence-transformers
Pillow
numpy
groq
python-dotenv
matplotlib
```

### 4. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If pip reports that `requirements.txt` cannot be found, verify your current directory:

```bash
pwd
ls -la
```

Ensure the file exists in the directory from which you run pip.

### 5. Configure the Groq API key

Create a `.env` file:

```bash
nano .env
```

Add your API key and model configuration:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
DISTANCE_METRIC=cosine
```

Replace the placeholder with your actual API key.

Get your key from:

https://console.groq.com/keys

Check the Groq console for the current availability of the selected model and your account's usage limits.

**Security:** Never commit your `.env` file or expose your API key in public repositories.

## Add Images

Place your images or website screenshots in the `images/` directory.

Supported formats:

- PNG
- JPG
- JPEG
- WEBP
- BMP

Example:

```text
images/
├── login_page.png
├── dashboard.png
├── registration_form.jpg
├── error_message.png
└── website_homepage.webp
```

The indexer searches recursively through subdirectories.

## Usage

### 1. Index images

Run the following command from the project directory:

```bash
python app.py index --folder images
```

The application will:

1. Discover supported images.
2. Load each image.
3. Generate a normalized CLIP embedding.
4. Store the embedding and image metadata in ChromaDB.
5. Persist the database locally.

Example output:

```text
Loading CLIP embedding model...
Found 120 images.
Processed 32/120 images
Processed 64/120 images
Processed 96/120 images
Processed 120/120 images

Indexing finished.
Processed successfully: 120
Failed: 0
Total records in collection: 120
Distance metric: cosine
```

The numbers are illustrative; actual results depend on your image folder.

### 2. Search images with natural language

Search for login pages:

```bash
python app.py ask "Find a login page with an email and password field"
```

Search for dashboards:

```bash
python app.py ask "Find a dashboard containing sales charts"
```

Search for navigation elements:

```bash
python app.py ask "Find a screenshot with a navigation sidebar"
```

Search for error messages:

```bash
python app.py ask "Find the screenshot containing an error message"
```

Search for forms:

```bash
python app.py ask "Which image contains a registration form?"
```

### 3. Retrieve more results

By default, the application retrieves five images.

Use `--top-k` to change the number:

```bash
python app.py ask "Find a dashboard" --top-k 10
```

Qwen receives up to three candidate images in the current implementation, even when more images are displayed in the search results.

### 4. View the results

The application prints the matching filenames, distances, and paths. It then asks Qwen to analyze the retrieved images.

The image previews are displayed through Matplotlib and saved to:

```text
search_results.png
```

The generated preview contains the retrieved images and their corresponding scores.

## Similarity Metrics

The application supports cosine and squared Euclidean distance through ChromaDB.

### Cosine distance

Configure `.env`:

```dotenv
DISTANCE_METRIC=cosine
```

Chroma returns:

```text
cosine_distance = 1 - cosine_similarity
```

A lower cosine distance indicates a more similar image. The application reports `1 - distance` as the cosine similarity score.

### Euclidean distance

Configure `.env`:

```dotenv
DISTANCE_METRIC=l2
```

Re-index the images:

```bash
python app.py index --folder images
```

Chroma's `l2` metric reports **squared Euclidean distance**. A lower value indicates a closer match.

The application uses separate collections for cosine and Euclidean indexes.

## How the System Works

### Image embedding

CLIP converts each image into a numerical vector that represents its visual and semantic characteristics.

The embedding model used is:

`sentence-transformers/clip-ViT-B-32`

### Text embedding

The same CLIP model converts a natural-language search query into a vector in the shared image-text embedding space.

This allows text queries and image embeddings to be compared.

### Vector retrieval

ChromaDB retrieves the nearest image vectors using the selected distance metric.

The corresponding image paths and filenames are stored as metadata.

### Answer generation

The application sends the user's question and up to three retrieved images to the Qwen vision model through the Groq API.

Qwen examines the actual images and generates a response based on the visible evidence.

### Result display

The application prints the answer and shows the retrieved image previews, allowing users to inspect the supporting images.

## Important Limitations

- CLIP is a semantic retrieval model, not a dedicated OCR engine.
- Small text, exact button labels, and subtle UI differences may not be retrieved reliably.
- Retrieval quality depends on the images, query wording, and embedding model.
- Qwen cannot reliably answer from an image that was not retrieved and included in its request.
- The current implementation sends at most three images to Qwen per request.
- Removed source images are not automatically deleted from the ChromaDB index.
- Re-indexing existing image paths updates their records, but does not detect every possible change to image contents automatically.
- Groq API usage is subject to account quotas, rate limits, model availability, and applicable pricing.
- Local embedding generation requires sufficient RAM and disk space.

## Troubleshooting

### `requirements.txt` not found

Check the current directory:

```bash
pwd
ls -la
```

Create the file in the project directory and retry the installation.

### `GROQ_API_KEY` missing

Verify that `.env` exists in the directory from which you run `app.py`.

Check that the key is assigned correctly:

```dotenv
GROQ_API_KEY=your_actual_api_key
```

Restart the application after updating the configuration.

### Model unavailable or API request fails

Check:

- Your Groq API key is valid.
- Your account has remaining usage quota.
- The configured model supports image input.
- The model ID is currently available to your account.
- Your internet connection is working.

### No images found

Verify that the image folder contains supported files:

```bash
find images -type f
```

Run indexing with the correct folder:

```bash
python app.py index --folder images
```

### Empty vector database

Index images before searching:

```bash
python app.py index --folder images
```

Use the same `DISTANCE_METRIC` configuration for indexing and searching.

### Image previews do not open

If running in a headless environment, Matplotlib may not be able to open a graphical window. The application still attempts to save `search_results.png`.

Open the saved file with your desktop image viewer.

### Poor screenshot search results

Consider adding OCR, combining OCR-text embeddings with CLIP embeddings, and testing a screenshot-focused retrieval model.

## Future Improvements

Potential extensions include:

- OCR using Tesseract or PaddleOCR.
- Hybrid text and image embeddings.
- Screenshot deduplication and content-hash tracking.
- Automatic removal of deleted images from the index.
- A Streamlit or FastAPI web interface.
- Batch image analysis and caching.
- Filtering by image type, filename, and folder.
- Adjustable retrieval thresholds.
- Reranking candidates with a vision-language model.
- Returning structured JSON with image paths and evidence.
- Browser integration for website screenshot collection.

## License and Usage

The application combines multiple third-party libraries and model weights. Review the individual licenses and terms for the selected embedding model, Qwen model, Groq service, and dependencies before redistributing or deploying the system commercially.

## Useful Resources

- Groq API keys: https://console.groq.com/keys
- Groq vision documentation: https://console.groq.com/docs/vision
- Sentence Transformers: https://www.sbert.net/
- CLIP image search: https://sbert.net/examples/sentence_transformer/applications/image-search/README.html
- ChromaDB documentation: https://docs.trychroma.com/
- Python virtual environments: https://docs.python.org/3/library/venv.html

---

**Omni Sight** — Semantic image retrieval and vision-based question answering with Python, CLIP, ChromaDB, and Qwen.
