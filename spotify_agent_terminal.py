import os
import sys
import threading
import time
import msvcrt
import argparse
from datetime import timedelta
from io import BytesIO
from PIL import Image
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from config import SPOTIFY_CONFIG, GENIUS_ACCESS_TOKEN
from spotify_controller import SpotifyController


class SpotifyTerminalAgent:
    """Terminal-based Spotify Smart Agent"""

    def __init__(self, start_mode='resume', quit_mode='pause'):
        self.console = Console()
        self.controller = SpotifyController(SPOTIFY_CONFIG)
        self.running = False
        self.current_track = None
        self.lyrics = "No lyrics available"
        self.is_playing = False
        self.progress_ms = 0
        self.duration_ms = 1
        self.status_message = "Starting..."
        self.play_mode = "Normal"
        self.current_track_index = -1  # Track the current index in context_tracks for scrolling
        self.initial_load_done = False  # Track if we've done the initial track load

        # Behavior settings
        self.start_mode = start_mode  # 'resume' or 'pause'
        self.quit_mode = quit_mode    # 'pause' or 'resume'

        # For keyboard input
        self.command_input = ""
        self.input_mode = False

    def cleanup(self):
        """Cleanup on exit - pause or resume based on quit_mode"""
        try:
            if self.quit_mode == 'pause':
                if self.is_playing:
                    self.controller.pause()
                    self.console.print("[dim]Paused playback[/dim]")
            else:
                # quit_mode == 'resume', keep playing
                if not self.is_playing:
                    self.controller.resume()
                    self.console.print("[dim]Resuming playback[/dim]")
        except:
            pass  # Ignore errors during cleanup

    def authenticate(self):
        """Authenticate with Spotify and Genius"""
        self.console.print("\n[bold cyan]🎵 Spotify Smart Agent - Terminal Mode[/bold cyan]\n")
        self.console.print("Authenticating with Spotify...", style="yellow")

        if self.controller.authenticate():
            self.console.print("✓ Connected to Spotify", style="bold green")
            self.console.print("✓ LRCLIB lyrics enabled (real-time synced lyrics)", style="green")
            return True
        else:
            self.console.print("\n[bold red]✗ Authentication Failed[/bold red]")
            self.console.print("\nPlease update config.py with your Spotify credentials:")
            self.console.print("1. Go to https://developer.spotify.com/dashboard")
            self.console.print("2. Create an app and get Client ID & Secret")
            self.console.print("3. Update SPOTIFY_CONFIG in config.py\n")
            return False

    def start(self):
        """Start the terminal agent"""
        if not self.authenticate():
            return

        self.running = True
        self.status_message = "Ready! Type 'play' or use keyboard shortcuts"

        # Start update thread
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()

        # Start input thread
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

        # Display UI
        self.display_ui()

    def update_loop(self):
        """Background loop to update track info"""
        while self.running:
            try:
                track = self.controller.get_current_track()
                if track:
                    # Check if this is a new track OR first time loading
                    is_new_track = not self.current_track or self.current_track.get('uri') != track['uri']
                    force_initial_load = not self.initial_load_done

                    if is_new_track or force_initial_load:
                        # New track or initial load
                        self.current_track = track

                        # IMPORTANT: Update controller's current_track for update_context_tracks to work
                        self.controller.current_track = track

                        if force_initial_load:
                            self.status_message = "Loading track info..."

                        self.fetch_lyrics()

                        # Update context tracks (album or artist) - do it synchronously for initial load
                        if force_initial_load:
                            self.controller.update_context_tracks()
                            self.initial_load_done = True

                            # Handle paused track based on start_mode setting
                            if not track['is_playing']:
                                if self.start_mode == 'resume':
                                    self.status_message = "Resuming paused track..."
                                    time.sleep(0.5)
                                    self.controller.resume()
                                    time.sleep(0.5)
                                    self.status_message = "Resumed playback!"
                                else:
                                    self.status_message = "Track loaded (paused)"
                            else:
                                self.status_message = "Track info loaded!"
                        else:
                            threading.Thread(target=self.controller.update_context_tracks, daemon=True).start()

                        # Update current track index by finding it in context_tracks
                        # Wait a moment for context_tracks to populate if needed
                        if force_initial_load:
                            time.sleep(0.5)

                        track_uri = track.get('uri')
                        for i, ctx_track in enumerate(self.controller.current_context_tracks):
                            if ctx_track.get('uri') == track_uri:
                                self.current_track_index = i
                                break

                    self.progress_ms = track['progress_ms']
                    self.duration_ms = track['duration_ms']
                    self.is_playing = track['is_playing']

                    # Auto-next when track ends
                    if self.controller.is_track_ended():
                        time.sleep(1)
                        self.auto_next_track()

                elif not self.initial_load_done:
                    # No track playing on startup
                    self.status_message = "No track currently playing. Type 'play' to start."
                    self.initial_load_done = True

                time.sleep(1)

            except Exception as e:
                self.status_message = f"Update error: {str(e)}"
                time.sleep(2)

    def fetch_lyrics(self):
        """Fetch lyrics for current track"""
        def fetch():
            if self.current_track:
                artist_name = self.current_track['artists'][0]['name'] if self.current_track['artists'] else 'Unknown'
                self.lyrics = self.controller.get_lyrics(
                    self.current_track['name'],
                    artist_name,
                    self.current_track.get('duration_ms', 0)
                )

        threading.Thread(target=fetch, daemon=True).start()

    def display_ui(self):
        """Display the terminal UI with live updates"""
        try:
            with Live(self.generate_layout(), refresh_per_second=20, console=self.console, screen=False) as live:
                while self.running:
                    live.update(self.generate_layout())
                    time.sleep(0.05)  # Very fast refresh for responsive input display
        except KeyboardInterrupt:
            self.running = False
        finally:
            # Always cleanup on exit
            self.cleanup()
            self.console.print("\n\n[bold yellow]Goodbye! 👋[/bold yellow]\n")

    def generate_layout(self):
        """Generate the terminal layout"""
        layout = Layout()

        # Split into sections (balanced sizes)
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="controls", size=4),
            Layout(name="input", size=4)
        )

        # Header
        layout["header"].update(
            Panel(
                Text("🎵 SPOTIFY SMART AGENT", justify="center", style="bold cyan"),
                style="cyan"
            )
        )

        # Main content (split into left panel and lyrics)
        layout["main"].split_row(
            Layout(name="left_panel", ratio=4),
            Layout(name="lyrics", ratio=1)
        )

        # Left panel (track info + track list)
        layout["main"]["left_panel"].split_column(
            Layout(name="track_info", ratio=3),
            Layout(name="track_list", ratio=2)
        )

        layout["main"]["left_panel"]["track_info"].update(self.generate_track_info())
        layout["main"]["left_panel"]["track_list"].update(self.generate_track_list())
        layout["main"]["lyrics"].update(self.generate_lyrics_panel())

        # Controls
        layout["controls"].update(self.generate_controls_panel())

        # Command input box
        layout["input"].update(self.generate_input_panel())

        return layout

    def generate_track_info(self):
        """Generate track information panel with status"""
        if not self.current_track:
            # Show status even when no track is playing
            content = Group(
                Text("[dim]No track playing[/dim]"),
                Text(f"\n💬 {self.status_message}", style="cyan italic")
            )
            return Panel(
                content,
                title="[bold]Now Playing[/bold]",
                border_style="blue",
                box=box.ROUNDED
            )

        track = self.current_track

        # Create info table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Label", style="dim")
        table.add_column("Value", style="bold")

        table.add_row("🎵 Song", track['name'])
        table.add_row("🎤 Artist", ", ".join([artist['name'] for artist in track['artists']]))
        table.add_row("💿 Album", track['album']['name'])
        table.add_row("🔁 Mode", self.play_mode)

        # Enhanced progress bar with percentage and status
        progress_percent = (self.progress_ms / self.duration_ms * 100) if self.duration_ms > 0 else 0
        current_time = str(timedelta(milliseconds=self.progress_ms)).split('.')[0]
        total_time = str(timedelta(milliseconds=self.duration_ms)).split('.')[0]

        # Status with visual indicator
        status_icon = "▶️ Playing ♪" if self.is_playing else "⏸️ Paused"
        status_color = "bold green" if self.is_playing else "bold yellow"

        # Progress bar - using more compatible characters
        bar_length = 30
        filled_length = int(bar_length * progress_percent / 100)
        progress_bar = "━" * filled_length + "─" * (bar_length - filled_length)
        progress_text = f"⏱  {current_time} │{progress_bar}│ {total_time}  ({int(progress_percent)}%)"

        # Status message
        status_text = f"💬 {self.status_message}"

        # Combine everything using Group (reduced blank lines for compactness)
        content = Group(
            table,
            Text(""),  # Blank line
            Text(status_icon, style=status_color),
            Text(progress_text, style="cyan bold"),
            Text(""),  # Blank line
            Text(status_text, style="yellow italic")
        )

        return Panel(
            content,
            title="[bold]Now Playing[/bold]",
            border_style="green" if self.is_playing else "yellow",
            box=box.ROUNDED
        )

    def generate_track_list(self):
        """Generate track list panel (album or artist tracks) with smart scrolling"""
        if not self.controller.current_context_tracks:
            return Panel(
                "[dim]No track list available[/dim]",
                title="Track List",
                border_style="yellow",
                box=box.ROUNDED
            )

        tracks_text = Text()
        current_uri = self.current_track.get('uri') if self.current_track else None

        # Determine context type
        context_type = "Album"
        if self.current_track and self.current_track.get('album'):
            context_type = f"Album: {self.current_track['album']['name']}"
        elif self.current_track and self.current_track.get('artists') and len(self.current_track['artists']) > 0:
            artist_name = self.current_track['artists'][0]['name']
            context_type = f"Top Tracks: {artist_name}"

        # Find current track index by URI matching
        current_index = -1
        for i, track in enumerate(self.controller.current_context_tracks):
            if track.get('uri') == current_uri:
                current_index = i
                self.current_track_index = i  # Update the stored index
                break

        # If URI matching failed, use the explicitly stored index (from play_track_by_index)
        if current_index == -1 and self.current_track_index >= 0:
            current_index = self.current_track_index

        # Smart scrolling: ALWAYS center on current track in a small focused window
        total_tracks = len(self.controller.current_context_tracks)
        visible_tracks = 5  # Show 5 tracks at once (focused window that scrolls)

        # Only show all tracks if album is VERY small (3 or fewer tracks)
        if total_tracks <= 3:
            start_idx = 0
            end_idx = total_tracks
        elif current_index == -1:
            # No current track found, show first tracks
            start_idx = 0
            end_idx = min(visible_tracks, total_tracks)
        else:
            # ALWAYS CENTER on current track in a focused window
            # Try to show: [tracks before] + [current track] + [tracks after]
            tracks_before = visible_tracks // 2
            tracks_after = visible_tracks - tracks_before - 1  # -1 for current track itself

            # Calculate ideal window centered on current track
            start_idx = max(0, current_index - tracks_before)
            end_idx = min(total_tracks, current_index + tracks_after + 1)

            # Keep the window focused - don't expand to fill visible_tracks
            # Just show what fits around the current track

        # Show scroll indicator at top if there are tracks above
        if start_idx > 0:
            tracks_text.append(f"  ▲ {start_idx} more above...\n", style="dim cyan italic")

        # Show tracks in the window
        for i in range(start_idx, end_idx):
            track = self.controller.current_context_tracks[i]
            track_uri = track.get('uri', '')
            track_name = track.get('name', 'Unknown')

            # Get artist name
            artists = track.get('artists', [])
            artist_name = artists[0]['name'] if artists else 'Unknown'

            # Truncate long track names to fit
            max_name_length = 35
            if len(track_name) > max_name_length:
                track_name = track_name[:max_name_length-3] + "..."
            if len(artist_name) > 20:
                artist_name = artist_name[:17] + "..."

            # Highlight current track
            if track_uri == current_uri:
                tracks_text.append(f"▶ {i+1:2}. ", style="bold green")
                tracks_text.append(f"{track_name}", style="bold green")
                tracks_text.append(f" - {artist_name}\n", style="green")
            else:
                tracks_text.append(f"  {i+1:2}. ", style="dim")
                tracks_text.append(f"{track_name}", style="white")
                tracks_text.append(f" - {artist_name}\n", style="dim")

        # Show scroll indicator at bottom if there are tracks below
        if end_idx < total_tracks:
            tracks_text.append(f"  ▼ {total_tracks - end_idx} more below...\n", style="dim cyan italic")

        # Show total count and current position
        if current_index >= 0:
            tracks_text.append(f"\n[Showing {start_idx+1}-{end_idx} of {total_tracks} tracks | ▶ Playing #{current_index+1}]", style="dim cyan italic")
        else:
            tracks_text.append(f"\n[Showing {start_idx+1}-{end_idx} of {total_tracks} tracks]", style="dim italic")

        return Panel(
            tracks_text,
            title=f"[bold yellow]📋 {context_type}[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        )

    def generate_lyrics_panel(self):
        """Generate lyrics panel with real-time sync"""
        lyrics_text = Text()

        # If we have synced lyrics, show them with current line highlighted
        if self.controller.synced_lyrics:
            # Find current line index
            current_index = -1
            for i, (timestamp_ms, _) in enumerate(self.controller.synced_lyrics):
                if timestamp_ms <= self.progress_ms:
                    current_index = i

            # Show lyrics with context (few lines before and after)
            start_index = max(0, current_index - 3)
            end_index = min(len(self.controller.synced_lyrics), current_index + 10)

            for i in range(start_index, end_index):
                _, line_text = self.controller.synced_lyrics[i]

                if i == current_index:
                    # Highlight current line
                    lyrics_text.append("♪ ", style="bold cyan")
                    lyrics_text.append(line_text + "\n", style="bold green")
                elif i < current_index:
                    # Past lines (dimmed)
                    lyrics_text.append(line_text + "\n", style="dim")
                else:
                    # Upcoming lines (normal)
                    lyrics_text.append(line_text + "\n", style="white")

            if not lyrics_text.plain:
                lyrics_text.append("🎵 Synced lyrics ready...\n", style="dim italic")

        else:
            # Plain lyrics (no sync)
            lyrics_lines = self.lyrics.split('\n')[:25]
            for line in lyrics_lines:
                lyrics_text.append(line + "\n")

            if len(self.lyrics.split('\n')) > 25:
                lyrics_text.append("\n... (more lyrics available)", style="dim")

        return Panel(
            lyrics_text,
            title="[bold magenta]🎵 Lyrics (Real-time)[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        )

    def generate_controls_panel(self):
        """Generate controls panel"""
        controls_text = Text()

        # Compact format - all on fewer lines
        controls_text.append("⚡ Shortcuts: ", style="bold yellow")
        controls_text.append("Space=Play/Pause  ↑↓=Prev/Next  ←→=Seek±10s  Q=Quit\n", style="cyan")

        controls_text.append("⌨️  Commands: ", style="bold yellow")
        controls_text.append("[Number]=Jump  normal/shuffle=Mode  help=Help", style="cyan")

        return Panel(
            controls_text,
            title="[bold]⚡ Quick Controls[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )

    def generate_input_panel(self):
        """Generate command input panel"""
        input_text = Text()
        input_text.append("Type your command and press Enter:\n", style="dim italic")
        input_text.append("💬 > ", style="bold green")

        # Show the current input buffer
        if self.command_input:
            input_text.append(self.command_input, style="bold white")

        input_text.append("█", style="bold green blink")  # Blinking cursor

        input_text.append("\n\n", style="dim")
        input_text.append("Examples: ", style="dim")
        input_text.append("play album folklore | 15 (jump to track) | help", style="cyan dim")

        return Panel(
            input_text,
            title="[bold cyan]⌨️  Command Input[/bold cyan]",
            border_style="green",
            box=box.ROUNDED
        )

    def input_loop(self):
        """Handle user input with real-time keyboard capture"""
        while self.running:
            try:
                if msvcrt.kbhit():
                    # Get the character
                    char = msvcrt.getch()

                    # Handle special keys and shortcuts IMMEDIATELY (no Enter needed)
                    if char == b' ':  # Space
                        # If already typing a command, add space to buffer
                        if self.command_input:
                            self.command_input += ' '
                            self.status_message = "Typing command..."
                        else:
                            # Otherwise, use as play/pause shortcut
                            self.toggle_play_pause()
                        continue

                    elif char == b'\x03':  # Ctrl+C
                        self.running = False
                        break

                    elif char == b'\xe0':  # Special keys (arrows, etc.)
                        # Read the second byte for arrow keys
                        char2 = msvcrt.getch()
                        if char2 == b'H':  # Up arrow - Previous track
                            self.previous_track()
                        elif char2 == b'P':  # Down arrow - Next track
                            self.next_track()
                        elif char2 == b'K':  # Left arrow - Seek backward
                            self.seek_backward()
                        elif char2 == b'M':  # Right arrow - Seek forward
                            self.seek_forward()
                        continue

                    # Handle single-key shortcuts IMMEDIATELY (removed 1-4 to avoid conflict with track numbers)
                    elif char in [b'q', b'Q']:
                        try:
                            decoded = char.decode('utf-8').lower()
                            if decoded == 'q':
                                self.running = False
                        except:
                            pass
                        continue

                    # Handle command input (requires Enter)
                    elif char == b'\r':  # Enter key
                        if self.command_input.strip():
                            command = self.command_input.strip()
                            self.command_input = ""
                            self.handle_command(command)

                    elif char == b'\x08':  # Backspace
                        if self.command_input:
                            self.command_input = self.command_input[:-1]

                    else:
                        # Regular character - add to command buffer
                        try:
                            decoded = char.decode('utf-8')
                            # Only add printable characters
                            if decoded.isprintable() or decoded == ' ':
                                self.command_input += decoded
                                self.status_message = "Typing command..."
                        except:
                            pass  # Silently ignore decode errors

                time.sleep(0.05)  # Small delay to prevent CPU overuse

            except Exception as e:
                self.status_message = f"Input error: {str(e)}"
                time.sleep(1)

    def handle_command(self, command):
        """Handle text commands"""
        command = command.lower().strip()

        if not command:
            return

        if command == 'help':
            self.show_help()
        elif command == 'quit' or command == 'exit' or command == 'q':
            self.status_message = "Exiting..."
            self.running = False
        elif command.startswith('play'):
            self.process_play_command(command)
        elif command == 'pause':
            self.controller.pause()
            self.status_message = "Paused"
        elif command == 'resume':
            self.controller.resume()
            self.status_message = "Resumed"
        elif command == 'next':
            self.next_track()
        elif command == 'prev' or command == 'previous':
            self.previous_track()
        elif command in ['normal', 'repeat', 'repeat one', 'repeat all', 'shuffle']:
            mode_map = {
                'normal': 'normal',
                'repeat': 'repeat_all',
                'repeat one': 'repeat_one',
                'repeat all': 'repeat_all',
                'shuffle': 'shuffle'
            }
            self.set_mode(mode_map[command])
        elif command.isdigit():
            # Play track by index number
            self.play_track_by_index(int(command))
        else:
            self.status_message = f"Unknown command: {command}. Type 'help' for commands."

    def process_play_command(self, command):
        """Process play command"""
        self.status_message = f"Processing: {command}"

        cmd_result = self.controller.parse_command(command)

        threading.Thread(
            target=self._execute_play_command,
            args=(cmd_result,),
            daemon=True
        ).start()

    def _execute_play_command(self, cmd):
        """Execute play command in background"""
        try:
            # Handle song playback
            if cmd.get('action') == 'play_song':
                song_name = cmd.get('song')
                artist_name = cmd.get('artist')
                if song_name:
                    track = self.controller.play_song(song_name, artist_name)
                    if track:
                        artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                        self.status_message = f"Playing: {track['name']} by {artist}"
                    else:
                        self.status_message = f"Song not found: {song_name}"
                else:
                    self.status_message = "No song name provided"

            # Handle album playback
            elif cmd.get('action') == 'play_album':
                album_name = cmd.get('album')
                artist_name = cmd.get('artist')
                if album_name:
                    track = self.controller.play_album(album_name, artist_name)
                    if track:
                        self.status_message = f"Playing album: {album_name}"
                    else:
                        self.status_message = f"Album not found: {album_name}"
                else:
                    self.status_message = "No album name provided"

            else:
                # Handle random track playback
                track = self.controller.play_random_track(
                    artist=cmd.get('artist'),
                    genre=cmd.get('genre')
                )

                if track:
                    msg = f"Playing: {track['name']}"
                    if cmd.get('artist'):
                        msg += f" (Artist: {cmd['artist']})"
                    if cmd.get('genre'):
                        msg += f" (Genre: {cmd['genre']})"
                    self.status_message = msg
                else:
                    self.status_message = "No tracks found"

        except Exception as e:
            self.status_message = f"Error: {str(e)}"

    def toggle_play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.controller.pause()
            self.status_message = "Paused"
        else:
            self.controller.resume()
            self.status_message = "Playing"

    def next_track(self):
        """Next track"""
        self.controller.next_track()
        self.status_message = "Next track"

    def previous_track(self):
        """Previous track"""
        self.controller.previous_track()
        self.status_message = "Previous track"

    def seek_forward(self):
        """Seek forward 10 seconds"""
        self.controller.seek_forward(10)
        self.status_message = "⏩ Forward 10s"

    def seek_backward(self):
        """Seek backward 10 seconds"""
        self.controller.seek_backward(10)
        self.status_message = "⏪ Backward 10s"

    def auto_next_track(self):
        """Auto-play next track based on play mode"""
        mode = self.controller.play_mode

        # For normal and repeat_all modes, manually play next track from context list
        if mode in ['normal', 'repeat_all'] and self.controller.current_context_tracks:
            if self.current_track_index >= 0:
                next_index = self.current_track_index + 1
                total_tracks = len(self.controller.current_context_tracks)

                # For repeat_all, loop back to start; for normal, pause
                if next_index >= total_tracks:
                    if mode == 'repeat_all':
                        next_index = 0
                        self.status_message = "Looping back to first track..."
                    else:
                        # Normal mode: pause at end of album
                        self.controller.pause()
                        self.status_message = "Album finished - Paused"
                        return

                # Play next track (1-based for user)
                self.play_track_by_index(next_index + 1)
                return

        # Fallback to controller's next_track for other modes
        self.controller.next_track()
        self.status_message = f"Auto-playing next track (mode: {mode})"

    def set_mode(self, mode):
        """Set play mode"""
        self.controller.set_play_mode(mode)
        mode_names = {
            'normal': 'Normal',
            'repeat_one': 'Repeat One',
            'repeat_all': 'Repeat All',
            'shuffle': 'Shuffle'
        }
        self.play_mode = mode_names.get(mode, 'Normal')
        self.status_message = f"Play mode: {self.play_mode}"

    def play_track_by_index(self, index):
        """Play track by its index in the current track list"""
        if not self.controller.current_context_tracks:
            self.status_message = "No track list available. Play an album or song first."
            return

        # Convert to 0-based index (user types 1-based)
        track_index = index - 1

        if track_index < 0 or track_index >= len(self.controller.current_context_tracks):
            self.status_message = f"Invalid track number. Please enter 1-{len(self.controller.current_context_tracks)}"
            return

        # Get the track at the specified index
        track = self.controller.current_context_tracks[track_index]
        track_uri = track.get('uri')
        track_name = track.get('name', 'Unknown')
        artists = track.get('artists', [])
        artist_name = artists[0]['name'] if artists else 'Unknown'

        if not track_uri:
            self.status_message = "Invalid track at that index"
            return

        # Play the track
        try:
            # Store the index we're trying to play (IMMEDIATELY for instant scrolling)
            self.current_track_index = track_index

            # Try to play within album context if available
            played = False
            if self.current_track and self.current_track.get('album'):
                album = self.current_track['album']
                if album.get('uri'):
                    # Play within album context with offset (use URI for reliability)
                    try:
                        devices = self.controller.get_available_devices()
                        if devices:
                            device_id = devices[0]['id']
                            self.controller.sp.start_playback(
                                device_id=device_id,
                                context_uri=album['uri'],
                                offset={"uri": track_uri}
                            )
                            played = True
                            self.status_message = f"▶ Playing track #{index} in album context"
                    except Exception as e:
                        self.status_message = f"Context play failed: {e}"
                        print(f"Failed to play with context: {e}")

            # Fallback to single track play if context play failed
            if not played:
                self.controller._play_track(track_uri)
                self.status_message = f"▶ Playing track #{index} (single track mode)"

            # Update status after initial message
            time.sleep(0.3)
            self.status_message = f"▶ Playing track #{index}: {track_name} by {artist_name}"

            # Wait for Spotify to update playback state and retry until we get the correct track
            max_retries = 5
            for retry in range(max_retries):
                time.sleep(0.5)
                updated_track = self.controller.get_current_track()

                # Check if we got the correct track
                if updated_track and updated_track.get('uri') == track_uri:
                    self.current_track = updated_track
                    # Trigger lyrics fetch for new track
                    self.fetch_lyrics()
                    break

                # If last retry, update anyway
                if retry == max_retries - 1:
                    self.current_track = updated_track

        except Exception as e:
            self.status_message = f"Error playing track: {str(e)}"

    def show_help(self):
        """Show help message"""
        help_text = """
Commands:
  play                         - Play random song
  play [artist]                - Play random song by artist
  play [genre]                 - Play random song from genre
  play song [name]             - Play a specific song
  play song [name] by [artist] - Play song by specific artist
  play album [name]            - Play an album
  play album [name] by [artist]- Play album by specific artist
  [number]                     - Jump to track # from track list (e.g., 5, 12, 15)
  pause                        - Pause playback
  resume                       - Resume playback
  next / prev                  - Next/Previous track
  normal / shuffle / repeat    - Change play mode
  help                         - Show this help
  quit / exit / q              - Exit agent

Examples:
  play album folklore          - Play an album
  15                           - Jump to track #15 from current list
  3                            - Jump to track #3
  shuffle                      - Enable shuffle mode
  normal                       - Return to normal playback
  play song Yesterday by The Beatles
        """
        self.status_message = "Help displayed (see terminal output)"
        self.console.print(help_text, style="cyan")


def main():
    """Main entry point for terminal mode"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Spotify Smart Agent - Terminal Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python spotify_agent_terminal.py                    # Default: resume on start, pause on quit
  python spotify_agent_terminal.py --start-mode pause # Start paused
  python spotify_agent_terminal.py --quit-mode resume # Keep playing on quit
  python spotify_agent_terminal.py --start-mode pause --quit-mode resume
        """
    )

    parser.add_argument(
        '--start-mode',
        choices=['resume', 'pause'],
        default='resume',
        help='Behavior when starting with a paused track (default: resume)'
    )

    parser.add_argument(
        '--quit-mode',
        choices=['pause', 'resume'],
        default='pause',
        help='Behavior when quitting (default: pause)'
    )

    args = parser.parse_args()

    # Create agent with specified modes
    agent = SpotifyTerminalAgent(start_mode=args.start_mode, quit_mode=args.quit_mode)

    try:
        agent.start()
    except KeyboardInterrupt:
        agent.running = False
        agent.cleanup()
        agent.console.print("\n\n[bold yellow]Shutting down... Goodbye! 👋[/bold yellow]\n")
    except Exception as e:
        agent.running = False
        agent.cleanup()
        agent.console.print(f"\n[bold red]Error: {e}[/bold red]\n")


if __name__ == "__main__":
    main()
