import json
import os
from typing import List, Dict, Any

DATA_FILE = "bible_data.json"
PROCESSED_FILE = "processed_bible_data.json"

def load_raw_data(file_path: str ) -> Dict[str, Any]:
    """Loads the raw Bible data from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def preprocess_bible_data(raw_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Flattens the nested Bible JSON structure into a list of verses.
    Each item in the list is a dictionary with 'reference' and 'text'.
    """
    processed_verses = []
    
    for book_data in raw_data.get("books", []):
        book_name = book_data.get("name")
        
        for chapter_data in book_data.get("chapters", []):
            chapter_num = chapter_data.get("chapter")
            
            for verse_data in chapter_data.get("verses", []):
                verse_num = verse_data.get("verse")
                verse_text = verse_data.get("text")
                
                if book_name and chapter_num and verse_num and verse_text:
                    reference = f"{book_name} {chapter_num}:{verse_num}"
                    processed_verses.append({
                        "reference": reference,
                        "text": verse_text.strip()
                    })
                    
    return processed_verses

def save_processed_data(data: List[Dict[str, str]], file_path: str):
    """Saves the processed data to a new JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print(f"Loading raw data from {DATA_FILE}...")
    try:
        raw_data = load_raw_data(DATA_FILE)
    except FileNotFoundError as e:
        print(e)
        return

    print("Preprocessing data...")
    processed_data = preprocess_bible_data(raw_data)
    print(f"Total verses processed: {len(processed_data)}")

    print(f"Saving processed data to {PROCESSED_FILE}...")
    save_processed_data(processed_data, PROCESSED_FILE)
    print("Preprocessing complete.")

if __name__ == "__main__":
    main()
