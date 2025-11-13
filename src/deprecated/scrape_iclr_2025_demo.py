#!/usr/bin/env python3
"""
Demo script to scrape 10 ICLR 2025 conference submissions from OpenReview
For demonstration purposes only - fetches a small sample
"""

import json
import time
import requests
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
import os

def get_sample_submissions(venue_id: str = "ICLR.cc/2025/Conference", 
                          output_dir: str = None, 
                          limit: int = 10) -> List[Dict]:
    """
    Fetch sample submissions for ICLR 2025 using OpenReview API
    """
    base_url = "https://api2.openreview.net"
    
    # Get submissions
    submissions_url = f"{base_url}/notes"
    params = {
        "invitation": f"{venue_id}/-/Submission",
        "details": "replies,invitation",
        "limit": limit,
        "offset": 0
    }
    
    all_submissions = []
    
    print(f"Fetching {limit} sample submissions from {venue_id}...")
    
    try:
        response = requests.get(submissions_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        notes = data.get('notes', [])
        all_submissions.extend(notes)
        print(f"✓ Fetched {len(all_submissions)} submissions")
        
        # Save immediately
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            submissions_file = os.path.join(output_dir, 'submissions_metadata.json')
            with open(submissions_file, 'w') as f:
                json.dump(all_submissions, f, indent=2)
            print(f"✓ Saved to {submissions_file}")
        
    except Exception as e:
        print(f"Error fetching submissions: {e}")
        return []
    
    print(f"Total submissions fetched: {len(all_submissions)}")
    return all_submissions


def extract_submission_data(submissions: List[Dict]) -> pd.DataFrame:
    """
    Extract key information from submissions including decision status
    """
    data = []
    
    for submission in tqdm(submissions, desc="Processing submissions"):
        submission_id = submission.get('id')
        number = submission.get('number', None)
        content = submission.get('content', {})
        
        # Get primary area
        primary_area = content.get('primary_area', {})
        if isinstance(primary_area, dict):
            primary_area = primary_area.get('value', 'N/A')
        
        # Extract decision from venue/venueid
        venue = content.get('venue', {})
        if isinstance(venue, dict):
            venue = venue.get('value', '')
        
        venueid = content.get('venueid', {})
        if isinstance(venueid, dict):
            venueid = venueid.get('value', '')
        
        # Determine decision status
        # Check in order of specificity: Oral > Spotlight > Poster > Reject > Withdrawn
        decision = 'Unknown'
        decision_type = 'Unknown'
        
        # Check for Withdrawn
        if 'Withdrawn' in venueid or 'Withdrawn' in venue:
            decision = 'Withdrawn'
            decision_type = 'Withdrawn'
        
        # Check for Desk Reject
        elif 'Desk_Rejected' in venueid or 'Desk Reject' in venue:
            decision = 'Desk Reject'
            decision_type = 'Reject'
        
        # Check for Reject (including "Submitted to ICLR 2025" which means rejected)
        elif 'Rejected_Submission' in venueid or 'Rejected' in venueid or \
             'Submitted to ICLR 2025' == venue:
            decision = 'Reject'
            decision_type = 'Reject'
        
        # Check for Accept - Oral (most specific, check first)
        elif 'Oral' in venueid or 'ICLR 2025 Oral' in venue:
            decision = 'Accept (Oral)'
            decision_type = 'Accept'
        
        # Check for Accept - Spotlight
        elif 'Spotlight' in venueid or 'ICLR 2025 Spotlight' in venue:
            decision = 'Accept (Spotlight)'
            decision_type = 'Accept'
        
        # Check for Accept - Poster
        elif 'Poster' in venueid or 'ICLR 2025 Poster' in venue:
            decision = 'Accept (Poster)'
            decision_type = 'Accept'
        
        # Fallback: if venue contains "ICLR 2025" but not "Submitted" or "Withdrawn", 
        # it's likely an accepted paper (assume Poster if type unclear)
        elif 'ICLR 2025' in venue and 'Submitted' not in venue and 'Withdrawn' not in venue:
            decision = 'Accept (Poster)'
            decision_type = 'Accept'
        
        # Extract reviews from replies
        replies = submission.get('details', {}).get('replies', [])
        
        ratings = []
        confidences = []
        soundness_scores = []
        presentation_scores = []
        contribution_scores = []
        
        for reply in replies:
            reply_content = reply.get('content', {})
            
            # Check if this is a review
            if 'rating' in reply_content and 'confidence' in reply_content:
                # Extract rating
                rating_val = reply_content['rating']
                if isinstance(rating_val, dict):
                    rating_val = rating_val.get('value')
                if rating_val:
                    ratings.append(rating_val)
                
                # Extract confidence
                conf_val = reply_content['confidence']
                if isinstance(conf_val, dict):
                    conf_val = conf_val.get('value')
                if conf_val:
                    confidences.append(conf_val)
                
                # Extract other scores
                for field, target_list in [('soundness', soundness_scores),
                                          ('presentation', presentation_scores),
                                          ('contribution', contribution_scores)]:
                    if field in reply_content:
                        val = reply_content[field]
                        if isinstance(val, dict):
                            val = val.get('value')
                        if val:
                            target_list.append(val)
        
        # Calculate averages
        avg_rating = None
        if ratings:
            # Parse numeric values from ratings
            numeric_ratings = []
            for r in ratings:
                if isinstance(r, (int, float)):
                    numeric_ratings.append(r)
                elif isinstance(r, str):
                    try:
                        # Try to extract number (format might be "5: Marginally below...")
                        numeric_ratings.append(int(r.split(':')[0]))
                    except:
                        pass
            if numeric_ratings:
                avg_rating = sum(numeric_ratings) / len(numeric_ratings)
        
        record = {
            'submission_id': submission_id,
            'submission_number': number,
            'primary_area': primary_area,
            'decision': decision,
            'decision_type': decision_type,
            'num_reviews': len(ratings),
            'ratings': str(ratings),
            'confidences': str(confidences),
            'soundness': str(soundness_scores),
            'presentation': str(presentation_scores),
            'contribution': str(contribution_scores),
            'avg_rating': avg_rating
        }
        
        data.append(record)
    
    return pd.DataFrame(data)


def main():
    """
    Main function to scrape demo ICLR 2025 data
    """
    print("="*60)
    print("ICLR 2025 Demo Data Scraper")
    print("Fetching 10 sample submissions")
    print("="*60)
    print()
    
    venue_id = "ICLR.cc/2025/Conference"
    output_dir = "iclr_2025/iclr_2025_demo"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch submissions
    submissions = get_sample_submissions(venue_id, output_dir, limit=10)
    
    if not submissions:
        print("❌ No submissions fetched. Exiting.")
        return
    
    # Extract data
    print("\nExtracting ratings and metadata...")
    df = extract_submission_data(submissions)
    
    # Save to CSV
    output_file = os.path.join(output_dir, 'ratings_data.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✅ Data saved to {output_file}")
    print(f"Total submissions collected: {len(df)}")
    
    # Print summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS (DEMO - 10 SAMPLES)")
    print("="*50)
    print(f"Total submissions: {len(df)}")
    
    # Decision breakdown
    print("\nDecision Breakdown (Detailed):")
    decision_counts = df['decision'].value_counts()
    
    # Define order for display
    decision_order = ['Accept (Oral)', 'Accept (Spotlight)', 'Accept (Poster)', 
                     'Reject', 'Desk Reject', 'Withdrawn', 'Unknown']
    
    for decision in decision_order:
        if decision in decision_counts.index:
            count = decision_counts[decision]
            pct = (count / len(df)) * 100
            print(f"  {decision}: {count} ({pct:.1f}%)")
    
    # Accept/Reject summary
    decision_type_counts = df['decision_type'].value_counts()
    print("\nOverall Status:")
    
    # Calculate acceptance rate
    total_non_withdrawn = len(df[df['decision_type'] != 'Withdrawn'])
    accepts = decision_type_counts.get('Accept', 0)
    
    for dtype in ['Accept', 'Reject', 'Withdrawn', 'Unknown']:
        if dtype in decision_type_counts.index:
            count = decision_type_counts[dtype]
            pct = (count / len(df)) * 100
            print(f"  {dtype}: {count} ({pct:.1f}%)")
    
    if total_non_withdrawn > 0 and accepts > 0:
        acceptance_rate = (accepts / total_non_withdrawn) * 100
        print(f"\nAcceptance Rate (excl. withdrawn): {acceptance_rate:.1f}%")
    
    print(f"\nSubmissions with reviews: {len(df[df['num_reviews'] > 0])}")
    if len(df[df['num_reviews'] > 0]) > 0:
        print(f"Average number of reviews per submission: {df['num_reviews'].mean():.2f}")
    
    if df['avg_rating'].notna().any():
        print(f"Average overall rating: {df['avg_rating'].mean():.2f}")
        print(f"Rating range: {df['avg_rating'].min():.2f} - {df['avg_rating'].max():.2f}")
    
    # Top areas
    print("\nPrimary Areas in sample:")
    areas = df['primary_area'].value_counts()
    for area, count in areas.items():
        print(f"  {area}: {count}")
    
    print("\n" + "="*50)
    print("✅ Demo scraping complete!")
    print(f"Data saved to: {output_dir}/")


if __name__ == "__main__":
    main()
