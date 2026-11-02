import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from app.ui import create_app


def test_ui_initialization():
    with patch("app.ui.MPDManager") as mock_manager_cls:
        mock_manager = MagicMock()
        mock_manager_cls.return_value = mock_manager
        mock_manager.is_connected = True
        mock_manager.get_status.return_value = {
            "state": "play",
            "volume": "70",
            "time": "30:180",
            "random": "0",
            "repeat": "0",
            "current_song": {"title": "Song A", "artist": "Artist A", "album": "Album A"},
        }
        mock_manager.get_playlist.return_value = [
            {"id": "1", "title": "Song A", "artist": "Artist A", "time": "180"}
        ]
        mock_manager.list_directory.return_value = [
            {"directory": "Rock"},
            {"file": "song.mp3", "title": "Song", "artist": "Artist", "time": "200"},
        ]

        app_fn = create_app()

        page = MagicMock(spec=ft.Page)
        page.overlay = []
        page.update = MagicMock()
        page.run_task = MagicMock()

        # Call page setup
        app_fn(page)

        assert page.title == "Music Player (MPD)"
        assert page.appbar is not None
        assert page.navigation_bar is not None
        mock_manager.connect.assert_called_once()
