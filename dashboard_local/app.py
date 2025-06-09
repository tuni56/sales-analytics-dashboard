import streamlit as st
import pandas as pd
import plotly.express as px
import os

# === Cargar dataset limpio ===
DATA_PATH = "../data/ventas_limpias.csv"
assert os.path.exists(DATA_PATH), f"No se encontró el archivo en {DATA_PATH}"
df = pd.read_csv(DATA_PATH)

# === Conversión de fechas ===
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['anio'] = df['Order Date'].dt.year
df['mes'] = df['Order Date'].dt.month

# === Sidebar de filtros ===
st.sidebar.header("🔍 Filtros")

anios = sorted(df['anio'].dropna().unique())
categorias = sorted(df['Category'].dropna().unique())
segmentos = sorted(df['Segment'].dropna().unique())

anio_seleccionado = st.sidebar.selectbox("Año", anios)
categoria_seleccionada = st.sidebar.selectbox("Categoría", categorias)
segmento_seleccionado = st.sidebar.selectbox("Segmento", segmentos)

# === Aplicar filtros ===
df_filtrado = df[
    (df['anio'] == anio_seleccionado) &
    (df['Category'] == categoria_seleccionada) &
    (df['Segment'] == segmento_seleccionado)
]

# === Top 10 ciudades ===
def abreviar_ciudad(nombre):
    return nombre if len(nombre) <= 15 else nombre[:12] + "..."

top_cities = df_filtrado.groupby("City")["Sales"].sum().sort_values(ascending=False).head(10)
top_cities.index = top_cities.index.map(abreviar_ciudad)

df_top_cities = top_cities.reset_index()
df_top_cities.columns = ['Ciudad', 'Ventas']

# === Gráfico interactivo con Plotly ===
fig = px.bar(
    df_top_cities,
    y='Ciudad',
    x='Ventas',
    orientation='h',
    text='Ventas',
    color='Ventas',
    color_continuous_scale='Blues',
    title=f'Top 10 Ciudades - {categoria_seleccionada} / {segmento_seleccionado} / {anio_seleccionado}',
    labels={'Ventas': 'Ventas', 'Ciudad': 'Ciudad'},
    height=500
)

fig.update_traces(
    texttemplate='%{text:,.0f}',
    textposition='outside',
    marker_line_width=0.5,
    marker_line_color='gray'
)
fig.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    coloraxis_showscale=False,
    margin=dict(l=100, r=20, t=60, b=40),
    plot_bgcolor='white'
)

# === Mostrar dashboard ===
st.title("📊 Dashboard de Ventas")
st.markdown("Explorá las ciudades con más ventas según categoría, segmento y año.")

# KPIs simples
ventas_totales = df_filtrado['Sales'].sum()
cantidad_ordenes = df_filtrado['Order ID'].nunique()
ticket_promedio = ventas_totales / cantidad_ordenes if cantidad_ordenes > 0 else 0

# HTML con f-string correctamente aplicado
kpi_html = f"""
<style>
.kpi-container {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
    gap: 1rem;
}}
.kpi-card {{
    flex: 1;
    background: #e8f1fa;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    text-align: center;
    border-left: 6px solid #1f77b4;
}}
.kpi-card h2 {{
    margin: 0;
    font-size: 1.8rem;
    color: #1f77b4;
}}
.kpi-card p {{
    margin: 0.5rem 0 0;
    font-size: 1.1rem;
    color: #333;
}}
</style>

<div class="kpi-container">
    <div class="kpi-card">
        <h2>💰 ${ventas_totales:,.0f}</h2>
        <p>Ventas Totales</p>
    </div>
    <div class="kpi-card">
        <h2>🧾 {cantidad_ordenes:,}</h2>
        <p>Cantidad de Órdenes</p>
    </div>
    <div class="kpi-card">
        <h2>📦 ${ticket_promedio:,.2f}</h2>
        <p>Ticket Promedio</p>
    </div>
</div>
"""

st.markdown(kpi_html, unsafe_allow_html=True)



st.plotly_chart(fig, use_container_width=True)
