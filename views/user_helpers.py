"""Helper functions for user views"""


def serialize_user(row):
    """
    Helper function to serialize a user row from the database into a dictionary
    that can be returned as JSON
    """
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
        "bio": row["bio"],
        "username": row["username"],
        "password": row["password"],
        "profile_image_url": row["profile_image_url"],
        "created_on": row["created_on"],
        "active": bool(row["active"]),
        "is_staff": bool(row["is_staff"]),
    }


def users_query_builder(active=None):
    """Helper function to build the SQL query for getting users based on the active parameter"""
    base_query = """
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

    if active is not None:
        return base_query + " WHERE active = ?"
    else:
        return base_query
