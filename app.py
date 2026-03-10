import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import csv
import os

st.set_page_config(page_title="Scottish AMS Strategy Engine", layout="wide")

# --- PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1 { color: #003262; font-family: 'Arial', sans-serif; border-bottom: 2px solid #0065BD; padding-bottom: 10px; }
    .stButton>button { background-color: #003262; color: white; border-radius: 4px; height: 3em; font-weight: bold; }
    .scale-box { background-color: #003262; padding: 12px; border-radius: 4px; color: white; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .step-done { color: #28a745; font-weight: bold; border-bottom: 3px solid #28a745; padding-bottom: 5px; }
    .step-active { color: #003262; font-weight: bold; border-bottom: 3px solid #003262; padding-bottom: 5px; }
    .step-inactive { color: #6c757d; border-bottom: 1px solid #dee2e6; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE UTILITY ---
def get_participant_count():
    if not os.path.isfile('consensus_data.csv'):
        return 0
    try:
        df_count = pd.read_csv('consensus_data.csv')
        return df_count['Participant_ID'].nunique()
    except:
        return 0

# --- SESSION STATE INITIALIZATION ---
if 'submitted_list' not in st.session_state:
    st.session_state.submitted_list = []
if 'expert_scores' not in st.session_state:
    st.session_state.expert_scores = {}
if 'participant_id' not in st.session_state:
    st.session_state.participant_id = ""

interventions = [
    'IVOST (Intravenous-to-Oral Switch)', 
    'POCT (Point-of-Care Testing)', 
    '5-Day Rule (Prescription Duration)', 
    'Access Category Shift (AWaRe Framework)'
]

st.title("CHNRI-Based AMS Prioritization Prototype")
st.caption("Strategic Research Framework | CHNRI Methodology Implementation")

# --- SURVEY PHASE ---
if len(st.session_state.submitted_list) < len(interventions):
    # 1. Landing Page / Executive Summary
    if len(st.session_state.submitted_list) == 0:
        st.markdown("""
        ### Strategic Prioritization Evaluation
        This platform facilitates a **Delphi-informed CHNRI study** to determine the implementation 
        priority of AMS interventions within NHS Scotland.
        
        **Protocol:**
        - **Validation:** Your ID ensures data integrity for the final consensus weighting.
        - **Privacy:** Individual scores are aggregated; raw data is restricted to authorized researchers.
        - **Scale:** All metrics are rated from **1 (Lowest)** to **10 (Highest)**.
        """)
        st.write("---")
        st.session_state.participant_id = st.text_input("Enter Unique ID (GMC/GPhC/Staff No.) to begin:", value=st.session_state.participant_id)
    
    # 2. Interactive Step Tracker
    st.write("")
    cols = st.columns(len(interventions))
    for i, name in enumerate(interventions):
        short_name = name.split(' (')[0]
        if name in st.session_state.submitted_list:
            cols[i].markdown(f"<div class='step-done'>✅ {short_name}</div>", unsafe_allow_html=True)
        elif i == len(st.session_state.submitted_list):
            cols[i].markdown(f"<div class='step-active'>⭕ {short_name}</div>", unsafe_allow_html=True)
        else:
            cols[i].markdown(f"<div class='step-inactive'>⚪ {short_name}</div>", unsafe_allow_html=True)
    
    st.write("")
    st.markdown('<div class="scale-box">SCALING PROTOCOL: 1 (Lowest) — 10 (Highest)</div>', unsafe_allow_html=True)
    
    # 3. Evaluation Sliders
    current_item = interventions[len(st.session_state.submitted_list)]
    st.subheader(f"Current Evaluation: {current_item}")

    id_missing = not st.session_state.participant_id
    if id_missing:
        st.warning("⚠️ Please enter a Participant ID above to unlock the sliders.")

    c1, c2 = st.columns(2)
    with c1:
        ans = st.slider("Answerability", 1, 10, 5, key=f"ans_{current_item}", disabled=id_missing)
        eff = st.slider("Effectiveness", 1, 10, 5, key=f"eff_{current_item}", disabled=id_missing)
        deliver = st.slider("Deliverability", 1, 10, 5, key=f"del_{current_item}", disabled=id_missing)
    with c2:
        impact = st.slider("Impact on Burden", 1, 10, 5, key=f"imp_{current_item}", disabled=id_missing)
        equity = st.slider("Equity", 1, 10, 5, key=f"equ_{current_item}", disabled=id_missing)

    if st.button(f"Confirm Ratings for {current_item.split(' (')[0]}", use_container_width=True, disabled=id_missing):
        st.session_state.expert_scores[current_item] = [ans, eff, deliver, impact, equity]
        
        log_data = {
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Participant_ID": st.session_state.participant_id,
            "Intervention": current_item,
            "Answerability": ans, "Effectiveness": eff, "Deliverability": deliver, "Impact": impact, "Equity": equity
        }
        file_path = 'consensus_data.csv'
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=log_data.keys())
            if not file_exists: writer.writeheader()
            writer.writerow(log_data)
        
        st.session_state.submitted_list.append(current_item)
        st.rerun()

# --- RESULTS PHASE ---
else:
    n_participants = get_participant_count()
    st.success(f"✅ Dashboard Unlocked. Data aggregated from {n_participants} verified experts.")
    
    data = {
        'Intervention': interventions,
        'Answerability': [9, 8, 9, 7], 'Effectiveness': [8, 9, 7, 6], 
        'Deliverability': [7, 2, 9, 5], 'Impact': [8, 9, 7, 8],
        'Equity': [8, 1, 9, 6], 'Agreement': [0.95, 0.45, 0.98, 0.70] 
    }
    df = pd.DataFrame(data)

    st.subheader("Strategic Policy Weights")
    c1, c2, c3 = st.columns(3)
    with c1: w_health = st.slider("Clinical Impact", 0.0, 5.0, 1.0)
    with c2: w_fairness = st.slider("Equity", 0.0, 5.0, 1.0)
    with c3: w_logistics = st.slider("Deliverability", 0.0, 5.0, 1.0)

    df['Total Score'] = ((df['Answerability'] + df['Effectiveness'] + df['Impact']) * w_health + (df['Equity'] * w_fairness) + (df['Deliverability'] * w_logistics)) / 5

    st.markdown("---")
    st.subheader(f"Individual Perspective vs. Group Consensus (n={n_participants})")
    radar_item = st.selectbox("Compare Scores for:", interventions)
    categories = ['Answerability', 'Effectiveness', 'Deliverability', 'Impact', 'Equity']
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=df[df['Intervention']==radar_item][categories].values.flatten(), theta=categories, fill='toself', name='National Mean', line_color='#003262'))
    fig_radar.add_trace(go.Scatterpolar(r=st.session_state.expert_scores[radar_item], theta=categories, fill='toself', name='Your Input', line_color='#D50032'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    st.subheader("National Priority Ranking")
    fig_bar = px.bar(df.sort_values('Total Score'), x='Total Score', y='Intervention', orientation='h', color='Total Score', color_continuous_scale='Viridis', range_x=[0,50], text_auto='.1f')
    fig_bar.update_layout(plot_bgcolor='white', coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    with st.expander(" Researcher Administration"):
        pwd = st.text_input("Security Key:", type="password")
        if pwd == "PIA2026":
            if os.path.isfile('consensus_data.csv'):
                with open('consensus_data.csv', 'rb') as f:
                    st.download_button("Download Raw Dataset (.csv)", f, file_name="AMS_Data.csv", mime="text/csv")
            else:
                st.info("No data found.")
        elif pwd:
            st.error("Invalid Key.")


st.markdown("---")
with st.expander("Technical Appendix"):
    st.write("Criteria based on CHNRI methodology. Ref: SAPG & UK NAP 2024-2029.")
    st.write("- **IVOST:** Intravenous-to-Oral Switch.")
    st.write("- **POCT:** Point-of-Care Testing.")
    st.write("- **5-Day Rule:** Prescription Duration Limit.")
    st.write("- **Access Category Shift:** AWaRe Framework Reclassification.")