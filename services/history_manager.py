"""
History Manager - Tracks and stores insight history
Maintains the last 10 insights generated
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Manages history of AI insights
    Stores last 10 insights in a JSON file
    """
    
    def __init__(
        self,
        history_file: Optional[Union[str, Path]] = None,
        max_entries: int = 10
    ):
        """
        Initialize the history manager
        
        Args:
            history_file: Path to JSON file for storing history
            max_entries: Maximum number of entries to keep (default: 10)
        """
        if history_file is None:
            history_file = Path("history") / "insights_history.json"

        self.history_file = Path(history_file)
        self.max_entries = max_entries
        self._migrate_legacy_history()
        self._ensure_file_exists()
        logger.info(f"📚 History Manager initialized (max entries: {max_entries})")
    
    def _ensure_file_exists(self):
        """Create history file if it doesn't exist"""
        if self.history_file.parent and not self.history_file.parent.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.history_file.exists():
            self._save_history([])
            logger.info(f"Created new history file: {self.history_file}")

    def _migrate_legacy_history(self):
        """Move legacy history file from root if it exists"""
        legacy_file = Path("insights_history.json")
        try:
            if legacy_file.exists() and not self.history_file.exists():
                if self.history_file.parent and not self.history_file.parent.exists():
                    self.history_file.parent.mkdir(parents=True, exist_ok=True)
                legacy_file.replace(self.history_file)
                logger.info(
                    f"📦 Migrated legacy history file to new location: {self.history_file}"
                )
        except Exception as e:
            logger.error(f"Failed to migrate legacy history file: {e}")
    
    def _load_history(self) -> List[Dict]:
        """Load history from JSON file"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return []
    
    def _save_history(self, history: List[Dict]):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def add_entry(self, insight_type: str, city: str, data: Dict):
        """
        Add a new entry to history
        
        Args:
            insight_type: Type of insight (weather, mood, activity)
            city: City name
            data: Complete insight data
        """
        try:
            history = self._load_history()
            
            # Create new entry
            entry = {
                "id": len(history) + 1,
                "timestamp": datetime.now().isoformat(),
                "type": insight_type,
                "city": city,
                "data": data
            }
            
            # Add to beginning of list (most recent first)
            history.insert(0, entry)
            
            # Keep only last max_entries
            history = history[:self.max_entries]
            
            # Re-number IDs
            for i, item in enumerate(history):
                item["id"] = i + 1
            
            self._save_history(history)
            logger.info(f"📝 Added {insight_type} insight for {city} to history")
        
        except Exception as e:
            logger.error(f"Error adding entry to history: {e}")
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get insight history
        
        Args:
            limit: Optional limit on number of entries to return
        
        Returns:
            List of insight entries
        """
        try:
            history = self._load_history()
            if limit:
                history = history[:limit]
            logger.info(f"📖 Retrieved {len(history)} history entries")
            return history
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return []
    
    def clear_history(self):
        """Clear all history"""
        try:
            self._save_history([])
            logger.info("🗑️ History cleared")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
    
    def get_stats(self) -> Dict:
        """Get history statistics"""
        history = self._load_history()
        
        # Count by type
        type_counts = {}
        for entry in history:
            insight_type = entry.get("type", "unknown")
            type_counts[insight_type] = type_counts.get(insight_type, 0) + 1
        
        # Count by city
        city_counts = {}
        for entry in history:
            city = entry.get("city", "unknown")
            city_counts[city] = city_counts.get(city, 0) + 1
        
        return {
            "total_entries": len(history),
            "by_type": type_counts,
            "by_city": city_counts,
            "oldest_entry": history[-1]["timestamp"] if history else None,
            "newest_entry": history[0]["timestamp"] if history else None
        }