import pandas as pd
from langchain.text_splitter import CharacterTextSplitter

# Constants for chunk size and overlap
CHUNK_SIZE = 500  # Adjust based on your requirement
CHUNK_OVERLAP = 50  # Adjust based on your requirement

def load_and_split_csv(filepath: str):
    # Read the CSV file
    df = pd.read_csv(filepath)

    # Ensure all columns are present and in correct format
    rows_as_text = []

    # Check if 'id' exists in the CSV columns
    if 'ID' not in df.columns:
        raise ValueError("The CSV file must contain an 'id' column.")

    # Convert each row into a dictionary with column names as keys
    for index, row in df.iterrows():
        product = {col: row.get(col, "") for col in df.columns}  # Include all columns dynamically
        # Convert product dictionary to string for chunking
        product_text = " | ".join(f"{key}: {value}" for key, value in product.items())
        rows_as_text.append(product_text)

    # Join all rows into a large document, then split into chunks
    joined_text = "\n".join(rows_as_text)

    splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_text(joined_text)

    return chunks

