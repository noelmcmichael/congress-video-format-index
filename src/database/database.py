"""
Database operations for Congress video format tracking system.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from src.database.models import Committee, Subcommittee, Hearing, VideoFormat, ScrapeLog


class CongressVideoDatabase:
    """Database manager for Congress video format tracking."""
    
    def __init__(self, db_path: str = "data/congress_video.db"):
        """Initialize database with given path."""
        self.db_path = db_path
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_tables(self):
        """Create all database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Committees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS committees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    chamber TEXT NOT NULL CHECK(chamber IN ('house', 'senate')),
                    official_url TEXT NOT NULL,
                    committee_code TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Subcommittees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subcommittees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_committee_id INTEGER NOT NULL,
                    official_url TEXT NOT NULL,
                    subcommittee_code TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_committee_id) REFERENCES committees (id)
                )
            ''')
            
            # Hearings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hearings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    committee_id INTEGER,
                    subcommittee_id INTEGER,
                    title TEXT NOT NULL,
                    hearing_date TIMESTAMP,
                    hearing_url TEXT NOT NULL,
                    video_url TEXT,
                    is_live BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'live', 'completed', 'archived')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (committee_id) REFERENCES committees (id),
                    FOREIGN KEY (subcommittee_id) REFERENCES subcommittees (id)
                )
            ''')
            
            # Video formats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS video_formats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hearing_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    video_id TEXT,
                    embed_code TEXT,
                    streaming_url TEXT,
                    resolution TEXT,
                    codec TEXT,
                    streaming_protocol TEXT,
                    player_type TEXT,
                    accessibility_features TEXT,
                    technical_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (hearing_id) REFERENCES hearings (id)
                )
            ''')
            
            # Scrape logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_url TEXT NOT NULL,
                    scrape_type TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('success', 'failed', 'partial')),
                    records_found INTEGER DEFAULT 0,
                    error_message TEXT,
                    scrape_duration REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_committees_chamber ON committees(chamber)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_committees_code ON committees(committee_code)')
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_committees_name_chamber ON committees(name, chamber)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_subcommittees_parent ON subcommittees(parent_committee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hearings_committee ON hearings(committee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hearings_subcommittee ON hearings(subcommittee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hearings_date ON hearings(hearing_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_formats_hearing ON video_formats(hearing_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_formats_platform ON video_formats(platform)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scrape_logs_type ON scrape_logs(scrape_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scrape_logs_status ON scrape_logs(status)')
            
            conn.commit()
    
    def insert_committee(self, committee: Committee) -> int:
        """Insert a new committee and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO committees (name, chamber, official_url, committee_code, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (committee.name, committee.chamber, committee.official_url, 
                      committee.committee_code, committee.description))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Committee already exists, return existing ID
                cursor.execute('''
                    SELECT id FROM committees WHERE name = ? AND chamber = ?
                ''', (committee.name, committee.chamber))
                result = cursor.fetchone()
                return result['id'] if result else None
    
    def insert_subcommittee(self, subcommittee: Subcommittee) -> int:
        """Insert a new subcommittee and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO subcommittees (name, parent_committee_id, official_url, subcommittee_code, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (subcommittee.name, subcommittee.parent_committee_id, subcommittee.official_url,
                  subcommittee.subcommittee_code, subcommittee.description))
            conn.commit()
            return cursor.lastrowid
    
    def insert_hearing(self, hearing: Hearing) -> int:
        """Insert a new hearing and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hearings (committee_id, subcommittee_id, title, hearing_date, 
                                    hearing_url, video_url, is_live, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hearing.committee_id, hearing.subcommittee_id, hearing.title,
                  hearing.hearing_date, hearing.hearing_url, hearing.video_url,
                  hearing.is_live, hearing.status))
            conn.commit()
            return cursor.lastrowid
    
    def insert_video_format(self, video_format: VideoFormat) -> int:
        """Insert a new video format and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO video_formats (hearing_id, platform, video_id, embed_code, streaming_url,
                                         resolution, codec, streaming_protocol, player_type,
                                         accessibility_features, technical_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (video_format.hearing_id, video_format.platform, video_format.video_id,
                  video_format.embed_code, video_format.streaming_url, video_format.resolution,
                  video_format.codec, video_format.streaming_protocol, video_format.player_type,
                  video_format.accessibility_features, video_format.technical_details))
            conn.commit()
            return cursor.lastrowid
    
    def insert_scrape_log(self, log: ScrapeLog) -> int:
        """Insert a new scrape log and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scrape_logs (target_url, scrape_type, status, records_found, 
                                       error_message, scrape_duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (log.target_url, log.scrape_type, log.status, log.records_found,
                  log.error_message, log.scrape_duration))
            conn.commit()
            return cursor.lastrowid
    
    def get_committees(self, chamber: Optional[str] = None) -> List[Committee]:
        """Get all committees, optionally filtered by chamber."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if chamber:
                cursor.execute('SELECT * FROM committees WHERE chamber = ? ORDER BY name', (chamber,))
            else:
                cursor.execute('SELECT * FROM committees ORDER BY name')
            
            return [Committee(**dict(row)) for row in cursor.fetchall()]
    
    def get_subcommittees(self, parent_committee_id: Optional[int] = None) -> List[Subcommittee]:
        """Get all subcommittees, optionally filtered by parent committee."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if parent_committee_id:
                cursor.execute('SELECT * FROM subcommittees WHERE parent_committee_id = ? ORDER BY name', 
                             (parent_committee_id,))
            else:
                cursor.execute('SELECT * FROM subcommittees ORDER BY name')
            
            return [Subcommittee(**dict(row)) for row in cursor.fetchall()]
    
    def get_hearings(self, committee_id: Optional[int] = None, 
                    subcommittee_id: Optional[int] = None) -> List[Hearing]:
        """Get hearings, optionally filtered by committee or subcommittee."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM hearings'
            params = []
            
            if committee_id:
                query += ' WHERE committee_id = ?'
                params.append(committee_id)
            elif subcommittee_id:
                query += ' WHERE subcommittee_id = ?'
                params.append(subcommittee_id)
            
            query += ' ORDER BY hearing_date DESC'
            cursor.execute(query, params)
            
            return [Hearing(**dict(row)) for row in cursor.fetchall()]
    
    def get_video_formats(self, hearing_id: Optional[int] = None) -> List[VideoFormat]:
        """Get video formats, optionally filtered by hearing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if hearing_id:
                cursor.execute('SELECT * FROM video_formats WHERE hearing_id = ?', (hearing_id,))
            else:
                cursor.execute('SELECT * FROM video_formats')
            
            return [VideoFormat(**dict(row)) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count committees by chamber
            cursor.execute('SELECT chamber, COUNT(*) as count FROM committees GROUP BY chamber')
            stats['committees_by_chamber'] = {row['chamber']: row['count'] for row in cursor.fetchall()}
            
            # Count total records
            cursor.execute('SELECT COUNT(*) as count FROM committees')
            stats['total_committees'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM subcommittees')
            stats['total_subcommittees'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM hearings')
            stats['total_hearings'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM video_formats')
            stats['total_video_formats'] = cursor.fetchone()['count']
            
            # Count video formats by platform
            cursor.execute('SELECT platform, COUNT(*) as count FROM video_formats GROUP BY platform')
            stats['formats_by_platform'] = {row['platform']: row['count'] for row in cursor.fetchall()}
            
            return stats