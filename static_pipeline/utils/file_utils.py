import os, json

def save_html(title, html, out_dir='static_pipeline/output/raw_html'):
    filename = title.lower().replace(' ', '_')[:50] + '.html'
    path = os.path.join(out_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

def save_json(filename, data, out_dir='static_pipeline/output/json_pages'):
    path = os.path.join(out_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
