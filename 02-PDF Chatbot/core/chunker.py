
from langchain_text_splitters import RecursiveCharacterTextSplitter

class chunker:

    def __init__(self,
                chunk_size=500,
                chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def fixed_chunks(self, text):

        chunks=[]

        start=0

        while start < len(text):

            end=start+self.chunk_size
            chunks.append(text[start:end])
            start=end
        return chunks

    def sliding_chunks(self,text):

        chunks=[]

        start = 0 

        while start < len(text):

            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def recursive_chunks(self,text):
        splitter=RecursiveCharacterTextSplitter(

            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap
        )

        return splitter.split_text(text)
