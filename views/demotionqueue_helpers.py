"""Helper functions for demotion queue queries and objects."""


def build_demotion_queue_query(query_params):
    """Build SELECT query and params for demotion queue filters."""

    base_query = """
        SELECT
            dq.id,
            dq.action,
            dq.target_admin_id,
            dq.initiator_id,
            dq.approver_id,
            dq.status,
            dq.created_on,
            dq.completed_on
        FROM DemotionQueue dq
    """

    conditions = []
    params = []

    if "id" in query_params:
        conditions.append("dq.id = ?")
        params.append(query_params["id"][0])

    if "target_admin_id" in query_params:
        conditions.append("dq.target_admin_id = ?")
        params.append(query_params["target_admin_id"][0])

    if "initiator_id" in query_params:
        conditions.append("dq.initiator_id = ?")
        params.append(query_params["initiator_id"][0])

    if "approver_id" in query_params:
        conditions.append("dq.approver_id = ?")
        params.append(query_params["approver_id"][0])

    if "status" in query_params:
        conditions.append("dq.status = ?")
        params.append(query_params["status"][0])

    if "action" in query_params:
        conditions.append("dq.action = ?")
        params.append(query_params["action"][0])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY dq.created_on DESC"

    return base_query, params


def build_demotion_queue_object(row):
    """Convert a demotion queue row into a dictionary."""

    return {
        "id": row["id"],
        "action": row["action"],
        "target_admin_id": row["target_admin_id"],
        "initiator_id": row["initiator_id"],
        "approver_id": row["approver_id"],
        "status": row["status"],
        "created_on": row["created_on"],
        "completed_on": row["completed_on"],
    }
