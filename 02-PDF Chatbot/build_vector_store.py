
from pathlib import Path
import json
import numpy as np

from tqdm import tqdm

from core.embedding import EmbeddingModel
from core.vector_store import VectorStore

CHUNK_DIR = Path("data/chunks")

VECTOR_DIR = Path("vector_store")

embedder = EmbeddingModel()

texts=[]

metadata=[]

for file in tqdm(CHUNK_DIR.glob("*_chunks.json")):

    with open(file, encoding="utf-8") as f:

        document = json.load(f)

    for chunk in document["chunks"]:

        texts.append(chunk["text"])

        metadata.append({

            "filename":document["filename"],

            "page":chunk["page"],

            "chunk_id":chunk["chunk_id"],

            "text":chunk["text"]       
        })

print(f"Encoding {len(texts)} chunks...")

embeddings = embedder.encode(texts)

store = VectorStore()

store.build(
    embeddings,
    metadata
)

store.save(VECTOR_DIR)

print("Vector database created.")

