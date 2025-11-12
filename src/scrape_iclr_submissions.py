#!/usr/bin/env python3
"""
Script to scrape ICLR 2026 conference submissions from OpenReview
Collects: submission number, ratings (overall, soundness, excitement, contribution), 
confidence, and topic information
"""

import json
import time
import requests
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
import os

def get_all_submissions(venue_id: str = "ICLR.cc/2026/Conference", output_dir: str = None) -> List[Dict]:
    """
    Fetch all submissions for ICLR 2026 using OpenReview API with retry logic
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


def get_reviews_for_submission(submission_id: str, venue_id: str = "ICLR.cc/2026/Conference") -> List[Dict]:
    """
    Fetch all reviews for a specific submission with persistent retry logic
    We get all notes in the forum and filter for reviews based on content structure
    """
    base_url = "https://api2.openreview.net"
    reviews_url = f"{base_url}/notes"
    
    params = {
        "forum": submission_id,
    }
    
    attempt = 0
    while True:
        try:
            response = requests.get(reviews_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            all_notes = data.get('notes', [])
            
            # Filter for actual reviews based on content structure
            # Reviews have 'rating', 'confidence', 'soundness', etc.
            reviews = []
            for note in all_notes:
                content = note.get('content', {})
                # Check if this looks like a review (has rating and confidence)
                if 'rating' in content and 'confidence' in content:
                    reviews.append(note)
            
            return reviews
        except Exception as e:
            attempt += 1
            # Wait times: 1min, 2min, 5min, then keep trying every 5min
            if attempt == 1:
                wait_time = 60  # 1 minute
            elif attempt == 2:
                wait_time = 120  # 2 minutes
            else:
                wait_time = 300  # 5 minutes (keep trying every 5 min)
            
            if attempt == 1:
                print(f"  ⚠ Error fetching reviews, retrying in {wait_time/60:.1f} min...")
            time.sleep(wait_time)


def extract_submission_data(submission: Dict, reviews: List[Dict]) -> Dict:
    """
    Extract relevant information from submission and its reviews
    """
    content = submission.get('content', {})
    
    # Extract basic submission info
    submission_data = {
        'submission_number': submission.get('number', 'N/A'),
        'submission_id': submission.get('id', 'N/A'),
        'title': content.get('title', {}).get('value', 'N/A'),
        'keywords': ', '.join(content.get('keywords', {}).get('value', [])),
        'primary_area': content.get('primary_area', {}).get('value', 'N/A'),
    }
    
    # Extract ratings from reviews
    if reviews:
        ratings = {
            'overall_ratings': [],
            'soundness_ratings': [],
            'presentation_ratings': [],
            'contribution_ratings': [],
            'confidences': []
        }
        
        for review in reviews:
            review_content = review.get('content', {})
            
            # Extract each rating type
            if 'rating' in review_content:
                rating_value = review_content['rating'].get('value') if isinstance(review_content['rating'], dict) else review_content['rating']
                if rating_value:
                    ratings['overall_ratings'].append(rating_value)
            
            if 'soundness' in review_content:
                soundness_value = review_content['soundness'].get('value') if isinstance(review_content['soundness'], dict) else review_content['soundness']
                if soundness_value:
                    ratings['soundness_ratings'].append(soundness_value)
            
            if 'presentation' in review_content:
                presentation_value = review_content['presentation'].get('value') if isinstance(review_content['presentation'], dict) else review_content['presentation']
                if presentation_value:
                    ratings['presentation_ratings'].append(presentation_value)
            
            if 'contribution' in review_content:
                contribution_value = review_content['contribution'].get('value') if isinstance(review_content['contribution'], dict) else review_content['contribution']
                if contribution_value:
                    ratings['contribution_ratings'].append(contribution_value)
            
            if 'confidence' in review_content:
                confidence_value = review_content['confidence'].get('value') if isinstance(review_content['confidence'], dict) else review_content['confidence']
                if confidence_value:
                    ratings['confidences'].append(confidence_value)
        
        # Add ratings info
        submission_data['num_reviews'] = len(reviews)
        submission_data['overall_ratings'] = str(ratings['overall_ratings'])
        submission_data['soundness_ratings'] = str(ratings['soundness_ratings'])
        submission_data['presentation_ratings'] = str(ratings['presentation_ratings'])
        submission_data['contribution_ratings'] = str(ratings['contribution_ratings'])
        submission_data['confidences'] = str(ratings['confidences'])
        
        # Calculate averages if ratings exist
        if ratings['overall_ratings']:
            # Extract numeric values from ratings (e.g., "6: Weak Accept" -> 6)
            numeric_ratings = []
            for r in ratings['overall_ratings']:
                try:
                    numeric_ratings.append(int(str(r).split(':')[0]))
                except:
                    pass
            submission_data['avg_overall_rating'] = sum(numeric_ratings) / len(numeric_ratings) if numeric_ratings else None
        else:
            submission_data['avg_overall_rating'] = None
            
    else:
        submission_data['num_reviews'] = 0
        submission_data['overall_ratings'] = '[]'
        submission_data['soundness_ratings'] = '[]'
        submission_data['presentation_ratings'] = '[]'
        submission_data['contribution_ratings'] = '[]'
        submission_data['confidences'] = '[]'
        submission_data['avg_overall_rating'] = None
    
    return submission_data


def main():
    """
    Main function to scrape all ICLR 2026 submissions with checkpoint support
    """
    venue_id = "ICLR.cc/2026/Conference"
    output_dir = 'data'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    checkpoint_file = os.path.join(output_dir, 'scrape_checkpoint.json')
    
    # Check if we have a checkpoint to resume from
    processed_ids = set()
    all_data = []
    
    if os.path.exists(checkpoint_file):
        print(f"Found checkpoint file. Loading progress...")
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
            all_data = checkpoint.get('data', [])
            processed_ids = set(checkpoint.get('processed_ids', []))
        print(f"Resuming from checkpoint: {len(all_data)} submissions already processed")
    
    # Step 1: Get all submissions (saves incrementally after each batch)
    print("\n" + "="*50)
    submissions = get_all_submissions(venue_id, output_dir)
    
    if not submissions:
        print("No submissions found. The data might not be publicly available yet.")
        return
    
    print(f"\n✅ All submission metadata saved to {os.path.join(output_dir, 'submissions_metadata.json')}")
    print(f"Total submissions to process: {len(submissions)}")
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining: {len(submissions) - len(processed_ids)}")
    print("="*50 + "\n")
    
    # Step 2: Get reviews for each submission
    print("Fetching reviews for each submission...")
    
    save_interval = 100  # Save checkpoint every 100 submissions
    submissions_since_save = 0
    
    for submission in tqdm(submissions):
        submission_id = submission.get('id')
        if not submission_id:
            continue
        
        # Skip if already processed
        if submission_id in processed_ids:
            continue
        
        reviews = get_reviews_for_submission(submission_id, venue_id)
        submission_data = extract_submission_data(submission, reviews)
        all_data.append(submission_data)
        processed_ids.add(submission_id)
        
        submissions_since_save += 1
        
        # Save checkpoint periodically
        if submissions_since_save >= save_interval:
            with open(checkpoint_file, 'w') as f:
                json.dump({
                    'data': all_data,
                    'processed_ids': list(processed_ids)
                }, f)
            submissions_since_save = 0
        
        time.sleep(1.5)  # Wait between each submission's reviews
    
    # Step 3: Save final results to CSV
    df = pd.DataFrame(all_data)
    
    # Sort by submission number
    df = df.sort_values('submission_number')
    
    output_file = os.path.join(output_dir, 'submissions.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✅ Data saved to {output_file}")
    print(f"Total submissions collected: {len(df)}")
    
    # Print summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    print(f"Total submissions: {len(df)}")
    print(f"Submissions with reviews: {len(df[df['num_reviews'] > 0])}")
    print(f"Average number of reviews per submission: {df['num_reviews'].mean():.2f}")
    
    if df['avg_overall_rating'].notna().any():
        print(f"Average overall rating: {df['avg_overall_rating'].mean():.2f}")
        print(f"Rating range: {df['avg_overall_rating'].min():.2f} - {df['avg_overall_rating'].max():.2f}")
    
    # Top areas
    print("\nTop 10 Primary Areas:")
    top_areas = df['primary_area'].value_counts().head(10)
    for area, count in top_areas.items():
        print(f"  {area}: {count}")
    
    print("\n" + "="*50)
    
    # Save raw data as JSON for reference
    json_output = os.path.join(output_dir, 'submissions_raw.json')
    with open(json_output, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"Raw data also saved to {json_output}")
    
    # Clean up checkpoint file
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        print(f"Checkpoint file removed")


if __name__ == "__main__":
    main()

