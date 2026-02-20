"""Module for handling posts related requests."""

import sqlite3
import json
from datetime import datetime


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
