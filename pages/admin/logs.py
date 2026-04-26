"""
pages/admin/logs.py
Provenance log viewer — five views: Timeline, By Actor, By Table, By Operation, By Request.
"""

import pandas as pd
import streamlit as st
from db import fetch_all


def _build_filters() -> tuple[str, dict]:
    """Build WHERE clause and params from sidebar filter widgets."""
    with st.sidebar:
        st.markdown("### 🔍 Log Filters")
        f_actor = st.text_input("Actor User ID", key="log_actor")
        f_role  = st.selectbox("Actor Role",
                               ["All", "STUDENT", "FACULTY", "ADMIN"], key="log_role")
        f_op    = st.multiselect("Operation Type",
                                 ["ADD", "DROP", "UPDATE", "INSERT", "DELETE",
                                  "APPROVE", "AUTO-ADVISE"],
                                 key="log_op")
        f_table = st.multiselect("Source Table", key="log_table",
                                 options=["enrollments", "registration_requests",
                                          "course_sections", "advising_windows",
                                          "users", "course_offerings", "faculty_messages"])
        f_req   = st.number_input("Request ID", min_value=0, value=0, key="log_req")
        f_from  = st.date_input("From Date", value=None, key="log_from")
        f_to    = st.date_input("To Date",   value=None, key="log_to")

    clauses = ["1=1"]
    params: dict = {}

    if f_actor:
        clauses.append("users_user_id = :actor")
        params["actor"] = f_actor.strip()
    if f_role != "All":
        clauses.append("actor_role = :role")
        params["role"] = f_role
    if f_op:
        placeholders = ", ".join(f":op{i}" for i in range(len(f_op)))
        clauses.append(f"operation_type IN ({placeholders})")
        for i, v in enumerate(f_op):
            params[f"op{i}"] = v
    if f_table:
        placeholders = ", ".join(f":tbl{i}" for i in range(len(f_table)))
        clauses.append(f"source_table IN ({placeholders})")
        for i, v in enumerate(f_table):
            params[f"tbl{i}"] = v
    if f_req:
        clauses.append("request_id = :req")
        params["req"] = f_req
    if f_from:
        clauses.append("TRUNC(event_time) >= :dfrom")
        params["dfrom"] = f_from
    if f_to:
        clauses.append("TRUNC(event_time) <= :dto")
        params["dto"] = f_to

    return " AND ".join(clauses), params


def _get_flat_logs(where: str, params: dict) -> list[dict]:
    return fetch_all(
        f"""
        SELECT log_id, source_table, row_pk, operation_type,
               users_user_id AS actor,
               actor_role,
               TO_CHAR(event_time,'YYYY-MM-DD HH24:MI:SS') AS event_time,
               why_provenance   AS why,
               where_provenance AS where_pg,
               how_provenance   AS how,
               old_value, new_value, request_id
        FROM   provenance_log
        WHERE  {where}
        ORDER  BY event_time DESC
        FETCH FIRST 500 ROWS ONLY
        """,
        params,
    )


def render():
    st.title("📜 Provenance Log")

    where, params = _build_filters()
    logs = _get_flat_logs(where, params)

    st.caption(f"Showing up to 500 entries — **{len(logs)}** found")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🕐 Timeline", "👤 By Actor", "📋 By Table", "⚙️ By Operation", "🔗 By Request"]
    )

    # ── Tab 1: Timeline ───────────────────────────────────────────────────────
    with tab1:
        if not logs:
            st.info("No log entries match the current filters.")
        else:
            for log in logs:
                with st.expander(
                    f"[{log['event_time']}] {log['operation_type']} on {log['source_table']} "
                    f"by {log['actor']} ({log['actor_role']})"
                ):
                    col1, col2 = st.columns(2)
                    col1.markdown(f"**Log ID:** {log['log_id']}")
                    col1.markdown(f"**Table:** {log['source_table']}")
                    col1.markdown(f"**Row PK:** {log['row_pk']}")
                    col1.markdown(f"**Operation:** {log['operation_type']}")
                    col2.markdown(f"**Actor:** {log['actor']}")
                    col2.markdown(f"**Role:** {log['actor_role']}")
                    col2.markdown(f"**Request ID:** {log['request_id'] or '—'}")
                    if log["why"]:
                        st.markdown(f"**Why:** {log['why']}")
                    if log["how"]:
                        st.markdown(f"**How:** {log['how']}")
                    if log["old_value"]:
                        st.markdown("**Old Value:**")
                        st.code(log["old_value"], language="json")
                    if log["new_value"]:
                        st.markdown("**New Value:**")
                        st.code(log["new_value"], language="json")

            # Export
            df_export = pd.DataFrame([{
                k: v for k, v in l.items() if k not in ("old_value", "new_value")
            } for l in logs])
            csv = df_export.to_csv(index=False).encode()
            st.download_button("⬇️ Download CSV", csv, "provenance_log.csv", "text/csv")

    # ── Tab 2: By Actor ───────────────────────────────────────────────────────
    with tab2:
        if not logs:
            st.info("No data.")
        else:
            actor_data: dict[str, dict] = {}
            for log in logs:
                a = log["actor"]
                if a not in actor_data:
                    actor_data[a] = {"actor": a, "role": log["actor_role"],
                                     "count": 0, "last_active": log["event_time"]}
                actor_data[a]["count"] += 1

            df = pd.DataFrame(list(actor_data.values()))
            df.columns = ["Actor ID", "Role", "Operations", "Last Active"]
            st.dataframe(df.sort_values("Operations", ascending=False),
                         use_container_width=True, hide_index=True)

    # ── Tab 3: By Table ───────────────────────────────────────────────────────
    with tab3:
        if not logs:
            st.info("No data.")
        else:
            tbl_data: dict[str, dict] = {}
            for log in logs:
                t = log["source_table"]
                if t not in tbl_data:
                    tbl_data[t] = {"table": t, "count": 0, "last": log["event_time"]}
                tbl_data[t]["count"] += 1

            df = pd.DataFrame(list(tbl_data.values()))
            df.columns = ["Table", "Total Operations", "Most Recent"]
            st.dataframe(df.sort_values("Total Operations", ascending=False),
                         use_container_width=True, hide_index=True)

    # ── Tab 4: By Operation ───────────────────────────────────────────────────
    with tab4:
        if not logs:
            st.info("No data.")
        else:
            op_data: dict[str, int] = {}
            for log in logs:
                op = log["operation_type"]
                op_data[op] = op_data.get(op, 0) + 1

            df = pd.DataFrame(
                [{"Operation Type": k, "Count": v} for k, v in op_data.items()]
            ).sort_values("Count", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Tab 5: By Request ─────────────────────────────────────────────────────
    with tab5:
        req_logs = [l for l in logs if l["request_id"]]
        if not req_logs:
            st.info("No request-linked log entries in the current filter.")
        else:
            req_groups: dict[int, list] = {}
            for log in req_logs:
                rid = log["request_id"]
                req_groups.setdefault(rid, []).append(log)

            for rid, entries in sorted(req_groups.items(), reverse=True):
                with st.expander(f"Request #{rid} — {len(entries)} log entries"):
                    for e in entries:
                        st.markdown(
                            f"**{e['event_time']}** | {e['operation_type']} on "
                            f"`{e['source_table']}` by {e['actor']}"
                        )
                        if e["why"]:
                            st.caption(f"Why: {e['why']}")
