import csv
import json
import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
PRACTICE_MODE = not os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-haiku-5-5"


def fetch_site(url, limit=4000):
    """Open a web page and collect its title, description and readable text."""
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    meta = soup.find("meta", attrs={"name": "description"})
    description = meta.get("content", "") if meta else ""
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())[:limit]
    return {
        "url": url,
        "title": title,
        "description": description,
        "text": text,
        "thin": len(text) < 300,
    }


def analyse(site):
    """Ask Claude to score the business and draft outreach (fake reply in practice mode)."""
    if PRACTICE_MODE:
        return {
            "score": 6,
            "summary": "PRACTICE MODE: this is a fake reply, not real Claude output.",
            "needs": ["Practice need 1", "Practice need 2"],
            "outreach_message": "Hi, I noticed your website and had a quick idea. (practice mode)",
            "confidence": "low" if site["thin"] else "medium",
        }
    import anthropic

    client = anthropic.Anthropic()
    note = (
        "The page had very little readable text, so say so and keep confidence low."
        if site["thin"]
        else ""
    )
    prompt = f"""You are helping an AI automation specialist qualify a small-business lead.
Use ONLY the information below. Do not invent facts. If something is unknown, say so.
{note}

Website: {site['url']}
Title: {site['title']}
Description: {site['description']}
Page text: {site['text']}

Reply with ONLY valid JSON using these keys:
"score" (1-10, how likely this business needs website or automation help),
"summary" (2 sentences on what the business does),
"needs" (a list of up to 3 possible needs, worded as possibilities),
"outreach_message" (a short, friendly 3-sentence message, no false claims),
"confidence" ("low", "medium" or "high")."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    raw = raw.removeprefix("```json").removesuffix("```").strip()
    return json.loads(raw)


def save_lead(site, result):
    """Add one row to leads.csv (the file is created with headers the first time)."""
    new_file = not os.path.exists("leads.csv")
    with open("leads.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(
                ["time", "url", "score", "confidence", "summary", "needs", "outreach_message", "status"]
            )
        writer.writerow(
            [
                datetime.now().isoformat(timespec="seconds"),
                site["url"],
                result["score"],
                result["confidence"],
                result["summary"],
                "; ".join(result["needs"]),
                result["outreach_message"],
                "Needs approval",
            ]
        )


if __name__ == "__main__":
    url = sys.argv[1]
    print("Mode:", "PRACTICE (fake Claude reply)" if PRACTICE_MODE else "LIVE (real Claude)")
    site = fetch_site(url)
    if site["thin"]:
        print("Warning: very little readable text. This site may load its content with JavaScript.")
    result = analyse(site)
    save_lead(site, result)
    print(json.dumps(result, indent=2))
    print("Saved to leads.csv")