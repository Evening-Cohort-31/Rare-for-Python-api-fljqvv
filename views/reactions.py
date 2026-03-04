"""Module for handling reactions related requests."""

import sqlite3
import json


def get_all_reactions():
    """Get all reactions"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT
                id,
                label,
                icon_class,
                color
            FROM Reactions
            """
        )

        reactions = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            reaction = {
                "id": row["id"],
                "label": row["label"],
                "icon_class": row["icon_class"],
                "color": row["color"],
            }
            reactions.append(reaction)

    return json.dumps(reactions)
