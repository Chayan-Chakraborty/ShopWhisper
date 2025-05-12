import tabula
import pandas as pd
from typing import List, Dict, Any
import os

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_products(self) -> List[Dict[str, Any]]:
        """
        Extract product information from PDF file.
        Returns a list of product dictionaries.
        """
        try:
            # Read tables from PDF
            tables = tabula.read_pdf(self.pdf_path, pages='all')
            
            if not tables:
                raise ValueError("No tables found in PDF")
            
            # Assume the first table contains our product data
            df = tables[0]
            
            # Clean column names - remove whitespace and special characters
            df.columns = df.columns.str.strip().str.replace(' ', '_')
            
            # Convert DataFrame to list of dictionaries
            products = []
            for _, row in df.iterrows():
                product = {
                    "ID": int(row.get('ID', 0)),
                    "Product_Name": str(row.get('Product_Name', '')),
                    "Category": str(row.get('Category', '')),
                    "Sub_Category": str(row.get('Sub_Category', '')),
                    "Price": float(str(row.get('Price_(INR)', '0')).replace(',', '').split('.')[0]),
                    "Brand": str(row.get('Brand', ''))
                }
                products.append(product)
            
            return products
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return []
    
    @staticmethod
    def save_products_to_csv(products: List[Dict[str, Any]], output_path: str):
        """
        Save extracted products to a CSV file
        """
        df = pd.DataFrame(products)
        df.to_csv(output_path, index=False)
        
def get_products(pdf_path: str = "products.pdf", csv_path: str = "products.csv") -> List[Dict[str, Any]]:
    """
    Main function to get products either from PDF or existing CSV
    """
    # If CSV exists and is newer than PDF, use it
    if os.path.exists(csv_path) and os.path.exists(pdf_path):
        if os.path.getmtime(csv_path) > os.path.getmtime(pdf_path):
            return pd.read_csv(csv_path).to_dict('records')
    
    # Otherwise process PDF
    if os.path.exists(pdf_path):
        processor = PDFProcessor(pdf_path)
        products = processor.extract_products()
        if products:
            PDFProcessor.save_products_to_csv(products, csv_path)
        return products
    
    raise FileNotFoundError(f"Product data file not found: {pdf_path}") 