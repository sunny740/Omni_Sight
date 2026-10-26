import os
import io
import argparse
import hashlib
import base64
import matplotlib as plt
from pathlib import Path
import chromadb

import chromadb
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image, ImageOps
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

load_dotenv()

IMAGE_FOLDER = Path("images")
CHROMA_PATH = "chroma_db"

# Local, free-to-use image + text embedding model.
EMBEDDING_MODEL = "sentence-transformers/clip-ViT-B-32"

# Groq-hosted Qwen vision model.
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

# Supported values: cosine, l2
DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", "cosine").lower()

if DISTANCE_METRIC not in {"cosine", "l2"}:
    raise ValueError("DISTANCE_METRIC must be 'cosine' or 'l2'.")

SUPPORTED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".bmp"
}

# Load the embedding model once per application run.
print("Loading CLIP embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)

# Persistent local vector database.
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Separate collection names prevent accidental mixing of
# cosine and Euclidean indexes.
COLLECTION_NAME = f"image_collection_{DISTANCE_METRIC}"

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": DISTANCE_METRIC},
)

# Groq is only required when asking a question.
groq_client = (
    Groq(api_key=os.environ["GROQ_API_KEY"])
    if os.getenv("GROQ_API_KEY")
    else None
)


# ---------------------------------------------------------
# IMAGE UTILITIES
# ---------------------------------------------------------

def find_images(folder: Path):
    """Return all supported images under a folder."""
    if not folder.exists():
        raise FileNotFoundError(
            f"Image folder does not exist: {folder.resolve()}"
        )

    return sorted(
        p.resolve()
        for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def open_rgb_image(path: str) -> Image.Image:
    """Open an image safely and normalize its orientation."""
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        return image.convert("RGB")


def make_image_embedding(path: str) -> np.ndarray:
    """Create a normalized CLIP image embedding."""
    image = open_rgb_image(path)

    vector = embedder.encode(
        image,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return np.asarray(vector, dtype=np.float32)


def make_text_embedding(query: str) -> np.ndarray:
    """Encode a natural-language query in CLIP's joint space."""
    vector = embedder.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return np.asarray(vector, dtype=np.float32)


def stable_image_id(path: str) -> str:
    """Create a stable ID so re-indexing updates existing records."""
    return hashlib.sha256(path.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# STEP 1: INDEX THE IMAGE FOLDER
# ---------------------------------------------------------

def index_images(folder: Path = IMAGE_FOLDER):
    """Embed all images and store them in persistent ChromaDB."""
    paths = find_images(folder)

    if not paths:
        print(f"No supported images found in {folder.resolve()}")
        return

    added = 0
    failed = 0
    batch_size = 32

    print(f"Found {len(paths)} images.")

    for start in range(0, len(paths), batch_size):
        batch_paths = paths[start:start + batch_size]

        valid_paths = []
        valid_embeddings = []
        valid_ids = []
        valid_metadata = []

        for path in batch_paths:
            try:
                image = open_rgb_image(str(path))

                embedding = embedder.encode(
                    image,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )

                valid_paths.append(str(path))
                valid_embeddings.append(
                    np.asarray(embedding, dtype=np.float32).tolist()
                )
                valid_ids.append(stable_image_id(str(path)))
                valid_metadata.append({
                    "path": str(path),
                    "filename": path.name,
                    "extension": path.suffix.lower(),
                })

            except Exception as exc:
                failed += 1
                print(f"Skipping {path}: {exc}")

        if valid_paths:
            collection.upsert(
                ids=valid_ids,
                embeddings=valid_embeddings,
                metadatas=valid_metadata,
            )
            added += len(valid_paths)

        print(
            f"Processed {min(start + batch_size, len(paths))}"
            f"/{len(paths)} images"
        )

    print("\nIndexing finished.")
    print(f"Processed successfully: {added}")
    print(f"Failed: {failed}")
    print(f"Total records in collection: {collection.count()}")
    print(f"Persistent database: {Path(CHROMA_PATH).resolve()}")
    print(f"Distance metric: {DISTANCE_METRIC}")


# ---------------------------------------------------------
# STEP 2: RETRIEVE RELEVANT IMAGES
# ---------------------------------------------------------

def search_images(query: str, top_k: int = 5):
    """
    Convert the text query into a vector and retrieve the
    closest image vectors from ChromaDB.
    """
    if collection.count() == 0:
        raise RuntimeError(
            "The image collection is empty. Run the index command first."
        )

    query_embedding = make_text_embedding(query)

    result = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, collection.count()),
        include=["metadatas", "distances"],
    )

    matches = []

    ids = result["ids"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    for image_id, metadata, distance in zip(
        ids, metadatas, distances
    ):
        distance = float(distance)

        # Chroma's cosine distance is 1 - cosine similarity.
        # Euclidean mode reports squared L2 distance.
        if DISTANCE_METRIC == "cosine":
            score = 1.0 - distance
        else:
            score = distance

        matches.append({
            "id": image_id,
            "path": metadata["path"],
            "filename": metadata["filename"],
            "distance": distance,
            "score": score,
        })

    return matches


# ---------------------------------------------------------
# STEP 3: PREPARE IMAGES FOR THE QWEN VISION API
# ---------------------------------------------------------

def image_as_data_url(path: str) -> str:
    """
    Encode an image as a base64 JPEG data URL.
    Resize very large images to reduce API payload size.
    """
    image = open_rgb_image(path)

    image.thumbnail((1800, 1800))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90, optimize=True)

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


# ---------------------------------------------------------
# STEP 4: ASK QWEN TO ANSWER USING RETRIEVED IMAGES
# ---------------------------------------------------------

def answer_with_qwen(query: str, matches: list) -> str:
    """
    Send the user's question and up to three retrieved images
    to Qwen via Groq for visual reasoning.
    """
    if groq_client is None:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    # This model's documented vision limit is three images/request.
    selected = matches[:3]

    if not selected:
        return "No matching images were found."

    content = [{
        "type": "text",
        "text": (
            "You are a visual question-answering assistant.\n"
            f"User question: {query}\n\n"
            "The following images were retrieved from a local image "
            "database using semantic similarity. They are candidate "
            "evidence, not guaranteed matches.\n"
            "Inspect the actual image contents before answering. "
            "Answer based only on what is visible in these images. "
            "If the images do not contain enough evidence, say so. "
            "Do not invent text, UI elements, or facts.\n"
            "Identify relevant image filenames in your answer."
        ),
    }]

    for index, match in enumerate(selected, start=1):
        content.append({
            "type": "text",
            "text": (
                f"Candidate image {index}: {match['filename']}\n"
                f"Retrieval distance: {match['distance']:.4f}"
            ),
        })

        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_as_data_url(match["path"])
            },
        })

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        temperature=0.2,
        max_completion_tokens=1200,
    )

    return response.choices[0].message.content or (
        "The model returned an empty answer."
    )


