#!/usr/bin/env python3
"""
Robust Data Migration Script: SQLite -> PostgreSQL
Migrates data from SQLite to PostgreSQL, skipping missing source tables.
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime

# Configuration
SQLITE_DB = "instance/psra.db"
# Use environment variable or fallback to default
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://psra_user:psra_pass123@localhost:5432/psra"
)

def get_pg_connection():
    """Create PostgreSQL connection."""
    return psycopg2.connect(DATABASE_URL)

def get_sqlite_connection():
    """Create SQLite connection."""
    if not os.path.exists(SQLITE_DB):
        raise FileNotFoundError(f"SQLite database not found at {SQLITE_DB}")
    return sqlite3.connect(SQLITE_DB)

def check_table_exists(cursor, table_name):
    """Check if a table exists in the SQLite database."""
    # Handle quoted table names for check
    clean_name = table_name.replace('"', '')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (clean_name,))
    return cursor.fetchone() is not None

def migrate_users(sqlite_conn, pg_conn):
    """Migrate users table."""
    print("Migrating users...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "user"):
        print("  Warning: Table 'user' not found in SQLite. Skipping.")
        return

    # Ensure password_hash column is wide enough
    try:
        pg_cursor.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)')
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
    
    sqlite_cursor.execute("""
        SELECT id, name, email, password_hash, batch_number, phone_number,
               whatsapp_number, is_member, status, headline, location, about,
               skills, education, experience, linkedin_url, is_admin, created_at,
               website_url, cover_photo_url, languages, certifications,
               projects, professional_summary, publications, profile_picture_url,
               email_notifications_enabled, event_reminders_enabled,
               new_research_alerts_enabled
        FROM "user"
    """)
    
    original_users = sqlite_cursor.fetchall()
    
    users = []
    for row in original_users:
        row = list(row)
        # Convert integer booleans to actual booleans
        row[7] = bool(row[7])   # is_member
        row[16] = bool(row[16])  # is_admin
        row[26] = bool(row[26])  # email_notifications_enabled
        row[27] = bool(row[27])  # event_reminders_enabled
        row[28] = bool(row[28])  # new_research_alerts_enabled
        users.append(tuple(row))
    
    query = """
        INSERT INTO "user" (id, name, email, password_hash, batch_number, phone_number,
               whatsapp_number, is_member, status, headline, location, about,
               skills, education, experience, linkedin_url, is_admin, created_at,
               website_url, cover_photo_url, languages, certifications,
               projects, professional_summary, publications, profile_picture_url,
               email_notifications_enabled, event_reminders_enabled,
               new_research_alerts_enabled)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            password_hash = EXCLUDED.password_hash,
            batch_number = EXCLUDED.batch_number,
            phone_number = EXCLUDED.phone_number,
            whatsapp_number = EXCLUDED.whatsapp_number,
            is_member = EXCLUDED.is_member,
            status = EXCLUDED.status,
            headline = EXCLUDED.headline,
            location = EXCLUDED.location,
            about = EXCLUDED.about,
            skills = EXCLUDED.skills,
            education = EXCLUDED.education,
            experience = EXCLUDED.experience,
            linkedin_url = EXCLUDED.linkedin_url,
            is_admin = EXCLUDED.is_admin,
            created_at = EXCLUDED.created_at,
            website_url = EXCLUDED.website_url,
            cover_photo_url = EXCLUDED.cover_photo_url,
            languages = EXCLUDED.languages,
            certifications = EXCLUDED.certifications,
            projects = EXCLUDED.projects,
            professional_summary = EXCLUDED.professional_summary,
            publications = EXCLUDED.publications,
            profile_picture_url = EXCLUDED.profile_picture_url,
            email_notifications_enabled = EXCLUDED.email_notifications_enabled,
            event_reminders_enabled = EXCLUDED.event_reminders_enabled,
            new_research_alerts_enabled = EXCLUDED.new_research_alerts_enabled
    """
    
    execute_batch(pg_cursor, query, users)
    pg_conn.commit()
    print(f"  Migrated {len(users)} users")

def migrate_researchers(sqlite_conn, pg_conn):
    """Migrate researchers table."""
    print("Migrating researchers...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "researcher"):
        print("  Warning: Table 'researcher' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, name, profile_picture_url, bio, is_registered_user, user_id, created_at
        FROM researcher
    """)
    
    original_researchers = sqlite_cursor.fetchall()
    
    researchers = []
    for row in original_researchers:
        row = list(row)
        row[4] = bool(row[4])  # is_registered_user
        researchers.append(tuple(row))
    
    query = """
        INSERT INTO researcher (id, name, profile_picture_url, bio, is_registered_user, user_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            profile_picture_url = EXCLUDED.profile_picture_url,
            bio = EXCLUDED.bio,
            is_registered_user = EXCLUDED.is_registered_user,
            user_id = EXCLUDED.user_id,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, researchers)
    pg_conn.commit()
    print(f"  Migrated {len(researchers)} researchers")

def migrate_posts(sqlite_conn, pg_conn):
    """Migrate posts table."""
    print("Migrating posts...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "post"):
        print("  Warning: Table 'post' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, user_id, category, title, content, image_url, created_at
        FROM post
    """)
    
    posts = sqlite_cursor.fetchall()
    
    query = """
        INSERT INTO post (id, user_id, category, title, content, image_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            category = EXCLUDED.category,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            image_url = EXCLUDED.image_url,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, posts)
    pg_conn.commit()
    print(f"  Migrated {len(posts)} posts")

def migrate_comments(sqlite_conn, pg_conn):
    """Migrate comments table."""
    print("Migrating comments...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "comment"):
        print("  Warning: Table 'comment' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, post_id, user_id, content, created_at
        FROM "comment"
    """)
    
    comments = sqlite_cursor.fetchall()
    
    query = """
        INSERT INTO "comment" (id, post_id, user_id, content, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            post_id = EXCLUDED.post_id,
            user_id = EXCLUDED.user_id,
            content = EXCLUDED.content,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, comments)
    pg_conn.commit()
    print(f"  Migrated {len(comments)} comments")

def migrate_likes(sqlite_conn, pg_conn):
    """Migrate likes table."""
    print("Migrating likes...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Check for "like" or "like_table"
    table_name = "like"
    if not check_table_exists(sqlite_cursor, "like"):
        if check_table_exists(sqlite_cursor, "like_table"):
            table_name = "like_table"
        else:
            print("  Warning: Table 'like' not found in SQLite. Skipping.")
            return

    sqlite_cursor.execute(f"""
        SELECT id, user_id, post_id
        FROM "{table_name}"
    """)
    
    likes = sqlite_cursor.fetchall()
    
    query = """
        INSERT INTO "like" (id, user_id, post_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            post_id = EXCLUDED.post_id
    """
    
    execute_batch(pg_cursor, query, likes)
    pg_conn.commit()
    print(f"  Migrated {len(likes)} likes")

def migrate_events(sqlite_conn, pg_conn):
    """Migrate events table."""
    print("Migrating events...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "event"):
        print("  Warning: Table 'event' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, title, description, event_date, event_time, image_url,
               presenter, event_url, is_archived, created_by, created_at
        FROM event
    """)
    
    original_events = sqlite_cursor.fetchall()
    
    events = []
    for row in original_events:
        row = list(row)
        row[8] = bool(row[8])  # is_archived
        events.append(tuple(row))
    
    query = """
        INSERT INTO event (id, title, description, event_date, event_time, image_url,
               presenter, event_url, is_archived, created_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            event_date = EXCLUDED.event_date,
            event_time = EXCLUDED.event_time,
            image_url = EXCLUDED.image_url,
            presenter = EXCLUDED.presenter,
            event_url = EXCLUDED.event_url,
            is_archived = EXCLUDED.is_archived,
            created_by = EXCLUDED.created_by,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, events)
    pg_conn.commit()
    print(f"  Migrated {len(events)} events")

def migrate_messages(sqlite_conn, pg_conn):
    """Migrate messages table."""
    print("Migrating messages...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "message"):
        print("  Warning: Table 'message' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, sender_id, receiver_id, content, is_read, read_at, created_at
        FROM message
    """)
    
    original_messages = sqlite_cursor.fetchall()
    
    messages = []
    for row in original_messages:
        row = list(row)
        row[4] = bool(row[4])  # is_read
        messages.append(tuple(row))
    
    query = """
        INSERT INTO message (id, sender_id, receiver_id, content, is_read, read_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            sender_id = EXCLUDED.sender_id,
            receiver_id = EXCLUDED.receiver_id,
            content = EXCLUDED.content,
            is_read = EXCLUDED.is_read,
            read_at = EXCLUDED.read_at,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, messages)
    pg_conn.commit()
    print(f"  Migrated {len(messages)} messages")

def migrate_researches(sqlite_conn, pg_conn):
    """Migrate researches table."""
    print("Migrating researches...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "research"):
        print("  Warning: Table 'research' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, title, doi_url, department, year, researcher_id,
               researcher_type, is_approved, submitted_by, created_at
        FROM research
    """)
    
    original_researches = sqlite_cursor.fetchall()
    
    researches = []
    for row in original_researches:
        row = list(row)
        row[7] = bool(row[7])  # is_approved
        researches.append(tuple(row))
    
    query = """
        INSERT INTO research (id, title, doi_url, department, year, researcher_id,
               researcher_type, is_approved, submitted_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            doi_url = EXCLUDED.doi_url,
            department = EXCLUDED.department,
            year = EXCLUDED.year,
            researcher_id = EXCLUDED.researcher_id,
            researcher_type = EXCLUDED.researcher_type,
            is_approved = EXCLUDED.is_approved,
            submitted_by = EXCLUDED.submitted_by,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, researches)
    pg_conn.commit()
    print(f"  Migrated {len(researches)} researches")

def migrate_announcements(sqlite_conn, pg_conn):
    """Migrate announcements table."""
    print("Migrating announcements...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "announcement"):
        print("  Warning: Table 'announcement' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, subject, body, target_filter, recipient_count,
               success_count, failure_count, created_by, sent_at, created_at
        FROM announcement
    """)
    
    announcements = sqlite_cursor.fetchall()
    
    query = """
        INSERT INTO announcement (id, subject, body, target_filter, recipient_count,
               success_count, failure_count, created_by, sent_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            subject = EXCLUDED.subject,
            body = EXCLUDED.body,
            target_filter = EXCLUDED.target_filter,
            recipient_count = EXCLUDED.recipient_count,
            success_count = EXCLUDED.success_count,
            failure_count = EXCLUDED.failure_count,
            created_by = EXCLUDED.created_by,
            sent_at = EXCLUDED.sent_at,
            created_at = EXCLUDED.created_at
    """
    
    execute_batch(pg_cursor, query, announcements)
    pg_conn.commit()
    print(f"  Migrated {len(announcements)} announcements")

