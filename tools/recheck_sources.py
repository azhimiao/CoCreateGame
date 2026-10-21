"""Record public-source access metadata; no accounts, submission or SDK calls."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
from zoneinfo import ZoneInfo
import requests

ROOT = Path(__file__).resolve().parents[1]

class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.title = ''
    def handle_starttag(self, tag, attrs):
        if tag == 'title': self.inside = True
    def handle_endtag(self, tag):
        if tag == 'title': self.inside = False
    def handle_data(self, data):
        if self.inside: self.title += data

def capture(source):
    item = dict(source)
    item['http_checked_at'] = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    try:
        response = requests.get(source['url'], timeout=30, headers={'User-Agent': 'Mozilla/5.0 (compatible; FoundryResearch/1.0)'})
        parser = TitleParser()
        # Most official pages are UTF-8 even when their HTTP charset is absent.
        try:
            decoded = response.content.decode('utf-8')
        except UnicodeDecodeError:
            decoded = response.text
        parser.feed(decoded)
        title = parser.title.strip()
        if not title and 'text/plain' in response.headers.get('Content-Type', ''):
            title = next((line[2:].strip() for line in decoded.splitlines() if line.startswith('# ')), '')
        item.update(http_status=response.status_code, final_url=response.url,
                    title=title, content_sha256=sha256(response.content).hexdigest(),
                    content_bytes=len(response.content), content_type=response.headers.get('Content-Type', ''),
                    http_last_modified=response.headers.get('Last-Modified', 'UNKNOWN'))
        item['http_interpretation'] = 'HTTP_OK_NOT_CONTENT_VERIFICATION' if response.ok else 'HTTP_ERROR_USE_SEPARATE_WEB_READ'
    except requests.RequestException as exc:
        item.update(http_status=None, error=str(exc), http_interpretation='FETCH_FAILED_USE_SEPARATE_WEB_READ')
    # No inferred publication date, ranking, revenue or playthrough is generated.
    return item

def main():
    sources = json.loads((ROOT / 'research/official-sources.json').read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        captured = list(pool.map(capture, sources))
    dest = ROOT / 'research/source-access-log.json'
    dest.write_text(json.dumps(captured, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sources': len(captured), 'http_ok': sum(x.get('http_status') == 200 for x in captured),
                      'output': str(dest)}, ensure_ascii=False))

if __name__ == '__main__': main()
