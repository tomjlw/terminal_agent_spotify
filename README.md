# 🎵 Spotify Smart Agent

A terminal-based spotify agent that intelligently plays music from Spotify with voice-like commands, displays lyrics and provides full playback control.

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
   
### Step 3: Configure the App

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
Make sure you have either Spotify PC/web app run in backgrounds before running terminal scripts!

### Choosing Your Mode

**🖼️ GUI Mode** (Graphical with album art, not completed yet):
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

# 🖥️ Terminal Mode Guide

## Features

✅ **Full-Featured Terminal UI**
- Real-time track information display with progress bar and percentage
- Live lyrics synchronized with current song (real-time highlighting)
- Scrollable track list showing current album/playlist
- Jump to any track by typing its number
- Color-coded panels (song info, lyrics, controls, status)
- No GUI window needed - everything in terminal!

✅ **All Controls Available**
- Keyboard shortcuts for instant actions (no Enter needed)
- Text commands for complex operations
- Play/Pause, Next/Previous, Seek ±10 seconds
- Play mode switching (Normal, Repeat One, Repeat All, Shuffle)
- Volume control via Spotify app

✅ **Smart Playback**
- Auto-continues to next track in album (Normal mode)
- Loops album continuously (Repeat All mode)
- Pauses at album end (Normal mode)
- Maintains album context for seamless playback

✅ **Beautiful Display**
- Powered by `rich` library (beautiful terminal formatting)
- Animated progress bars with time and percentage
- Color-coded status messages
- Auto-refreshing display (20x per second for smooth updates)

## Starting Terminal Mode

### Quick Start (Windows)

Double-click: **`run_terminal.bat`**

### Command Line

```bash
cd C:\Users\liwenj\spotify_agent
python spotify_agent_terminal.py
```

### Command-Line Arguments (NEW!)

Control startup and quit behavior:

```bash
# Default: Resume paused tracks on start, pause on quit
python spotify_agent_terminal.py

# Start with track paused (don't auto-resume)
python spotify_agent_terminal.py --start-mode pause

# Keep playing on quit (don't auto-pause)
python spotify_agent_terminal.py --quit-mode resume

# Both options
python spotify_agent_terminal.py --start-mode pause --quit-mode resume

# See all options
python spotify_agent_terminal.py --help
```

**Arguments:**
- `--start-mode [resume|pause]` - Resume or keep paused on startup (default: resume)
- `--quit-mode [pause|resume]` - Pause or keep playing on quit (default: pause)

## Terminal UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│                    🎵 SPOTIFY SMART AGENT                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────── Now Playing ─────┐  ┌────────── Lyrics ──────────────┐ │
│  │ 🎵 Song   │ Karma       │  │ [00:45] Karma is my boyfriend │ │
│  │ 🎤 Artist │ T. Swift    │  │ [00:47] Karma is a god        │ │
│  │ 💿 Album  │ Midnights   │  │ ♪ [00:50] Karma is the breeze │ │
│  │ 🔁 Mode   │ Normal      │  │ [00:53] in my hair on weekend │ │
│  │                         │  │ [00:56] Karma's a relaxing... │ │
│  │ ▶️ Playing ♪            │  │                               │ │
│  │                         │  │ (Synced lyrics with real-time │ │
│  │ ⏱  2:15 │━━━━━━━━━─│   │  │  highlighting - powered by    │ │
│  │         4:30  (50%)     │  │  LRCLIB)                      │ │
│  │                         │  │                               │ │
│  │ 💬 Playing track #5     │  └───────────────────────────────┘ │
│  └─────────────────────────┘                                     │
│  ┌──── Track List ────────┐                                      │
│  │  ▲ 2 more above...     │                                      │
│  │   3. Anti-Hero         │                                      │
│  │   4. Snow On The Beach │                                      │
│  │ ▶ 5. Karma (playing)   │                                      │
│  │   6. Vigilante Shit    │                                      │
│  │   7. Bejeweled         │                                      │
│  │  ▼ 6 more below...     │                                      │
│  │ [Showing 3-7 of 13]    │                                      │
│  └────────────────────────┘                                      │
├──────────────────────────────────────────────────────────────────┤
│  ⚡ Quick Controls                                                │
│  ─────────────────                                               │
│  ⚡ Shortcuts: Space=Play/Pause  ↑↓=Prev/Next  ←→=Seek±10s  Q=Quit│
│  ⌨️  Commands: [Number]=Jump  normal/shuffle=Mode  help=Help     │
├──────────────────────────────────────────────────────────────────┤
│  ⌨️  Command Input                                                │
│  ─────────────────────                                           │
│  Type your command and press Enter:                              │
│  💬 > 7█                                                         │
│  Examples: play album folklore | 15 | help                      │
└──────────────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

