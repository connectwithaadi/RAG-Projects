
from core.embedding import EmbeddingModel
from core.vector_store import VectorStore

embedder = EmbeddingModel()

store = VectorStore()

store.load("vector_store")

question = input("Question: ")

query = embedder.encode(question)

results = store.search(query,k=5)

print()

print("="*80)

for i,result in enumerate(results,1):

    print(f"Result {i}")

    print("Score :",round(result["score"],4))

    print("File :",result["filename"])

    print("Page :",result["page"])

    print()

    print(result["text"][:500])

    print()

    print("-"*80)
