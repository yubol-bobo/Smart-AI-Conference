#!/usr/bin/env python3
"""
Test script to verify decision extraction logic handles all decision types
"""

def test_decision_extraction():
    """Test that the decision logic correctly identifies all decision types"""
    
    test_cases = [
        # (venue, venueid, expected_decision, expected_type)
        ("ICLR 2025 Oral", "ICLR.cc/2025/Conference", "Accept (Oral)", "Accept"),
        ("ICLR 2025 Spotlight", "ICLR.cc/2025/Conference", "Accept (Spotlight)", "Accept"),
        ("ICLR 2025 Poster", "ICLR.cc/2025/Conference", "Accept (Poster)", "Accept"),
        ("Submitted to ICLR 2025", "ICLR.cc/2025/Conference/Rejected_Submission", "Reject", "Reject"),
        ("ICLR 2025 Conference Withdrawn Submission", "ICLR.cc/2025/Conference/Withdrawn_Submission", "Withdrawn", "Withdrawn"),
        ("ICLR 2025 Conference Desk Rejected Submission", "ICLR.cc/2025/Conference/Desk_Rejected_Submission", "Desk Reject", "Reject"),
    ]
    
    print("Testing Decision Extraction Logic")
    print("=" * 80)
    
    all_passed = True
    
    for venue, venueid, expected_decision, expected_type in test_cases:
        # Simulate decision logic from scraper
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
        
        # Check for Reject
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
        
        # Fallback
        elif 'ICLR 2025' in venue and 'Submitted' not in venue and 'Withdrawn' not in venue:
            decision = 'Accept (Poster)'
            decision_type = 'Accept'
        
        # Check results
        passed = (decision == expected_decision and decision_type == expected_type)
        status = "✅ PASS" if passed else "❌ FAIL"
        
        if not passed:
            all_passed = False
        
        print(f"\n{status}")
        print(f"  Venue: '{venue}'")
        print(f"  VenueID: '{venueid}'")
        print(f"  Expected: {expected_decision} ({expected_type})")
        print(f"  Got:      {decision} ({decision_type})")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All tests passed! Decision extraction logic is correct.")
    else:
        print("❌ Some tests failed. Please review the logic.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    test_decision_extraction()
