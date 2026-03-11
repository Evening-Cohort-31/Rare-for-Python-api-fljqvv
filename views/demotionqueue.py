"""Module for handling demotion queue related requests."""

import sqlite3
import json


def get_demotion_queue_by_target_id_status_pending(query_params):
    """Get all demotion queue entries with status 'pending' for a given target id"""

    target_id = query_params.get("target_id", [None])[0]

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT *
            FROM DemotionQueue
            WHERE target_admin_id = ? AND status = 'pending'
            """,
            (target_id,),
        )

        demotion_queue_row_data = db_cursor.fetchall()

        if demotion_queue_row_data:
            demotion_queue_entries = [dict(row) for row in demotion_queue_row_data]
        else:
            demotion_queue_entries = []

    return json.dumps(demotion_queue_entries)


def create_demotion_queue_entry(request_body):
    """Create a new demotion queue entry Unless last admin"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT COUNT(*) as admin_count
            FROM Users
            WHERE is_admin = 1
            """
        )
        admin_count = db_cursor.fetchone()["admin_count"]
        if admin_count <= 1:
            return json.dumps(
                {
                    "error": "Cannot create demotion queue entry. At least one admin must remain."
                }
            )

        db_cursor.execute(
            """
            SELECT id FROM DemotionQueue
            WHERE target_admin_id = ? AND status = 'pending'
            """,
            (request_body["target_admin_id"],),
        )
        if db_cursor.fetchone():
            return json.dumps(
                {"error": "A pending demotion already exists for this user."}
            )

        db_cursor.execute(
            """
            INSERT INTO DemotionQueue 
            (action,
            target_admin_id,
            initiator_id,
            status,
            created_on)
                VALUES (?, ?, ?, 'pending', ?)
                """,
            (
                request_body["action"],
                request_body["target_admin_id"],
                request_body["initiator_id"],
                request_body["created_on"],
            ),
        )

        new_entry_id = db_cursor.lastrowid

    return json.dumps({"id": new_entry_id})


def update_demotion_queue_entry(entry_id, request_body):
    """Update an existing demotion queue entry unless last admin"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # If the status is being updated to 'approved', check if the target admin is the last one
        if request_body.get("status") == "approved":
            db_cursor.execute(
                """
                SELECT COUNT(*) as admin_count
                FROM Users
                WHERE is_admin = 1
                """
            )
            admin_count = db_cursor.fetchone()["admin_count"]
            if admin_count <= 1:
                return json.dumps(
                    {
                        "error": "Cannot approve demotion. At least one admin must remain."
                    }
                )

        db_cursor.execute(
            """
            UPDATE DemotionQueue
            SET approver_id = ?, status = ?, completed_on = ?
            WHERE id = ?
            """,
            (
                request_body["approver_id"],
                request_body["status"],
                request_body["completed_on"],
                entry_id,
            ),
        )

        if db_cursor.rowcount == 0:
            return json.dumps({"error": "Entry not found."})

        conn.commit()

    return json.dumps({"id": entry_id})


def delete_demotion_queue_entry(entry_id):
    """Delete a demotion queue entry if status is still pending"""

    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            DELETE FROM DemotionQueue
            WHERE id = ? AND status = 'pending'
            """,
            (entry_id,),
        )

        if db_cursor.rowcount == 0:
            return json.dumps(
                {"error": "Entry not found or not in pending status."}
            )

        conn.commit()

    return json.dumps({"id": entry_id})
