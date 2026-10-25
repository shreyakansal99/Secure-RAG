import json
import os
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer
from app import config


def load_document(path):
    """Return list of (page_number, text) for a txt or pdf file."""
    if path.endswith(".pdf"):
        doc = fitz.open(path)
        return [(i + 1, page.get_text()) for i, page in enumerate(doc)]
    with open(path, "r", encoding="utf-8") as f:
        return [(1, f.read())]


def chunk_text(text, chunk_words=150, overlap=30):
    words = text.split()
    chunks = []
    step = chunk_words - overlap
    for start in range(0, len(words), step):
        piece = " ".join(words[start:start + chunk_words])
        if piece.strip():
            chunks.append(piece)
        if start + chunk_words >= len(words):
            break
    return chunks


def main():
    with open(config.ACL_FILE) as f:
        acl = json.load(f)

    model = SentenceTransformer(config.EMBED_MODEL)
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)

    # start fresh each run
    try:
        client.delete_collection(config.COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(
        config.COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    ids, texts, metas = [], [], []
    for filename in sorted(os.listdir(config.DOCS_DIR)):
        path = os.path.join(config.DOCS_DIR, filename)
        allowed = acl.get(filename, [])
        for page_no, page_text in load_document(path):
            for i, chunk in enumerate(chunk_text(page_text)):
                ids.append(f"{filename}-p{page_no}-c{i}")
                texts.append(chunk)
                meta = {"source": filename, "page": page_no}
                # Chroma metadata can't hold lists, so one boolean flag per role.
                # We'll use these for access control in Step 3.
                for role in config.ROLES:
                    meta[f"role_{role}"] = role in allowed
                metas.append(meta)

    embeddings = model.encode(texts).tolist()
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metas)
    print(f"Indexed {len(texts)} chunks from {len(set(m['source'] for m in metas))} files.")


if __name__ == "__main__":
    main()