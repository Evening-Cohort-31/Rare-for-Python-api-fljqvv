"""Module for handling avatar related requests."""

import json
from pathlib import Path

# Allowed file extensions for avatars
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def get_all_avatars():
    """Return a list of available avatar URLs from /static/avatars."""

    # This assumes static/ is in the same directory as json-server.py
    # AND that you run the server with working directory set to that same folder
    # Assigns a URL path for each valid image file found in the avatars directory
    # Path returns objects that we can use methods like is_file() and suffix on, which is more robust than string manipulation
    avatars_dir = Path("./static/avatars")

    if not avatars_dir.exists() or not avatars_dir.is_dir():
        # Return empty list instead of error to keep frontend simple
        return json.dumps([])

    avatar_urls = []

    # Sort for consistent ordering in the UI
    for file_path in sorted(avatars_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
            avatar_urls.append(f"/static/avatars/{file_path.name}")

    return json.dumps(avatar_urls)
