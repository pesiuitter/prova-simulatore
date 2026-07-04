import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione Pagina
st.set_page_config(page_title="Sito Pro v3", layout="wide")

# --- CODICE PER NASCONDERE DEPLOY E IL MENU A TRE PUNTINI ---
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- TITOLO E BRANDING ---
st.title("📈 Simulatore Professionale - versione demo in prova")
st.write("---")

# --- STATO DELLA SESSIONE ---
if 'anni_100' not in st.session_state:
    st.session_state.anni_100 = 5

def update_slider():
    st.session_state.anni_100 = st.session_state.anni_input_100

def update_input():
    st.session_state.anni_input_100 = st.session_state.anni_100

# --- SEZIONE PARAMETRI IN PAGINA PRINCIPALE (OTTIMIZZATA MOBILE) ---
st.subheader("⚙️ Parametri Finanziari")

# Layout a 3 colonne su desktop, si incolonna su mobile
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    inv_iniziale = st.number_input('Investimento iniziale (€)', value=100.0, step=50.0)
    
with col2:
    inv_annuale = st.number_input('Investimento annuale (€)', value=10.0, step=10.0)

with col3:
    rendimento_perc = st.number_input('Rendimento medio annuo (%)', value=7.0, step=0.5)

st.write("")

# Sezione Opzione di Limitazione (Ben visibile su mobile)
st.markdown("#### Limite Investimento Annuale")
st.write("L'investimento annuale viene eseguito per tutto il periodo?")
investe_tutto_periodo = st.toggle("Sì", value=True)

# Gestione dinamica dell'input degli anni di contribuzione
if investe_tutto_periodo:
    st.markdown("<span style='color: #a1a1aa;'>Per quanti anni?</span>", unsafe_allow_html=True)
    anni_contribuzione = st.number_input(
        "Inserisci anni contribuzione", 
        value=int(st.session_state.anni_100), 
        disabled=True, 
        label_visibility="collapsed"
    )
else:
    st.markdown("<span style='color: #1e293b; font-weight: bold;'>Per quanti anni?</span>", unsafe_allow_html=True)
    anni_contribuzione = st.number_input(
        "Inserisci anni contribuzione", 
        min_value=1, 
        max_value=100, 
        value=5, 
        disabled=False, 
        label_visibility="collapsed"
    )

st.write("---")

# --- CONTROLLI ANNI ---
st.subheader("⏳ Orizzonte Temporale")
c1, c2 = st.columns([3, 1])
with c1:
    anni = st.slider("Seleziona gli anni", 1, 100, key="anni_100", on_change=update_input)
with c2:
    anni_input = st.number_input("Inserisci manuale", 1, 100, key="anni_input_100", on_change=update_slider)

# --- LOGICA DEL CICLO WHILE ---
rendimento_medio_annuale = 1 + (rendimento_perc / 100)
total_investment = inv_iniziale
counter = 0
storia = []

while counter <= anni:
    if counter > 0:
        if investe_tutto_periodo or counter <= anni_contribuzione:
            total_investment = (total_investment * rendimento_medio_annuale) + inv_annuale
        else:
            total_investment = total_investment * rendimento_medio_annuale
    
    storia.append({
        "Anno": counter,
        "Capitale (€)": round(total_investment, 2)
    })
    counter += 1

df = pd.DataFrame(storia)

# --- METRICHE DINAMICHE ---
st.divider()
capitale_finale = df["Capitale (€)"].iloc[-1]
st.metric(label=f"Capitale Totale Stimato dopo {anni} anni", value=f"€ {capitale_finale:,.2f}")

# --- AREA GRAFICO ---
st.write("---")
scala_log = st.toggle("Scala Logaritmica", value=False)

fig = px.line(df, x="Anno", y="Capitale (€)", 
              title="Andamento della Crescita",
              markers=True,
              template="plotly_white")

fig.update_traces(line_color='#10b981', marker=dict(size=6, color='#065f46'))
fig.update_layout(
    yaxis_type="log" if scala_log else "linear", 
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20) # Margini ottimizzati per schermi stretti
)

st.plotly_chart(fig)

# --- TABELLA DATI ---
st.write("---")
st.subheader("📊 Dati della Simulazione")

inverti = st.toggle("Incrocia righe/colonne (Trasponi)")
df_view = df.transpose() if inverti else df

st.table(df_view)

csv = df_view.to_csv(index=inverti).encode('utf-8')
st.download_button(
    label="📥 Esporta i dati in .csv",
    data=csv,
    file_name='simulazione_investimento.csv',
    mime='text/csv',
)


# streamlit run sito_pro_v3.py