**Instant Shortcuts (No Enter Needed):**

| Key | Action |
|-----|--------|
| **Space** | Play/Pause toggle |
| **↑** | Previous track |
| **↓** | Next track |
| **←** | Seek backward 10 seconds |
| **→** | Seek forward 10 seconds |
| **Q** | Quit application |

## Text Commands

Type commands and press Enter:

### Playback Commands
```
play                                   → Play random song from Spotify
play Coldplay                          → Play random Coldplay song
play rock                              → Play random rock song
play song Yesterday                    → Play specific song by name
play song Yesterday by Beatles         → Play specific song by artist
play album folklore                    → Play album by name
play album folklore by Taylor Swift    → Play specific album

[number]                               → Jump to track # in current album (e.g., "5" plays track #5)

pause                                  → Pause playback
resume                                 → Resume playback
next                                   → Next track
prev / previous                        → Previous track
```

### Mode Commands
```
normal                                 → Normal play mode (auto-continues, pauses at end)
repeat one                             → Repeat current song
repeat all / repeat                    → Repeat entire album
shuffle                                → Shuffle mode
```

### System Commands
```
help                                   → Show help
quit / exit / q                        → Exit agent
```

## Examples

### Example 1: Play an Album
```
> play album Midnights
```
→ Plays "Midnights" album from the beginning
→ Track list shows all songs in the album
→ Auto-continues through tracks in Normal mode

### Example 2: Jump to a Track
```
> 7
```
→ Jumps directly to track #7 in the current album
→ Track list scrolls to show track #7 centered
→ Continues playing through the album

### Example 3: Play Specific Song
```
> play song Bohemian Rhapsody by Queen
```
→ Searches and plays the specific song
→ Shows artist's top tracks in track list

### Example 4: Quick Controls
```
(Press Space)  → Pause/Resume
(Press ↓)      → Skip to next track
(Type: 12)     → Jump to track #12
(Type: repeat all) → Enable repeat all mode
```

## Display Features

### Now Playing Panel (Top Left - 60% of space)
- 🎵 **Song name** (current track)
- 🎤 **Artist(s)** (all artists)
- 💿 **Album name**
- 🔁 **Play mode** (Normal/Repeat One/Repeat All/Shuffle)
- ▶️ **Status** (Playing ♪ / Paused ⏸️) - color-coded
- ⏱ **Progress bar** (visual + current time + total time + percentage)
  - Example: `⏱  2:15 │━━━━━━━━━━━━━━━─────│ 4:30  (50%)`
- 💬 **Status message** (current action/info)

### Track List Panel (Bottom Left - 40% of space)
- Shows current album or artist's top tracks
- **Auto-scrolling**: Centers on currently playing track
- **Scroll indicators**: Shows ▲ and ▼ when more tracks available
- **Compact view**: Shows 5-7 tracks at a time
- **Track numbers**: Type number to jump to that track
- **Current track**: Highlighted with ▶ symbol

### Lyrics Panel (Right Side - 40% width)
- **Real-time synced lyrics** (powered by LRCLIB)
- **Current line highlighting** in bold green
- **Past lines** shown dimmed
- **Upcoming lines** shown in white
- **Auto-scrolls** to follow playback
- Fallback to plain lyrics if sync not available

