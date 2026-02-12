import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import io
import threading
import time
from config import SPOTIFY_CONFIG, GENIUS_ACCESS_TOKEN, UI_CONFIG
from spotify_controller import SpotifyController


class SpotifyAgentGUI:
    """Main GUI application for Spotify Smart Agent"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Spotify Smart Agent")
        self.root.geometry(f"{UI_CONFIG['window_width']}x{UI_CONFIG['window_height']}")
        self.root.configure(bg=UI_CONFIG['bg_color'])

        # Initialize controller
        self.controller = SpotifyController(SPOTIFY_CONFIG)
        self.running = False
        self.update_thread = None

        # UI Variables
        self.current_track_info = None
        self.album_art_image = None
        self.is_playing = False
        self.progress_ms = 0
        self.duration_ms = 1

        self.setup_ui()
        self.authenticate()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=UI_CONFIG['bg_color'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="🎵 Spotify Smart Agent",
            font=(UI_CONFIG['font_family'], 24, 'bold'),
            bg=UI_CONFIG['bg_color'],
            fg=UI_CONFIG['accent_color']
        )
        title_label.pack(pady=(0, 20))

        # Album Art
        self.album_art_label = tk.Label(
            main_frame,
            bg=UI_CONFIG['bg_color'],
            width=UI_CONFIG['album_art_size'],
            height=UI_CONFIG['album_art_size']
        )
        self.album_art_label.pack(pady=10)

        # Track Info Frame
        info_frame = tk.Frame(main_frame, bg=UI_CONFIG['bg_color'])
        info_frame.pack(pady=10)

        self.track_name_label = tk.Label(
            info_frame,
            text="No track playing",
            font=(UI_CONFIG['font_family'], 18, 'bold'),
            bg=UI_CONFIG['bg_color'],
            fg=UI_CONFIG['fg_color']
        )
        self.track_name_label.pack()

        self.artist_label = tk.Label(
            info_frame,
            text="",
            font=(UI_CONFIG['font_family'], 14),
            bg=UI_CONFIG['bg_color'],
            fg='#b3b3b3'
        )
        self.artist_label.pack()

        self.album_label = tk.Label(
            info_frame,
            text="",
            font=(UI_CONFIG['font_family'], 12),
            bg=UI_CONFIG['bg_color'],
            fg='#808080'
        )
        self.album_label.pack()

        # Progress Bar
        progress_frame = tk.Frame(main_frame, bg=UI_CONFIG['bg_color'])
        progress_frame.pack(pady=15, fill=tk.X)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.on_progress_change
        )
        self.progress_bar.pack(fill=tk.X, padx=10)

        self.time_label = tk.Label(
            progress_frame,
            text="0:00 / 0:00",
            font=(UI_CONFIG['font_family'], 10),
            bg=UI_CONFIG['bg_color'],
            fg='#b3b3b3'
        )
        self.time_label.pack()

        # Playback Controls
        controls_frame = tk.Frame(main_frame, bg=UI_CONFIG['bg_color'])
        controls_frame.pack(pady=15)

        btn_style = {
            'font': (UI_CONFIG['font_family'], 16),
            'bg': UI_CONFIG['accent_color'],
            'fg': 'white',
            'relief': tk.FLAT,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }

        self.prev_btn = tk.Button(controls_frame, text="⏮", command=self.previous_track, **btn_style)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.play_pause_btn = tk.Button(controls_frame, text="▶️", command=self.toggle_play_pause, **btn_style)
        self.play_pause_btn.grid(row=0, column=1, padx=5)

        self.next_btn = tk.Button(controls_frame, text="⏭", command=self.next_track, **btn_style)
        self.next_btn.grid(row=0, column=2, padx=5)

        # Play Mode Buttons
        mode_frame = tk.Frame(main_frame, bg=UI_CONFIG['bg_color'])
        mode_frame.pack(pady=10)

        mode_btn_style = {
            'font': (UI_CONFIG['font_family'], 12),
            'bg': '#282828',
            'fg': 'white',
            'relief': tk.FLAT,
            'padx': 10,
            'pady': 5,
            'cursor': 'hand2'
        }

        tk.Button(mode_frame, text="🔁 Repeat All", command=lambda: self.set_mode('repeat_all'), **mode_btn_style).grid(row=0, column=0, padx=3)
        tk.Button(mode_frame, text="🔂 Repeat One", command=lambda: self.set_mode('repeat_one'), **mode_btn_style).grid(row=0, column=1, padx=3)
        tk.Button(mode_frame, text="🔀 Shuffle", command=lambda: self.set_mode('shuffle'), **mode_btn_style).grid(row=0, column=2, padx=3)
        tk.Button(mode_frame, text="▶️ Normal", command=lambda: self.set_mode('normal'), **mode_btn_style).grid(row=0, column=3, padx=3)

        self.mode_label = tk.Label(
            mode_frame,
            text="Mode: Normal",
            font=(UI_CONFIG['font_family'], 10),
            bg=UI_CONFIG['bg_color'],
            fg='#b3b3b3'
        )
        self.mode_label.grid(row=1, column=0, columnspan=4, pady=5)

        # Volume Control
        volume_frame = tk.Frame(main_frame, bg=UI_CONFIG['bg_color'])
        volume_frame.pack(pady=10)

        tk.Label(volume_frame, text="🔊 Volume:", bg=UI_CONFIG['bg_color'], fg='#b3b3b3').pack(side=tk.LEFT, padx=5)

        self.volume_var = tk.IntVar(value=50)
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.on_volume_change,
            length=200
        )
        volume_scale.pack(side=tk.LEFT, padx=5)

        self.volume_label = tk.Label(volume_frame, text="50%", bg=UI_CONFIG['bg_color'], fg='#b3b3b3')
        self.volume_label.pack(side=tk.LEFT, padx=5)

        # Command Input
        command_frame = tk.Frame(main_frame, bg=UI_CONFIG['bg_color'])
        command_frame.pack(pady=15, fill=tk.X)

        tk.Label(
            command_frame,
            text="Command:",
            font=(UI_CONFIG['font_family'], 12),
            bg=UI_CONFIG['bg_color'],
            fg='#b3b3b3'
        ).pack(side=tk.LEFT, padx=5)

        self.command_entry = tk.Entry(
            command_frame,
            font=(UI_CONFIG['font_family'], 12),
            bg='#282828',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.command_entry.bind('<Return>', lambda e: self.process_command())

        tk.Button(
            command_frame,
            text="Go",
            command=self.process_command,
            bg=UI_CONFIG['accent_color'],
            fg='white',
            font=(UI_CONFIG['font_family'], 12),
            relief=tk.FLAT,
            padx=20,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)

        # Lyrics Display
        lyrics_label = tk.Label(
            main_frame,
            text="Lyrics:",
            font=(UI_CONFIG['font_family'], 12, 'bold'),
            bg=UI_CONFIG['bg_color'],
            fg='#b3b3b3'
        )
        lyrics_label.pack(pady=(10, 5))

        self.lyrics_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            font=(UI_CONFIG['font_family'], 10),
            bg='#282828',
            fg='white',
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.lyrics_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Status Bar
        self.status_label = tk.Label(
            self.root,
            text="Status: Not authenticated",
            font=(UI_CONFIG['font_family'], 9),
            bg='#282828',
            fg='#b3b3b3',
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def authenticate(self):
        """Authenticate with Spotify and Genius"""
        try:
            if self.controller.authenticate():
                self.status_label.config(text="Status: Connected to Spotify ✓", fg=UI_CONFIG['accent_color'])
                self.running = True
                self.start_update_thread()

                # Try to authenticate with Genius
                if GENIUS_ACCESS_TOKEN and GENIUS_ACCESS_TOKEN != 'YOUR_GENIUS_TOKEN_HERE':
                    self.controller.authenticate_genius(GENIUS_ACCESS_TOKEN)
            else:
                self.status_label.config(text="Status: Authentication failed. Check config.py", fg='#ff4444')
                messagebox.showerror(
                    "Authentication Error",
                    "Failed to authenticate with Spotify.\n\n"
                    "Please update config.py with your credentials:\n"
                    "1. Go to https://developer.spotify.com/dashboard\n"
                    "2. Create an app and get Client ID & Secret\n"
                    "3. Update SPOTIFY_CONFIG in config.py"
                )
        except Exception as e:
            self.status_label.config(text=f"Status: Error - {str(e)}", fg='#ff4444')

    def start_update_thread(self):
        """Start background thread for updating UI"""
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def update_loop(self):
        """Background loop to update track info and progress"""
        while self.running:
            try:
                # Update current track info
                track = self.controller.get_current_track()
                if track:
                    if not self.current_track_info or self.current_track_info['uri'] != track['uri']:
                        # New track started
                        self.current_track_info = track
                        self.root.after(0, self.update_track_display, track)
                        self.root.after(0, self.fetch_and_display_lyrics, track)

                    # Update progress
                    self.progress_ms = track['progress_ms']
                    self.duration_ms = track['duration_ms']
                    self.is_playing = track['is_playing']
                    self.root.after(0, self.update_progress)

                    # Update play/pause button
                    button_text = "⏸️" if self.is_playing else "▶️"
                    self.root.after(0, self.play_pause_btn.config, {'text': button_text})

                    # Check if track ended and auto-play next
                    if self.controller.is_track_ended():
                        time.sleep(1)
                        self.root.after(0, self.auto_next_track)

                time.sleep(1)  # Update every second

            except Exception as e:
                print(f"Update loop error: {e}")
                time.sleep(2)

    def update_track_display(self, track):
        """Update UI with current track info"""
        self.track_name_label.config(text=track['name'])
        self.artist_label.config(text=", ".join([artist['name'] for artist in track['artists']]))
        self.album_label.config(text=f"Album: {track['album']['name']}")

        # Download and display album art
        if track['album_art']:
            threading.Thread(target=self.load_album_art, args=(track['album_art'],), daemon=True).start()

    def load_album_art(self, url):
        """Load album artwork from URL"""
        try:
            image_data = self.controller.download_album_art(url)
            if image_data:
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((UI_CONFIG['album_art_size'], UI_CONFIG['album_art_size']), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                self.album_art_image = photo  # Keep reference
                self.root.after(0, self.album_art_label.config, {'image': photo})
        except Exception as e:
            print(f"Error loading album art: {e}")

    def fetch_and_display_lyrics(self, track):
        """Fetch and display lyrics"""
        def fetch():
            artist_name = track['artists'][0]['name'] if track['artists'] else 'Unknown'
            lyrics = self.controller.get_lyrics(track['name'], artist_name)
            self.root.after(0, self.display_lyrics, lyrics)

        threading.Thread(target=fetch, daemon=True).start()

    def display_lyrics(self, lyrics):
        """Display lyrics in text widget"""
        self.lyrics_text.delete(1.0, tk.END)
        self.lyrics_text.insert(1.0, lyrics)

    def update_progress(self):
        """Update progress bar and time label"""
        if self.duration_ms > 0:
            progress_percent = (self.progress_ms / self.duration_ms) * 100
            self.progress_var.set(progress_percent)

            current_min = self.progress_ms // 60000
            current_sec = (self.progress_ms % 60000) // 1000
            total_min = self.duration_ms // 60000
            total_sec = (self.duration_ms % 60000) // 1000

            self.time_label.config(text=f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}")

    def on_progress_change(self, value):
        """Handle progress bar drag"""
        # Only seek if user is dragging (not if auto-updating)
        if self.duration_ms > 0:
            new_position = int((float(value) / 100) * self.duration_ms)
            # Add small delay to avoid too many API calls
            self.root.after(500, lambda: self.controller.seek(new_position))

    def on_volume_change(self, value):
        """Handle volume change"""
        volume = int(float(value))
        self.volume_label.config(text=f"{volume}%")
        self.controller.set_volume(volume)

    def toggle_play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.controller.pause()
        else:
            self.controller.resume()

    def previous_track(self):
        """Go to previous track"""
        self.controller.previous_track()

    def next_track(self):
        """Go to next track"""
        self.controller.next_track()

    def auto_next_track(self):
        """Automatically play next track when current ends"""
        # Parse last command or play random
        if hasattr(self, 'last_command_result'):
            cmd = self.last_command_result
            self.controller.play_random_track(artist=cmd.get('artist'), genre=cmd.get('genre'))
        else:
            self.controller.play_random_track()

    def set_mode(self, mode):
        """Set playback mode"""
        self.controller.set_play_mode(mode)
        mode_names = {
            'normal': 'Normal',
            'repeat_one': 'Repeat One',
            'repeat_all': 'Repeat All',
            'shuffle': 'Shuffle'
        }
        self.mode_label.config(text=f"Mode: {mode_names.get(mode, 'Normal')}")
        self.status_label.config(text=f"Status: Play mode set to {mode_names.get(mode, 'Normal')}")

    def process_command(self):
        """Process user command"""
        command = self.command_entry.get().strip()
        if not command:
            return

        self.status_label.config(text=f"Processing: {command}")

        # Parse command
        cmd_result = self.controller.parse_command(command)
        self.last_command_result = cmd_result

        # Execute command
        threading.Thread(
            target=self._execute_command,
            args=(cmd_result,),
            daemon=True
        ).start()

        self.command_entry.delete(0, tk.END)

    def _execute_command(self, cmd):
        """Execute parsed command in background"""
        try:
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
                self.root.after(0, self.status_label.config, {'text': f"Status: {msg}"})
            else:
                self.root.after(0, self.status_label.config, {'text': "Status: No tracks found"})

        except Exception as e:
            self.root.after(0, self.status_label.config, {'text': f"Status: Error - {str(e)}"})

    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SpotifyAgentGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
