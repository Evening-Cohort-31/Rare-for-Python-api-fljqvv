"""Module for helper functions related to comments."""


def build_comment_query(expand_params):
    """Helper function to dynamically build SQL query based on expand parameters.

    Args:
        expand_params: List of strings indicating what to expand (e.g., ['post'])

    Returns:
        Tuple of (select_clause, join_clause) as strings
    """
    # Base SELECT fields — always included on every comment query
    # These are the minimum fields needed to display a comment
    select_fields = [
        "c.id",
        "c.post_id",
        "c.author_id",
        "c.content",
        "c.subject",
        "c.created_on",
        # Combine first and last name from the Users table into one "author" field
        "u.first_name || ' ' || u.last_name AS author",
    ]

    # Base JOIN — always join Users so we can display the author's name
    # c.author_id links to the Users table id
    joins = ["JOIN Users u ON c.author_id = u.id"]

    # Add post fields and join if the client requests ?_expand=post
    if "post" in expand_params:
        select_fields.extend(["p.id AS post_obj_id", "p.title AS post_title"])
        joins.append("JOIN Posts p ON c.post_id = p.id")

    # Ticket #21 - Add display_name from Users when client requests ?_expand=user
    # The client uses comment.user.display_name to show who wrote the comment
    # We map u.username to display_name since there is no display_name column in Users
    if "user" in expand_params:
        select_fields.extend(["u.username AS display_name"])

    select_clause = ",\n                    ".join(select_fields)
    join_clause = "\n                ".join(joins)

    return select_clause, join_clause


def build_comment_object(row, expand_params):
    """Helper function to build a comment dictionary from a database row.

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
        # Ticket #21 I added the subject and created_on keys to the build_comment_object
        "subject": row["subject"],
        "created_on": row["created_on"],
        "author": row["author"],
    }

    # Add post object if expanded via ?_expand=post
    if "post" in expand_params:
        comment["post"] = {
            "id": row["post_obj_id"],
            "title": row["post_title"],
        }

    # Ticket #21 - Build the user object with display_name when _expand=user is requested
    # row["display_name"] pulls the u.username value we aliased in build_comment_query
    if "user" in expand_params:
        comment["user"] = {"display_name": row["display_name"]}

    return comment


