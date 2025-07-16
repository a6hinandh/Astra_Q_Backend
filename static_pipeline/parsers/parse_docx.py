import os, json
import docx
from utils.file_utils import save_json

docx_dir = 'static_pipeline/output/docs_raw'
output_dir = 'static_pipeline/output/docs_parsed'

for file in os.listdir(docx_dir):
    if file.endswith('.docx'):
        doc = docx.Document(os.path.join(docx_dir, file))
        text = "\n".join([para.text for para in doc.paragraphs])
        parsed = {
            "filename": file,
            "text": text
        }
        save_json(file.replace('.docx', '.json'), parsed, output_dir)
