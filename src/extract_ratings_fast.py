#!/usr/bin/env python3
"""
Fast extraction of paper numbers, ratings, confidence, and primary area from metadata
This script processes the already-downloaded metadata.json file (no API calls needed!)
"""

import json
import pandas as pd
from tqdm import tqdm
import sys

def extract_reviews_from_submission(submission):
    """Extract all review ratings and confidences from a submission"""
    ratings = []
    confidences = []
    soundness = []
    presentation = []
    contribution = []
    
    replies = submission.get('details', {}).get('replies', [])
    
    for reply in replies:
        content = reply.get('content', {})
        
        # Check if this is a review (has rating and confidence)
        if 'rating' in content and 'confidence' in content:
            # Extract rating value
            rating_val = content['rating']
            if isinstance(rating_val, dict):
                rating_val = rating_val.get('value')
            if rating_val:
                ratings.append(rating_val)
            
            # Extract confidence value
            conf_val = content['confidence']
            if isinstance(conf_val, dict):
                conf_val = conf_val.get('value')
            if conf_val:
                confidences.append(conf_val)
            
            # Extract other ratings if available
            for field, target_list in [('soundness', soundness), 
                                       ('presentation', presentation), 
                                       ('contribution', contribution)]:
                if field in content:
                    val = content[field]
                    if isinstance(val, dict):
                        val = val.get('value')
                    if val:
                        target_list.append(val)
    
    return {
        'ratings': ratings,
        'confidences': confidences,
        'soundness': soundness,
        'presentation': presentation,
        'contribution': contribution
    }


def main(metadata_file='data/submissions_metadata.json', 
         output_file='data/ratings_data.csv'):
    """
    Extract ratings data from metadata file
    """
    print("="*60)
    print("Fast Rating Extraction")
    print("="*60)
    
    # Load metadata
    print(f"\nLoading metadata from {metadata_file}...")
    with open(metadata_file, 'r') as f:
        submissions = json.load(f)
    
    print(f"✓ Loaded {len(submissions):,} submissions")
    
    # Extract data
    print("\nExtracting ratings and confidence scores...")
    results = []
    
    for submission in tqdm(submissions):
        # Get basic info
        number = submission.get('number', None)
        content = submission.get('content', {})
        
        # Get primary area
        primary_area = content.get('primary_area', {})
        if isinstance(primary_area, dict):
            primary_area = primary_area.get('value', 'N/A')
        
        # Extract reviews
        reviews = extract_reviews_from_submission(submission)
        
        # Create record
        record = {
            'submission_number': number,
            'primary_area': primary_area,
            'num_reviews': len(reviews['ratings']),
            'ratings': str(reviews['ratings']),  # Store as string for CSV
            'confidences': str(reviews['confidences']),
            'soundness': str(reviews['soundness']),
            'presentation': str(reviews['presentation']),
            'contribution': str(reviews['contribution']),
        }
        
        # Add computed fields
        if reviews['ratings']:
            # Extract numeric values from ratings
            numeric_ratings = []
            for r in reviews['ratings']:
                try:
                    # Handle both "6: Weak Accept" format and plain numbers
                    if isinstance(r, str):
                        numeric_ratings.append(int(r.split(':')[0]))
                    else:
                        numeric_ratings.append(int(r))
                except:
                    pass
            
            if numeric_ratings:
                record['avg_rating'] = sum(numeric_ratings) / len(numeric_ratings)
                record['min_rating'] = min(numeric_ratings)
                record['max_rating'] = max(numeric_ratings)
            else:
                record['avg_rating'] = None
                record['min_rating'] = None
                record['max_rating'] = None
        else:
            record['avg_rating'] = None
            record['min_rating'] = None
            record['max_rating'] = None
        
        if reviews['confidences']:
            # Extract numeric confidence values
            numeric_conf = []
            for c in reviews['confidences']:
                try:
                    if isinstance(c, str):
                        numeric_conf.append(int(c.split(':')[0]))
                    else:
                        numeric_conf.append(int(c))
                except:
                    pass
            
            if numeric_conf:
                record['avg_confidence'] = sum(numeric_conf) / len(numeric_conf)
            else:
                record['avg_confidence'] = None
        else:
            record['avg_confidence'] = None
        
        results.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Sort by submission number
    df = df.sort_values('submission_number')
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Data saved to {output_file}")
    print(f"   Total submissions: {len(df):,}")
    print(f"   Submissions with reviews: {len(df[df['num_reviews'] > 0]):,}")
    
    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    reviewed = df[df['num_reviews'] > 0]
    print(f"Total submissions: {len(df):,}")
    print(f"Submissions with reviews: {len(reviewed):,} ({len(reviewed)/len(df)*100:.1f}%)")
    
    if len(reviewed) > 0:
        print(f"\nReview statistics:")
        print(f"  Average reviews per submission: {df['num_reviews'].mean():.2f}")
        print(f"  Total reviews: {df['num_reviews'].sum():,}")
        
        rated = df[df['avg_rating'].notna()]
        if len(rated) > 0:
            print(f"\nRating statistics:")
            print(f"  Average rating: {rated['avg_rating'].mean():.2f}")
            print(f"  Rating range: {rated['min_rating'].min():.0f} - {rated['max_rating'].max():.0f}")
            
        conf = df[df['avg_confidence'].notna()]
        if len(conf) > 0:
            print(f"\nConfidence statistics:")
            print(f"  Average confidence: {conf['avg_confidence'].mean():.2f}")
        
        print(f"\nTop 10 primary areas:")
        top_areas = df['primary_area'].value_counts().head(10)
        for area, count in top_areas.items():
            pct = count / len(df) * 100
            print(f"  {area[:50]:<50} {count:>5} ({pct:>4.1f}%)")
    
    print("\n" + "="*60)
    print("\n✨ Extraction complete!")
    print(f"\nOutput columns:")
    print(f"  - submission_number")
    print(f"  - primary_area")
    print(f"  - num_reviews")
    print(f"  - ratings (list)")
    print(f"  - confidences (list)")
    print(f"  - soundness (list)")
    print(f"  - presentation (list)")
    print(f"  - contribution (list)")
    print(f"  - avg_rating, min_rating, max_rating")
    print(f"  - avg_confidence")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        metadata_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'ratings_data.csv'
        main(metadata_file, output_file)
    else:
        main()

