"""Module for handling demotion queue related requests."""

import sqlite3
import json
from datetime import datetime


def get_demotion_queue_by_target_id_status_pending(query_params):
    """Get all pending demotion queue entries for a given target admin id"""

    target_id = query_params.get("target_id", [None])[0]

    if target_id is None:
        return json.dumps({"error": "target_id query parameter is required"})

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
        demotion_queue_entries = [dict(row) for row in demotion_queue_row_data]

    return json.dumps(demotion_queue_entries)


def create_demotion_queue_entry(request_body):
    """Create a new demotion queue entry unless the target admin is the last admin"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Validate target user exists and is currently an admin
        db_cursor.execute(
            """
            SELECT id, is_staff
            FROM Users
            WHERE id = ?
            """,
            (request_body["target_admin_id"],),
        )
        target_user = db_cursor.fetchone()

        if not target_user:
            return json.dumps({"error": "Target user not found."})

        if not target_user["is_staff"]:
            return json.dumps({"error": "Target user is not an admin."})

        # Ensure there will still be at least one admin
        db_cursor.execute(
            """
            SELECT COUNT(*) as admin_count
            FROM Users
            WHERE is_staff = 1
            """
        )
        admin_count = db_cursor.fetchone()["admin_count"]

        if admin_count <= 1:
            return json.dumps(
                {
                    "error": "Cannot create demotion queue entry. At least one admin must remain."
                }
            )

        # Prevent duplicate pending demotion requests
        db_cursor.execute(
            """
            SELECT id
            FROM DemotionQueue
            WHERE target_admin_id = ?
              AND status = 'pending'
            """,
            (request_body["target_admin_id"],),
        )

        if db_cursor.fetchone():
            return json.dumps(
                {"error": "A pending demotion already exists for this user."}
            )

        created_on = datetime.utcnow().isoformat()

        db_cursor.execute(
            """
            INSERT INTO DemotionQueue
                (action, target_admin_id, initiator_id, status, created_on)
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (
                request_body["action"],
                request_body["target_admin_id"],
                request_body["initiator_id"],
                created_on,
            ),
        )

        new_entry_id = db_cursor.lastrowid
        conn.commit()

    return json.dumps(
        {
            "id": new_entry_id,
            "status": "pending",
            "created_on": created_on,
        }
    )


def update_demotion_queue_entry(entry_id, request_body):
    """Approve an existing demotion queue entry unless it would demote the last admin"""

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Fetch the existing queue entry
        db_cursor.execute(
            """
            SELECT *
            FROM DemotionQueue
            WHERE id = ?
            """,
            (entry_id,),
        )
        existing_entry = db_cursor.fetchone()

        if not existing_entry:
            return json.dumps({"error": "Entry not found."})

        if existing_entry["status"] != "pending":
            return json.dumps({"error": "Only pending entries can be approved."})

        # Prevent initiator from approving their own request
        if existing_entry["initiator_id"] == request_body["approver_id"]:
            return json.dumps(
                {
                    "error": "The initiating admin cannot approve their own demotion request."
                }
            )

        # Make sure target user is still an admin
        db_cursor.execute(
            """
            SELECT is_staff
            FROM Users
            WHERE id = ?
            """,
            (existing_entry["target_admin_id"],),
        )
        target_user = db_cursor.fetchone()

        if not target_user:
            return json.dumps({"error": "Target user not found."})

        if not target_user["is_staff"]:
            return json.dumps({"error": "Target user is not an admin."})

        # Prevent demoting the last admin
        db_cursor.execute(
            """
            SELECT COUNT(*) as admin_count
            FROM Users
            WHERE is_staff = 1
            """
        )
        admin_count = db_cursor.fetchone()["admin_count"]

        if admin_count <= 1:
            return json.dumps(
                {"error": "Cannot approve demotion. At least one admin must remain."}
            )

        completed_on = datetime.utcnow().isoformat()

        db_cursor.execute(
            """
            UPDATE DemotionQueue
            SET approver_id = ?, status = ?, completed_on = ?
            WHERE id = ?
            """,
            (
                request_body["approver_id"],
                "approved",
                completed_on,
                entry_id,
            ),
        )

        conn.commit()

    return json.dumps(
        {
            "id": entry_id,
            "status": "approved",
            "completed_on": completed_on,
        }
    )


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
            return json.dumps({"error": "Entry not found or not in pending status."})

        conn.commit()

    return json.dumps({"id": entry_id})
