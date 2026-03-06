import sys
import os
import csv
from sqlalchemy.exc import IntegrityError
import datetime

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import app, db
    from models import Researcher, Research
except ImportError as e:
    print(f"Error importing app modules: {e}")
    print("Make sure you are running this script from within the virtual environment.")
    sys.exit(1)

def import_researches(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: Could not find '{csv_path}'. Please ensure the file exists in the correct location.")
        return

    print(f"Starting import from {csv_path}...")
    
    with app.app_context():
        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                headers = next(reader) # Skip headers
                
                records_added = 0
                researchers_added = 0
                duplicates_skipped = 0
                errors = 0
                
                for row_idx, row in enumerate(reader, start=2): # Start at 2 because of header
                    if len(row) < 6:
                        print(f"Row {row_idx}: Skipped due to missing columns.")
                        errors += 1
                        continue
                    
                    # Extract fields based on CSV structure
                    # Timestamp, Name of Researcher, Title of Research, DOI of the Research, Department Name, Date
                    name = row[1].strip()
                    title = row[2].strip()
                    doi_url = row[3].strip()
                    department = row[4].strip()
                    year_str = row[5].strip()
                    
                    if not name or not title:
                        print(f"Row {row_idx}: Skipped due to missing Name or Title.")
                        errors += 1
                        continue
                        
                    # Handle year parsing
                    try:
                        year = int(year_str) if year_str.isdigit() else datetime.datetime.now().year
                    except ValueError:
                        year = datetime.datetime.now().year

                    # 1. Get or create Researcher
                    researcher = Researcher.query.filter_by(name=name).first()
                    if not researcher:
                        researcher = Researcher(name=name, is_registered_user=False)
                        db.session.add(researcher)
                        db.session.flush() # Flush to get the researcher ID
                        researchers_added += 1

                    # 2. Check if Research already exists to prevent duplicates
                    existing_research = Research.query.filter_by(title=title).first()
                    if existing_research:
                        duplicates_skipped += 1
                        continue

                    # 3. Create Research
                    research = Research(
                        title=title,
                        doi_url=doi_url if doi_url else None,
                        department=department,
                        year=year,
                        researcher_id=researcher.id,
                        researcher_type='doctor', # Defaulting to doctor based on models.py
                        is_approved=True # Automatically approve since it's an admin import
                    )
                    db.session.add(research)
                    records_added += 1

                # Commit all changes as a single transaction
                db.session.commit()
                
                print("\n--- Import Summary ---")
                print(f"New researchers added: {researchers_added}")
                print(f"New research papers added: {records_added}")
                print(f"Duplicates skipped: {duplicates_skipped}")
                print(f"Rows skipped due to errors: {errors}")
                print("Import completed successfully!")
                
        except UnicodeDecodeError:
            print(f"Error: Could not decode {csv_path}. Please ensure it is saved with UTF-8 encoding.")
            db.session.rollback()
        except IntegrityError as e:
            db.session.rollback()
            print(f"\nDatabase Integrity Error during commit. Transaction rolled back.")
            print(f"Error details: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"\nAn unexpected error occurred. Transaction rolled back.")
            print(f"Error details: {str(e)}")

if __name__ == '__main__':
    # Default paths to check
    possible_paths = [
        'researches.csv',
        '../researches.csv',
        os.path.join(os.path.dirname(__file__), '..', 'researches.csv')
    ]
    
    target_csv = None
    for path in possible_paths:
        if os.path.exists(path):
            target_csv = path
            break
            
    if target_csv:
        import_researches(target_csv)
    else:
        print("Error: Could not locate researches.csv in the current directory or parent directory.")
        print("Please provide the full path to the file:")
        if len(sys.argv) > 1:
            import_researches(sys.argv[1])
        else:
            print("Usage: python import_researches.py [path_to_csv]")