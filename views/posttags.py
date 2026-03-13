"""Module for handling PostTags related requests."""

import sqlite3
import json
from datetime import datetime


def delete_posttag(posttag_id):
    """Delete a PostTag by its ID"""

    with sqlite3.connect("db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            DELETE FROM PostTags
            WHERE id = ?
        """,
            (posttag_id,),
        )

        if db_cursor.rowcount == 0:
            return json.dumps({"error": "PostTag not found"})

        return json.dumps({"message": "Deleted"})
