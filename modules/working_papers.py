import os
import pandas as pd
import streamlit as st

from utils.common import load_clients


def show_working_papers():

    st.subheader("🗂️ Working Papers")

    df = load_clients()

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0 if len(client_list) > 0 else None,
        placeholder="Search client name..."
    )

    if len(df) > 0 and selected_client:

        selected_row = df[df["Client Name"] == selected_client].iloc[0]
        selected_ay = selected_row["AY"]

        wp_path = f"clients/{selected_client}/AY {selected_ay}/working_papers_tracker.xlsx"

        if os.path.exists(wp_path):

            wp_df = pd.read_excel(wp_path)

            wp_df["Working Paper"] = wp_df["Working Paper"].astype(str)
            wp_df["Clause Reference"] = wp_df["Clause Reference"].astype(str)
            wp_df["Status"] = wp_df["Status"].astype(str)
            wp_df["Prepared By"] = wp_df["Prepared By"].astype(str)
            wp_df["Reviewed By"] = wp_df["Reviewed By"].astype(str)
            wp_df["Remarks"] = wp_df["Remarks"].astype(str)

            wp_df = wp_df.replace("nan", "")

            st.write(f"### Working Papers for {selected_client} - AY {selected_ay}")

            edited_wp_df = st.data_editor(
                wp_df,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=[
                            "Pending",
                            "In Progress",
                            "Completed",
                            "Under Review"
                        ],
                        required=True
                    ),
                    "Prepared By": st.column_config.TextColumn(
                        "Prepared By"
                    ),
                    "Reviewed By": st.column_config.TextColumn(
                        "Reviewed By"
                    ),
                    "Remarks": st.column_config.TextColumn(
                        "Remarks"
                    )
                },
                disabled=[
                    "Working Paper",
                    "Clause Reference"
                ]
            )

            if st.button("💾 Save Working Papers"):

                edited_wp_df.to_excel(wp_path, index=False)

                total_wp = len(edited_wp_df)

                completed_wp = len(
                    edited_wp_df[
                        edited_wp_df["Status"] == "Completed"
                    ]
                )

                wp_completion = round(
                    (completed_wp / total_wp) * 100,
                    2
                )

                st.success(
                    f"✅ Working Papers Updated! Completion: {wp_completion}%"
                )

                st.rerun()

            # Completion Dashboard
            st.subheader("📊 Working Paper Completion Dashboard")

            wp_report_df = pd.read_excel(wp_path)
            wp_report_df["Status"] = wp_report_df["Status"].astype(str)

            total_wp = len(wp_report_df)
            completed_wp = len(wp_report_df[wp_report_df["Status"] == "Completed"])
            pending_wp = len(wp_report_df[wp_report_df["Status"] == "Pending"])
            in_progress_wp = len(wp_report_df[wp_report_df["Status"] == "In Progress"])
            under_review_wp = len(wp_report_df[wp_report_df["Status"] == "Under Review"])

            wp_completion_percentage = round((completed_wp / total_wp) * 100, 2)

            wp_col1, wp_col2, wp_col3, wp_col4, wp_col5 = st.columns(5)

            with wp_col1:
                st.metric("Total WPs", total_wp)

            with wp_col2:
                st.metric("Completed", completed_wp)

            with wp_col3:
                st.metric("Pending", pending_wp)

            with wp_col4:
                st.metric("In Progress", in_progress_wp)

            with wp_col5:
                st.metric("Completion %", wp_completion_percentage)

            st.write("### Pending / Incomplete Working Papers")

            incomplete_wp_df = wp_report_df[
                wp_report_df["Status"].isin([
                    "Pending",
                    "In Progress",
                    "Under Review"
                ])
            ]

            st.dataframe(incomplete_wp_df, use_container_width=True)

        else:
            st.warning("Working paper tracker file not found.")

    else:
        st.info("Please select a client.")
        