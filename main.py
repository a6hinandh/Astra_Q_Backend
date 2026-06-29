import os

def run(script_path):
    print(f"\nRunning {script_path}...")
    os.system(f'python {script_path}')

if __name__ == "__main__":
    print("Choose a pipeline step to run:\n")
    print("1. Crawl static HTML pages")
    print("2. Download PDFs/DOCXs")
    print("3. Parse PDFs")
    print("4. Parse DOCXs")
    print("5. Normalize parsed docs")
    print("6. Run ALL")

    choice = input("\nEnter your choice [1-6]: ").strip()

    scripts = {
        "1": "static_pipeline/crawlers/crawl_static.py",
        "2": "static_pipeline/crawlers/download_docs.py",
        "3": "static_pipeline/parsers/parse_pdfs.py",
        "4": "static_pipeline/parsers/parse_docx.py",
        "5": "static_pipeline/parsers/normalize.py"
    }

    if choice == "6":
        for i in range(1, 6):
            run(scripts[str(i)])
    elif choice in scripts:
        run(scripts[choice])
    else:
        print("Invalid option.")
