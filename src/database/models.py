"""
Database models for Congress video format tracking system.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class Committee:
    """Model for Congressional committees."""
    id: Optional[int] = None
    name: str = ""
    chamber: str = ""  # 'house' or 'senate'
    official_url: str = ""
    committee_code: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class Subcommittee:
    """Model for Congressional subcommittees."""
    id: Optional[int] = None
    name: str = ""
    parent_committee_id: int = 0
    official_url: str = ""
    subcommittee_code: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class Hearing:
    """Model for committee hearings."""
    id: Optional[int] = None
    committee_id: Optional[int] = None
    subcommittee_id: Optional[int] = None
    title: str = ""
    hearing_date: Optional[datetime] = None
    hearing_url: str = ""
    video_url: str = ""
    is_live: bool = False
    status: str = ""  # 'scheduled', 'live', 'completed', 'archived'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.hearing_date:
            data['hearing_date'] = self.hearing_date.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class VideoFormat:
    """Model for video streaming formats and technical details."""
    id: Optional[int] = None
    hearing_id: int = 0
    platform: str = ""  # 'youtube', 'vimeo', 'custom', etc.
    video_id: str = ""  # Platform-specific video ID
    embed_code: str = ""
    streaming_url: str = ""
    resolution: str = ""  # '1080p', '720p', etc.
    codec: str = ""  # 'h264', 'h265', etc.
    streaming_protocol: str = ""  # 'hls', 'dash', 'rtmp', etc.
    player_type: str = ""  # 'embedded', 'native', 'custom'
    accessibility_features: str = ""  # JSON string of accessibility features
    technical_details: str = ""  # JSON string of additional technical info
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data
    
    def set_accessibility_features(self, features: Dict[str, Any]):
        """Set accessibility features as JSON string."""
        self.accessibility_features = json.dumps(features)
    
    def get_accessibility_features(self) -> Dict[str, Any]:
        """Get accessibility features from JSON string."""
        if self.accessibility_features:
            return json.loads(self.accessibility_features)
        return {}
    
    def set_technical_details(self, details: Dict[str, Any]):
        """Set technical details as JSON string."""
        self.technical_details = json.dumps(details)
    
    def get_technical_details(self) -> Dict[str, Any]:
        """Get technical details from JSON string."""
        if self.technical_details:
            return json.loads(self.technical_details)
        return {}


@dataclass
class ScrapeLog:
    """Model for tracking scraping activities."""
    id: Optional[int] = None
    target_url: str = ""
    scrape_type: str = ""  # 'committee', 'hearing', 'video'
    status: str = ""  # 'success', 'failed', 'partial'
    records_found: int = 0
    error_message: str = ""
    scrape_duration: float = 0.0  # seconds
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data