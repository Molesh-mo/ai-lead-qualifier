# AI Lead Qualifier

A Python tool that reads a business website, uses Claude to score the lead and draft a personalised outreach message, and saves the result for human approval.

## The problem
Finding and qualifying small-business leads by hand is slow, and generic outreach gets ignored.

## What it does
1. Takes a website URL
2. Fetches the page and extracts its title, description and readable text
3. Detects pages with too little text (for example sites that load their content with JavaScript) and flags them
4. Asks Claude (Haiku 5.5) to return a structured result: score (1-10), a short summary, possible needs, a draft outreach message and a confidence level
5. Saves the result to `leads.csv` with the status "Needs approval", so a human reviews every message before anything is sent

## Prompt rules
Claude is told to use only the information on the page, never invent facts, word needs as possibilities, and keep confidence low when the page has little text.

## Practice mode
If no API key is set, the tool runs in practice mode and returns a clearly labelled fake reply, so the whole flow can be tested without any cost.

## Tools used
Python 3.14, Anthropic Claude API, Requests, BeautifulSoup, python-dotenv

## How to run it
1. `py -3.14 -m venv venv`
2. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your own Anthropic API key (optional, practice mode works without it)
5. `python qualifier.py https://example.com`

## Known limitation
Simple page fetching cannot read sites that draw their content with JavaScript. The tool detects this and warns instead of guessing.

## What I learned
- Setting up a Python project end to end: virtual environment, dependencies, and keeping API keys out of the code with `.env` and `.gitignore`.
- Many sites built with no-code builders return almost no text to a basic scraper, so the tool detects thin pages and tells Claude to lower its confidence rather than guess.

## What I'd improve next
- Read JavaScript-based sites with a headless browser
- Trigger it from a webhook and save results to Google Sheets or a database
- Add automated tests with sample pages

## Built by
Molebogeng Matipwili, AI automation specialist. Built with Claude's help while learning Python.