def migrate_notification_logs(sqlite_conn, pg_conn):
    """Migrate notification_logs table."""
    print("Migrating notification_logs...")
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    if not check_table_exists(sqlite_cursor, "notification_log"):
        print("  Warning: Table 'notification_log' not found in SQLite. Skipping.")
        return
    
    sqlite_cursor.execute("""
        SELECT id, user_id, notification_type, reference_id, recipient_email,
               subject, sent_at, status, error_message
        FROM notification_log
    """)
    
    logs = sqlite_cursor.fetchall()
    
    query = """
        INSERT INTO notification_log (id, user_id, notification_type, reference_id, recipient_email,
               subject, sent_at, status, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            notification_type = EXCLUDED.notification_type,
            reference_id = EXCLUDED.reference_id,
            recipient_email = EXCLUDED.recipient_email,
            subject = EXCLUDED.subject,
            sent_at = EXCLUDED.sent_at,
            status = EXCLUDED.status,
            error_message = EXCLUDED.error_message
    """
    
    execute_batch(pg_cursor, query, logs)
    pg_conn.commit()
    print(f"  Migrated {len(logs)} notification logs")

def reset_sequences(pg_conn):
    """Reset PostgreSQL sequences to continue from max id."""
    print("Resetting sequences...")
    pg_cursor = pg_conn.cursor()
    
    tables = ['"user"', 'post', 'comment', '"like"', 'event', 'message', 
              'researcher', 'research', 'announcement', 'notification_log']
    
    for table in tables:
        try:
            # Get sequence name
            pg_cursor.execute(f"SELECT pg_get_serial_sequence('{table}', 'id')")
            result = pg_cursor.fetchone()
            if result and result[0]:
                seq_name = result[0]
                # Reset sequence
                pg_cursor.execute(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)")
            else:
                pass # Silently skip missing tables/sequences
        except Exception as e:
            # Warning: Could not reset sequence for ...
            # Usually happens if table doesn't exist or transaction aborted
            pg_conn.rollback()
    
    pg_conn.commit()
    print("  Sequences reset complete")

