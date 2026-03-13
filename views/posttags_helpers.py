"""Module for handling PostTags helper functions."""


def build_posttags_select_and_joins(query_params):
    """Build the SELECT clause and necessary JOINs for PostTags queries based on _expand parameters.
    Returns a tuple of (select_sql, join_sql) where:
    - select_sql is a string of the SELECT fields to retrieve
    - join_sql is a string of the JOIN statements needed for the query

    """

    expand_values = query_params.get("_expand", [])

    select_parts = [
        "pt.id AS posttag_id",
        "pt.post_id AS posttag_post_id",
        "pt.tag_id AS posttag_tag_id",
        "pt.created_on AS posttag_created_on",
    ]

    join_parts = []

    if "post" in expand_values:
        select_parts.extend(
            [
                "p.id AS post_id",
                "p.title AS post_title",
                "p.user_id AS post_user_id",
                "p.category_id AS post_category_id",
                "p.publication_date AS post_publication_date",
                "p.image_url AS post_image_url",
                "p.content AS post_content",
                "p.approved AS post_approved",
            ]
        )
        join_parts.append("LEFT JOIN Posts p ON pt.post_id = p.id")

    if "tag" in expand_values:
        select_parts.extend(
            [
                "t.id AS tag_id",
                "t.label AS tag_label",
            ]
        )
        join_parts.append("LEFT JOIN Tags t ON pt.tag_id = t.id")

    return ", ".join(select_parts), " ".join(join_parts)


def build_posttags_where_clause(query_params):
    """Build the WHERE clause for PostTags queries based on query parameters.

    Args:
        query_params (dict): Dictionary of query parameters.

    Returns:
        tuple: A tuple containing the WHERE clause string and a list of parameters.
    """
    where_clauses = []
    params = []

    post_id_values = query_params.get("post_id")
    if post_id_values:
        where_clauses.append("pt.post_id = ?")
        params.append(int(post_id_values[0]))

    tag_id_values = query_params.get("tag_id")
    if tag_id_values:
        where_clauses.append("pt.tag_id = ?")
        params.append(int(tag_id_values[0]))

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    return where_sql, params


def serialize_posttag_row(row, query_params):
    """Serialize a database row into a PostTag dictionary, including expanded related entities if requested."""

    expand_values = query_params.get("_expand", [])

    posttag = {
        "id": row["posttag_id"],
        "post_id": row["posttag_post_id"],
        "tag_id": row["posttag_tag_id"],
        "created_on": row["posttag_created_on"],
    }

    if "post" in expand_values and row["post_id"] is not None:
        posttag["post"] = {
            "id": row["post_id"],
            "title": row["post_title"],
            "user_id": row["post_user_id"],
            "category_id": row["post_category_id"],
            "publication_date": row["post_publication_date"],
            "image_url": row["post_image_url"],
            "content": row["post_content"],
            "approved": (
                bool(row["post_approved"]) if row["post_approved"] is not None else None
            ),
        }

    if "tag" in expand_values and row["tag_id"] is not None:
        posttag["tag"] = {
            "id": row["tag_id"],
            "label": row["tag_label"],
        }

    return posttag