# ---------------------------------------------------------
# STEP 5: DISPLAY MATCHING IMAGES
# ---------------------------------------------------------

def display_matches(query: str, matches: list):
    """Display retrieved images and their similarity/distance."""
    if not matches:
        print("No matching images found.")
        return

    count = len(matches)
    columns = min(3, count)
    rows = (count + columns - 1) // columns

    fig, axes = plt.subplots(
        rows,
        columns,
        figsize=(5 * columns, 4 * rows),
        squeeze=False,
    )

    flat_axes = axes.ravel()

    for axis, match in zip(flat_axes, matches):
        try:
            image = open_rgb_image(match["path"])
            axis.imshow(image)
            axis.axis("off")

            if DISTANCE_METRIC == "cosine":
                title = (
                    f"{match['filename']}\n"
                    f"Cosine similarity: {match['score']:.4f}"
                )
            else:
                title = (
                    f"{match['filename']}\n"
                    f"Squared L2 distance: {match['distance']:.4f}"
                )

            axis.set_title(title, fontsize=9)

        except Exception as exc:
            axis.set_title(f"Unable to display: {exc}")
            axis.axis("off")

    for axis in flat_axes[count:]:
        axis.axis("off")

    fig.suptitle(f"Image search results: {query}", fontsize=13)
    fig.tight_layout()

    output_path = Path("search_results.png")
    fig.savefig(output_path, dpi=150, bbox_inches="tight")

    print(f"\nSaved image preview to: {output_path.resolve()}")

    # Opens the figure in a graphical desktop environment.
    plt.show()


# ---------------------------------------------------------
# STEP 6: COMPLETE QUESTION-ANSWERING PIPELINE
# ---------------------------------------------------------

def ask_question(query: str, top_k: int = 5):
    """Retrieve images, generate an answer, and show the results."""
    print(f"\nQuestion: {query}")
    print("\nSearching ChromaDB...")

    matches = search_images(query, top_k=top_k)

    if not matches:
        print("No relevant images were found.")
        return

    print("\nRetrieved images:")

    for index, match in enumerate(matches, start=1):
        if DISTANCE_METRIC == "cosine":
            print(
                f"{index}. {match['filename']} | "
                f"cosine similarity={match['score']:.4f} | "
                f"{match['path']}"
            )
        else:
            print(
                f"{index}. {match['filename']} | "
                f"squared L2 distance={match['distance']:.4f} | "
                f"{match['path']}"
            )

    print("\nAsking Qwen to analyze the top candidate images...")

    try:
        answer = answer_with_qwen(query, matches)
        print("\n" + "=" * 65)
        print("ANSWER")
        print("=" * 65)
        print(answer)
    except Exception as exc:
        print(f"\nQwen API request failed: {exc}")
        print(
            "The retrieved images are still available. "
            "Check your API key, quota, model availability, "
            "and network connection."
        )

    display_matches(query, matches)


# ---------------------------------------------------------
# COMMAND-LINE INTERFACE
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Local semantic image search with CLIP, "
                    "ChromaDB and Qwen vision."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser(
        "index",
        help="Index an image directory into ChromaDB",
    )
    index_parser.add_argument(
        "--folder",
        default=str(IMAGE_FOLDER),
        help="Folder containing images",
    )

    ask_parser = subparsers.add_parser(
        "ask",
        help="Search images and ask Qwen a question",
    )
    ask_parser.add_argument(
        "query",
        help='Natural-language question, e.g. "Find a login page"',
    )
    ask_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of images to retrieve (default: 5)",
    )

    args = parser.parse_args()

    if args.command == "index":
        index_images(Path(args.folder))
    elif args.command == "ask":
        if args.top_k < 1:
            parser.error("--top-k must be at least 1")
        ask_question(args.query, top_k=args.top_k)


if __name__ == "__main__":
    main()
