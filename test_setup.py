import chromadb
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer

print("Chroma version:", chromadb.__version__)
print("PyMuPDF OK")

model = SentenceTransformer("all-MiniLM-L6-v2")
emb = model.encode("hello world")
print("Embedding size:", len(emb))
print("Setup is working!")