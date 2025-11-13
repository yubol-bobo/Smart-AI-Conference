import pandas as pd
import json

df = pd.read_csv('iclr_2026/iclr_2026_v1/ratings_data.csv')
meta = json.load(open('iclr_2026/iclr_2026_v1/submissions_metadata.json'))
no_rating = set(df[df['num_reviews'] == 0]['submission_number'].tolist())
results = []
for sub in meta:
    num = sub.get('number')
    if num in no_rating:
        title = sub.get('content', {}).get('title', '')
        results.append({'number': num, 'title': title})
print('Total:', len(results))
print('---')
for r in results[:50]:
    print(f"{r['number']}: {r['title']}")
print('...')