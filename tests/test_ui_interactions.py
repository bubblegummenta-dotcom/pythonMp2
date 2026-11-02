import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from app.ui import create_app


def test_ui_tab_switching_and_actions():
    with patch("app.ui.MPDManager") as mock_manager_cls:
        mock_manager = MagicMock()
        mock_manager_cls.return_value = mock_manager
        mock_manager.is_connected = True
        mock_manager.get_status.return_value = {
            "state": "stop",
            "volume": "50",
            "time": "0:200",
            "random": "1",
            "repeat": "0",
            "current_song": {},
        }
        mock_manager.get_playlist.return_value = []
        mock_manager.list_directory.return_value = []

        app_fn = create_app()

        page = MagicMock(spec=ft.Page)
        page.overlay = []
        page.update = MagicMock()
        page.run_task = MagicMock()

        app_fn(page)

        # Check navigation
        page.navigation_bar.selected_index = 1
        page.navigation_bar.on_change(None)
        mock_manager.get_playlist.assert_called()

        page.navigation_bar.selected_index = 2
        page.navigation_bar.on_change(None)
        mock_manager.list_directory.assert_called()
