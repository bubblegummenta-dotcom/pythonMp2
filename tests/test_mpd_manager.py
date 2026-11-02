import pytest
from unittest.mock import MagicMock, patch
from app.mpd_manager import MPDManager


@pytest.fixture
def mock_mpd():
    with patch("app.mpd_manager.mpd.MPDClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        manager = MPDManager(host="mockhost", port=6600, password="secret")
        yield manager, mock_instance


def test_connect_success(mock_mpd):
    manager, client = mock_mpd
    assert manager.connect() is True
    assert manager.is_connected is True
    client.connect.assert_called_once_with("mockhost", 6600)
    client.password.assert_called_once_with("secret")


def test_connect_failure(mock_mpd):
    manager, client = mock_mpd
    client.connect.side_effect = Exception("Connection refused")
    assert manager.connect() is False
    assert manager.is_connected is False


def test_get_status_when_connected(mock_mpd):
    manager, client = mock_mpd
    manager._connected = True
    client.status.return_value = {"state": "play", "volume": "80"}
    client.currentsong.return_value = {"title": "Test Title", "artist": "Test Artist"}

    status = manager.get_status()
    assert status["state"] == "play"
    assert status["volume"] == "80"
    assert status["current_song"]["title"] == "Test Title"


def test_playback_controls(mock_mpd):
    manager, client = mock_mpd
    manager._connected = True

    manager.play()
    client.play.assert_called_once()

    manager.pause(1)
    client.pause.assert_called_once_with(1)

    manager.stop()
    client.stop.assert_called_once()

    manager.next()
    client.next.assert_called_once()

    manager.previous()
    client.previous.assert_called_once()


def test_volume_and_seek(mock_mpd):
    manager, client = mock_mpd
    manager._connected = True

    manager.set_volume(75)
    client.setvol.assert_called_once_with(75)

    client.status.return_value = {"songid": "42"}
    manager.seek_current(120.5)
    client.seekid.assert_called_once_with("42", 120)


def test_queue_and_library_methods(mock_mpd):
    manager, client = mock_mpd
    manager._connected = True

    # Delete ID
    manager.delete_id("10")
    client.deleteid.assert_called_once_with("10")

    # Clear
    manager.clear_playlist()
    client.clear.assert_called_once()

    # List directory
    client.lsinfo.return_value = [{"directory": "Rock"}, {"file": "song.mp3"}]
    res = manager.list_directory("Music")
    assert len(res) == 2
    client.lsinfo.assert_called_once_with("Music")

    # Add URI
    manager.add_uri("Music/song.mp3")
    client.add.assert_called_once_with("Music/song.mp3")

    # Play URI
    client.status.return_value = {"playlistlength": "0"}
    client.addid.return_value = "99"
    manager.play_uri("Music/song.mp3")
    client.playid.assert_called_once_with("99")
