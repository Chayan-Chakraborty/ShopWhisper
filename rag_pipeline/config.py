OPENAI_API_KEY = "your_api_key"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 5
PDF_PATH = "/Users/sandeep/Downloads/Dummy Data Pdf - Sheet1.csv"
FALL_BACK_DATA = {
    "answer": {
        "products": [
            {
                "ID": 1,
                "name": "BWP Marine Plywood 18mm",
                "type": "Plywood",
                "properties": {
                    "Category": "Waterproof",
                    "Material": "Hardwood",
                    "Size": "8x4 ft",
                    "Waterproof": "Yes",
                    "Termite-Proof": "Yes",
                    "Fire-Rated": "No",
                    "Usage": "Bathrooms, Boats"
                },
                "wood_type": "Hardwood",
                "thickness": "18mm",
                "dimensions": "8x4 ft",
                "color": "Brown",
                "price": 1650,
                "brand": "GreenPly",
                "eco_friendly": "No",
                "fire_resistant": "No",
                "termite_resistant": "Yes",
                "recommended_for": "Bathrooms, Boats",
                "rating": 4.7,
                "discount": "5%",
                "stock": 50,
                "isSponsored": True
            },
            {
                "ID": 2,
                "name": "MR Commercial Plywood 12mm",
                "type": "Plywood",
                "properties": {
                    "Category": "Interior",
                    "Material": "Softwood",
                    "Size": "8x4 ft",
                    "Waterproof": "No",
                    "Termite-Proof": "No",
                    "Fire-Rated": "No",
                    "Usage": "Furniture"
                },
                "wood_type": "Softwood",
                "thickness": "12mm",
                "dimensions": "8x4 ft",
                "color": "Light Brown",
                "price": 1100,
                "brand": "Century",
                "eco_friendly": "No",
                "fire_resistant": "No",
                "termite_resistant": "No",
                "recommended_for": "Furniture",
                "rating": 4.2,
                "discount": "0%",
                "stock": 120,
                "isSponsored": True
            },
            {
                "ID": 4,
                "name": "Teak Veneer Plywood 19mm",
                "type": "Plywood",
                "properties": {
                    "Category": "Premium",
                    "Material": "Teak",
                    "Size": "8x4 ft",
                    "Waterproof": "Yes",
                    "Termite-Proof": "Yes",
                    "Fire-Rated": "Yes",
                    "Usage": "Luxury Furniture"
                },
                "wood_type": "Teak",
                "thickness": "19mm",
                "dimensions": "8x4 ft",
                "color": "Golden",
                "price": 2400,
                "brand": "Kitply",
                "eco_friendly": "No",
                "fire_resistant": "Yes",
                "termite_resistant": "Yes",
                "recommended_for": "Luxury Furniture",
                "rating": 4.9,
                "discount": "15%",
                "stock": 35,
                "isSponsored": False
            }
        ]
    }
}