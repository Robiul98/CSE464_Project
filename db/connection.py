"""
db/connection.py
Oracle DB connection helper using oracledb (thin mode).
Credentials are read from st.secrets: DB_USER, DB_PASSWORD, DB_DSN.
"""

import oracledb
import streamlit as st


def get_connection():
    """
    Return a cached Oracle connection stored in st.session_state.
    Creates a new connection if one does not exist or has been lost.
    """
    if "db_conn" not in st.session_state or st.session_state.db_conn is None:
        _open_connection()
    else:
        # Ping to detect stale connections
        try:
            st.session_state.db_conn.ping()
        except Exception:
            _open_connection()
    return st.session_state.db_conn


def _open_connection():
    try:
        conn = oracledb.connect(
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            dsn=st.secrets["DB_DSN"],
        )
        st.session_state.db_conn = conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()


def fetch_all(sql: str, params: dict = None) -> list[dict]:
    """Execute a SELECT and return list of dicts."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or {})
        cols = [c[0].lower() for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_one(sql: str, params: dict = None) -> dict | None:
    """Execute a SELECT and return a single dict or None."""
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: dict = None, commit: bool = True):
    """Execute a DML statement."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or {})
    if commit:
        conn.commit()


def execute_many(sql: str, params_list: list[dict], commit: bool = True):
    """Execute a DML statement for a list of parameter dicts."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.executemany(sql, params_list)
    if commit:
        conn.commit()


def call_function(func_name: str, return_type, args: list):
    """Call a stored Oracle function and return its return value."""
    conn = get_connection()
    with conn.cursor() as cur:
        result = cur.callfunc(func_name, return_type, args)
    return result


def call_procedure(proc_name: str, args: list):
    """Call a stored Oracle procedure."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.callproc(proc_name, args)
    conn.commit()


def raw_execute(sql: str):
    """
    Execute raw SQL (admin terminal). Returns (columns, rows, error).
    Does not auto-commit DML — admin must be intentional.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                cols = [c[0] for c in cur.description]
                rows = cur.fetchall()
                return cols, rows, None
            else:
                conn.commit()
                rowcount = cur.rowcount
                return None, rowcount, None
    except Exception as e:
        return None, None, str(e)
