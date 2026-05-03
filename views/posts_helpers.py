"""Module for helper functions related to posts."""


def build_post_query(expand_params):
    """Helper function to dynamically build SQL query based on expand parameters.

    Args:
        expand_params: List of strings indicating what to expand (e.g., ['category', 'user'])

    Returns:
        Tuple of (select_clause, join_clause) as strings
    """
    # Base SELECT fields
    select_fields = [
        "p.id",
        "p.user_id",
        "p.category_id",
        "p.title",
        "p.publication_date",
        "p.image_url",
        "p.content",
        "p.approved",
        "u.first_name || ' ' || u.last_name AS author",
    ]

    # Base JOIN - always join Users for author
    joins = ["JOIN Users u ON p.user_id = u.id"]

    # Add category fields and join if requested
    if "category" in expand_params:
        # Add category fields to select clause with aliases
        select_fields.extend(["c.id AS cat_id", "c.label AS cat_label"])
        # Add LEFT JOIN for Categories since not all posts may have a category
        joins.append("LEFT JOIN Categories c ON p.category_id = c.id")

    # Add user fields if requested (for full user object)
    if "user" in expand_params:
        select_fields.extend(
            [
                "u.id AS user_obj_id",
                "u.first_name AS user_first_name",
                "u.last_name AS user_last_name",
                "u.email AS user_email",
                "u.bio AS user_bio",
                "u.username AS user_username",
                "u.profile_image_url AS user_profile_image_url",
            ]
        )

    # Join the select fields and join clauses into strings for the final query
    select_clause = ",\n                    ".join(select_fields)
    join_clause = "\n                ".join(joins)

    return select_clause, join_clause


def build_post_object(row, expand_params):
    """Helper function to build post object from database row.

    Args:
        row: sqlite3.Row object from database query
        expand_params: List of strings indicating what to expand

    Returns:
        Dictionary representing the post object
    """
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

    # Add category object if expanded
    if "category" in expand_params:
        post["category"] = {"id": row["cat_id"], "label": row["cat_label"]}

    # Add user object if expanded
    if "user" in expand_params:
        post["user"] = {
            "id": row["user_obj_id"],
            "first_name": row["user_first_name"],
            "last_name": row["user_last_name"],
            "email": row["user_email"],
            "bio": row["user_bio"],
            "username": row["user_username"],
            "profile_image_url": row["user_profile_image_url"],
        }

    return post
