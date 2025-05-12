import pandas as pd
from typing import List, Dict, Any
import os
from config import PDF_PATH  # Update this to your actual CSV path


class CSVProcessor:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def extract_products(self) -> List[Dict[str, Any]]:
        """
        Extract product information from a CSV file.
        Returns a list of product dictionaries.
        """
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

            # Read the CSV file into a DataFrame
            df = pd.read_csv(self.csv_path)

            # Clean column names (strip whitespace and replace spaces with underscores)
            df.columns = df.columns.str.strip().str.replace(' ', '_')

            # Convert DataFrame rows to dictionaries
            products = df.to_dict(orient="records")
            return products

        except Exception as e:
            print(f"Error processing CSV: {str(e)}")
            return []

    @staticmethod
    def save_products_to_csv(products: List[Dict[str, Any]], output_path: str):
        """
        Save extracted products to a CSV file
        """
        df = pd.DataFrame(products)
        df.to_csv(output_path, index=False)


def get_products(csv_path: str = PDF_PATH, output_csv_path: str = PDF_PATH) -> List[Dict[str, Any]]:
    """
    Main function to get products either from CSV or an existing CSV file.
    """
    # If the CSV file exists, load the data
    if os.path.exists(csv_path):
        processor = CSVProcessor(csv_path)
        return processor.extract_products()
    
    raise FileNotFoundError(f"Product data file not found: {csv_path}")
