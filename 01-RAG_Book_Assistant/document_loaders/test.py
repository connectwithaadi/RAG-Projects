from langchain_community.document_loaders import TextLoader

data = TextLoader("D:/Mission Project/RAG Project/document_loaders/notes.txt")

docs = data.load()

print(docs)