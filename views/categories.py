"""Module for handling categories related requests."""

import sqlite3
import json


def get_all_categories():
    """Get all categories"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        SELECT
            id,
            label
        FROM Categories
        """
        )

        # Initialize an empty list to hold the categories
        categories = []

        # get a list of dictionaries where each dictionary represents a row in the dataset
        # example of what the list of dictionaries would look like:
        # [
        #     {"id": 1, "label": "News"},
        #     {"id": 2, "label": "Sports"},
        #     {"id": 3, "label": "Tech"},
        # ]
        cat_list_dicts = db_cursor.fetchall()

        if len(cat_list_dicts) == 0:
            return json.dumps({"error": "No categories found"})

        # Iterate over each row and build a standard Python dictionary for each category
        for row in cat_list_dicts:
            category = {
                "id": row["id"],
                "label": row["label"],
            }
            categories.append(category)

        # Convert Python list of dictionaries to JSON string for HTTP response
        # Example: [{"id": 1, "label": "News"}, {"id": 2, "label": "Sports"}]
        # becomes: '[{"id": 1, "label": "News"}, {"id": 2, "label": "Sports"}]'
        json_response = json.dumps(categories)

    return json_response


def get_category_by_id(category_id):
    """Get a single category by id"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT
                id,
                label
            FROM Categories
            WHERE id = ?
            """,
            (category_id,),
        )

        # Use fetchone() to get a single row from the result set
        row = db_cursor.fetchone()

        if row is None:
            return json.dumps({"error": "Category not found"})

        category = {
            "id": row["id"],
            "label": row["label"],
        }

    return json.dumps(category)


def create_category(category):
    """Create a new category"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO Categories (label)
            VALUES (?)
            """,
            (category["label"],),
        )

        # Get the id of the newly created category
        category_id = db_cursor.lastrowid

        json_response = json.dumps({"id": category_id, "label": category["label"]})

    return json_response
