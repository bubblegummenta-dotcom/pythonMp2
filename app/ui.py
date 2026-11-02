import asyncio
import os
import flet as ft
from app.mpd_manager import MPDManager
from app.utils import format_time, get_song_display


def create_app():
    # Read MPD settings from env
    mpd_host = os.environ.get("MPD_HOST", "localhost")
    mpd_port = int(os.environ.get("MPD_PORT", "6600"))
    mpd_password = os.environ.get("MPD_PASSWORD", "")
    manager = MPDManager(host=mpd_host, port=mpd_port, password=mpd_password)

    def main(page: ft.Page):
        page.title = "Music Player (MPD)"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 10
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # UI Controls for Player View
        song_title_text = ft.Text(
            "No song playing",
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        song_artist_text = ft.Text(
            "Unknown Artist",
            size=15,
            color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        song_album_text = ft.Text(
            "",
            size=13,
            color=ft.Colors.GREY_500,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        time_elapsed_text = ft.Text("0:00", size=12, color=ft.Colors.GREY_400)
        time_total_text = ft.Text("0:00", size=12, color=ft.Colors.GREY_400)

        is_seeking = False

        def on_seek_change(e):
            nonlocal is_seeking
            is_seeking = True

        def on_seek_end(e):
            nonlocal is_seeking
            manager.seek_current(seek_slider.value)
            is_seeking = False

        seek_slider = ft.Slider(
            min=0,
            max=100,
            value=0,
            on_change=on_seek_change,
            on_change_end=on_seek_end,
            expand=True,
            active_color=ft.Colors.ORANGE_ACCENT,
        )

        # VLC orange accent style button
        play_btn_icon = ft.Icons.PLAY_ARROW_ROUNDED

        def on_prev_click(e):
            manager.previous()
            refresh_status()

        def on_play_pause_click(e):
            manager.toggle_play_pause()
            refresh_status()

        def on_stop_click(e):
            manager.stop()
            refresh_status()

        def on_next_click(e):
            manager.next()
            refresh_status()

        prev_btn = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
            icon_size=34,
            on_click=on_prev_click,
            tooltip="Previous",
        )
        play_pause_btn = ft.IconButton(
            icon=play_btn_icon,
            icon_size=52,
            icon_color=ft.Colors.ORANGE_ACCENT,
            on_click=on_play_pause_click,
            tooltip="Play/Pause",
        )
        stop_btn = ft.IconButton(
            icon=ft.Icons.STOP_ROUNDED,
            icon_size=34,
            on_click=on_stop_click,
            tooltip="Stop",
        )
        next_btn = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT_ROUNDED,
            icon_size=34,
            on_click=on_next_click,
            tooltip="Next",
        )

        # Shuffle and Repeat
        def on_random_click(e):
            manager.toggle_random()
            refresh_status()

        def on_repeat_click(e):
            manager.toggle_repeat()
            refresh_status()

        random_btn = ft.IconButton(
            icon=ft.Icons.SHUFFLE_ROUNDED,
            icon_size=24,
            icon_color=ft.Colors.GREY_500,
            on_click=on_random_click,
            tooltip="Random",
        )
        repeat_btn = ft.IconButton(
            icon=ft.Icons.REPEAT_ROUNDED,
            icon_size=24,
            icon_color=ft.Colors.GREY_500,
            on_click=on_repeat_click,
            tooltip="Repeat",
        )

        # Volume slider
        is_changing_vol = False

        def on_volume_change(e):
            nonlocal is_changing_vol
            is_changing_vol = True
            manager.set_volume(int(volume_slider.value))

        def on_volume_end(e):
            nonlocal is_changing_vol
            is_changing_vol = False

        volume_slider = ft.Slider(
            min=0,
            max=100,
            value=100,
            on_change=on_volume_change,
            on_change_end=on_volume_end,
            expand=True,
            active_color=ft.Colors.ORANGE_ACCENT,
        )

        volume_icon = ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, color=ft.Colors.GREY_400)

        # Album Art / VLC Cone Placeholder
        album_art_icon = ft.Container(
            content=ft.Icon(
                ft.Icons.MUSIC_NOTE_ROUNDED,
                size=110,
                color=ft.Colors.ORANGE_ACCENT,
            ),
            width=220,
            height=220,
            border_radius=20,
            bgcolor=ft.Colors.GREY_900,
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )

        player_view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=10),
                    album_art_icon,
                    ft.Container(height=15),
                    song_title_text,
                    song_artist_text,
                    song_album_text,
                    ft.Container(height=10),
                    ft.Row(
                        controls=[
                            time_elapsed_text,
                            seek_slider,
                            time_total_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            random_btn,
                            prev_btn,
                            play_pause_btn,
                            stop_btn,
                            next_btn,
                            repeat_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        controls=[
                            volume_icon,
                            volume_slider,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding(left=15, right=15, top=0, bottom=0),
        )

        # ==========================================
        # Queue / Playlist View
        # ==========================================
        playlist_list_view = ft.ListView(
            expand=True,
            spacing=4,
            padding=10,
        )

        def clear_queue_click(e):
            manager.clear_playlist()
            refresh_queue()
            refresh_status()

        clear_queue_btn = ft.FilledButton(
            content=ft.Text("Clear Queue"),
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            on_click=clear_queue_click,
            color=ft.Colors.RED_400,
        )

        queue_view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Playback Queue", size=18, weight=ft.FontWeight.BOLD),
                            clear_queue_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    playlist_list_view,
                ],
                expand=True,
            ),
            expand=True,
            padding=10,
            visible=False,
        )

        # ==========================================
        # Library / Folder Browser View
        # ==========================================
        current_path = ""
        path_text = ft.Text("/", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ORANGE_ACCENT)
        browser_list_view = ft.ListView(
            expand=True,
            spacing=4,
            padding=10,
        )

        def navigate_up(e):
            nonlocal current_path
            if current_path:
                parts = current_path.strip("/").split("/")
                parts.pop()
                current_path = "/".join(parts)
                refresh_browser()

        up_btn = ft.IconButton(
            icon=ft.Icons.ARROW_UPWARD_ROUNDED,
            tooltip="Up one folder",
            on_click=navigate_up,
        )

        def refresh_library_click(e):
            manager.update_database()
            refresh_browser()

        update_db_btn = ft.IconButton(
            icon=ft.Icons.SYNC_ROUNDED,
            tooltip="Update MPD database",
            on_click=refresh_library_click,
        )

        browser_view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            up_btn,
                            ft.Container(content=path_text, expand=True),
                            update_db_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    browser_list_view,
                ],
                expand=True,
            ),
            expand=True,
            padding=10,
            visible=False,
        )

        # ==========================================
        # Settings Dialog / View
        # ==========================================
        host_input = ft.TextField(label="MPD Host", value=manager.host)
        port_input = ft.TextField(label="MPD Port", value=str(manager.port))
        password_input = ft.TextField(label="Password (optional)", password=True, can_reveal_password=True, value=manager.password)
        conn_status_text = ft.Text("Checking...", color=ft.Colors.GREY_400)

        def save_settings(e):
            manager.host = host_input.value.strip() or "localhost"
            try:
                manager.port = int(port_input.value.strip())
            except ValueError:
                manager.port = 6600
            manager.password = password_input.value.strip()
            manager.disconnect()
            manager.connect()
            refresh_status()
            settings_dialog.open = False
            page.update()

        settings_dialog = ft.AlertDialog(
            title=ft.Text("MPD Settings"),
            content=ft.Column(
                controls=[
                    conn_status_text,
                    host_input,
                    port_input,
                    password_input,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=lambda e: setattr(settings_dialog, "open", False) or page.update()),
                ft.FilledButton(content=ft.Text("Save & Reconnect"), on_click=save_settings),
            ],
        )

        def open_settings(e):
            conn_status_text.value = f"Status: {'Connected' if manager.is_connected else 'Disconnected'}"
            conn_status_text.color = ft.Colors.GREEN_400 if manager.is_connected else ft.Colors.RED_400
            settings_dialog.open = True
            page.overlay.append(settings_dialog)
            page.update()

        # Navigation Bar
        def on_nav_change(e):
            idx = nav_bar.selected_index
            player_view.visible = (idx == 0)
            queue_view.visible = (idx == 1)
            browser_view.visible = (idx == 2)
            if idx == 1:
                refresh_queue()
            elif idx == 2:
                refresh_browser()
            page.update()

        nav_bar = ft.NavigationBar(
            selected_index=0,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.PLAY_CIRCLE_OUTLINE, selected_icon=ft.Icons.PLAY_CIRCLE, label="Player"),
                ft.NavigationBarDestination(icon=ft.Icons.QUEUE_MUSIC_OUTLINED, selected_icon=ft.Icons.QUEUE_MUSIC, label="Queue"),
                ft.NavigationBarDestination(icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER, label="Folders"),
            ],
            on_change=on_nav_change,
        )

        app_bar = ft.AppBar(
            leading=ft.Icon(ft.Icons.HEADPHONES_ROUNDED, color=ft.Colors.ORANGE_ACCENT),
            title=ft.Text("Flet Music Player"),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions=[
                ft.IconButton(ft.Icons.SETTINGS_OUTLINED, on_click=open_settings, tooltip="Settings"),
            ],
        )

        # Data Refreshing
        def refresh_status():
            status = manager.get_status()
            current_song = status.get("current_song", {})

            # Play state
            state = status.get("state", "stop")
            if state == "play":
                play_pause_btn.icon = ft.Icons.PAUSE_ROUNDED
            else:
                play_pause_btn.icon = ft.Icons.PLAY_ARROW_ROUNDED

            # Song metadata
            title, artist, album = get_song_display(current_song)
            song_title_text.value = title
            song_artist_text.value = artist
            song_album_text.value = album

            # Progress / seek
            elapsed = 0.0
            total = 0.0
            if "time" in status:
                try:
                    time_parts = status["time"].split(":")
                    elapsed = float(time_parts[0])
                    total = float(time_parts[1])
                except (IndexError, ValueError):
                    pass
            elif "elapsed" in status and "duration" in status:
                try:
                    elapsed = float(status["elapsed"])
                    total = float(status["duration"])
                except ValueError:
                    pass

            time_elapsed_text.value = format_time(elapsed)
            time_total_text.value = format_time(total)

            if not is_seeking:
                seek_slider.max = max(total, 1.0)
                seek_slider.value = min(elapsed, seek_slider.max)

            # Volume
            if not is_changing_vol:
                try:
                    vol = int(status.get("volume", 100))
                    if vol >= 0:
                        volume_slider.value = vol
                        if vol == 0:
                            volume_icon.name = ft.Icons.VOLUME_MUTE_ROUNDED
                        elif vol < 50:
                            volume_icon.name = ft.Icons.VOLUME_DOWN_ROUNDED
                        else:
                            volume_icon.name = ft.Icons.VOLUME_UP_ROUNDED
                except (ValueError, TypeError):
                    pass

            # Random & Repeat
            random_on = int(status.get("random", 0)) == 1
            repeat_on = int(status.get("repeat", 0)) == 1
            random_btn.icon_color = ft.Colors.ORANGE_ACCENT if random_on else ft.Colors.GREY_500
            repeat_btn.icon_color = ft.Colors.ORANGE_ACCENT if repeat_on else ft.Colors.GREY_500

            page.update()

        def refresh_queue():
            playlist = manager.get_playlist()
            status = manager.get_status()
            current_song_id = status.get("songid")

            items = []
            if not playlist:
                items.append(
                    ft.Container(
                        content=ft.Text("Queue is empty. Browse folders to add music!", color=ft.Colors.GREY_400),
                        padding=20,
                        alignment=ft.Alignment(0, 0),
                    )
                )
            else:
                for idx, song in enumerate(playlist):
                    sid = song.get("id")
                    stitle, sartist, _ = get_song_display(song)
                    sduration = format_time(song.get("time", 0))
                    is_current = sid == current_song_id

                    def play_this(e, song_id=sid):
                        manager.play_id(song_id)
                        refresh_status()
                        refresh_queue()

                    def delete_this(e, song_id=sid):
                        manager.delete_id(song_id)
                        refresh_queue()
                        refresh_status()

                    item_row = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{idx + 1}.", size=12, color=ft.Colors.GREY_500, width=28),
                                ft.Icon(
                                    ft.Icons.PLAYING_CARDS if is_current else ft.Icons.MUSIC_NOTE,
                                    color=ft.Colors.ORANGE_ACCENT if is_current else ft.Colors.GREY_400,
                                    size=20,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            stitle,
                                            size=14,
                                            weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
                                            color=ft.Colors.ORANGE_ACCENT if is_current else ft.Colors.WHITE,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            f"{sartist} • {sduration}",
                                            size=12,
                                            color=ft.Colors.GREY_400,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    expand=True,
                                    spacing=2,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                    icon_size=20,
                                    tooltip="Play",
                                    on_click=play_this,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE_ROUNDED,
                                    icon_size=18,
                                    icon_color=ft.Colors.GREY_500,
                                    tooltip="Remove",
                                    on_click=delete_this,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.Colors.SURFACE_CONTAINER if is_current else ft.Colors.SURFACE_CONTAINER_LOW,
                        border_radius=8,
                        padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                    )
                    items.append(item_row)

            playlist_list_view.controls = items
            page.update()

        def refresh_browser():
            path_text.value = f"/{current_path}"
            entries = manager.list_directory(current_path)
            items = []

            dirs = []
            files = []
            for entry in entries:
                if "directory" in entry:
                    dirs.append(entry)
                elif "file" in entry:
                    files.append(entry)

            # Sort alphabetically
            dirs.sort(key=lambda d: d.get("directory", "").lower())
            files.sort(key=lambda f: f.get("file", "").lower())

            if not dirs and not files:
                items.append(
                    ft.Container(
                        content=ft.Text("Empty directory", color=ft.Colors.GREY_400),
                        padding=20,
                        alignment=ft.Alignment(0, 0),
                    )
                )

            # Render directories
            for d in dirs:
                dir_path = d.get("directory", "")
                dir_name = dir_path.split("/")[-1]

                def enter_dir(e, path=dir_path):
                    nonlocal current_path
                    current_path = path
                    refresh_browser()

                def add_dir(e, path=dir_path):
                    manager.add_uri(path)
                    page.snack_bar = ft.SnackBar(ft.Text(f"Added '{dir_name}' to queue"))
                    page.snack_bar.open = True
                    page.update()

                item = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ft.Colors.AMBER_400),
                            ft.TextButton(
                                content=ft.Text(dir_name),
                                on_click=enter_dir,
                                expand=True,
                                style=ft.ButtonStyle(alignment=ft.Alignment(-1, 0)),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_ROUNDED,
                                tooltip="Add folder to queue",
                                on_click=add_dir,
                            ),
                        ],
                    ),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    border_radius=8,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                )
                items.append(item)

            # Render files
            for f in files:
                file_path = f.get("file", "")
                ftitle, fartist, _ = get_song_display(f)
                ftime = format_time(f.get("time", 0))

                def play_file(e, path=file_path):
                    manager.play_uri(path)
                    refresh_status()
                    page.snack_bar = ft.SnackBar(ft.Text("Playing song"))
                    page.snack_bar.open = True
                    page.update()

                def add_file(e, path=file_path):
                    manager.add_uri(path)
                    page.snack_bar = ft.SnackBar(ft.Text("Added to queue"))
                    page.snack_bar.open = True
                    page.update()

                item = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.AUDIO_FILE_ROUNDED, color=ft.Colors.GREY_400),
                            ft.Column(
                                controls=[
                                    ft.Text(ftitle, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, size=13),
                                    ft.Text(f"{fartist} • {ftime}", size=11, color=ft.Colors.GREY_500),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                tooltip="Play now",
                                on_click=play_file,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_ROUNDED,
                                tooltip="Add to queue",
                                on_click=add_file,
                            ),
                        ],
                    ),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    border_radius=8,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                )
                items.append(item)

            browser_list_view.controls = items
            page.update()

        # Add components to page
        page.appbar = app_bar
        page.navigation_bar = nav_bar
        page.add(
            ft.Stack(
                controls=[
                    player_view,
                    queue_view,
                    browser_view,
                ],
                expand=True,
            )
        )

        # Background polling task for MPD status
        async def poll_status():
            while True:
                try:
                    if nav_bar.selected_index == 0:
                        refresh_status()
                    await asyncio.sleep(1)
                except Exception:
                    await asyncio.sleep(2)

        page.run_task(poll_status)

        # Initial connect and refresh
        manager.connect()
        refresh_status()

    return main
