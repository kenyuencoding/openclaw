#!/usr/bin/env python3
"""
Daily Market & News Brief generator
- Fetches market data via yfinance
- Scrapes headlines from CNBC, CNN, Reuters, AP, SCMP (simple scraping)
- Uses OpenAI / local model invocation placeholder (github-copilot/gpt-5-mini) to compose text
- Renders an HTML template and converts it to PDF (weasyprint or wkhtmltopdf)
- Saves PDF to ./output and posts to Telegram via OpenClaw message tool (placeholder)

NOTE: This script is a template. It expects required Python packages to be installed in the environment
(e.g., yfinance, requests, beautifulsoup4, jinja2, plotly, weasyprint). It does NOT store credentials.
"""
import os
import sys
import datetime
from pathlib import Path

# Third-party imports (assumed installed)
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import plotly.graph_objects as go

# Config
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HKT = datetime.timezone(datetime.timedelta(hours=8))
RUN_TIME = datetime.datetime.now(tz=HKT)
DATE_STR = RUN_TIME.strftime("%Y-%m-%d %H:%M %Z")

# Tickers and indices to fetch
INDICES = {
    'S&P 500': '^GSPC',
    'Nasdaq Composite': '^IXIC',
    'Dow Jones': '^DJI',
    'FTSE 100': '^FTSE',
    'Nikkei 225': '^N225',
    'Hang Seng': '^HSI'
}
TOP_STOCKS = ['NVDA','MSFT','AAPL','AMZN','GOOG','TSLA','META','JPM','UNH','MRVL']

# Simple market fetch
def fetch_quotes(tickers):
    data = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period='5d')
            last = hist['Close'].iloc[-1] if not hist.empty else None
            change = None
            if hist.shape[0] >= 2:
                prev = hist['Close'].iloc[-2]
                change = (last - prev) / prev * 100 if prev else None
            data[name] = {'symbol': sym, 'last': float(last) if last is not None else None, 'change_pct': change, 'history': hist}
        except Exception as e:
            data[name] = {'symbol': sym, 'error': str(e)}
    return data

# Headline sources: prefer RSS feeds, fallback to tuned scrapers
FEEDS = {
    'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'CNN': 'http://rss.cnn.com/rss/edition_business.rss',
    'Reuters': 'http://feeds.reuters.com/Reuters/worldNews',
    'AP': 'https://apnews.com/rss/apf-business',
    'SCMP': 'https://www.scmp.com/rss/91/feed'
}

from newspaper import Article
import feedparser


def fetch_headlines():
    headlines = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'}
    for name, feed in FEEDS.items():
        try:
            parsed = feedparser.parse(feed)
            items = []
            for e in parsed.entries[:6]:
                title = e.title
                link = e.link if 'link' in e else ''
                summary = e.get('summary') or ''
                # If no summary, try to fetch article and extract first paragraph
                if not summary and link:
                    try:
                        art = Article(link)
                        art.download()
                        art.parse()
                        summary = art.text.split('\n')[0][:500]
                    except Exception:
                        summary = ''
                items.append({'text': title, 'link': link, 'summary': summary})
            headlines[name] = items
        except Exception as e:
            headlines[name] = [{'text': f'Error fetching {name}: {e}', 'link': '', 'summary': ''}]
    return headlines

# Render HTML (Jinja2 template)
def render_pdf(context, outpath: Path):
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    tpl = env.get_template('brief_template.html')
    html = tpl.render(**context)
    # Attempt to use Chromium (pyppeteer) if available
    try:
        from pyppeteer import launch
        import asyncio
        async def render_pdf(html_str, path):
            # Try system Chrome/Chromium first (common install locations)
            possible = [
                r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                r'C:\\Program Files\\Chromium\\Application\\chrome.exe'
            ]
            exe = None
            for p in possible:
                if os.path.exists(p):
                    exe = p
                    break
            if exe:
                browser = await launch(executablePath=exe, args=['--no-sandbox'])
            else:
                browser = await launch(args=['--no-sandbox'])
            page = await browser.newPage()
            await page.setContent(html_str)
            # let the page render
            await asyncio.sleep(1)
            await page.pdf({'path': path, 'format': 'A4', 'printBackground': True})
            await browser.close()
        asyncio.run(render_pdf(html, str(outpath)))
        return True
    except Exception as e:
        print('Chromium PDF generation failed or pyppeteer not available:', e, file=sys.stderr)
    # Attempt to use weasyprint if available
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(str(outpath))
        return True
    except Exception as e:
        print('WeasyPrint PDF generation failed:', e, file=sys.stderr)
        # Fallback: write HTML for manual conversion
        open(str(outpath.with_suffix('.html')), 'w', encoding='utf-8').write(html)
        return False


def build_context():
    indices = fetch_quotes(INDICES)
    stocks = fetch_quotes({s: s for s in TOP_STOCKS})
    headlines = fetch_headlines()

    context = {
        'generated_at': DATE_STR,
        'indices': indices,
        'stocks': stocks,
        'headlines': headlines,
        'theme': 'dark'
    }
    return context


def main():
    ctx = build_context()
    outname = OUTPUT_DIR / f"market_brief_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    ok = render_pdf(ctx, outname)
    if ok:
        print('PDF written to', outname)
    else:
        print('HTML written as fallback at', outname.with_suffix('.html'))
    # Placeholder: send to Telegram via OpenClaw message tool — implemented by agent runtime.

if __name__ == '__main__':
    main()
