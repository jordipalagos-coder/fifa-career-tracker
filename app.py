import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="FCB Career Mode Tracker", layout="wide")

st.title("⚽ FCB Career Mode Tracker & Comparador d'Entrenadors")

# Base de dades d'entrenadors de referència amb perfils i pesos per a l'índex
ENTRENADORS = {
    "Hansi Flick (Gegenpressing)": {
        "Perfil": {"Possessio": 60, "Xuts": 15, "Passes": 88, "xG": 2.5, "Recuperacio": 12},
        "PesosIndex": {"Possessio": 10, "Xuts": 20, "Passes": 10, "xG": 30, "Recuperacio": 30}
    },
    "Pep Guardiola (Joc de Posició)": {
        "Perfil": {"Possessio": 65, "Xuts": 16, "Passes": 92, "xG": 2.3, "Recuperacio": 10},
        "PesosIndex": {"Possessio": 40, "Xuts": 15, "Passes": 30, "xG": 10, "Recuperacio": 5}
    },
    "Jürgen Klopp (Rock & Roll / Pressió Alta)": {
        "Perfil": {"Possessio": 58, "Xuts": 18, "Passes": 85, "xG": 2.6, "Recuperacio": 15},
        "PesosIndex": {"Possessio": 10, "Xuts": 25, "Passes": 10, "xG": 25, "Recuperacio": 30}
    },
    "Diego Simeone (Bloc Baix)": {
        "Perfil": {"Possessio": 42, "Xuts": 9, "Passes": 80, "xG": 1.2, "Recuperacio": 18},
        "PesosIndex": {"Possessio": 5, "Xuts": 10, "Passes": 5, "xG": 40, "Recuperacio": 40}
    }
}

def calcular_index_entrenador(m_poss, m_xuts, m_pass, m_xg, m_recup, pesos):
    """Calcula un índex de rendiment mitjà basat en els pesos de l'entrenador triat."""
    index_score = (
        (m_poss * pesos["Possessio"]) +
        (m_xuts * pesos["Xuts"] * 2.5) +
        (m_pass * pesos["Passes"]) +
        (m_xg * pesos["xG"] * 20) +
        (m_recup * pesos["Recuperacio"] * 3)
    ) / 100
    return max(0, min(100, index_score))

uploaded_file = st.file_uploader("Penja el teu fitxer 'CAREER MODE TRACKER.xlsx'", type=["xlsx"])

if uploaded_file:
    # Carregar la fulla de Match Log
    raw_df = pd.read_excel(uploaded_file, sheet_name="Match Log")
    cols = list(raw_df.columns)
    data_df = raw_df.iloc[1:].copy().dropna(subset=[cols[0], cols[1]])

    st.success(f"S'han carregat {len(data_df)} partits del teu Match Log!")

    # Càlcul de mitjanes basat en les columnes exactes del teu Excel
    poss_mean = data_df[cols[8]].astype(float).mean() * 100
    xuts_mean = data_df[cols[9]].astype(float).mean()
    pass_mean = data_df[cols[13]].astype(float).mean() * 100
    xg_mean = data_df[cols[17]].astype(float).mean()
    recup_mean = data_df[cols[19]].astype(float).mean()

    # Panell de Mètriques Principals
    st.subheader("📊 Estadístiques Globals de l'Equip")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Possessió Mitjana", f"{poss_mean:.1f}%")
    c2.metric("Xuts / Partit", f"{xuts_mean:.1f}")
    c3.metric("Passes Encertades", f"{pass_mean:.1f}%")
    c4.metric("xG Generat", f"{xg_mean:.2f}")
    c5.metric("Temps Recuperació", f"{recup_mean:.1f}s")

    st.markdown("---")

    # Comparador d'Entrenadors
    st.subheader("🧠 Comparació d'Estil Tàctic")
    entrenador = st.selectbox("Selecciona un entrenador per comparar el teu joc:", list(ENTRENADORS.keys()))
    
    perfil = ENTRENADORS[entrenador]["Perfil"]
    pesos = ENTRENADORS[entrenador]["PesosIndex"]

    # Càlcul del grau de coincidència (%)
    diff_poss = 100 - abs(poss_mean - perfil["Possessio"])
    diff_xuts = 100 - (abs(xuts_mean - perfil["Xuts"]) / perfil["Xuts"] * 100)
    diff_pass = 100 - abs(pass_mean - perfil["Passes"])
    diff_xg = 100 - (abs(xg_mean - perfil["xG"]) / perfil["xG"] * 100)
    
    match_score = max(0, min(100, (diff_poss + diff_xuts + diff_pass + diff_xg) / 4))
    index_custom = calcular_index_entrenador(poss_mean, xuts_mean, pass_mean, xg_mean, recup_mean, pesos)

    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Coincidència d'Estil (%)", f"{match_score:.1f}%")
    col_res2.metric(f"Índex Adaptat ({entrenador.split(' (')[0]})", f"{index_custom:.1f} / 100")

    # Gràfic de Radar
    categories = ['Possessió (%)', 'Xuts / Partit', 'Passes (%)', 'xG Favor (x5)', 'Recuperació (s)']
    valors_jugador = [poss_mean, xuts_mean, pass_mean, xg_mean * 5, recup_mean]
    valors_coach = [perfil["Possessio"], perfil["Xuts"], perfil["Passes"], perfil["xG"] * 5, perfil["Recuperacio"]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=valors_jugador, theta=categories, fill='toself', name='El teu Equip'))
    fig.add_trace(go.Scatterpolar(r=valors_coach, theta=categories, fill='toself', name=entrenador))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Penja el teu fitxer Excel per començar a analitzar el teu mode carrera.")
