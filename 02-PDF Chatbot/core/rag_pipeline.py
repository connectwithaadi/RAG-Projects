 
from core.embedding import EmbeddingModel
from core.vector_store import VectorStore
from core.prompt import build_prompt
from core.groq_client import GroqClient

class RAGPipeline:

    def __init__(self):
        self.embedder = EmbeddingModel()

        self.store = VectorStore()

        self.store.load("vector_store")

        self.llm = GroqClient()

    def ask(self, question, top_k=5):
        query = self.embedder.encode(question)

        results = self.store.search(query, k=top_k)

        contexts = [

            r["text"]
            for r in results    
        ]

        prompt = build_prompt(
            question,
            contexts
        )

        answer = self.llm.generate(prompt)

        return {
            "answer": answer,
            "sources": results
        }
