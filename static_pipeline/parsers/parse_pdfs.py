import fitz  # PyMuPDF
import os, json
from utils.file_utils import save_json

pdf_dir = 'static_pipeline/output/docs_raw'
output_dir = 'static_pipeline/output/docs_parsed'

for file in os.listdir(pdf_dir):
    if file.endswith('.pdf'):
        doc = fitz.open(os.path.join(pdf_dir, file))
        text = "\n".join([page.get_text() for page in doc])
        parsed = {
            "filename": file,
            "text": text
        }
        save_json(file.replace('.pdf', '.json'), parsed, output_dir)
