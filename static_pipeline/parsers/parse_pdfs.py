import fitz  # PyMuPDF
import os
import json
import sys

# Add the root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

from static_pipeline.utils.file_utils import save_json

pdf_dir = 'static_pipeline/output/docs_raw'
output_dir = 'static_pipeline/output/docs_parsed'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(pdf_dir):
    if file.endswith('.pdf'):
        try:
            print(f"[PARSING] {file}")
            doc = fitz.open(os.path.join(pdf_dir, file))
            text = "\n".join([page.get_text() for page in doc])
            doc.close()  # Close the document to free memory
            
            parsed = {
                "filename": file,
                "text": text
            }
            
            # Save with the same filename but .json extension
            json_filename = file.replace('.pdf', '.json')
            if save_json(json_filename, parsed, output_dir):
                print(f"[SUCCESS] Parsed {file}")
            else:
                print(f"[ERROR] Failed to save {file}")
                
        except Exception as e:
            print(f"[ERROR] Failed to parse {file}: {e}")