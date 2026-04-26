"""
utils/provenance.py
Single utility function that writes every data-modifying event to provenance_log.
Every module that changes data MUST call write_provenance().
"""

import json
import streamlit as st
from db import execute


def write_provenance(
    source_table: str,
    row_pk: str,
    operation_type: str,
    actor_id: str,
    actor_role: str,
    why: str,
    where_page: str,
    how: str,
    old_value=None,
    new_value=None,
    request_id: int = None, # type: ignore
):
    """
    Insert a row into provenance_log.

    operation_type must be one of:
        'ADD', 'DROP', 'UPDATE', 'INSERT', 'DELETE', 'APPROVE', 'AUTO-ADVISE'
    """
    old_str = json.dumps(old_value) if old_value is not None else None
    new_str = json.dumps(new_value) if new_value is not None else None

    sql = """
        INSERT INTO provenance_log (
            source_table, row_pk, operation_type,
            users_user_id, actor_role,
            why_provenance, where_provenance, how_provenance,
            old_value, new_value, request_id
        ) VALUES (
            :source_table, :row_pk, :op_type,
            :actor_id, :actor_role,
            :why, :where_page, :how,
            :old_val, :new_val, :req_id
        )
    """
    execute(sql, {
        "source_table": source_table[:50],
        "row_pk": str(row_pk)[:100],
        "op_type": operation_type,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "why": (why or "")[:300],
        "where_page": (where_page or "")[:300],
        "how": (how or "")[:300],
        "old_val": old_str,
        "new_val": new_str,
        "req_id": request_id,
    }, commit=True)
