#!/usr/bin/env python3
"""
Script to scrape ICLR 2025 conference submissions from OpenReview
Collects: submission number, ratings, confidence, decisions (Oral/Spotlight/Poster/Reject/Withdrawn)
Uses same optimizations as ICLR 2026 scraper: batch processing, retry logic, checkpoints
"""

import json
import time
import requests
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
import os

def get_all_submissions(venue_id: str = "ICLR.cc/2025/Conference", output_dir: str = None) -> List[Dict]:
    """
    Fetch all submissions for ICLR 2025 using OpenReview API with retry logic
    Saves incrementally after each batch if output_dir is provided
    """
    base_url = "https://api2.openreview.net"
    
    # Get all submissions
    submissions_url = f"{base_url}/notes"
    params = {
        "invitation": f"{venue_id}/-/Submission",
        "details": "replies,invitation",
        "limit": 500,  # Smaller batches to avoid timeouts
        "offset": 0
    }
    
    all_submissions = []
    
    print(f"Fetching submissions from {venue_id}...")
    
    while True:
        retry_count = 0
        success = False
        
        while not success:
            try:
                response = requests.get(submissions_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                notes = data.get('notes', [])
                if not notes:
                    return all_submissions
                    
                all_submissions.extend(notes)
                print(f"Fetched {len(all_submissions)} submissions so far...")
                
                # Save incrementally after each batch
                if output_dir:
                    submissions_file = os.path.join(output_dir, 'submissions_metadata.json')
                    with open(submissions_file, 'w') as f:
                        json.dump(all_submissions, f, indent=2)
                    print(f"  ✓ Saved to {submissions_file}")
                
                # Check if there are more results
                if len(notes) < params['limit']:
                    print(f"✓ Reached end of submissions")
                    return all_submissions
                
                params['offset'] += params['limit']
                time.sleep(5)  # Wait between successful batches
                success = True
                
            except Exception as e:
                retry_count += 1
                print(f"Error fetching submissions (attempt {retry_count}): {e}")
                
                # Wait times: 1min, 2min, 5min, then keep trying every 5min
                if retry_count == 1:
                    wait_time = 60  # 1 minute
                elif retry_count == 2:
                    wait_time = 120  # 2 minutes
                else:
                    wait_time = 300  # 5 minutes (keep trying every 5 min)
                
                print(f"Retrying in {wait_time} seconds ({wait_time/60:.1f} minutes)...")
                time.sleep(wait_time)
    
    print(f"Total submissions fetched: {len(all_submissions)}")
    return all_submissions


def extract_submission_data(submissions: List[Dict]) -> pd.DataFrame:
    """
    Extract key information from submissions including decision status
    Fast extraction - no API calls needed!
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
    Main function to scrape full ICLR 2025 dataset
    """
    print("="*60)
    print("ICLR 2025 Full Dataset Scraper")
    print("Fetching ALL submissions with decisions")
    print("="*60)
    print()
    
    venue_id = "ICLR.cc/2025/Conference"
    output_dir = "iclr_2025/iclr_2025_v1"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch submissions
    print("STEP 1: Fetching submissions from OpenReview API")
    print("This may take 30-60 minutes depending on total submissions...")
    print()
    
    submissions = get_all_submissions(venue_id, output_dir)
    
    if not submissions:
        print("❌ No submissions fetched. Exiting.")
        return
    
    print()
    print("="*60)
    print(f"✅ Successfully fetched {len(submissions):,} submissions!")
    print("="*60)
    print()
    
    # Extract data
    print("STEP 2: Extracting ratings, decisions, and metadata...")
    print("This is fast - processing locally, no API calls!")
    print()
    
    df = extract_submission_data(submissions)
    
    # Save to CSV
    output_file = os.path.join(output_dir, 'ratings_data.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✅ Data saved to {output_file}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS - ICLR 2025 FULL DATASET")
    print("="*60)
    print(f"Total submissions: {len(df):,}")
    
    # Decision breakdown
    print("\n📊 Decision Breakdown (Detailed):")
    decision_counts = df['decision'].value_counts()
    
    # Define order for display
    decision_order = ['Accept (Oral)', 'Accept (Spotlight)', 'Accept (Poster)', 
                     'Reject', 'Desk Reject', 'Withdrawn', 'Unknown']
    
    for decision in decision_order:
        if decision in decision_counts.index:
            count = decision_counts[decision]
            pct = (count / len(df)) * 100
            print(f"  {decision}: {count:,} ({pct:.1f}%)")
    
    # Accept/Reject summary
    decision_type_counts = df['decision_type'].value_counts()
    print("\n📈 Overall Status:")
    
    # Calculate acceptance rate
    total_non_withdrawn = len(df[df['decision_type'] != 'Withdrawn'])
    accepts = decision_type_counts.get('Accept', 0)
    
    for dtype in ['Accept', 'Reject', 'Withdrawn', 'Unknown']:
        if dtype in decision_type_counts.index:
            count = decision_type_counts[dtype]
            pct = (count / len(df)) * 100
            print(f"  {dtype}: {count:,} ({pct:.1f}%)")
    
    if total_non_withdrawn > 0 and accepts > 0:
        acceptance_rate = (accepts / total_non_withdrawn) * 100
        print(f"\n🎯 Acceptance Rate (excl. withdrawn): {acceptance_rate:.1f}%")
    
    # Review statistics
    print(f"\n📝 Review Statistics:")
    print(f"Submissions with reviews: {len(df[df['num_reviews'] > 0]):,}")
    if len(df[df['num_reviews'] > 0]) > 0:
        print(f"Average reviews per submission: {df['num_reviews'].mean():.2f}")
        print(f"Total reviews collected: {df['num_reviews'].sum():,}")
    
    # Rating statistics
    if df['avg_rating'].notna().any():
        print(f"\n⭐ Rating Statistics:")
        print(f"Average overall rating: {df['avg_rating'].mean():.2f}")
        print(f"Median rating: {df['avg_rating'].median():.2f}")
        print(f"Rating range: {df['avg_rating'].min():.2f} - {df['avg_rating'].max():.2f}")
    
    # Top areas
    print("\n🔬 Top 10 Primary Research Areas:")
    top_areas = df['primary_area'].value_counts().head(10)
    for i, (area, count) in enumerate(top_areas.items(), 1):
        pct = (count / len(df)) * 100
        print(f"  {i}. {area}: {count:,} ({pct:.1f}%)")
    
    # Rating by decision type
    if df['avg_rating'].notna().any():
        print("\n📊 Average Rating by Decision Type:")
        for dtype in ['Accept', 'Reject', 'Withdrawn']:
            subset = df[(df['decision_type'] == dtype) & (df['avg_rating'].notna())]
            if len(subset) > 0:
                mean_rating = subset['avg_rating'].mean()
                median_rating = subset['avg_rating'].median()
                print(f"  {dtype}: Mean={mean_rating:.2f}, Median={median_rating:.2f} (n={len(subset):,})")
        
        # Breakdown by detailed decision
        print("\n📊 Average Rating by Detailed Decision:")
        for decision in decision_order:
            subset = df[(df['decision'] == decision) & (df['avg_rating'].notna())]
            if len(subset) > 0:
                mean_rating = subset['avg_rating'].mean()
                median_rating = subset['avg_rating'].median()
                print(f"  {decision}: Mean={mean_rating:.2f}, Median={median_rating:.2f} (n={len(subset):,})")
    
    print("\n" + "="*60)
    print("✅ Full ICLR 2025 scraping complete!")
    print(f"📁 Data saved to: {output_dir}/")
    print("="*60)


if __name__ == "__main__":
    main()
