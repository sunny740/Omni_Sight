# Visual Image Search with CLIP, ChromaDB, and Qwen Vision

A Python application that indexes images from a local folder, retrieves visually relevant images using natural-language queries, and asks a hosted Qwen vision model to answer questions about the retrieved images.

## Features

- **Local image embeddings:** Uses `sentence-transformers/clip-ViT-B-32` to encode images and text into a shared embedding space.
- **Persistent vector storage:** Stores image embeddings and metadata in ChromaDB on disk.
- **Semantic image retrieval:** Search for images using natural-language descriptions.
- **Similarity metrics:** Supports cosine distance and squared Euclidean (`l2`) distance.
- **Vision-language answers:** Sends the top retrieved images to Qwen through the Groq API for visual analysis.
- **Image previews:** Displays the retrieved images and their scores, and saves a preview as `search_results.png`.
- **Incremental indexing:** Re-indexing updates records for existing image paths and adds new images.

## Architecture

```text
Local image folder
       |
       v
CLIP image encoder (local)
       |
       v
ChromaDB persistent vector collection
       ^
       |
Text query -> CLIP text encoder -> nearest-neighbor search
                                      |
                                      v
                           Top matching image files
                                      |
                                      v
                            Qwen vision API (Groq)
                                      |
                                      v
                         Answer + ranked image previews
```

**Important distinction:** CLIP is the embedding model used for retrieval. Qwen is the vision-language model used to inspect retrieved images and generate an answer. The Groq chat API is not used to generate embeddings.

## Project structure

```text
visual_image_search/
├── images/                  # Add supported images here
├── chroma_db/               # Persistent ChromaDB data (created automatically)
├── .env                     # API key and optional settings
├── requirements.txt
├── app.py
└── README.md
```

Supported extensions in the application: `.png`, `.jpg`, `.jpeg`, `.webp`, and `.bmp`.

## Requirements

- Python 3.10 or newer recommended
- Internet access for downloading the CLIP model the first time and for Qwen API calls
- A Groq API key for question-answering
- Enough disk space and RAM to load the embedding model and process your images

Image embedding runs locally after the model weights have been downloaded. Qwen inference uses the hosted Groq API, so API quotas and provider policies apply.

## Installation

### 1. Create and enter the project directory

Place `app.py`, `requirements.txt`, and this README in your project root. Create an `images` folder and add images to it.

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python directly:

```powershell
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Create `requirements.txt` with:

```text
chromadb
sentence-transformers
Pillow
numpy
groq
python-dotenv
matplotlib
```

Then run:

```bash
python -m pip install -r requirements.txt
```

The first execution downloads the CLIP model weights. This requires an internet connection.

### 4. Configure the Groq API key

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
DISTANCE_METRIC=cosine
```