def main():
    print("=" * 50)
    print("Robust SQLite to PostgreSQL Data Migration")
    print("=" * 50)
    
    if not os.path.exists(SQLITE_DB):
        print(f"Error: SQLite database not found at {SQLITE_DB}")
        return
    
    print(f"\nSource: SQLite ({SQLITE_DB})")
    print(f"Target: PostgreSQL ({DATABASE_URL})")
    
    try:
        sqlite_conn = get_sqlite_connection()
        pg_conn = get_pg_connection()
    except Exception as e:
        print(f"Connection error: {e}")
        return
    
    try:
        migrate_users(sqlite_conn, pg_conn)
        migrate_researchers(sqlite_conn, pg_conn)
        migrate_posts(sqlite_conn, pg_conn)
        migrate_comments(sqlite_conn, pg_conn)
        migrate_likes(sqlite_conn, pg_conn)
        migrate_events(sqlite_conn, pg_conn)
        migrate_messages(sqlite_conn, pg_conn)
        migrate_researches(sqlite_conn, pg_conn)
        migrate_announcements(sqlite_conn, pg_conn)
        migrate_notification_logs(sqlite_conn, pg_conn)
        
        reset_sequences(pg_conn)
        
        print("\n" + "=" * 50)
        print("Migration Complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during migration: {e}")
        pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()

if __name__ == "__main__":
    main()
