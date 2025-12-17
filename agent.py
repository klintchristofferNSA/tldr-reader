import feedparser
import requests
from collections import defaultdict
from datetime import date
from readability import Document
from newspaper import Article

from sources import TLDR_FEED, CATEGORIES
from summarizer import summarize_text


def extract_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        if len(article.text) > 500:
            return article.text
    except Exception:
        pass

    try:
        html = requests.get(url, timeout=10).text
        doc = Document(html)
        return doc.summary(html_partial=True)
    except Exception:
        return ""


def classify_entries(entries):
    categorized = defaultdict(list)

    for entry in entries:
        combined = f"{entry.title} {entry.summary}".lower()

        for category, keywords in CATEGORIES.items():
            if any(k in combined for k in keywords):
                categorized[category].append(entry)

    return categorized


def main():
    feed = feedparser.parse(TLDR_FEED)
    categorized = classify_entries(feed.entries)

    seen_links = set()
    today = date.today()

    report = []
    report.append("Weekly Technology Intelligence Brief")
    report.append(f"Week of {today}\n")

    for category, entries in categorized.items():
        if not entries:
            continue

        report.append(f"## {category}\n")

        for entry in entries[:8]:
            link = entry.link

            if link in seen_links:
                continue
            seen_links.add(link)

            text = extract_article_text(link)
            if not text or len(text) < 500:
                continue

            summary = summarize_text(text)

            report.append(f"- **{entry.title}**")
            report.append(summary + "\n")

    with open("weekly_report.txt", "w") as f:
        f.write("\n".join(report))


if __name__ == "__main__":
    main()