Obtain an API key from the [Groq Console](https://console.groq.com/keys). Check the [Groq vision documentation](https://console.groq.com/docs/vision) for currently supported vision models and request formats. Model IDs, access, and quotas can change, so confirm that the configured model is available to your account.

**Security:** Never commit `.env` or expose your API key in source control, logs, screenshots, or public repositories. Add the following to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
chroma_db/
images/
search_results.png
```

Remove `images/` from `.gitignore` if the project intentionally includes a small, shareable sample image set.

## Usage

Run commands from the project root, where `app.py` is located.

### 1. Index images

```bash
python app.py index --folder images
```

To index another folder:

```bash
python app.py index --folder "D:/datasets/screenshots"
```

The application recursively finds supported image files, computes normalized CLIP embeddings, and stores the vectors with image paths and filenames in ChromaDB. The database persists in `chroma_db/`.

Example output (illustrative):

```text
Loading CLIP embedding model...
Found 120 images.
Processed 32/120 images
...
Indexing finished.
Processed successfully: 120
Failed: 0
Total records in collection: 120
Distance metric: cosine
```

Actual output depends on your dataset.

### 2. Search and ask a question

```bash
python app.py ask "Find a website login page with an email and password field"
```

More examples:

```bash
python app.py ask "Find screenshots containing a navigation sidebar"
python app.py ask "Show images with a red submit button"
python app.py ask "Find a dashboard with sales charts"
python app.py ask "Find the screenshot that shows an error message"
python app.py ask "Which image contains a registration form?"
```

Retrieve more candidates:

```bash
python app.py ask "Find a dashboard" --top-k 10
```

The application:
1. Encodes the text query with CLIP.
2. Searches the selected ChromaDB collection.
3. Prints the best matching filenames and distances.
4. Sends up to three retrieved images and the question to Qwen via Groq.
5. Prints Qwen's answer and opens a Matplotlib preview of the retrieved images.
6. Saves the preview to `search_results.png`.

A graphical desktop environment is needed for `plt.show()` to open a window. On a headless server, remove or disable the `plt.show()` call and use the saved preview or another image-serving interface.

## Similarity metrics

The app reads `DISTANCE_METRIC` from `.env`. Supported values are `cosine` and `l2`.

### Cosine distance

```dotenv
DISTANCE_METRIC=cosine
```

Chroma returns cosine **distance**, calculated as `1 - cosine_similarity`. The code displays `1 - distance` as the cosine similarity score. Higher similarity is better.

### Euclidean distance

```dotenv
DISTANCE_METRIC=l2
```

Chroma's HNSW `l2` space returns **squared Euclidean distance**. Lower distance is better; zero means identical vectors. It is not a similarity percentage.

Each metric uses a separate collection name to avoid mixing index configurations. After changing the metric, run the indexing command again to populate the corresponding collection.

## How it works

### Image embedding

Each image is loaded with Pillow, EXIF orientation is corrected, and the image is converted to RGB. CLIP generates a normalized vector using `sentence-transformers/clip-ViT-B-32`.

### Text embedding and retrieval

The query is encoded by the same CLIP model. Because CLIP places image and text representations in a shared vector space, the query vector can be compared with image vectors. Chroma returns the nearest candidates and their distances.

### Answer generation

The app encodes up to three retrieved images as base64 JPEG data URLs and sends them with the question to the configured Qwen vision model through Groq. The prompt asks the model to answer from visible evidence and acknowledge when evidence is insufficient.

The model's answer depends on retrieval quality: if the relevant image is not among the retrieved candidates, Qwen may not be able to answer correctly.

## Updating and removing images

- **New or changed images:** Run the indexing command again. `upsert` updates the record for an existing path and adds records for new paths.
- **Deleted or renamed files:** Old records are not automatically removed from ChromaDB. Delete stale records explicitly or rebuild the collection if you need an exact mirror of the folder.
- **Moved project directory:** Chroma metadata stores paths used at indexing time. Re-index after moving images or the project if those paths no longer resolve.

## Limitations and improvements

- CLIP is a general-purpose image-text retrieval model, not an OCR engine. It may miss tiny UI labels, exact text, error codes, or subtle layout differences.
- For text-heavy screenshots, add OCR (for example, Tesseract or PaddleOCR) and index extracted text alongside image vectors.
- Consider hybrid retrieval combining image embeddings, OCR/text embeddings, and metadata filters.
- The implementation sends only the top three candidates to Qwen. Increase the number only if the chosen API/model supports the resulting image count and payload size.
- Similarity values are ranking signals, not calibrated probabilities. A cosine similarity of `0.8` does not mean an 80% chance that an image is correct.
- The script is a command-line baseline, not a multi-user production service. Production deployment should add request validation, logging, retries, concurrency controls, authentication, monitoring, and appropriate data-retention policies.
- Images sent to Groq leave the local machine and are processed by the hosted API. Do not send confidential or regulated images unless your organization's policies and the provider's terms permit it.

## Troubleshooting

### `GROQ_API_KEY is missing`

Check that `.env` is in the same working directory from which you run `app.py`, and that the variable is spelled correctly.

### Model unavailable or API error

Check the current model ID and vision support in the [Groq vision documentation](https://console.groq.com/docs/vision), verify your account's access and quota, and confirm that your installed `groq` SDK is current.

### No images found

Confirm that the selected folder exists and contains files with supported extensions. The indexing command searches subfolders too.

### Search results are poor

Try a more descriptive query, inspect the top results, and consider adding OCR or testing another image-text embedding model. Re-index after changing embedding models; vectors from different models must not be mixed.

### Matplotlib window does not open

Check that you are running in a graphical desktop environment. On servers or containers, use the saved `search_results.png` instead of relying on an interactive window.

## Useful links

- [Groq vision documentation](https://console.groq.com/docs/vision)
- [Groq API keys](https://console.groq.com/keys)
- [Sentence Transformers image search](https://sbert.net/examples/sentence_transformer/applications/image-search/README.html)
- [CLIP model card](https://huggingface.co/sentence-transformers/clip-ViT-B-32)
- [ChromaDB documentation](https://docs.trychroma.com/)

## License and costs

This project combines third-party libraries and pretrained models. Review each dependency's and model's license before commercial use. The CLIP model runs locally after download; hosted Qwen calls use Groq and may be subject to free-tier quotas, rate limits, and pricing changes.
