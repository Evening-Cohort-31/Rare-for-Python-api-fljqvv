"""Module for handling profile image related requests."""

import json
import sqlite3
from pathlib import Path

# Allowed file extensions for profile images
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def get_all_profile_images(user_id):
    """Retrieve all profile images for a specific user."""

    images_dir = Path(f"./static/uploads/users/{user_id}")

    if not images_dir.exists() or not images_dir.is_dir():
        # Return empty list instead of error to keep frontend simple
        return json.dumps([])

    profile_image_urls = []

    # Sort for consistent ordering in the UI
    for file_path in sorted(images_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
            profile_image_urls.append(
                f"/static/uploads/users/{user_id}/{file_path.name}"
            )

    return json.dumps(profile_image_urls)


def save_uploaded_profile_image(user_id, image_url, original_filename, mime_type):
    """Save uploaded profile image metadata and update user's current profile image."""

    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        # Insert new profile image record
        db_cursor.execute(
            """
            INSERT INTO UserProfileImages (user_id, image_url, original_filename, mime_type)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, image_url, original_filename, mime_type),
        )

        # Get the ID of the newly inserted profile image
        image_id = db_cursor.lastrowid

        # Update the user's current profile image URL in the Users table
        db_cursor.execute(
            """
            UPDATE Users
            SET profile_image_url = ?
            WHERE id = ?
            """,
            (image_url, user_id),
        )

        if db_cursor.rowcount == 0:
            return json.dumps({"error": "User not found"})

        conn.commit()

    return json.dumps(
        {
            "id": image_id,
            "user_id": user_id,
            "image_url": image_url,
            "original_filename": original_filename,
            "mime_type": mime_type,
        }
    )
