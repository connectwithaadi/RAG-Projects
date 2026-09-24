from langchain_community.document_loaders import PyPDFLoader

data = PyPDFLoader("document_loaders/GRU.pdf")

docs = data.load()

print(len(docs))