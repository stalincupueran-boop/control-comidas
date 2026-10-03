import streamlit as st
import pandas as pd
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Control de Alimentación", page_icon="🍔", layout="centered")

# Estilos CSS
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E293B;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #F1F5F9;
    }
    </style>
""", unsafe_allow_html=True)

# Tarifas fijas
P_DESAYUNO = 1.60
P_ALMUERZO = 3.16
P_MERIENDA = 1.60
P_PISCINA_MENSUAL = 2.00
P_EXTRA = 10.00

st.markdown("<h1 class='main-title'>🍽️ Control Diario de Comidas</h1>", unsafe_allow_html=True)

# Inicializar base de datos temporal
if "historial" not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=[
        "Fecha", "Guardia", "Desayuno", "Almuerzo", "Merienda", "Aporte Extra", "Total ($)", "Anio_Mes"
    ])

# --- SECCIÓN 1: REGISTRO DIARIO ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Registrar Día")
    
    col_fecha, col_guardia = st.columns([2, 1])
    with col_fecha:
        fecha_sel = st.date_input("Fecha", date.today())
    with col_guardia:
        st.write(" ")
        st.write(" ")
        es_guardia = st.toggle("¿Día de Guardia?", value=False)

    st.write("---")
    st.write("**Comidas consumidas:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        c_desayuno = st.checkbox(f"Desayuno (${P_DESAYUNO:.2f})", value=True)
    with col2:
        c_almuerzo = st.checkbox(f"Almuerzo (${P_ALMUERZO:.2f})", value=True)
    with col3:
        if es_guardia:
            c_merienda = st.checkbox(f"Merienda (${P_MERIENDA:.2f})", value=True)
        else:
            c_merienda = False
            st.caption("Merienda solo en guardia")

    st.write("---")
    st.write("**Otros Rubros:**")
    c_extra = st.checkbox(f"Aporte Extra (${P_EXTRA:.2f})")

    # Cálculo del total diario
    val_desayuno = P_DESAYUNO if c_desayuno else 0.0
    val_almuerzo = P_ALMUERZO if c_almuerzo else 0.0
    val_merienda = P_MERIENDA if (c_merienda and es_guardia) else 0.0
    val_extra = P_EXTRA if c_extra else 0.0
    
    total_dia = val_desayuno + val_almuerzo + val_merienda + val_extra

    st.markdown("</div>", unsafe_allow_html=True)

st.metric(label="💰 Total a Registrar Hoy", value=f"${total_dia:.2f}")

if st.button("💾 Guardar Registro", use_container_width=True, type="primary"):
    nuevo_registro = {
        "Fecha": fecha_sel.strftime("%Y-%m-%d"),
        "Guardia": "Sí" if es_guardia else "No",
        "Desayuno": val_desayuno,
        "Almuerzo": val_almuerzo,
        "Merienda": val_merienda,
        "Aporte Extra": val_extra,
        "Total ($)": total_dia,
        "Anio_Mes": fecha_sel.strftime("%Y-%m")
    }
    st.session_state.historial = pd.concat([st.session_state.historial, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("✅ Registro guardado con éxito")

# --- SECCIÓN 2: RESUMEN MENSUAL ---
if not st.session_state.historial.empty:
    st.write("---")
    st.subheader("📅 Resumen Mensual")

    df = st.session_state.historial.copy()
    
    meses_disponibles = sorted(df["Anio_Mes"].unique(), reverse=True)
    mes_seleccionado = st.selectbox("Selecciona el mes a consultar:", meses_disponibles)

    df_mes = df[df["Anio_Mes"] == mes_seleccionado]

    # Cálculos mensuales
    subtotal_comidas_extras = df_mes["Total ($)"].sum()
    total_mes_final = subtotal_comidas_extras + P_PISCINA_MENSUAL  # Se suma el cargo fijo mensual de $2.00
    
    dias_guardia = len(df_mes[df_mes["Guardia"] == "Sí"])
    total_desayunos = df_mes["Desayuno"].sum()
    total_almuerzos = df_mes["Almuerzo"].sum()
    total_meriendas = df_mes["Merienda"].sum()
    total_extra = df_mes["Aporte Extra"].sum()

    # Métricas principales
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Final del Mes", f"${total_mes_final:.2f}", help="Incluye el cobro único mensual de $2.00 de piscina")
    with col_m2:
        st.metric("Días Registrados", len(df_mes))
    with col_m3:
        st.metric("Días de Guardia", f"{dias_guardia}")

    # Desglose detallado por rubro
    st.write("**Desglose acumulado del mes:**")
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.write(f"☕ **Desayunos:** ${total_desayunos:.2f}")
    col_d2.write(f"🍲 **Almuerzos:** ${total_almuerzos:.2f}")
    col_d3.write(f"🌙 **Meriendas:** ${total_meriendas:.2f}")
    
    col_d4, col_d5 = st.columns(2)
    col_d4.write(f"🏊 **Piscina (Fijo mensual):** ${P_PISCINA_MENSUAL:.2f}")
    col_d5.write(f"💵 **Aportes Extras:** ${total_extra:.2f}")

    st.write(" ")
    
    # Formatear tabla para vista previa
    df_mostrar = df_mes[["Fecha", "Guardia", "Desayuno", "Almuerzo", "Merienda", "Aporte Extra", "Total ($)"]].copy()
    for col in ["Desayuno", "Almuerzo", "Merienda", "Aporte Extra", "Total ($)"]:
        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"${x:.2f}")

    st.dataframe(df_mostrar, use_container_width=True)

    # Exportación a CSV
    csv = df_mes[["Fecha", "Guardia", "Desayuno", "Almuerzo", "Merienda", "Aporte Extra", "Total ($)"]].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Mensual (CSV)",
        data=csv,
        file_name=f'consumo_comidas_{mes_seleccionado}.csv',
        mime='text/csv',
    )