### Controls Panel (Middle - 4 lines)
- Compact reference for shortcuts and commands
- Always visible for quick reference

### Command Input Panel (Bottom - 4 lines)
- Live input with blinking cursor
- Shows examples
- Real-time feedback as you type

## Play Modes Explained

### 🔁 Normal Mode
- Plays tracks in order within album/playlist
- **Auto-continues** to next track when song ends
- **Pauses at album end** (shows "Album finished - Paused")
- Best for: Listening to albums as intended

### 🔂 Repeat One Mode
- Replays the same track continuously
- When track ends, restarts from beginning
- Best for: Focus/concentration with one song

### 🔁 Repeat All Mode
- Plays through entire album
- **Loops back to first track** when last track ends
- Shows "Looping back to first track..." message
- Best for: Continuous album listening

### 🔀 Shuffle Mode
- Plays tracks in random order
- Remembers played tracks to avoid immediate repeats
- Resets history when changing modes
- Best for: Music discovery

## Auto-Features

### Auto-Resume on Startup
- If a track was paused when you last quit
- Terminal automatically resumes playback (default)
- Configurable with `--start-mode pause` to keep paused

### Auto-Pause on Quit
- When you quit the terminal (Press Q)
- Automatically pauses the current track (default)
- Configurable with `--quit-mode resume` to keep playing

### Auto-Next
- When a track ends, automatically plays next based on mode:
  - **Normal**: Next track in album → Pause at end
  - **Repeat All**: Next track → Loop to first at end
  - **Repeat One**: Replay same track
  - **Shuffle**: Random unplayed track

### Auto-Refresh
- Display updates **20 times per second** for smooth progress bar
- Real-time status updates
- Live lyrics synchronized with playback

### Auto-Lyrics
- Automatically fetches when new song starts
- Tries synced lyrics first (LRCLIB)
- Falls back to plain lyrics if sync unavailable
- Background fetching (non-blocking)

### Auto-Context Loading
- When playing an album, loads full track list
- When playing a song, loads artist's top tracks
- Enables track jumping by number

## Track List Navigation

### Auto-Scrolling
- **Always centers** on currently playing track
- Shows context: tracks before and after
- Smooth scrolling as you jump between tracks

### Visual Indicators
```
▲ 5 more above...       ← Tracks hidden above
  6. Song Name
  7. Another Song
▶ 8. Current Song       ← Currently playing (centered)
  9. Next Song
 10. Following Song
▼ 8 more below...       ← Tracks hidden below

[Showing 6-10 of 18 tracks | ▶ Playing #8]
```

### Jump to Track
1. Look at track numbers in the Track List
2. Type the number (e.g., `12`)
3. Press Enter
4. Track list scrolls to show that track
5. Playback starts with album context maintained

## Color Scheme

- **Cyan/Bold Cyan**: Progress bar, headers, shortcuts
- **Green/Bold Green**: Playing status, current lyric line
- **Yellow/Bold Yellow**: Paused status, warnings, section headers
- **Magenta**: Lyrics panel
- **Red**: Errors
- **Dim**: Secondary information, past lyrics, scroll indicators

## Tips & Tricks

### 1. Quick Album Exploration
```
> play album Thriller
> 3                    ← Jump to track 3
> 7                    ← Jump to track 7
> repeat all           ← Loop the whole album
```

### 2. Find Your Favorite Track
```
> play album folklore
[Look at track list, see track #8 is "august"]
> 8                    ← Play it!
> repeat one           ← Loop it!
```

### 3. Background Music Workflow
```
> play album Chill Vibes
> normal               ← Plays through, stops at end
OR
> repeat all           ← Loops forever
```

### 4. Quick Mode Switching
Type mode names to instantly switch:
- `normal` → Auto-continue, pause at end
- `repeat` → Loop album
- `repeat one` → Loop current track
- `shuffle` → Random order

### 5. Smart Startup
```bash
# Start paused (for when you're not ready to listen)
python spotify_agent_terminal.py --start-mode pause

# Keep playing after quit (for background music)
python spotify_agent_terminal.py --quit-mode resume
```

