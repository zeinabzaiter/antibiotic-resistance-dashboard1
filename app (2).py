import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(
    page_title="Antibiotic Resistance Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_and_process_data():
    df1 = pd.read_excel('/content/ATB cles staph aureus.xlsx')
    df2 = pd.read_excel('/content/staph aureus autre atb.xlsx')
    df3 = pd.read_excel('/content/staph aureus phenotypes R.xlsx')

    df3 = df3[~df3["Month"].isin(["Total", "Prevalence %"])]
    df3["Month"] = pd.to_datetime(df3["Month"] + " 2024", format='%B %Y', errors='coerce')
    df3 = df3.dropna(subset=["Month"])
    df3.sort_values(by="Month", inplace=True)
    df3["MoM Change (%)"] = df3["Total"].pct_change() * 100
    df3["YoY Change (%)"] = df3["Total"].pct_change(periods=12) * 100
    df3["Day"] = df3["Month"].dt.date  # Ajout ici

    return df1, df2, df3

df1, df2, df3 = load_and_process_data()

# Tabs
tab_overview, tab_metrics, tab_trends, tab_phenotypes, tab_clinical = st.tabs([
    "Overview", "Key Metrics", "Temporal Trends", "Phenotype Analysis", "Clinical Guidance"
])

# Sidebar
with st.sidebar:
    st.header("Filters")
    months_2024 = [f"{month} 2024" for month in [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]]
    start_month, end_month = st.select_slider("Select month range (2024)", options=months_2024,
                                              value=(months_2024[0], months_2024[-1]))
    start_date = pd.to_datetime(start_month)
    end_date = pd.to_datetime(end_month)
    
    day_filter = st.date_input("Filtrer un jour précis (optionnel)")  # <-- Ajout ici

    selected_phenotypes = st.multiselect("Select phenotypes to highlight",
                                         options=["MRSA", "VRSA", "Wild", "others"],
                                         default=["MRSA", "VRSA"])

# Apply date filters
if day_filter:
    filtered_df3 = df3[df3["Day"] == day_filter]
else:
    filtered_df3 = df3[(df3["Month"] >= start_date) & (df3["Month"] <= end_date)]

# Tab: Overview
with tab_overview:
    st.subheader("Dashboard Summary")

    if filtered_df3.empty:
        st.warning("Aucune donnée trouvée pour cette date ou période.")
    else:
        latest_month = filtered_df3.iloc[-1]
        mrsa_rate = (latest_month["MRSA"] / latest_month["Total"]) * 100
        vrsa_cases = latest_month["VRSA"]
        total_cases = filtered_df3["Total"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cases Analyzed", f"{total_cases:,}")
        col2.metric("Current MRSA Rate", f"{mrsa_rate:.1f}%")
        col3.metric("VRSA Cases Detected", vrsa_cases,
                    delta="⚠️ Immediate attention" if vrsa_cases > 0 else None)

        st.subheader("Resistance Alerts")
        if mrsa_rate > filtered_df3["MRSA"].sum()/filtered_df3["Total"].sum()*100 * 1.2:
            val = mrsa_rate/(filtered_df3['MRSA'].sum()/filtered_df3['Total'].sum()*100)-1
            st.warning(f"⚠️ MRSA cases are {val:.0%} above average")
        if vrsa_cases > 0:
            st.error("🚨 VRSA cases detected - immediate attention required")

        st.subheader("Phenotype Distribution Overview")
        fig_stacked = go.Figure()
        for col in selected_phenotypes:
            fig_stacked.add_trace(go.Scatter(x=filtered_df3["Month"], y=filtered_df3[col],
                                             mode="lines", stackgroup="one", name=col))
        fig_stacked.update_layout(title="Phenotype Distribution Over Time",
                                  xaxis_title="Month", yaxis_title="Cases")
        st.plotly_chart(fig_stacked, use_container_width=True)

# (le reste du code continue inchangé...)

# Tab: Key Metrics
# Tab: Temporal Trends
# Tab: Phenotype Analysis
# Tab: Clinical Guidance
# ... (tout ça reste comme dans ta version actuelle)
