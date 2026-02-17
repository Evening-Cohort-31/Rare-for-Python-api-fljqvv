"""Module for handling posts related requests."""

import sqlite3
import json


def get_all_posts(query_params):
    """Get all approved posts sorted by newest first"""

    expand = query_params.get("_expand", [])

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if "category" in expand:
            db_cursor.execute("""
                SELECT
                    p.id,
                    p.user_id,
                    p.category_id,
                    p.title,
                    p.publication_date,
                    p.image_url,
                    p.content,
                    u.first_name || ' ' || u.last_name AS author,
                    c.id AS cat_id,
                    c.label AS cat_label
                FROM Posts p
                JOIN Users u ON p.user_id = u.id
                LEFT JOIN Categories c ON p.category_id = c.id
                WHERE p.approved = 1
                AND p.publication_date <= datetime('now')
                ORDER BY p.publication_date DESC
            """)
        else:
            db_cursor.execute("""
                SELECT
                    p.id,
                    p.user_id,
                    p.category_id,
                    p.title,
                    p.publication_date,
                    p.image_url,
                    p.content,
                    u.first_name || ' ' || u.last_name AS author
                FROM Posts p
                JOIN Users u ON p.user_id = u.id
                WHERE p.approved = 1
                AND p.publication_date <= datetime('now')
                ORDER BY p.publication_date DESC
            """)

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
                "author": row["author"],
            }

            if "category" in expand:
                post["category"] = {
                    "id": row["cat_id"],
                    "label": row["cat_label"]
                }

            posts.append(post)

    return json.dumps(posts)


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
                "author": row["author"],
            }

            if "category" in expand:
                post["category"] = {
                    "id": row["cat_id"],
                    "label": row["cat_label"],
                }

            posts.append(post)

    return json.dumps(posts)

def delete_post(post_id):
    """Delete a post by id"""

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
