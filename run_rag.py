import os
from rag_pipeline.retrieve import run_rag_pipeline

# from dotenv import load_dotenv
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")


def run(script_path):
    print(f"\nRunning {script_path}...")
    os.system(f'python {script_path}')

print("Did you store the data? Enter Y/N")
choice = input().strip().upper()
if choice == "Y":
    run("Astra_Q_Backend/rag_pipeline/store_vectordb.py")
else:
    print("Already stored")

print("Enter your query:")
query = input().strip()
print("Do you want to use fallback? Enter Y/N")
use_fallback_choice = input().strip().upper()
if (use_fallback_choice == "Y"):
    print("Enter fallback keyword:")
    fallback_keyword = input().strip()
    use_fallback=True
else:
    fallback_keyword = None
    use_fallback=False

response= run_rag_pipeline(query, use_fallback=use_fallback, fallback_keyword=fallback_keyword)
print("Response:", response)
