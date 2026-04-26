"""
pages/admin/terminal.py
Direct SQL pass-through terminal for admin.
Purpose: live demo and ad-hoc data inspection.
No LLM — raw SQL is executed directly against Oracle DB.
"""

import pandas as pd
import streamlit as st
from db import raw_execute


_DML_KEYWORDS = ("INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE")


def _is_dml(sql: str) -> bool:
    first = sql.strip().upper().split()[0] if sql.strip() else ""
    return first in _DML_KEYWORDS


def render():
    st.title("🖥️ SQL Terminal")
    st.caption(
        "Direct Oracle DB query terminal — admin use only. "
        "Type any SQL query and press Execute. Results display below."
    )

    # ── History ───────────────────────────────────────────────────────────────
    if "terminal_history" not in st.session_state:
        st.session_state.terminal_history = []

    if st.session_state.terminal_history:
        with st.expander("📋 Query History (last 10)"):
            for i, hist_sql in enumerate(reversed(st.session_state.terminal_history[-10:])):
                col1, col2 = st.columns([8, 1])
                col1.code(hist_sql, language="sql")
                if col2.button("Use", key=f"hist_{i}"):
                    st.session_state["terminal_prefill"] = hist_sql
                    st.rerun()

    # ── Input ─────────────────────────────────────────────────────────────────
    prefill = st.session_state.pop("terminal_prefill", "")

    st.markdown(
        """
        <style>
        .sql-terminal textarea {
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 14px !important;
            background-color: #1e1e1e !important;
            color: #d4d4d4 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        sql_input = st.text_area(
            "SQL>",
            value=prefill,
            height=180,
            placeholder="SELECT * FROM students WHERE ROWNUM <= 10",
            key="terminal_sql_input",
            help="Enter a valid Oracle SQL statement and click Execute.",
        )

        col1, col2 = st.columns([1, 5])
        execute_btn = col1.button("▶ Execute", type="primary", use_container_width=True)
        if col2.button("🗑 Clear", use_container_width=False):
            st.session_state["terminal_prefill"] = ""
            st.rerun()

    if not execute_btn:
        return

    sql = sql_input.strip() # type: ignore
    if not sql:
        st.warning("Please enter a SQL query.")
        return

    # DML warning
    if _is_dml(sql):
        st.warning(
            "⚠️ **DML Statement Detected** — This query may modify data. "
            "It will still execute."
        )
        if not st.session_state.get("terminal_dml_confirmed"):
            if st.button("⚠️ I understand — Execute anyway", key="dml_confirm_btn"):
                st.session_state["terminal_dml_confirmed"] = True
                st.rerun()
            return
    else:
        st.session_state.pop("terminal_dml_confirmed", None)

    # Save to history
    history = st.session_state.terminal_history
    if not history or history[-1] != sql:
        history.append(sql)
    st.session_state.terminal_history = history[-20:]

    # ── Execute ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("**Output:**")

    with st.spinner("Executing..."):
        cols, rows, error = raw_execute(sql)

    if error:
        st.markdown(
            f"<div style='background:#2d1b1b;color:#ff6b6b;padding:12px;"
            f"border-radius:6px;font-family:monospace;'>"
            f"ERROR: {error}</div>",
            unsafe_allow_html=True,
        )
        return

    if cols is None:
        # DML result
        st.success(f"✅ Statement executed. Rows affected: {rows}")
        return

    if not rows:
        st.info("Query returned 0 rows.")
        return

    df = pd.DataFrame(rows, columns=cols)
    st.caption(f"{len(df)} row(s) returned")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode()
    st.download_button(
        "⬇️ Download Results as CSV",
        csv,
        "query_result.csv",
        "text/csv",
        key="terminal_csv_dl",
    )
