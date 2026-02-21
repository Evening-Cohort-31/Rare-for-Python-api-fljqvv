"""Module for handling posts related requests."""

import sqlite3
import json
from datetime import datetime

from .posts_helpers import build_post_query, build_post_object


def get_all_posts(query_params):
    """Get all approved posts sorted by newest first"""

    expand = query_params.get("_expand", [])

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if "category" in expand:
            db_cursor.execute(
                """
                SELECT
                    p.id,
                    p.user_id,
                    p.category_id,
                    p.title,
                    p.publication_date,
                    p.image_url,
                    p.content,
                    p.approved,
                    u.first_name || ' ' || u.last_name AS author,
                    c.id AS cat_id,
                    c.label AS cat_label
                FROM Posts p
                JOIN Users u ON p.user_id = u.id
                LEFT JOIN Categories c ON p.category_id = c.id
                WHERE p.approved = 1
                AND p.publication_date <= datetime('now')
                ORDER BY p.publication_date DESC
            """
            )
        else:
            db_cursor.execute(
                """
                SELECT
                    p.id,
                    p.user_id,
                    p.category_id,
                    p.title,
                    p.publication_date,
                    p.image_url,
                    p.content,
                    p.approved,
                    u.first_name || ' ' || u.last_name AS author
                FROM Posts p
                JOIN Users u ON p.user_id = u.id
                WHERE p.approved = 1
                AND p.publication_date <= datetime('now')
                ORDER BY p.publication_date DESC
            """
            )

        posts = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            post = {
                "id": row["id"],
                "user_id": row["user_id"],
                "category_id": row["category_id"],
                "title": row["title"],
                "publication_date": row["publication_date"],
                "image_url": row["image_url"],
                "content": row["content"],
                "approved": row["approved"],
                "author": row["author"],
            }

            if "category" in expand:
                post["category"] = {"id": row["cat_id"], "label": row["cat_label"]}

            posts.append(post)

    return json.dumps(posts)


def get_post_by_id(post_id, query_params):
    """Get a single post by its ID"""

    expand = query_params.get("_expand", [])

    # Build query dynamically based on expand parameters using helper function
    # select_clause: string of fields to select
    # join_clause: string of JOIN statements needed for the query
    select_clause, join_clause = build_post_query(expand)

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        query = f"""
            SELECT
                {select_clause}
            FROM Posts p
            {join_clause}
            WHERE p.id = ?
        """

        # execute the query with the post_id parameter to prevent SQL injection
        db_cursor.execute(query, (post_id,))

        # Fetch the single post row (if it exists)
        post_row_data = db_cursor.fetchone()

        if post_row_data:
            # Build the post object using the helper function
            # build_post_object takes the database row and the expand parameters
            # to construct the final post dictionary
            post_dictionary = build_post_object(post_row_data, expand)
            return json.dumps(post_dictionary)

    return json.dumps({"error": "Post not found."})


def get_posts_by_user_id(user_id, query_params):
    """Get all posts for a specific user"""

    expand = query_params.get("_expand", [])

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if "category" in expand:
            db_cursor.execute(
                """
            SELECT
                p.id,
                p.user_id,
                p.category_id,
                p.title,
                p.publication_date,
                p.image_url,
                p.content,
                p.approved,
                u.first_name || ' ' || u.last_name AS author,
                c.id AS cat_id,
                c.label AS cat_label
            FROM Posts p
            JOIN Users u ON p.user_id = u.id
            JOIN Categories c ON p.category_id = c.id
            WHERE p.user_id = ?
            """,
                (user_id,),
            )
        else:
            db_cursor.execute(
                """
            SELECT
                p.id,
                p.user_id,
                p.category_id,
                p.title,
                p.publication_date,
                p.image_url,
                p.content,
                p.approved,
                u.first_name || ' ' || u.last_name AS author
            FROM Posts p
            JOIN Users u ON p.user_id = u.id
            WHERE p.user_id = ?
            """,
                (user_id,),
            )

        posts = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            post = {
                "id": row["id"],
                "user_id": row["user_id"],
                "category_id": row["category_id"],
                "title": row["title"],
                "publication_date": row["publication_date"],
                "image_url": row["image_url"],
                "content": row["content"],
                "approved": row["approved"],
                "author": row["author"],
            }

            if "category" in expand:
                post["category"] = {
                    "id": row["cat_id"],
                    "label": row["cat_label"],
                }

            posts.append(post)

    return json.dumps(posts)

def _add_tags_to_post(db_cursor, post_id, tag_ids):
    for tag_id in tag_ids:
        db_cursor.execute(
            "INSERT INTO PostTags (post_id, tag_id) VALUES (?, ?)",
            (post_id, tag_id)
        )

def create_post(post):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
            INSERT INTO Posts (user_id, category_id, title, publication_date, image_url, content, approved)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            post["user_id"],
            post["category_id"],
            post["title"],
            datetime.now().isoformat(),
            post["image_url"],
            post["content"]
        ))


        post_id = db_cursor.lastrowid


        _add_tags_to_post(db_cursor, post_id, post.get("tag_ids", []))


        return json.dumps({"id": post_id})



def update_post(post_id, post_data):
    """Update an existing post with new data"""

    try:
        with sqlite3.connect("./db.sqlite3") as conn:
            db_cursor = conn.cursor()

            db_cursor.execute(
                """
                UPDATE Posts
                SET user_id = ?, 
                category_id = ?, 
                title = ?, 
                publication_date = ?, 
                image_url = ?, 
                content = ?, 
                approved = ?
                WHERE id = ?
                """,
                (
                    post_data["user_id"],
                    post_data["category_id"],
                    post_data["title"],
                    post_data["publication_date"],
                    post_data["image_url"],
                    post_data["content"],
                    post_data["approved"],
                    post_id,
                ),
            )

            if db_cursor.rowcount == 0:
                return json.dumps({"error": "Post not found."})

            return json.dumps({"message": "Post updated successfully."})

    except sqlite3.Error as e:
        return json.dumps({"error": str(e)})

def delete_post(post_id):
    """Delete a post by id"""
    #Added try/except block to catch any potential database errors and return them as JSON error messages
    try:
        with sqlite3.connect("./db.sqlite3") as conn:
            db_cursor = conn.cursor()

            db_cursor.execute(
                """
                DELETE FROM Posts
                WHERE id = ?
                """,
                (post_id,),
            )

            if db_cursor.rowcount == 0:
                return json.dumps({"error": "Post not found"})

        return json.dumps({"message": "Post deleted successfully"})
    
    except sqlite3.Error as e:
        return json.dumps({"error": str(e)})