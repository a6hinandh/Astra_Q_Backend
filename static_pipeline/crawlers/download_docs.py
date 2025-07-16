import os
import json
import requests

json_dir = 'static_pipeline/output/json_pages'
output_dir = 'static_pipeline/output/docs_raw'

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(json_dir):
    if file.endswith('.json'):
        # Fix: Specify UTF-8 encoding when reading JSON files
        with open(os.path.join(json_dir, file), 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                links = data.get('pdf_links', [])

                for link in links:
                    filename = link.split('/')[-1]
                    filepath = os.path.join(output_dir, filename)

                    if os.path.exists(filepath):
                        print(f"[SKIP] {filename} already downloaded.")
                        continue

                    try:
                        print(f"[DOWNLOAD] {link}")
                        r = requests.get(link, stream=True, timeout=15)
                        r.raise_for_status()
                        with open(filepath, 'wb') as out_file:
                            for chunk in r.iter_content(chunk_size=1024):
                                out_file.write(chunk)
                        print(f"[SAVED] {filename}")
                    except Exception as e:
                        print(f"[ERROR] Failed to download {link}: {e}")
                        
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON in file {file}: {e}")
            except UnicodeDecodeError as e:
                print(f"[ERROR] Encoding error in file {file}: {e}")