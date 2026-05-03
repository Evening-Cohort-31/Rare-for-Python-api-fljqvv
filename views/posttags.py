"""Module for handling PostTags related requests."""

import sqlite3
import json

from .posttags_helpers import (
    build_posttags_select_and_joins,
    build_posttags_where_clause,
    serialize_posttag_row,
)


def get_all_posttags(query_params):
    """Get all PostTags, with optional filtering by post_id or tag_id"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        select_sql, join_sql = build_posttags_select_and_joins(query_params)
        where_sql, params = build_posttags_where_clause(query_params)

        query = f"""
            SELECT {select_sql}
            FROM PostTags pt
            {join_sql}
            {where_sql}
            ORDER BY pt.id
        """

        db_cursor.execute(query, params)
        rows = db_cursor.fetchall()

        posttags = [serialize_posttag_row(row, query_params) for row in rows]

        return json.dumps(posttags)


def get_single_posttag(pk, query_params):
    """Get a single PostTag by its ID"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        select_sql, join_sql = build_posttags_select_and_joins(query_params)

        query = f"""
            SELECT {select_sql}
            FROM PostTags pt
            {join_sql}
            WHERE pt.id = ?
        """

        db_cursor.execute(query, (pk,))
        row = db_cursor.fetchone()

        if row is None:
            return json.dumps({"error": "PostTag not found"})

        posttag = serialize_posttag_row(row, query_params)
        return json.dumps(posttag)


def create_posttag(posttag_data):
    """Create a new PostTag assignment between a post and a tag"""

    if "post_id" not in posttag_data or "tag_id" not in posttag_data:
        return json.dumps({"error": "post_id and tag_id are required."})

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        db_cursor = conn.cursor()

        try:
            db_cursor.execute(
                """
                INSERT INTO PostTags (post_id, tag_id)
                VALUES (?, ?)
                """,
                (posttag_data["post_id"], posttag_data["tag_id"]),
            )

            new_id = db_cursor.lastrowid

            db_cursor.execute(
                """
                SELECT id, post_id, tag_id, created_on
                FROM PostTags
                WHERE id = ?
                """,
                (new_id,),
            )

            new_posttag = db_cursor.fetchone()

            return json.dumps(
                {
                    "id": new_posttag["id"],
                    "post_id": new_posttag["post_id"],
                    "tag_id": new_posttag["tag_id"],
                    "created_on": new_posttag["created_on"],
                }
            )

        except sqlite3.IntegrityError as ex:
            error_message = str(ex).lower()

            if "unique" in error_message:
                return json.dumps(
                    {"error": "This tag is already assigned to this post."}
                )
            if "foreign key" in error_message:
                return json.dumps({"error": "Invalid post_id or tag_id."})

            return json.dumps({"error": "Unable to create post tag assignment."})


def delete_posttag(pk):
    """Delete a PostTag by its ID"""

    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            DELETE FROM PostTags
            WHERE id = ?
        """,
            (pk,),
        )

        if db_cursor.rowcount == 0:
            return json.dumps({"error": "PostTag not found"})

        return json.dumps({"message": "PostTag successfully deleted"})
