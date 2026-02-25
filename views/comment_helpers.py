"""Module for helper functions related to comments."""


def build_comment_query(expand_params):
    """Helper function to dynamically build SQL query based on expand parameters.

    Args:
        expand_params: List of strings indicating what to expand
        (e.g., ['author' or 'user', 'post'])

    Returns:
        Tuple of (select_clause, join_clause) as strings
    """
    # Base SELECT fields
    select_fields = [
        "c.id",
        "c.post_id",
        "c.author_id",
        "c.content",
        "c.publication_date",
    ]

    # Base JOIN - always join Users for author
    joins = ["JOIN Users u ON c.author_id = u.id"]

    # Add author fields if requested (for full user object)
    if "author" in expand_params or "user" in expand_params:
        select_fields.extend(
            [
                "u.id AS author_id",
                "u.first_name AS author_first_name",
                "u.last_name AS author_last_name",
                "u.email AS author_email",
                "u.bio AS author_bio",
                "u.username AS author_username",
                "u.profile_image_url AS author_profile_image_url",
            ]
        )

    # Add post fields if requested
    if "post" in expand_params:
        select_fields.extend(
            [
                "p.id AS post_id",
                "p.user_id AS post_user_id",
                "p.category_id AS post_category_id",
                "p.title AS post_title",
                "p.publication_date AS post_publication_date",
                "p.image_url AS post_image_url",
                "p.content AS post_content",
                "p.approved AS post_approved",
            ]
        )
        joins.append("JOIN Posts p ON c.post_id = p.id")

    # Join the select fields and join clauses into strings for the final query
    select_clause = ",\n                    ".join(select_fields)
    join_clause = "\n                ".join(joins)

    return select_clause, join_clause


def build_comment_object(row, expand_params):
    """Helper function to build comment object from database row.

    Args:
        row: sqlite3.Row object from database query
        expand_params: List of strings indicating what to expand
    Returns:
        Dictionary representing the comment object
    """
    comment = {
        "id": row["id"],
        "post_id": row["post_id"],
        "author_id": row["author_id"],
        "content": row["content"],
        "publication_date": row["publication_date"],
    }

    if "author" in expand_params or "user" in expand_params:
        comment["author"] = {
            "id": row["author_id"],
            "first_name": row["author_first_name"],
            "last_name": row["author_last_name"],
            "email": row["author_email"],
            "bio": row["author_bio"],
            "username": row["author_username"],
            "profile_image_url": row["author_profile_image_url"],
        }

    if "post" in expand_params:
        comment["post"] = {
            "id": row["post_id"],
            "user_id": row["post_user_id"],
            "category_id": row["post_category_id"],
            "title": row["post_title"],
            "publication_date": row["post_publication_date"],
            "image_url": row["post_image_url"],
            "content": row["post_content"],
            "approved": bool(row["post_approved"]),
        }

    return comment
