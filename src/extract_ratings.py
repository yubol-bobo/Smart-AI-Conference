#!/usr/bin/env python3
"""
Universal extraction of ratings and decision data from metadata
This script automatically detects whether decision information is available and extracts it if present.

Usage:
    python3 src/extract_ratings_universal.py <metadata_file> [output_file]
    
Example:
    python3 src/extract_ratings_universal.py iclr_2025/iclr_2025_v1/submissions_metadata.json iclr_2025/iclr_2025_v1/ratings_data.csv
    python3 src/extract_ratings_universal.py iclr_2026/iclr_2026_v1/submissions_metadata.json iclr_2026/iclr_2026_v1/ratings_data.csv
"""

import json
import pandas as pd
from tqdm import tqdm
import sys
import os


def extract_decision(venue, venueid):
    """
    Extract decision information from venue and venueid fields.
    Returns tuple: (decision, decision_type)
    
    Decision categories:
    - Accept (Oral/Spotlight/Poster)
    - Reject
    - Desk Reject
    - Withdrawn
    - Pending (no decision yet)
    """
    venue_str = str(venue).lower() if venue else ""
    venueid_str = str(venueid).lower() if venueid else ""
    
    # Check for withdrawn
    if "withdrawn" in venue_str or "withdrawn" in venueid_str:
        return "Withdrawn", "Withdrawn"
    
    # Check for desk reject
    if "desk reject" in venue_str or "desk_rejected" in venueid_str:
        return "Reject", "Desk Reject"
    
    # Check for acceptance types (check in order of specificity)
    if "oral" in venue_str:
        return "Accept", "Oral"
    elif "spotlight" in venue_str:
        return "Accept", "Spotlight"
    elif "poster" in venue_str or ("conference" in venue_str and "202" in venue_str):
        # "ICLR 202X Conference" typically means accepted as poster
        return "Accept", "Poster"
    
    # Check for rejection
    if "reject" in venue_str or "rejected" in venueid_str:
        return "Reject", "Reject"
    
    # No decision found
    return "Pending", "Pending"


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
                if rating_val is not None:
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
                        if val is not None:
                            target_list.append(val)
    
    return {
        'ratings': ratings,
        'confidences': confidences,
        'soundness': soundness,
        'presentation': presentation,
        'contribution': contribution
    }


def detect_if_decisions_available(submissions, sample_size=100):
    """
    Automatically detect if decision information is available in the metadata.
    Checks a sample of submissions for venue/venueid patterns.
    """
    sample = submissions[:min(sample_size, len(submissions))]
    
    decision_indicators = 0
    for submission in sample:
        venue = submission.get('content', {}).get('venue', '')
        venueid = submission.get('content', {}).get('venueid', '')
        
        decision, decision_type = extract_decision(venue, venueid)
        
        # If we find any non-pending decisions, decisions are available
        if decision != "Pending":
            decision_indicators += 1
    
    # If more than 10% of sample has decisions, consider decisions available
    has_decisions = decision_indicators > (sample_size * 0.1)
    
    return has_decisions


def main(metadata_file='data/submissions_metadata.json', 
         output_file='data/ratings_data.csv'):
    """
    Extract ratings and decision data from metadata file.
    Automatically detects whether decision information is available.
    """
    print("="*60)
    print("Universal Rating & Decision Extraction")
    print("="*60)
    
    # Load metadata
    print(f"\nLoading metadata from {metadata_file}...")
    if not os.path.exists(metadata_file):
        print(f"❌ Error: File not found: {metadata_file}")
        sys.exit(1)
    
    with open(metadata_file, 'r') as f:
        submissions = json.load(f)
    
    print(f"✓ Loaded {len(submissions):,} submissions")
    
    # Auto-detect if decisions are available
    print("\nDetecting if decision information is available...")
    has_decisions = detect_if_decisions_available(submissions)
    
    if has_decisions:
        print("✓ Decision information detected! Will extract decision data.")
    else:
        print("✓ No decision information found. Extracting ratings only.")
    
    # Extract data
    print("\nExtracting data from submissions...")
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
        
        # Extract decision information if available
        if has_decisions:
            venue = content.get('venue', '')
            venueid = content.get('venueid', '')
            decision, decision_type = extract_decision(venue, venueid)
            record['decision'] = decision
            record['decision_type'] = decision_type
        
        # Add computed fields for ratings
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
        
        # Add computed fields for confidence
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
    
    # Decision statistics (if available)
    if has_decisions and 'decision' in df.columns:
        print("\n" + "="*60)
        print("DECISION STATISTICS")
        print("="*60)
        
        decision_counts = df['decision'].value_counts()
        print("\nDecision breakdown:")
        for decision, count in decision_counts.items():
            pct = count / len(df) * 100
            print(f"  {decision:<15} {count:>6} ({pct:>5.1f}%)")
        
        if 'decision_type' in df.columns:
            print("\nDecision type breakdown:")
            decision_type_counts = df['decision_type'].value_counts()
            for dtype, count in decision_type_counts.items():
                pct = count / len(df) * 100
                print(f"  {dtype:<15} {count:>6} ({pct:>5.1f}%)")
        
        # Acceptance rate
        accepts = len(df[df['decision'] == 'Accept'])
        total_decided = len(df[df['decision'] != 'Pending'])
        if total_decided > 0:
            acceptance_rate = accepts / total_decided * 100
            print(f"\nAcceptance rate: {acceptance_rate:.1f}% ({accepts:,} / {total_decided:,})")
    
    # Top areas
    print("\n" + "="*60)
    print("TOP 10 PRIMARY AREAS")
    print("="*60)
    top_areas = df['primary_area'].value_counts().head(10)
    for area, count in top_areas.items():
        pct = count / len(df) * 100
        print(f"  {area[:50]:<50} {count:>5} ({pct:>4.1f}%)")
    
    # Output summary
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
    if has_decisions:
        print(f"  - decision (Accept/Reject/Withdrawn/Pending)")
        print(f"  - decision_type (Oral/Spotlight/Poster/Reject/Desk Reject/Withdrawn/Pending)")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        metadata_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'ratings_data.csv'
        main(metadata_file, output_file)
    else:
        print("Usage: python3 src/extract_ratings_universal.py <metadata_file> [output_file]")
        print("\nExample:")
        print("  python3 src/extract_ratings_universal.py iclr_2025/iclr_2025_v1/submissions_metadata.json iclr_2025/iclr_2025_v1/ratings_data.csv")
        sys.exit(1)
