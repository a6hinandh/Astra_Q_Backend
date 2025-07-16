import os
import json
import re

def safe_filename(filename):
    """
    Convert a string to a safe filename by removing/replacing invalid characters
    """
    # Remove or replace invalid characters for Windows/Unix filesystems
    # Invalid characters: < > : " | ? * \ /
    filename = re.sub(r'[<>:"|?*\\/]', '_', filename)
    filename = re.sub(r'[&]', 'and', filename)  # Replace & with 'and'
    filename = re.sub(r'[^\w\s\-_.]', '', filename)  # Keep only alphanumeric, spaces, hyphens, underscores, dots
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores with single
    filename = filename.strip('_')  # Remove leading/trailing underscores
    
    # Limit length to avoid filesystem issues
    if len(filename) > 100:
        filename = filename[:100]
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    return filename

def save_html(title, html, out_dir='static_pipeline/output/raw_html'):
    """
    Save HTML content to a file with a safe filename
    """
    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)
    
    # Generate safe filename
    safe_title = safe_filename(title)
    filename = safe_title + '.html'
    
    # Full path
    path = os.path.join(out_dir, filename)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[SAVED HTML] {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save HTML {filename}: {e}")
        return False

def save_json(filename, data, out_dir='static_pipeline/output/json_pages'):
    """
    Save JSON data to a file
    """
    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)
    
    # Make sure filename is safe
    if not filename.endswith('.json'):
        filename = safe_filename(filename) + '.json'
    else:
        base_name = filename.replace('.json', '')
        filename = safe_filename(base_name) + '.json'
    
    path = os.path.join(out_dir, filename)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[SAVED JSON] {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save JSON {filename}: {e}")
        return False