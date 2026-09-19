import os
import re
import urllib.request
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPT_PATH = os.path.join(SCRIPT_DIR, 'python-typing-issue-548-transcript.md')

headers = {'User-Agent': 'Python/Pyright-HKT-Survey'}
token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
if token:
    headers['Authorization'] = f'Bearer {token}'

# 1. Read existing comment IDs and last comment date if transcript exists
existing_ids = set()
latest_date = None
if os.path.exists(TRANSCRIPT_PATH):
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    for m in re.finditer(r'### Comment \[(\d+)\]', content):
        existing_ids.add(int(m.group(1)))
    dates = re.findall(r'- \*\*Date\*\*: `([^`]+)`', content)
    if dates:
        latest_date = max(dates)

print(f"Existing transcript has {len(existing_ids)} comments (latest: {latest_date}).")

# 2. Fetch comments page by page
# If we have a latest_date, we can use the 'since' parameter
url_base = 'https://api.github.com/repos/python/typing/issues/548/comments?per_page=100'
if latest_date:
    url_base += f'&since={latest_date}'

page = 1
new_entries = []

while True:
    url = f'{url_base}&page={page}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        comments = json.loads(resp.read().decode('utf-8'))
    if not comments:
        break
    for c in comments:
        c_id = c['id']
        if c_id in existing_ids:
            continue
        c_user = c['user']['login']
        c_url = c['html_url']
        c_date = c['created_at']
        c_body = c.get('body') or ''

        entry = [
            f'### Comment [{c_id}]({c_url})\n',
            f'- **Author**: @{c_user}',
            f'- **Date**: `{c_date}`\n',
            c_body,
            '\n\n---\n'
        ]
        new_entries.append('\n'.join(entry))
        existing_ids.add(c_id)
    page += 1

if new_entries:
    with open(TRANSCRIPT_PATH, 'a', encoding='utf-8') as f:
        f.write('\n' + '\n'.join(new_entries))
    print(f"Appended {len(new_entries)} new comments to {TRANSCRIPT_PATH}.")
else:
    print("Transcript is already up to date! No new comments found.")
