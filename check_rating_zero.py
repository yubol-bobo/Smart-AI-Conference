import json

with open('iclr_2026/iclr_2026_v1/submissions_metadata.json') as f:
    meta = json.load(f)

sub = next((s for s in meta if s.get('number') == 25599), None)
if not sub:
    print('Submission 25599 not found.')
else:
    found = False
    for reply in sub.get('details', {}).get('replies', []):
        content = reply.get('content', {})
        rating = content.get('rating')
        if rating is not None:
            if isinstance(rating, dict):
                val = rating.get('value')
            else:
                val = rating
            print('Rating:', val)
            if str(val).strip() == '0':
                found = True
    if not found:
        print('No rating 0 found in API data.')