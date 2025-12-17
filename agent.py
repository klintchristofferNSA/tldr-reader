import feedparser
import requests
from collections import defaultdict
from datetime import date
from readability import Document
from newspaper import Article

from sources import TLDR_FEED, CATEGORIES
from summarizer import summarize_text


def extract_article_text(url):
    """
    Fetch and extract main article text.
    Tries newspaper3k first, then readability as fallback.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text and len(article.text) > 500:
            return article.text
    except Exception:
        pass

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        doc = Document(response.text)
        return doc.summary(html_partial=True)
    except Exception:
        return ""


def classify_entries(entries):
    categorized = defaultdict(list)

    for entry in entries:
        title = getattr(entry, "title", "")
        summary = getattr(entry, "summary", "")
        combined = f"{title} {summary}".lower()

        for category, keywords in CATEGORIES.items():
            if any(keyword in combined for keyword in keywords):
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

        for entry in entries[:8]:  # cap per category (Phase 1)
            link = getattr(entry, "link", None)
            if not link or link in seen_links:
                continue

            seen_links.add(link)

            article_text = extract_article_text(link)
            if not article_text or len(article_text) < 500:
                continue

            summary = summarize_text(article_text)

            report.append(f"- **{entry.title}**")
            report.append(summary + "\n")

    with open("weekly_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))


if __name__ == "__main__":
    main()
