"""Module for handling user related database queries and operations"""

import sqlite3
import json
from datetime import datetime
from .user_helpers import serialize_user, users_query_builder


def get_all_users(active=None):
    """Gets all users from the database and returns them as a JSON string"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        query = users_query_builder(active)

        if active is not None:
            db_cursor.execute(query, (1 if active else 0,))
        else:
            db_cursor.execute(query)

        users = []
        user_query_data = db_cursor.fetchall()

        for row in user_query_data:
            users.append(serialize_user(row))

    return json.dumps(users)


def get_user_by_id(pk):
    """Gets a single user from the database by their id and returns it as a JSON string"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT 
                id, 
                first_name, 
                last_name, 
                email, 
                bio, 
                username,
                password, 
                profile_image_url, 
                created_on, 
                active, 
                is_staff
            FROM Users
            WHERE id = ?
        """,
            (pk,),
        )

        user = db_cursor.fetchone()

        if user:
            return json.dumps(serialize_user(user))
        else:
            return json.dumps({})


def login_user(user):
    """Checks for the user in the database

    Args:
        user (dict): Contains the username and password of the user trying to login

    Returns:
        json string: If the user was found will return valid boolean of True and the user's id as the token
                     If the user was not found will return valid boolean False
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT 
                id, 
                username
            FROM Users
            WHERE username = ?
            AND password = ?
        """,
            (user["username"], user["password"]),
        )

        user_from_db = db_cursor.fetchone()

        if user_from_db is not None:
            response = {"valid": True, "token": user_from_db["id"]}
        else:
            response = {"valid": False}

        return json.dumps(response)


def create_user(user):
    """Adds a user to the database when they register

    Args:
        user (dictionary): The dictionary passed to the register post request

    Returns:
        json string: Contains the token of the newly created user
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        Insert into Users 
        (first_name, last_name, username, email, password, bio, created_on, active, is_staff) 
        values (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
            (
                user["first_name"],
                user["last_name"],
                user["username"],
                user["email"],
                user["password"],
                user["bio"],
                datetime.now(),
                1 if user.get("is_staff", False) else 0,
            ),
        )

        new_user_id = db_cursor.lastrowid

        return json.dumps({"token": new_user_id, "valid": True})


def update_user(user_id, updated_user):
    """Updates a user's information in the database

    Args:
        user_id (int): The id of the user to update
        updated_user (dict): A dictionary containing the updated user information

    Returns:
        json string: Contains the updated user information
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Guard against removing the last admin (via demotion or deactivation)
        requesting_demotion = not updated_user.get("is_staff", False)
        requesting_deactivation = not updated_user.get("active", True)
        if requesting_demotion or requesting_deactivation:
            db_cursor.execute("SELECT is_staff FROM Users WHERE id = ?", (user_id,))
            current_user = db_cursor.fetchone()
            if current_user and current_user["is_staff"]:
                db_cursor.execute(
                    "SELECT COUNT(*) as admin_count FROM Users WHERE is_staff = 1"
                )
                if db_cursor.fetchone()["admin_count"] <= 1:
                    if requesting_demotion:
                        return json.dumps({"error": "Cannot remove the last admin."})
                    if requesting_deactivation:
                        return json.dumps(
                            {"error": "Cannot deactivate the last admin."}
                        )

        db_cursor.execute(
            """
            UPDATE Users
            SET
                first_name = ?, 
                last_name = ?, 
                username = ?, 
                email = ?, 
                password = ?, 
                bio = ?, 
                profile_image_url = ?, 
                active = ?, 
                is_staff = ?
            WHERE id = ?
            """,
            (
                updated_user["first_name"],
                updated_user["last_name"],
                updated_user["username"],
                updated_user["email"],
                updated_user["password"],
                updated_user["bio"],
                updated_user.get("profile_image_url"),
                1 if updated_user.get("active", True) else 0,
                1 if updated_user.get("is_staff", False) else 0,
                user_id,
            ),
        )

        db_cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        return json.dumps(serialize_user(db_cursor.fetchone()))
