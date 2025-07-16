import os, json
from utils.text_cleaning import clean_text

input_dir = 'static_pipeline/output/docs_parsed'

for file in os.listdir(input_dir):
    if file.endswith('.json'):
        with open(os.path.join(input_dir, file), 'r') as f:
            data = json.load(f)
            data['text'] = clean_text(data['text'])
        with open(os.path.join(input_dir, file), 'w') as f:
            json.dump(data, f, indent=2)
