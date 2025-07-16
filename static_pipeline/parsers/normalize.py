import os
import json
import sys

# Add the root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

from static_pipeline.utils.text_cleaning import clean_text

input_dir = 'static_pipeline/output/docs_parsed'

if not os.path.exists(input_dir):
    print(f"[ERROR] Input directory not found: {input_dir}")
    exit(1)

for file in os.listdir(input_dir):
    if file.endswith('.json'):
        try:
            print(f"[NORMALIZING] {file}")
            with open(os.path.join(input_dir, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Clean the text
            if 'text' in data:
                data['text'] = clean_text(data['text'])
            
            # Save back to the same file
            with open(os.path.join(input_dir, file), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"[SUCCESS] Normalized {file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to normalize {file}: {e}")

print("[COMPLETED] Text normalization finished")