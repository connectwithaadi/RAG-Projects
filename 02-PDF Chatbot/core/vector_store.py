
import json
from pathlib import Path

import faiss
import numpy as np

class VectorStore:

    def __init__(self):

        self.index = None
        self.metadata = []

    def build(self, embeddings, metadata):

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings.astype("float32"))

        self.metadata = metadata

    def save(self, directory):

        directory = Path(directory)

        directory.mkdir(parents=True, exist_ok = True)

        faiss.write_index(
            self.index,
            str(directory/"faiss_index.bin")
        )

        with open(directory/"metadata.json","w", encoding="utf-8") as f:

            json.dump(
                self.metadata,
                f,
                indent = 4,
                ensure_ascii=False
            )
    def load(self,directory):

        directory=Path(directory)

        self.index = faiss.read_index(
            str(directory/"faiss_index.bin")
        )

        with open(directory/"metadata.json", encoding="utf-8") as f:

            self.metadata = json.load(f)

    def search(self, query_vector, k=5):

        scores, indices = self.index.search(
            query_vector.astype("float32"),
            k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            item = self.metadata[idx]

            item["score"] = float(score)

            results.append(item)

        return results
