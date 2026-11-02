def format_time(seconds: float) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    try:
        sec = int(round(float(seconds)))
    except (ValueError, TypeError):
        return "0:00"

    if sec <= 0:
        return "0:00"

    hours = sec // 3600
    minutes = (sec % 3600) // 60
    secs = sec % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_song_display(song: dict) -> tuple[str, str, str]:
    """Returns (title, artist, album) formatted for display."""
    if not song:
        return "No song playing", "Unknown Artist", ""

    title = song.get("title")
    if not title:
        # Fallback to filename
        file = song.get("file", "Unknown Title")
        title = file.split("/")[-1]

    artist = song.get("artist", "Unknown Artist")
    album = song.get("album", "")

    return str(title), str(artist), str(album)
