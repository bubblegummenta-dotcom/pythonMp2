import os
import logging
from typing import Optional, Dict, Any, List
import mpd

logger = logging.getLogger("mpd_client")


class MPDManager:
    """Manages MPD connection, status fetching, and commands."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, password: Optional[str] = None):
        self.host = host or os.environ.get("MPD_HOST", "localhost")
        self.port = int(port or os.environ.get("MPD_PORT", "6600"))
        self.password = password or os.environ.get("MPD_PASSWORD", "")
        self.client = mpd.MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        if self._connected:
            try:
                self.client.ping()
                return True
            except Exception:
                self.disconnect()

        try:
            self.client = mpd.MPDClient()
            self.client.timeout = 10
            self.client.connect(self.host, self.port)
            if self.password:
                self.client.password(self.password)
            self._connected = True
            logger.info("Connected to MPD at %s:%d", self.host, self.port)
            return True
        except Exception as e:
            logger.warning("Failed to connect to MPD (%s:%d): %s", self.host, self.port, e)
            self._connected = False
            return False

    def disconnect(self):
        try:
            self.client.close()
        except Exception:
            pass
        try:
            self.client.disconnect()
        except Exception:
            pass
        self._connected = False

    def _ensure_connection(self) -> bool:
        if not self._connected:
            return self.connect()
        try:
            self.client.ping()
            return True
        except Exception:
            self.disconnect()
            return self.connect()

    def get_status(self) -> Dict[str, Any]:
        if not self._ensure_connection():
            return {"state": "disconnected"}
        try:
            status = self.client.status()
            current_song = self.client.currentsong()
            status["current_song"] = current_song
            return status
        except Exception as e:
            logger.error("Error getting status: %s", e)
            self.disconnect()
            return {"state": "disconnected"}

    def play(self):
        if self._ensure_connection():
            try:
                self.client.play()
            except Exception as e:
                logger.error("Error playing: %s", e)

    def play_id(self, song_id: str):
        if self._ensure_connection():
            try:
                self.client.playid(song_id)
            except Exception as e:
                logger.error("Error playing id %s: %s", song_id, e)

    def pause(self, pause_state: Optional[int] = None):
        if self._ensure_connection():
            try:
                if pause_state is not None:
                    self.client.pause(pause_state)
                else:
                    self.client.pause()
            except Exception as e:
                logger.error("Error pausing: %s", e)

    def toggle_play_pause(self):
        status = self.get_status()
        state = status.get("state")
        if state == "play":
            self.pause(1)
        elif state in ("pause", "stop"):
            self.play()

    def stop(self):
        if self._ensure_connection():
            try:
                self.client.stop()
            except Exception as e:
                logger.error("Error stopping: %s", e)

    def next(self):
        if self._ensure_connection():
            try:
                self.client.next()
            except Exception as e:
                logger.error("Error next: %s", e)

    def previous(self):
        if self._ensure_connection():
            try:
                self.client.previous()
            except Exception as e:
                logger.error("Error previous: %s", e)

    def set_volume(self, volume: int):
        volume = max(0, min(100, int(volume)))
        if self._ensure_connection():
            try:
                self.client.setvol(volume)
            except Exception as e:
                logger.error("Error setting volume: %s", e)

    def seek_current(self, seconds: float):
        if self._ensure_connection():
            try:
                status = self.client.status()
                song_id = status.get("songid")
                if song_id is not None:
                    self.client.seekid(song_id, int(seconds))
            except Exception as e:
                logger.error("Error seeking: %s", e)

    def toggle_random(self):
        status = self.get_status()
        current = int(status.get("random", 0))
        new_val = 0 if current == 1 else 1
        if self._ensure_connection():
            try:
                self.client.random(new_val)
            except Exception as e:
                logger.error("Error toggling random: %s", e)

    def toggle_repeat(self):
        status = self.get_status()
        current = int(status.get("repeat", 0))
        new_val = 0 if current == 1 else 1
        if self._ensure_connection():
            try:
                self.client.repeat(new_val)
            except Exception as e:
                logger.error("Error toggling repeat: %s", e)

    def get_playlist(self) -> List[Dict[str, Any]]:
        if not self._ensure_connection():
            return []
        try:
            return self.client.playlistinfo()
        except Exception as e:
            logger.error("Error fetching playlistinfo: %s", e)
            return []

    def delete_id(self, song_id: str):
        if self._ensure_connection():
            try:
                self.client.deleteid(song_id)
            except Exception as e:
                logger.error("Error deleting id %s: %s", song_id, e)

    def clear_playlist(self):
        if self._ensure_connection():
            try:
                self.client.clear()
            except Exception as e:
                logger.error("Error clearing playlist: %s", e)

    def list_directory(self, uri: str = "") -> List[Dict[str, Any]]:
        """List contents of a directory in the music library."""
        if not self._ensure_connection():
            return []
        try:
            return self.client.lsinfo(uri)
        except Exception as e:
            logger.error("Error listing directory '%s': %s", uri, e)
            return []

    def add_uri(self, uri: str):
        if self._ensure_connection():
            try:
                self.client.add(uri)
            except Exception as e:
                logger.error("Error adding uri %s: %s", uri, e)

    def play_uri(self, uri: str):
        """Adds uri and immediately plays it if playlist was empty, or plays the added song."""
        if self._ensure_connection():
            try:
                status = self.client.status()
                was_empty = int(status.get("playlistlength", 0)) == 0
                song_id = self.client.addid(uri)
                if was_empty or song_id:
                    self.client.playid(song_id)
            except Exception as e:
                logger.error("Error playing uri %s: %s", uri, e)

    def update_database(self, uri: str = ""):
        if self._ensure_connection():
            try:
                self.client.update(uri)
            except Exception as e:
                logger.error("Error updating db: %s", e)
