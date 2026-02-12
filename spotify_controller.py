import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import time
import requests
from typing import Optional, List, Dict, Tuple
import re


class SpotifyController:
    """Handles all Spotify API interactions and playback logic"""

    def __init__(self, config):
        self.config = config
        self.sp = None
        self.current_track = None
        self.play_mode = 'normal'  # normal, repeat_one, repeat_all, shuffle
        self.playlist_queue = []
        self.current_index = 0
        self.played_tracks_history = set()  # Track URIs that have been played in shuffle mode
        self.max_history_size = 100  # Max number of tracks to remember
        self.synced_lyrics = []  # List of (timestamp_ms, lyric_line) tuples
        self.current_context_tracks = []  # List of tracks in current album/context

    def authenticate(self):
        """Authenticate with Spotify"""
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                redirect_uri=self.config['redirect_uri'],
                scope=self.config['scope']
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            print("Spotify authentication successful!")
            return True
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def parse_lrc_lyrics(self, lrc_text: str) -> List[Tuple[int, str]]:
        """Parse LRC format lyrics into (timestamp_ms, text) tuples"""
        lyrics = []
        # LRC format: [MM:SS.xx]Lyric text
        pattern = r'\[(\d{2}):(\d{2})\.(\d{2})\](.*)'

        for line in lrc_text.split('\n'):
            match = re.match(pattern, line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                centiseconds = int(match.group(3))
                text = match.group(4).strip()

                # Convert to milliseconds
                timestamp_ms = (minutes * 60 * 1000) + (seconds * 1000) + (centiseconds * 10)

                if text:  # Only add non-empty lines
                    lyrics.append((timestamp_ms, text))

        return sorted(lyrics, key=lambda x: x[0])  # Sort by timestamp

    def get_available_devices(self):
        """Get list of available Spotify devices"""
        try:
            devices = self.sp.devices()
            return devices['devices']
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

    def play_random_track(self, artist: Optional[str] = None, genre: Optional[str] = None):
        """Play a random track based on criteria"""
        try:
            tracks = self._search_tracks(artist=artist, genre=genre)

            if not tracks:
                print("No tracks found matching criteria")
                return None

            # In shuffle mode, filter out already-played tracks
            if self.play_mode == 'shuffle':
                unplayed_tracks = [t for t in tracks if t.get('uri') not in self.played_tracks_history]

                # If all tracks have been played, reset history and use all tracks
                if not unplayed_tracks:
                    print("All tracks played - resetting shuffle history")
                    self.played_tracks_history.clear()
                    unplayed_tracks = tracks

                tracks = unplayed_tracks

            # Select random track
            track = random.choice(tracks)

            # Add to history if in shuffle mode
            if self.play_mode == 'shuffle':
                self.played_tracks_history.add(track['uri'])
                # Limit history size to prevent memory issues
                if len(self.played_tracks_history) > self.max_history_size:
                    # Remove oldest entries (convert to list, remove first half, convert back)
                    history_list = list(self.played_tracks_history)
                    self.played_tracks_history = set(history_list[len(history_list)//2:])

            self._play_track(track['uri'])
            self.current_track = track
            return track

        except Exception as e:
            print(f"Error playing random track: {e}")
            return None

    def search_album(self, album_name: str, artist_name: Optional[str] = None) -> Optional[Dict]:
        """Search for an album by name, optionally filtered by artist"""
        try:
            # Build search query
            query = album_name
            if artist_name:
                query = f'album:{album_name} artist:{artist_name}'

            results = self.sp.search(q=query, type='album', limit=5)
            if results and 'albums' in results and results['albums']['items']:
                albums = results['albums']['items']

                # If artist specified, try to find exact match
                if artist_name:
                    for album in albums:
                        for artist in album['artists']:
                            if artist_name.lower() in artist['name'].lower():
                                return album

                # Return first result (most popular)
                return albums[0]

            return None
        except Exception as e:
            print(f"Error searching album: {e}")
            return None

    def search_song(self, song_name: str, artist_name: Optional[str] = None) -> Optional[Dict]:
        """Search for a song by name, optionally filtered by artist"""
        try:
            # Build search query
            query = song_name
            if artist_name:
                query = f'track:{song_name} artist:{artist_name}'

            results = self.sp.search(q=query, type='track', limit=5)
            if results and 'tracks' in results and results['tracks']['items']:
                tracks = results['tracks']['items']

                # If artist specified, try to find exact match
                if artist_name:
                    for track in tracks:
                        for artist in track['artists']:
                            if artist_name.lower() in artist['name'].lower():
                                return track

                # Return first result (most popular)
                return tracks[0]

            return None
        except Exception as e:
            print(f"Error searching song: {e}")
            return None

    def play_album(self, album_name: str, artist_name: Optional[str] = None):
        """Play an album from the beginning"""
        try:
            # Search for the album
            album = self.search_album(album_name, artist_name)

            if not album:
                print(f"Album not found: {album_name}")
                return None

            album_uri = album['uri']
            album_id = album['id']
            album_title = album['name']
            artist = album['artists'][0]['name'] if album['artists'] else 'Unknown'

            print(f"Playing album: {album_title} by {artist}")

            # Preload album tracks
            self.current_context_tracks = self.get_album_tracks(album_id)

            # Check for available devices
            devices = self.get_available_devices()
            if not devices:
                print("\n[ERROR] No active Spotify devices found!")
                return None

            # Play the album (starts from first track)
            device_id = devices[0]['id'] if devices else None
            self.sp.start_playback(device_id=device_id, context_uri=album_uri)
            time.sleep(0.5)

            # Get current track info
            self.current_track = self.get_current_track()
            return self.current_track

        except Exception as e:
            print(f"Error playing album: {e}")
            return None

    def play_song(self, song_name: str, artist_name: Optional[str] = None):
        """Play a specific song"""
        try:
            # Search for the song
            track = self.search_song(song_name, artist_name)

            if not track:
                print(f"Song not found: {song_name}")
                return None

            track_title = track['name']
            artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'

            print(f"Playing song: {track_title} by {artist}")

            # Play the track
            self._play_track(track['uri'])
            self.current_track = track
            return track

        except Exception as e:
            print(f"Error playing song: {e}")
            return None

    def _search_tracks(self, artist: Optional[str] = None, genre: Optional[str] = None, limit: int = 20):
        """Search for tracks based on criteria from Spotify's entire catalog"""
        try:
            query_parts = []

            if artist:
                query_parts.append(f'artist:{artist}')
            if genre:
                query_parts.append(f'genre:{genre}')

            if not query_parts:
                # No criteria - get random tracks from Spotify catalog
                return self._get_random_tracks_from_spotify(limit)

            # Get user's market/country
            market = 'US'  # Default fallback
            try:
                user_profile = self.sp.current_user()
                if user_profile and 'country' in user_profile:
                    market = user_profile['country']
            except:
                pass

            query = ' '.join(query_parts)
            # Use limit of 10 with explicit market
            results = self.sp.search(q=query, type='track', limit=10, market=market)
            return results['tracks']['items']

        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    def _get_random_tracks_from_spotify(self, limit: int = 50):
        """Get random tracks from Spotify's entire catalog"""
        # Use simple search API (most reliable method)
        return self._search_with_random_query(limit)

    def _get_tracks_from_featured_playlists(self, limit: int = 50):
        """Get tracks from Spotify's featured playlists"""
        try:
            # Get featured playlists
            playlists = self.sp.featured_playlists(limit=10)
            if not playlists or 'playlists' not in playlists:
                return []

            # Pick a random playlist
            playlist_items = playlists['playlists']['items']
            if not playlist_items:
                return []

            random_playlist = random.choice(playlist_items)

            # Get tracks from that playlist
            playlist_tracks = self.sp.playlist_tracks(random_playlist['id'], limit=limit)
            if playlist_tracks and 'items' in playlist_tracks:
                return [item['track'] for item in playlist_tracks['items'] if item['track']]

            return []

        except Exception as e:
            print(f"Error getting featured playlist tracks: {e}")
            return []

    def _search_with_random_query(self, limit: int = 50):
        """Search with random query to get random tracks"""
        try:
            # Get user's market/country from their profile
            market = 'US'  # Default fallback
            try:
                user_profile = self.sp.current_user()
                if user_profile and 'country' in user_profile:
                    market = user_profile['country']
            except:
                pass  # Use default market if profile fetch fails

            # Use random common words or letters
            random_queries = [
                'love', 'night', 'day', 'time', 'life', 'heart', 'dream',
                'dance', 'summer', 'light', 'way', 'world', 'baby', 'girl',
                'boy', 'feel', 'want', 'need', 'forever', 'tonight', 'music',
                'a', 'b', 'c', 'd', 'e', 'the', 'you', 'me', 'we'
            ]

            query = random.choice(random_queries)
            # Try with minimal limit and explicit market
            results = self.sp.search(q=query, type='track', limit=10, market=market)

            if results and 'tracks' in results and 'items' in results['tracks']:
                return results['tracks']['items']

            return []

        except Exception as e:
            print(f"Error with random query search: {e}")
            return []

    def _play_track(self, uri: str):
        """Play a specific track"""
        try:
            # Check for available devices first
            devices = self.get_available_devices()
            if not devices:
                print("\n[ERROR] No Spotify devices found!")
                print("Please open Spotify on one of your devices (computer, phone, etc.)\n")
                return

            # If no device is active, try to activate the first available one
            active_device = None
            for device in devices:
                if device.get('is_active'):
                    active_device = device
                    break

            if not active_device and devices:
                # Try to transfer playback to first available device
                print(f"Activating device: {devices[0]['name']}...")
                try:
                    self.sp.transfer_playback(device_id=devices[0]['id'], force_play=False)
                    time.sleep(1)  # Give it time to activate
                    active_device = devices[0]
                except Exception as transfer_error:
                    print(f"Could not activate device automatically: {transfer_error}")
                    print("\nPlease manually start playing something on your Spotify app first,")
                    print("then try the 'play' command again.\n")
                    return

            # Now try to play on the active device
            device_id = active_device['id'] if active_device else None
            self.sp.start_playback(device_id=device_id, uris=[uri])
            time.sleep(0.5)  # Give it time to start
        except Exception as e:
            print(f"Error playing track: {e}")
            if "NO_ACTIVE_DEVICE" in str(e) or "Device not found" in str(e):
                print("\n[TIP] Open Spotify on your phone/computer and play any song first,")
                print("then try again. Just having the app open isn't enough.\n")

    def pause(self):
        """Pause playback"""
        try:
            self.sp.pause_playback()
        except Exception as e:
            print(f"Error pausing: {e}")

    def resume(self):
        """Resume playback"""
        try:
            self.sp.start_playback()
        except Exception as e:
            print(f"Error resuming: {e}")

    def next_track(self):
        """Skip to next track and auto-play"""
        try:
            if self.play_mode == 'repeat_one':
                # Replay current track
                if self.current_track:
                    self._play_track(self.current_track['uri'])
            elif self.play_mode == 'shuffle':
                # In shuffle mode, play a new random track that hasn't been played
                self.play_random_track()
            else:
                # Try to skip to next track in queue
                try:
                    self.sp.next_track()
                    time.sleep(0.5)
                    new_track = self.get_current_track()

                    # If still on same track (no queue), play a random track instead
                    if new_track and self.current_track and new_track.get('uri') == self.current_track.get('uri'):
                        self.play_random_track()
                    else:
                        self.current_track = new_track
                except:
                    # If next_track fails, play a random track
                    self.play_random_track()
        except Exception as e:
            print(f"Error skipping track: {e}")

    def previous_track(self):
        """Go to previous track and auto-play"""
        try:
            # Try to skip to previous track
            try:
                self.sp.previous_track()
                time.sleep(0.5)
                new_track = self.get_current_track()

                # If still on same track (no queue), play a random track instead
                if new_track and self.current_track and new_track.get('uri') == self.current_track.get('uri'):
                    self.play_random_track()
                else:
                    self.current_track = new_track
            except:
                # If previous_track fails, play a random track
                self.play_random_track()
        except Exception as e:
            print(f"Error going to previous track: {e}")

    def seek_forward(self, seconds: int = 10):
        """Seek forward in current track"""
        try:
            current = self.get_current_track()
            if current:
                new_position = current['progress_ms'] + (seconds * 1000)
                # Don't seek past the end
                new_position = min(new_position, current['duration_ms'] - 1000)
                self.sp.seek_track(new_position)
        except Exception as e:
            print(f"Error seeking forward: {e}")

    def seek_backward(self, seconds: int = 10):
        """Seek backward in current track"""
        try:
            current = self.get_current_track()
            if current:
                new_position = current['progress_ms'] - (seconds * 1000)
                # Don't seek before the beginning
                new_position = max(new_position, 0)
                self.sp.seek_track(new_position)
        except Exception as e:
            print(f"Error seeking backward: {e}")

    def seek(self, position_ms: int):
        """Seek to position in current track"""
        try:
            self.sp.seek_track(position_ms)
        except Exception as e:
            print(f"Error seeking: {e}")

    def set_volume(self, volume: int):
        """Set playback volume (0-100)"""
        try:
            self.sp.volume(volume)
        except Exception as e:
            print(f"Error setting volume: {e}")

    def get_current_track(self) -> Optional[Dict]:
        """Get currently playing track info"""
        try:
            current = self.sp.current_playback()
            if current and current['item']:
                track = current['item']
                return {
                    'name': track['name'],
                    'artists': track['artists'],  # Keep full artist objects with IDs
                    'album': track['album'],  # Keep full album object with ID
                    'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration_ms': track['duration_ms'],
                    'progress_ms': current['progress_ms'],
                    'uri': track['uri'],
                    'is_playing': current['is_playing']
                }
            return None
        except Exception as e:
            print(f"Error getting current track: {e}")
            return None

    def get_lyrics(self, song_name: str, artist_name: str, duration_ms: int = 0) -> Optional[str]:
        """Fetch synced lyrics from LRCLIB"""
        try:
            # LRCLIB API endpoint
            url = "https://lrclib.net/api/get"
            params = {
                'track_name': song_name,
                'artist_name': artist_name,
            }

            # Add duration if available (helps with accuracy)
            if duration_ms > 0:
                params['duration'] = int(duration_ms / 1000)  # Convert to seconds

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                # Try to get synced lyrics first
                if data.get('syncedLyrics'):
                    self.synced_lyrics = self.parse_lrc_lyrics(data['syncedLyrics'])
                    return data['syncedLyrics']

                # Fallback to plain lyrics
                elif data.get('plainLyrics'):
                    self.synced_lyrics = []  # No sync data
                    return data['plainLyrics']

            # If not found, return message
            self.synced_lyrics = []
            return "Lyrics not found"

        except Exception as e:
            self.synced_lyrics = []
            return "Lyrics unavailable"

    def get_current_lyric_line(self, progress_ms: int) -> Optional[str]:
        """Get the current lyric line based on playback position"""
        if not self.synced_lyrics:
            return None

        # Find the most recent lyric line that should be displayed
        current_line = None
        for timestamp_ms, text in self.synced_lyrics:
            if timestamp_ms <= progress_ms:
                current_line = text
            else:
                break

        return current_line

    def get_album_tracks(self, album_id: str) -> List[Dict]:
        """Get all tracks from an album"""
        try:
            results = self.sp.album_tracks(album_id)
            if results and 'items' in results:
                return results['items']
            return []
        except Exception as e:
            print(f"Error getting album tracks: {e}")
            return []

    def get_artist_top_tracks(self, artist_id: str) -> List[Dict]:
        """Get artist's top tracks"""
        try:
            # Get user's market/country
            market = 'US'
            try:
                user_profile = self.sp.current_user()
                if user_profile and 'country' in user_profile:
                    market = user_profile['country']
            except:
                pass

            results = self.sp.artist_top_tracks(artist_id, country=market)
            if results and 'tracks' in results:
                return results['tracks']
            return []
        except Exception as e:
            print(f"Error getting artist top tracks: {e}")
            return []

    def update_context_tracks(self):
        """Update the current context tracks (album or artist)"""
        try:
            if not self.current_track:
                self.current_context_tracks = []
                return

            # Check if track has an album
            if self.current_track.get('album') and self.current_track['album'].get('id'):
                album_id = self.current_track['album']['id']
                self.current_context_tracks = self.get_album_tracks(album_id)
            # Otherwise get artist's top tracks
            elif self.current_track.get('artists') and len(self.current_track['artists']) > 0:
                artist_id = self.current_track['artists'][0]['id']
                self.current_context_tracks = self.get_artist_top_tracks(artist_id)
            else:
                self.current_context_tracks = []

        except Exception as e:
            print(f"Error updating context tracks: {e}")
            self.current_context_tracks = []

    def download_album_art(self, url: str) -> Optional[bytes]:
        """Download album artwork"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error downloading album art: {e}")
            return None

    def set_play_mode(self, mode: str):
        """Set play mode: normal, repeat_one, repeat_all, shuffle"""
        valid_modes = ['normal', 'repeat_one', 'repeat_all', 'shuffle']
        if mode in valid_modes:
            # Clear shuffle history when changing modes
            if mode != self.play_mode:
                self.played_tracks_history.clear()

            self.play_mode = mode

            # Update Spotify player state
            try:
                if mode == 'shuffle':
                    self.sp.shuffle(True)
                else:
                    self.sp.shuffle(False)

                if mode == 'repeat_all':
                    self.sp.repeat('context')
                elif mode == 'repeat_one':
                    self.sp.repeat('track')
                else:
                    self.sp.repeat('off')
            except Exception as e:
                print(f"Error setting play mode: {e}")

    def is_track_ended(self) -> bool:
        """Check if current track has ended"""
        try:
            current = self.sp.current_playback()
            if current and current['item']:
                progress = current['progress_ms']
                duration = current['item']['duration_ms']
                # Consider ended if within last 2 seconds
                return (duration - progress) < 2000
            return False
        except Exception as e:
            return False

    def parse_command(self, command: str) -> Dict:
        """Parse user command and extract intent"""
        command = command.lower().strip()

        result = {
            'action': 'play_random',
            'artist': None,
            'genre': None,
            'album': None,
            'song': None
        }

        # Simple parsing logic
        if 'play' in command:
            # Remove "play" from command
            command = command.replace('play', '').strip()

            # Check for "by [artist]" pattern
            artist_filter = None
            if ' by ' in command:
                parts = command.split(' by ')
                command = parts[0].strip()
                artist_filter = parts[1].strip()

            # Check for song request
            if 'song' in command:
                result['action'] = 'play_song'
                song_name = command.replace('song', '').strip()
                result['song'] = song_name
                result['artist'] = artist_filter
                return result

            # Check for album request
            if 'album' in command:
                result['action'] = 'play_album'
                album_name = command.replace('album', '').strip()
                result['album'] = album_name
                result['artist'] = artist_filter
                return result

            # Check for genre keywords (only if no "by" specified)
            if not artist_filter:
                genres = ['rock', 'pop', 'jazz', 'classical', 'hip hop', 'rap',
                         'electronic', 'country', 'metal', 'indie', 'blues']
                for genre in genres:
                    if genre in command:
                        result['genre'] = genre
                        command = command.replace(genre, '').strip()
                        break

            # Remaining text could be artist name or song name
            if command:
                # If it looks like a song title (contains common words), treat as song
                # Otherwise treat as artist
                if any(word in command for word in ['the', 'my', 'your', 'me', 'you', 'love', 'life']):
                    result['action'] = 'play_song'
                    result['song'] = command
                    result['artist'] = artist_filter
                else:
                    result['artist'] = command if not artist_filter else artist_filter

        return result
