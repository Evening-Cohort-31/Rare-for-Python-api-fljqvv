"""Module for handling posts related requests."""

import sqlite3
import json


def get_all_posts():
    """Get all posts"""
    return json.dumps([])


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
