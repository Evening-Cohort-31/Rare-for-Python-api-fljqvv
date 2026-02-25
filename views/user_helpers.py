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
