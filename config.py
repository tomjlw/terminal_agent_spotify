# Spotify Agent Configuration
# Replace these with your actual Spotify API credentials from:
# https://developer.spotify.com/dashboard

SPOTIFY_CONFIG = {
    'client_id': 'YOUR_SPOTIFY_CLIENT_ID',
    'client_secret': 'YOUR_SPOTIFY_CLIENT_SECRET',
    'redirect_uri': 'http://127.0.0.1:8888/callback',
    'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing '
             'user-library-read playlist-read-private streaming'
}

# Genius API for lyrics (optional - get from https://genius.com/api-clients)
# Set to 'YOUR_GENIUS_TOKEN_HERE' to disable lyrics
GENIUS_ACCESS_TOKEN = 'YOUR_GENIUS_TOKEN_HERE'

# UI Settings
UI_CONFIG = {
    'window_width': 800,
    'window_height': 900,
    'bg_color': '#1a1a1a',
    'fg_color': '#ffffff',
    'accent_color': '#1db954',  # Spotify green
    'font_family': 'Segoe UI',
    'album_art_size': 300
}
