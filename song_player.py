import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)


def play_song(file_path):
    """Play a song file using VLC or the system default player."""
    try:
        vlc_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        vlc_cmd = "vlc"  # Default to PATH
        if sys.platform.startswith("win"):
            for path in vlc_paths:
                if os.path.exists(path):
                    vlc_cmd = path
                    break
        if sys.platform.startswith("win"):
            try:
                subprocess.Popen([vlc_cmd, "--play-and-exit", file_path], shell=True)
                logger.info(f"Playing song with VLC: {file_path}")
            except (
                OSError,
                FileNotFoundError,
                subprocess.SubprocessError,
            ) as e:
                logger.error(f"Failed to play song with VLC: {e}")
                try:
                    os.startfile(file_path)
                    logger.info(f"Playing song with default app: {file_path}")
                except OSError as e2:
                    logger.error(f"Failed to play song with default app: {e2}")
        else:
            try:
                subprocess.Popen(["vlc", "--play-and-exit", file_path])
                logger.info(f"Playing song with VLC: {file_path}")
            except (
                OSError,
                FileNotFoundError,
                subprocess.SubprocessError,
            ) as e:
                logger.error(f"Failed to play song with VLC: {e}")
                try:
                    subprocess.Popen(["xdg-open", file_path])
                    logger.info(f"Playing song with xdg-open: {file_path}")
                except OSError as e2:
                    logger.error(f"Failed to play song with xdg-open: {e2}")
    except (OSError, FileNotFoundError) as e:
        logger.error(f"Failed to play song: {e}")
