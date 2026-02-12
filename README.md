# 🎵 Spotify Smart Agent

A desktop application for Windows that intelligently plays music from Spotify with voice-like commands, displays lyrics, album art, and provides full playback control.

**Two Modes Available:**
- **🖼️ GUI Mode** - Beautiful graphical interface with album art (Not fully tested yet)
- **🖥️ Terminal Mode** - Text-based interface for terminal lovers (NEW!)

## Features

✅ **Smart Music Selection**
- Random shuffle from **Spotify's entire catalog** (not your local library)
- Play by specific artist: "Play Coldplay"
- Play by genre: "Play rock music"
- Combine: "Play Beatles and rock"

✅ **Rich Display**
- Album artwork (300x300 thumbnail)
- Song name, artist(s), album name
- Real-time lyrics (via Genius API)
- Progress bar with time display

✅ **Full Playback Control**
- Play/Pause
- Next/Previous track
- Seek to any position
- Volume control

✅ **Play Modes**
- Normal playback
- Repeat One (loop current song)
- Repeat All (loop playlist)
- Shuffle mode

✅ **Auto-Continuation**
- Automatically plays next random song when current ends
- Remembers your last command (artist/genre preference)

## Requirements

- **Windows 10/11**
- **Python 3.8 or higher**
- **Spotify Premium Account** (required for playback control API)
- **Spotify Developer Account** (free - for API credentials)

## Installation

### Step 1: Install Python Dependencies

Open Command Prompt in the `spotify_agent` folder and run:

```bash
pip install -r requirements.txt
```

### Step 2: Get Spotify API Credentials

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click **"Create App"**
4. Fill in:
   - App name: "Spotify Smart Agent"
   - App description: "Personal music player"
   - Redirect URI: `http://localhost:8888/callback`
5. Accept terms and click **"Save"**
6. Copy your **Client ID** and **Client Secret**

### Step 3: (Optional) Get Genius API Token for Lyrics

1. Go to https://genius.com/api-clients
2. Create a new API client
3. Generate an **Access Token**

### Step 4: Configure the App

Open `config.py` and replace placeholders:

```python
SPOTIFY_CONFIG = {
    'client_id': 'paste_your_client_id_here',
    'client_secret': 'paste_your_client_secret_here',
    'redirect_uri': 'http://localhost:8888/callback',
    'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing '
             'user-library-read playlist-read-private streaming'
}

# Optional - for lyrics
GENIUS_ACCESS_TOKEN = 'paste_your_genius_token_here'
```

## Usage

### Choosing Your Mode

**🖼️ GUI Mode** (Graphical with album art):
```bash
python spotify_agent_gui.py
# Or double-click: run_agent.bat
```

**🖥️ Terminal Mode** (Text-based, lightweight):
```bash
python spotify_agent_terminal.py
# Or double-click: run_terminal.bat

# With options (NEW!):
python spotify_agent_terminal.py --start-mode pause --quit-mode resume
```

### Starting the Agent (Both Modes)

1. Open Spotify desktop app or web player on your device
2. Start playing any song (then you can pause it)
3. Run the agent (choose mode above)
4. On first run, a browser window will open asking you to authorize the app
5. Click "Agree" and you'll be redirected (the browser will show an error page - that's expected)
6. The agent should now show "Connected to Spotify ✓"

**📖 For detailed Terminal Mode guide, see [TERMINAL_MODE.md](TERMINAL_MODE.md)**

### Using Commands

Type commands in the input box at the bottom:

**Examples:**
```
play                          → Random song from your library
play Coldplay                 → Random Coldplay song
play rock                     → Random rock song
play Beatles                  → Random Beatles song
play Taylor Swift             → Random Taylor Swift song
play jazz                     → Random jazz song
```

**Supported genres:**
rock, pop, jazz, classical, hip hop, rap, electronic, country, metal, indie, blues

### Playback Controls

- **▶️/⏸️ Button**: Play/Pause
- **⏮ Button**: Previous track
- **⏭ Button**: Next track
- **Progress Bar**: Click or drag to seek
- **Volume Slider**: Adjust playback volume

### Play Modes

- **🔁 Repeat All**: Loop through your playlist/search results
- **🔂 Repeat One**: Repeat current song indefinitely
- **🔀 Shuffle**: Shuffle playback order
- **▶️ Normal**: Standard playback

### Auto-Play Feature

When a song finishes:
- Agent automatically plays another random song
- Uses your last command criteria (artist/genre)
- If no command given, plays from your library

## Troubleshooting

### "Authentication failed"
- Make sure you've updated `config.py` with correct credentials
- Check that redirect URI is exactly: `http://localhost:8888/callback`
- Verify Spotify Premium account is active

### "No devices available"
- Make sure Spotify is open and playing (or paused) on your device
- Refresh available devices in Spotify settings

### "Lyrics not available"
- Add Genius API token to `config.py`
- Some songs may not have lyrics in Genius database

### "Can't control playback"
- Spotify Premium is required for API playback control
- Make sure you're not using Spotify Free

### Connection issues
- Check your internet connection
- Restart Spotify application
- Re-authenticate by deleting `.cache` file and restarting agent

## File Structure

```
spotify_agent/
├── config.py                 # Configuration (API credentials)
├── spotify_controller.py     # Spotify API logic
├── spotify_agent_gui.py      # Main GUI application
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Technical Details

**APIs Used:**
- Spotify Web API (via spotipy)
- Genius API (for lyrics)

**Libraries:**
- `spotipy`: Spotify API wrapper
- `tkinter`: GUI framework (built into Python)
- `Pillow`: Image processing for album art
- `lyricsgenius`: Genius API wrapper
- `requests`: HTTP requests

**Architecture:**
- Main thread: GUI and user interaction
- Background thread: Track info updates and progress monitoring
- Separate threads: Album art loading, lyrics fetching

## Keyboard Shortcuts

- **Enter** (in command box): Execute command
- **Alt+F4**: Close application

## Tips & Tricks

1. **Build Playlists**: Use consistent artist/genre commands to create themed listening sessions
2. **Discover Music**: Use genre commands without artist to explore new music
3. **Party Mode**: Set to Shuffle + Repeat All for continuous playback
4. **Focus Mode**: Repeat One for concentration with one song
5. **Background Agent**: Minimize window - it keeps running and playing music

## Limitations

- Requires Spotify Premium (API limitation)
- Lyrics depend on Genius database availability
- Genre detection is keyword-based (simple matching)
- Must have Spotify open on at least one device

## Future Enhancements

Potential features for future versions:
- Voice command support
- Playlist creation from agent
- Music recommendations
- Mood-based selection
- Integration with more lyrics sources
- System tray icon support
- Global hotkeys

## License

For personal use only. Spotify API and Genius API usage subject to their respective terms of service.

## Credits

Built with ❤️ using:
- Spotify Web API
- Genius Lyrics API
- Python, Tkinter, and open-source libraries

---

**Enjoy your smart music experience! 🎵**
