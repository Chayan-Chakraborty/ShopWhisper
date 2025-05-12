from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

def load_and_split(filepath: str):
    loader = TextLoader(filepath)
    documents = loader.load()

    splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(documents)
