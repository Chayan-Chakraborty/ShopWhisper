OPENAI_API_KEY = "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"
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
                    "sub-category": "Waterproof",
                    "material": "Hardwood",
                    "waterproof": "Yes",
                    "termite_proof": "Yes",
                    "fire_rated": "No",
                    "usage": "Bathrooms, Boats"
                },
                "wood_type": "Hardwood",
                "thickness": "18mm",
                "dimensions": "8x4 ft",
                "color": "Brown",
                "price": 1650,
                "brand": "GreenPly",
                "eco_friendly": "Yes",
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
                    "sub-category": "Interior",
                    "material": "Softwood",
                    "waterproof": "No",
                    "termite_proof": "No",
                    "fire_rated": "No",
                    "usage": "Furniture"
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
                    "sub-category": "Premium",
                    "material": "Teak",
                    "waterproof": "Yes",
                    "termite_proof": "Yes",
                    "fire_rated": "Yes",
                    "usage": "Luxury Furniture"
                },
                "wood_type": "Teak",
                "thickness": "19mm",
                "dimensions": "8x4 ft",
                "color": "Golden",
                "price": 2400,
                "brand": "Kitply",
                "eco_friendly": "Yes",
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