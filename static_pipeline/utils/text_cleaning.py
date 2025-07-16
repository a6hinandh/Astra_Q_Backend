def clean_text(text):
    lines = text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip() and not line.strip().isdigit()]
    return "\n".join(cleaned)
