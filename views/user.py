"""Module for handling user related database queries and operations"""

import sqlite3
import json
from datetime import datetime
from .user_helpers import serialize_user


def get_all_users():
    """Gets all users from the database and returns them as a JSON string"""
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
        """
        )

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
        values (?, ?, ?, ?, ?, ?, ?, 1, 0)
        """,
            (
                user["first_name"],
                user["last_name"],
                user["username"],
                user["email"],
                user["password"],
                user["bio"],
                datetime.now(),
            ),
        )

        id = db_cursor.lastrowid

        return json.dumps({"token": id, "valid": True})
