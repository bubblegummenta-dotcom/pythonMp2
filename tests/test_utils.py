import pytest
from app.utils import format_time, get_song_display


def test_format_time():
    assert format_time(0) == "0:00"
    assert format_time(5) == "0:05"
    assert format_time(65) == "1:05"
    assert format_time(3600) == "1:00:00"
    assert format_time(3665) == "1:01:05"
    assert format_time(-10) == "0:00"
    assert format_time("invalid") == "0:00"
    assert format_time(None) == "0:00"


def test_get_song_display():
    # Empty song
    assert get_song_display({}) == ("No song playing", "Unknown Artist", "")

    # Song with title, artist, album
    song = {"title": "Imagine", "artist": "John Lennon", "album": "Imagine"}
    assert get_song_display(song) == ("Imagine", "John Lennon", "Imagine")

    # Song with only file
    song2 = {"file": "Rock/classic/song.mp3"}
    assert get_song_display(song2) == ("song.mp3", "Unknown Artist", "")
