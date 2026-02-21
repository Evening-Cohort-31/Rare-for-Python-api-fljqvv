"""Module for handling comments related requests."""

import sqlite3
import json

from .comment_helpers import build_comment_query, build_comment_object


def get_comments_by_post_id(post_id, query_params):
    """Get all comments for a given post id"""

    # Get expand parameters from query params
    expand = query_params.get("_expand", [])

    # Connect to the database and execute the query
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Build query dynamically based on expand parameters
        # select_clause will contain the fields to select
        # join_clause will contain the necessary JOIN statements
        select_clause, join_clause = build_comment_query(expand)

        query = f"""
            SELECT
                {select_clause}
            FROM Comments c
            {join_clause}
            WHERE c.post_id = ?
            ORDER BY c.publication_date ASC
        """

        db_cursor.execute(query, (post_id,))
        comment_row_data = db_cursor.fetchall()

        if comment_row_data:
            # Build comment objects from the database rows using the helper function
            comments = [build_comment_object(row, expand) for row in comment_row_data]
        else:
            comments = []

    return json.dumps(comments)


def create_comment(comment_data):
    """Create a new comment in the database"""

    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        # Insert the new comment into the Comments table
        db_cursor.execute(
            """
            INSERT INTO Comments (post_id, author_id, content)
            VALUES (?, ?, ?)
            """,
            (
                comment_data["post_id"],
                comment_data["author_id"],
                comment_data["content"],
            ),
        )

        # Get the ID of the newly created comment
        new_comment_id = db_cursor.lastrowid

        # Commit the transaction to save the new comment
        conn.commit()

        created_comment = {
            "id": new_comment_id,
            "post_id": comment_data["post_id"],
            "author_id": comment_data["author_id"],
            "content": comment_data["content"],
        }

    return json.dumps(created_comment)
