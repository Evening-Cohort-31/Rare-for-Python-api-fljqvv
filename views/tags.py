"""Module for retrieving tag data from the SQLite database."""

import sqlite3
import json


def get_all_tags():
    """Get all tags from the database"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT id, label
            FROM Tags
        """
        )

        tags = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            tags.append(dict(row))

        return json.dumps(tags)


def get_tag_by_id(tag_id):
    """Get a single tag by its ID"""
    pass


def create_tag(tag_data):
    """Create a new tag in the database"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Insert the new tag into the Tags table
        db_cursor.execute(
            """
            INSERT INTO Tags (label)
            VALUES (?)
        """,
            (tag_data["label"],),
        )

        # Get the ID of the newly created tag
        tag_id = db_cursor.lastrowid

        json_response = json.dumps({"id": tag_id, "label": tag_data["label"]})

    return json_response


def delete_tag(tag_id):
    """Delete a tag by id"""
    # Added try/except block to catch any potential database errors and return them as JSON error messages
    try:
        with sqlite3.connect("./db.sqlite3") as conn:
            db_cursor = conn.cursor()

            db_cursor.execute(
                """
                DELETE FROM Tags
                WHERE id = ?
                """,
                (tag_id,),
            )

            if db_cursor.rowcount == 0:
                return json.dumps({"error": "Tag not found"})

        return json.dumps({"message": "Tag deleted successfully"})

    except sqlite3.Error as e:
        return json.dumps({"error": str(e)})
