import pandas as pd
from langchain.text_splitter import CharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

def load_and_split_csv(filepath: str):
    df = pd.read_csv(filepath)

    # Join all column values into a single string per row
    rows_as_text = df.apply(lambda row: ' | '.join(row.dropna().astype(str)), axis=1).tolist()

    # Optional: Join all rows into a large document, then chunk it
    joined_text = "\n".join(rows_as_text)

    splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_text(joined_text)

    return chunks