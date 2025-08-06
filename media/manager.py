"""
Media manager for handling song playback.
"""

import logging
import os
import subprocess
import threading
from typing import List, Optional


class MediaManager:
    """Handles media playback for synchronized robot actions."""

    def __init__(self, config):
        """Initialize media manager."""
        self.config = config
        self.logger = logging.getLogger("MediaManager")
        self.current_process: Optional[subprocess.Popen] = None
        self.playback_thread: Optional[threading.Thread] = None

    def get_song_files(self, song_folder: str) -> List[str]:
        """Get list of song files in the folder."""
        try:
            if not os.path.exists(song_folder):
                self.logger.error(f"Song folder does not exist: {song_folder}")
                return []

            files = [f for f in os.listdir(song_folder) if f.endswith(".mp4")]
            files.sort()  # Sort alphabetically
            return files

        except Exception as e:
            self.logger.error(f"Error getting song files: {e}")
            return []

    def start_media_for_song(self, song_file_path: str, song_name: str) -> bool:
        """Start media playback for a song."""
        try:
            if not os.path.exists(song_file_path):
                self.logger.error(f"Song file does not exist: {song_file_path}")
                return False

            self.logger.info(f"Starting media playback: {song_name}")

            # Try to play the video file using VLC (like original version)
            if os.name == "nt":  # Windows
                # Try VLC first with --play-and-exit flag (like original)
                vlc_paths = [
                    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
                ]
                vlc_cmd = None
                for path in vlc_paths:
                    if os.path.exists(path):
                        vlc_cmd = path
                        break
                
                if vlc_cmd:
                    try:
                        self.current_process = subprocess.Popen(
                            [vlc_cmd, "--play-and-exit", song_file_path],
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        self.logger.info(f"Playing song with VLC: {song_name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to play with VLC: {e}, trying default player")
                        self.current_process = subprocess.Popen(
                            ["start", "", song_file_path],
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                else:
                    # Fallback to default player
                    self.current_process = subprocess.Popen(
                        ["start", "", song_file_path],
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            else:  # Unix/Linux/Mac
                # Try VLC first
                try:
                    self.current_process = subprocess.Popen(
                        ["vlc", "--play-and-exit", song_file_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    self.logger.info(f"Playing song with VLC: {song_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to play with VLC: {e}, trying xdg-open")
                    self.current_process = subprocess.Popen(
                        ["xdg-open", song_file_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

            self.logger.info(f"Media playback started for: {song_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start media playback: {e}")
            return False

    def stop_media(self) -> None:
        """Stop current media playback."""
        try:
            if self.current_process:
                if os.name == "nt":  # Windows
                    # Try to stop VLC processes like original version
                    try:
                        subprocess.run(
                            ["taskkill", "/IM", "vlc.exe", "/F"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=False
                        )
                        self.logger.info("Stopped VLC process with taskkill")
                    except:
                        pass
                    
                    # Also try to terminate the current process
                    try:
                        self.current_process.terminate()
                    except:
                        pass
                else:  # Unix/Linux/Mac
                    # Try to stop VLC processes like original version
                    try:
                        subprocess.run(
                            ["pkill", "vlc"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=False
                        )
                        self.logger.info("Stopped VLC process with pkill")
                    except:
                        pass
                    
                    # Also try to terminate the current process
                    try:
                        self.current_process.terminate()
                    except:
                        pass

                self.current_process = None
                self.logger.info("Media playback stopped")

        except Exception as e:
            self.logger.error(f"Error stopping media: {e}")

    def cleanup(self) -> None:
        """Clean up media resources."""
        self.stop_media()
