"""Module for handling subscriptions related requests."""

import sqlite3
import json

def get_all_subscriptions():
    """Get all subscriptions"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT
                id,
                follower_id,
                author_id,
                created_on
            FROM Subscriptions
            """
        )

        subscriptions = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            subscriptions.append(dict(row))

    return json.dumps(subscriptions)

def create_subscription(subscription_data):
    """Subscribe to a user's posts creating a new subscription entry in the database"""

    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO
            Subscriptions(follower_id, author_id, created_on)
            VALUES (?, ?, ?)
            """,
            (
                subscription_data["follower_id"],
                subscription_data["author_id"],
                subscription_data["created_on"],
            ),
        )

        #Get the ID of the newly created subscription
        new_subscription_id = db_cursor.lastrowid

        #Commit the transaction to save the new subscription
        conn.commit()

        created_subscription = {
            "id": new_subscription_id,
            "follower_id": subscription_data["follower_id"],
            "author_id": subscription_data["author_id"],
            "created_on": subscription_data["created_on"],
        }

        return json.dumps(created_subscription)

def delete_subscription(subscription_id):
    """Delete a subscription by id"""
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            DELETE FROM Subscriptions
            WHERE id = ?
            """,
            (subscription_id,)
        )
        conn.commit()

        if db_cursor.rowcount == 0:
            return json.dumps({"error": "Subscription not found"})
        
        return json.dumps({"message": "Subscription deleted successfully"})