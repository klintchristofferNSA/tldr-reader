import re


def summarize_text(text, max_sentences=10):
    sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = [s.strip() for s in sentences if len(s) > 40]
    return " ".join(sentences[:max_sentences])
