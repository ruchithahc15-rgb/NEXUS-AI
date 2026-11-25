
from sqlalchemy import text

from database.config import engine


# 1. Retrieve Unresolved Payment Complaints
def get_unresolved_payment_complaints():
    query = text("""
        SELECT
            st.ticket_id,
            st.customer_id,
            c.full_name AS customer_name,
            c.email,
            st.order_id,
            st.issue_type,
            st.priority,
            st.status,
            st.created_at,
            CURRENT_DATE - st.created_at::date AS days_unresolved,
            p.payment_status

        FROM support_tickets st

        JOIN customers c
            ON st.customer_id = c.customer_id

        LEFT JOIN payments p
            ON st.order_id = p.order_id

        WHERE st.status = 'open'
          AND st.issue_type = 'Payment Failure'

        ORDER BY st.created_at ASC
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        records = result.mappings().all()

    return {
        "status": "success",
        "total_unresolved_payment_complaints": len(records),
        "data": [
            {
                "ticket_id": row["ticket_id"],
                "customer_id": row["customer_id"],
                "customer_name": row["customer_name"],
                "email": row["email"],
                "order_id": row["order_id"],
                "issue_type": row["issue_type"],
                "priority": row["priority"],
                "status": row["status"],
                "created_at": str(row["created_at"]),
                "days_unresolved": row["days_unresolved"],
                "payment_status": row["payment_status"]
            }
            for row in records
        ]
    }


# 2. Customer Complaint Summary
def get_complaint_summary():
    with engine.connect() as connection:

        # Overall ticket summary
        summary_result = connection.execute(text("""
            SELECT
                COUNT(*) AS total_tickets,
                COUNT(*) FILTER (
                    WHERE status = 'open'
                ) AS unresolved_tickets,
                COUNT(*) FILTER (
                    WHERE status = 'resolved'
                ) AS resolved_tickets
            FROM support_tickets
        """))

        summary = summary_result.mappings().first()

        # Tickets grouped by priority
        priority_result = connection.execute(text("""
            SELECT
                priority,
                COUNT(*) AS ticket_count
            FROM support_tickets
            GROUP BY priority
            ORDER BY
                CASE priority
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                END
        """))

        priorities = priority_result.mappings().all()

        # Tickets grouped by issue type
        issue_result = connection.execute(text("""
            SELECT
                issue_type,
                COUNT(*) AS ticket_count
            FROM support_tickets
            GROUP BY issue_type
            ORDER BY ticket_count DESC
        """))

        issues = issue_result.mappings().all()

    return {
        "status": "success",
        "summary": {
            "total_tickets": summary["total_tickets"],
            "unresolved_tickets": summary["unresolved_tickets"],
            "resolved_tickets": summary["resolved_tickets"]
        },
        "by_priority": [
            {
                "priority": row["priority"],
                "ticket_count": row["ticket_count"]
            }
            for row in priorities
        ],
        "by_issue_type": [
            {
                "issue_type": row["issue_type"],
                "ticket_count": row["ticket_count"]
            }
            for row in issues
        ]
    }
