
from sentence_transformers import SentenceTransformer

class EmbeddingModel:

    def __init__(self,
                model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):

        if isinstance(texts, str):
            texts = [texts]

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return vectors
