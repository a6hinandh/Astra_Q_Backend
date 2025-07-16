import os
import json
import sys
import docx

# Add the root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

from static_pipeline.utils.file_utils import save_json

docx_dir = 'static_pipeline/output/docs_raw'
output_dir = 'static_pipeline/output/docs_parsed'

# Check if input directory exists
if not os.path.exists(docx_dir):
    print(f"[ERROR] Input directory not found: {docx_dir}")
    exit(1)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# List all files in the directory
all_files = os.listdir(docx_dir)
docx_files = [f for f in all_files if f.endswith('.docx')]

print(f"[INFO] Found {len(all_files)} total files in {docx_dir}")
print(f"[INFO] Found {len(docx_files)} DOCX files to process")

if len(docx_files) == 0:
    print("[WARNING] No DOCX files found to process")
    exit(0)

for file in docx_files:
    if file.endswith('.docx'):
        try:
            print(f"[PARSING] {file}")
            doc = docx.Document(os.path.join(docx_dir, file))
            text = "\n".join([para.text for para in doc.paragraphs])
            
            parsed = {
                "filename": file,
                "text": text
            }
            
            # Save with the same filename but .json extension
            json_filename = file.replace('.docx', '.json')
            if save_json(json_filename, parsed, output_dir):
                print(f"[SUCCESS] Parsed {file}")
            else:
                print(f"[ERROR] Failed to save {file}")
                
        except Exception as e:
            print(f"[ERROR] Failed to parse {file}: {e}")