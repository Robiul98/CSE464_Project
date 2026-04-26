"""
pages/admin/approvals.py
User account management: approve, reject, block, unblock.
"""

import streamlit as st
from db import fetch_all, execute
from utils.provenance import write_provenance


STATUS_BADGE = {
    "APPROVED": "🟢 APPROVED",
    "PENDING":  "🟡 PENDING",
    "REJECTED": "🔴 REJECTED",
    "BLOCKED":  "⚫ BLOCKED",
}

def _get_display_name(uid: str, role: str) -> str:
    from db import fetch_one
    if role == "STUDENT":
        # Changed :p_user_id to :p_user_id
        r = fetch_one("SELECT student_name FROM students WHERE users_user_id = :p_user_id", {"p_user_id": uid})
        return r["student_name"] if r else uid
    elif role == "FACULTY":
        # Changed :p_user_id to :p_user_id
        r = fetch_one("SELECT faculty_name FROM faculty WHERE user_id = :p_user_id", {"p_user_id": uid})
        return r["faculty_name"] if r else uid
    return uid

def _update_status(uid: str, new_status: str, admin_id: str, old_status: str):
    extra = ", approved_at = SYSTIMESTAMP, users_user_id = :admin" if new_status == "APPROVED" else ""
    if new_status == "APPROVED":
        execute(
            # Changed :p_user_id to :p_user_id
            f"UPDATE users SET account_status = :st, approved_at = SYSTIMESTAMP, users_user_id = :admin WHERE user_id = :p_user_id",
            {"st": new_status, "admin": admin_id, "p_user_id": uid},
        )
    else:
        execute(
            # Changed :p_user_id to :p_user_id
            "UPDATE users SET account_status = :st WHERE user_id = :p_user_id",
            {"st": new_status, "p_user_id": uid},
        )
    write_provenance(
        "users", uid, "UPDATE", admin_id, "ADMIN",
        f"Account status changed to {new_status}",
        "Admin / User Approvals", "Admin action",
        old_value={"account_status": old_status},
        new_value={"account_status": new_status},
    )


def _render_user_row(u: dict, admin_id: str, show_actions: list[str]):
    uid    = u["user_id"]
    status = u["account_status"]
    role   = u["role"]
    name   = _get_display_name(uid, role)

    with st.container(border=True):
        col1, col2, col3 = st.columns([2.5, 1.5, 3])
        col1.markdown(f"**{name}**  \n`{uid}`")
        col2.markdown(f"Role: **{role}**  \n{STATUS_BADGE.get(status, status)}")
        col3.markdown(f"Created: {u.get('created_at', '—')}")

        action_cols = st.columns(len(show_actions) + 1)
        for i, action in enumerate(show_actions):
            if action == "APPROVE" and status != "APPROVED":
                if action_cols[i].button("✅ Approve", key=f"appr_{uid}"):
                    _update_status(uid, "APPROVED", admin_id, status)
                    st.toast(f"{name} approved.", icon="✅")
                    st.rerun()
            if action == "REJECT" and status not in ("REJECTED",):
                if action_cols[i].button("❌ Reject", key=f"rej_{uid}"):
                    _update_status(uid, "REJECTED", admin_id, status)
                    st.toast(f"{name} rejected.", icon="❌")
                    st.rerun()
            if action == "BLOCK" and status != "BLOCKED":
                if action_cols[i].button("🚫 Block", key=f"blk_{uid}"):
                    st.session_state[f"confirm_block_{uid}"] = True
            if action == "UNBLOCK" and status == "BLOCKED":
                if action_cols[i].button("🔓 Unblock", key=f"unblk_{uid}"):
                    _update_status(uid, "APPROVED", admin_id, status)
                    st.toast(f"{name} unblocked.", icon="🔓")
                    st.rerun()

        if st.session_state.get(f"confirm_block_{uid}"):
            st.warning(f"Block account for **{name}**? They will not be able to log in.")
            c1, c2 = st.columns(2)
            if c1.button("Confirm Block", key=f"cblk_{uid}", type="primary"):
                _update_status(uid, "BLOCKED", admin_id, status)
                st.session_state.pop(f"confirm_block_{uid}", None)
                st.toast(f"{name} blocked.", icon="🚫")
                st.rerun()
            if c2.button("Cancel", key=f"cancelblk_{uid}"):
                st.session_state.pop(f"confirm_block_{uid}", None)
                st.rerun()


def render():
    st.title("👥 User Approvals & Management")
    admin_id = st.session_state.user_id

    tab1, tab2, tab3 = st.tabs(["🟡 Pending", "👤 All Users", "⚫ Blocked"])

    all_users = fetch_all(
        """
        SELECT user_id, role, account_status,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') AS created_at,
               TO_CHAR(approved_at,'YYYY-MM-DD HH24:MI') AS approved_at
        FROM   users
        ORDER  BY created_at DESC
        """,
    )

    with tab1:
        pending = [u for u in all_users if u["account_status"] == "PENDING"]
        if not pending:
            st.info("No pending accounts.")
        for u in pending:
            _render_user_row(u, admin_id, ["APPROVE", "REJECT"])

    with tab2:
        search = st.text_input("🔍 Search by User ID or Name", key="usr_search")
        role_f = st.selectbox("Filter by Role", ["All", "STUDENT", "FACULTY", "ADMIN"], key="usr_role_f")
        stat_f = st.selectbox("Filter by Status", ["All", "APPROVED", "PENDING", "REJECTED", "BLOCKED"], key="usr_stat_f")

        filtered = all_users
        if role_f != "All":
            filtered = [u for u in filtered if u["role"] == role_f]
        if stat_f != "All":
            filtered = [u for u in filtered if u["account_status"] == stat_f]
        if search:
            s = search.lower()
            filtered = [u for u in filtered if s in u["user_id"].lower()]

        st.caption(f"Showing {len(filtered)} user(s)")
        for u in filtered:
            _render_user_row(u, admin_id, ["APPROVE", "REJECT", "BLOCK", "UNBLOCK"])

    with tab3:
        blocked = [u for u in all_users if u["account_status"] == "BLOCKED"]
        if not blocked:
            st.info("No blocked accounts.")
        for u in blocked:
            _render_user_row(u, admin_id, ["UNBLOCK"])
