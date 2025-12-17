import feedparser
from datetime import date
FEED_URL = "https://tldr.tech/tech"
feed = feedparser.parse(FEED_URL)

output = []
output.append(f"TLDR Teck Summary - {date.today()}\n")

for entry in feed.entries[:5]:
  output.append(f"- {entry.title}")
  output.append(f" {entry.summary}\n")

summary_text = "\n".join(output)

with open ("summary.txt", "w") as f:
  f.write(summary_text)
