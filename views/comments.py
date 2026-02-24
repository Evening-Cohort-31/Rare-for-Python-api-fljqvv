"""Module for handling comments related requests."""

import sqlite3
import json

# from .comment_helpers import build_comment_query, build_comment_object


def get_comments_by_post_id(post_id, query_params):
    """Get all comments for a given post id"""

    # Get expand parameters from query params

    # Connect to the database and execute the query

    # Build query dynamically based on expand parameters
    # You can use build_comment_query to get the select clause and join clause based on the expand parameters
    # You will have to uncomment the helpers on line 6 and implement the build_comment_query function in comment_helpers.py
    # select_clause will contain the fields to select
    # join_clause will contain the necessary JOIN statements

    # Build comment objects from the database rows using the helper function

    pass


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
