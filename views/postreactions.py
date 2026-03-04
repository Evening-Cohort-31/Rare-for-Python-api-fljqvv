"""Module for handling reactions related requests."""

import sqlite3
import json


def get_all_postreactions(post_id=None):
    """Get all post reactions"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if post_id:
            db_cursor.execute(
                """
                SELECT
                    pr.id,
                    pr.user_id,
                    pr.post_id,
                    pr.reaction_id,
                    r.label,
                    r.icon_class,
                    u.first_name || ' ' || u.last_name AS user_name
                FROM PostReactions pr
                JOIN Reactions r ON pr.reaction_id = r.id
                JOIN Users u ON pr.user_id = u.id
                WHERE pr.post_id = ?
                """,
                (post_id,),
            )
        else:
            db_cursor.execute(
                """
                SELECT
                    pr.id,
                    pr.user_id,
                    pr.post_id,
                    pr.reaction_id,
                    r.label,
                    r.icon_class,
                    u.first_name || ' ' || u.last_name AS user_name
                FROM PostReactions pr
                JOIN Reactions r ON pr.reaction_id = r.id
                JOIN Users u ON pr.user_id = u.id
                """
            )

        reactions = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            reaction = {
                "id": row["id"],
                "user_id": row["user_id"],
                "post_id": row["post_id"],
                "reaction_id": row["reaction_id"],
                "label": row["label"],
                "icon_class": row["icon_class"],
                "user_name": row["user_name"],
            }
            reactions.append(reaction)

    return json.dumps(reactions)


def create_or_update_postreactions(reaction_data):
    """Create a new post reaction or update an existing one"""

    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO
            PostReactions (user_id, post_id, reaction_id)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, post_id) DO UPDATE SET reaction_id=excluded.reaction_id
            """,
            (
                reaction_data["user_id"],
                reaction_data["post_id"],
                reaction_data["reaction_id"],
            ),
        )

        db_cursor.execute(
            "SELECT id FROM PostReactions WHERE user_id = ? AND post_id = ?",
            (reaction_data["user_id"], reaction_data["post_id"]),
        )
        row = db_cursor.fetchone()
        reaction_id = row[0]

    return json.dumps({"id": reaction_id})
