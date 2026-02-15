"""
Script to migrate research data from CSV to database.

This script reads the researches.csv file and populates the database
with Researcher and Research records.

Usage:
    python migrate_researches.py
"""

import csv
import os
import sys
from app import app, db
from models import Researcher, Research


def migrate_researches(csv_path='researches.csv'):
    """
    Migrate research data from CSV to database.
    
    Args:
        csv_path: Path to the CSV file containing research data
    """
    # Ensure we're in the application context
    with app.app_context():
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"Error: CSV file '{csv_path}' not found.")
            return False
        
        # Track statistics
        researchers_created = 0
        researchers_skipped = 0
        researches_created = 0
        researches_skipped = 0
        
        # Dictionary to cache researcher objects
        researcher_cache = {}
        
        # Read and process CSV
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                researcher_name = row.get('Name of Researcher', '').strip()
                title = row.get('Title of Research', '').strip()
                doi_url = row.get('DOI of the Research', '').strip()
                department = row.get('Department Name', '').strip()
                year_str = row.get('Date', '').strip()
                
                # Skip if missing required fields
                if not researcher_name or not title or not department:
                    print(f"Skipping row - missing required fields: {row}")
                    researches_skipped += 1
                    continue
                
                # Parse year
                try:
                    year = int(year_str) if year_str else None
                except ValueError:
                    year = None
                
                if not year:
                    print(f"Skipping row - invalid year: {year_str}")
                    researches_skipped += 1
                    continue
                
                # Get or create researcher
                if researcher_name in researcher_cache:
                    researcher = researcher_cache[researcher_name]
                else:
                    researcher = Researcher.query.filter_by(name=researcher_name).first()
                    if not researcher:
                        researcher = Researcher(name=researcher_name)
                        db.session.add(researcher)
                        db.session.flush()  # Get the ID without committing
                        researchers_created += 1
                        print(f"Created researcher: {researcher_name}")
                    else:
                        researchers_skipped += 1
                    researcher_cache[researcher_name] = researcher
                
                # Check if research already exists
                existing_research = Research.query.filter_by(
                    title=title, 
                    researcher_id=researcher.id
                ).first()
                
                if existing_research:
                    print(f"Skipping existing research: {title[:50]}...")
                    researches_skipped += 1
                    continue
                
                # Create research record
                research = Research(
                    title=title,
                    doi_url=doi_url if doi_url else None,
                    department=department,
                    year=year,
                    researcher_id=researcher.id,
                    is_approved=True  # Existing research is already approved
                )
                db.session.add(research)
                researches_created += 1
                # Use ASCII-safe output for console
                safe_title = title[:50].encode('ascii', 'replace').decode('ascii')
                print(f"Created research: {safe_title}...")
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "="*50)
            print("Migration completed successfully!")
            print(f"Researchers created: {researchers_created}")
            print(f"Researchers skipped (already existed): {researchers_skipped}")
            print(f"Researches created: {researches_created}")
            print(f"Researches skipped: {researches_skipped}")
            print("="*50)
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            return False


def clear_research_data():
    """
    Clear all research and researcher data from database.
    Use with caution!
    """
    with app.app_context():
        try:
            # Delete all research records first (due to foreign key constraint)
            num_researches = Research.query.delete()
            # Delete all researcher records
            num_researchers = Researcher.query.delete()
            db.session.commit()
            print(f"Deleted {num_researches} research records")
            print(f"Deleted {num_researchers} researcher records")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate research data from CSV to database')
    parser.add_argument('--clear', action='store_true', help='Clear existing research data before migration')
    parser.add_argument('--csv', default='researches.csv', help='Path to CSV file (default: researches.csv)')
    
    args = parser.parse_args()
    
    if args.clear:
        confirm = input("Are you sure you want to clear all research data? (yes/no): ")
        if confirm.lower() == 'yes':
            clear_research_data()
        else:
            print("Operation cancelled.")
    
    migrate_researches(args.csv)