### 6. Track List as Song Browser
- See all tracks in current album
- Jump to any track by number
- Perfect for exploring new albums

## Troubleshooting

### Display Issues

**Problem**: UI looks broken or overlaps
```bash
# Make sure terminal window is wide enough (at least 120 columns)
# Resize terminal window wider and taller
# Recommended: 140 columns × 40 rows
```

**Problem**: Colors not showing
```bash
# Windows Terminal or PowerShell recommended
# Command Prompt has limited color support
# Install Windows Terminal from Microsoft Store (best experience)
```

**Problem**: Progress bar not visible
```bash
# The Now Playing panel needs vertical space
# Make terminal window taller
# Default layout gives 60% to Now Playing, 40% to Track List
```

### Playback Issues

**Problem**: Track doesn't auto-continue (pauses at end)
```bash
# Make sure you're in Normal or Repeat All mode
# Type: normal
# If playing individual tracks, use "play album [name]" instead
```

**Problem**: Track list empty or not showing
```bash
# Play an album first: play album [name]
# Individual song playback shows artist's top tracks
# Wait a moment for track list to load
```

### Input Issues

**Problem**: Keyboard shortcuts not working
```bash
# Make sure you're in the terminal window (click it first)
# Space, arrows, Q work instantly - no Enter needed
# For track numbers, you need to press Enter
```

**Problem**: Can't see what I'm typing
```bash
# Input section might be too small
# Make terminal window taller
# Your typing appears in the "💬 > " line
```

### Performance Issues

**Problem**: Display lagging or slow
```bash
# Close other programs
# Reduce terminal window size slightly
# Updates happen 20x/second - normal slight delay
```

## Comparison: GUI vs Terminal

| Feature | GUI Mode | Terminal Mode |
|---------|----------|---------------|
| **Display** | Graphical window | Text-based |
| **Album Art** | ✅ Full-size image | ❌ Not available |
| **Lyrics** | ✅ Scrollable widget | ✅ Real-time synced display |
| **Track List** | ❌ Not available | ✅ Scrollable with jump |
| **Controls** | ✅ Buttons | ✅ Keyboard + commands |
| **Progress** | ✅ Draggable slider | ✅ Visual bar (auto-updates) |
| **Jump to Track** | ❌ Not available | ✅ Type track number |
| **Resource Usage** | Higher (GUI) | Lower (text) |
| **SSH/Remote** | ❌ Not supported | ✅ Works over SSH |
| **Terminal Friendly** | ❌ No | ✅ Yes |
| **Startup Options** | ❌ No | ✅ CLI arguments |

## System Requirements

- **Python 3.8+** (same as GUI mode)
- **Terminal**: Windows Terminal (recommended), PowerShell, or Command Prompt
- **Width**: Minimum 120 columns, 140+ recommended
- **Height**: Minimum 30 rows, 40+ recommended
- **Rich library**: Installed automatically from requirements.txt

## Exit/Stop

Multiple ways to exit:

1. Press **Q** (instant quit)
2. Type **quit** and Enter
3. Type **exit** and Enter
4. Press **Ctrl+C** (emergency stop)
5. Close terminal window

**Default behavior**: Pauses current track on exit
**With `--quit-mode resume`**: Keeps track playing after exit

## Benefits of Terminal Mode

1. **✅ Lightweight**: Lower memory and CPU usage than GUI
2. **✅ SSH Compatible**: Control remotely over SSH
3. **✅ Scriptable**: Easy to integrate with shell scripts and automation
4. **✅ Terminal-Friendly**: For terminal enthusiasts and power users
5. **✅ No GUI Dependencies**: Works without display server
6. **✅ Professional**: Clean, focused interface
7. **✅ Copy-Friendly**: Easy to copy song info/lyrics as text
8. **✅ Album Navigation**: Track list with jump-to-track feature
9. **✅ Real-Time Lyrics**: Synced lyrics with current line highlighting
10. **✅ Configurable**: Command-line arguments for custom behavior

---

**Enjoy your terminal music experience! 🎵🖥️**
