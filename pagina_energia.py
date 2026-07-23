import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Energético", layout="wide")

# --- VARIABLE DE PRECIO COLOMBIA (Tarifa promedio aproximada) ---
PRECIO_KWH_COP = 850

st.title("⚡ Analizador Energético Residencial por Potencia (Académico)")
st.write(
    f"Herramienta de proyección basada en la **Potencia Nominal (Watts)** de la etiqueta del dispositivo "
    f"y las horas de uso estimadas al mes. (Tarifa calculada a: **{PRECIO_KWH_COP} COP / kWh**)."
)

# Inicializar almacenamiento en la sesión
if "dispositivos" not in st.session_state:
    st.session_state.dispositivos = []

# --- DICCIONARIO DE DISPOSITIVOS Y SUS MARCAS ---
mapeo_dispositivos_marcas = {
    "Lampara LED de techo": ["Philips", "Osram", "Otro (Escribir manualmente)"],
    "Cargador celular/dispositivos": ["Honor x8b", "IPhone 16e", "Samsung", "No reconocida", "Otro (Escribir manualmente)"],
    "portátil": ["LENOVO","Hp", "Asus","Dell","Otro (Escribir manualmente)"],
    "Tirilla LED": ["No reconocida", "Otro (Escribir manualmente)"],
    "Secador": ["Remington", "Otro (Escribir manualmente)"],
    "Plancha pelo": ["Remington", "Otro (Escribir manualmente)"],
    "Plancha ropa": ["Universal", "Otro (Escribir manualmente)"],
    "Televisor": ["Panasonic", "Hyundai", "Samsung", "Otro (Escribir manualmente)"],
    "Xbox": ["Series x", "Otro (Escribir manualmente)"],
    "Cargador de batería Xbox": ["Duracell", "Otro (Escribir manualmente)"],
    "Impresora": ["HP smart", "Otro (Escribir manualmente)"],
    "Camara": ["No reconocida", "Otro (Escribir manualmente)"],
    "Consola Play 5": ["Play 5", "Otro (Escribir manualmente)"],
    "control Play 5": ["Play 5", "Otro (Escribir manualmente)"],
    "Internet (Router/Módem)": ["Claro", "Movistar", "Otro (Escribir manualmente)"],
    "Computador": ["LENOVO", "Otro (Escribir manualmente)"],
    "Luz LED panel cuadrado": ["No reconocida", "Otro (Escribir manualmente)"],
    "Bombilla LED tipo filamento": ["No reconocida", "Otro (Escribir manualmente)"],
    "Microondas": ["Challenger", "Otro (Escribir manualmente)"],
    "Air fryer": ["Oster", "Otro (Escribir manualmente)"],
    "Nevecon": ["Electrolux", "Otro (Escribir manualmente)"],
    "Licuadora": ["Oster", "Otro (Escribir manualmente)"],
    "lavadora": ["Samsung", "Otro (Escribir manualmente)"],
    "Otro (Escribir manualmente)": ["No reconocida", "Otro (Escribir manualmente)"]
}

# --- FUNCIÓN AUXILIAR PARA DETERMINAR EL FACTOR DE UTILIZACIÓN ---
def obtener_factor_sugerido(nombre_dispositivo):
    nombre_min = nombre_dispositivo.lower()
    if "nevera" in nombre_min or "nevecon" in nombre_min:
        return 0.40, "40% (El compresor enciende/apaga automáticamente por ciclos térmicos)"
    elif "televisor" in nombre_min or "tv" in nombre_min:
        return 0.70, "70% (Varía según el brillo del panel y volumen de audio)"
    elif "computador" in nombre_min or "portátil" in nombre_min or "portatil" in nombre_min:
        return 0.60, "60% (Varía según el procesamiento, carga de trabajo y batería)"
    elif "cargador" in nombre_min:
        return 0.25, "25% (A medida que la batería se llena, la demanda disminuye)"
    else:
        return 1.00, "100% (Resistencia pura, iluminación constante o motor de velocidad fija)"

opciones_dispositivos = list(mapeo_dispositivos_marcas.keys())

# --- FORMULARIO DE INGRESO ---
col1, col2, col3 = st.columns(3)

with col1:
    disp_seleccionado = st.selectbox("Seleccione el Dispositivo", opciones_dispositivos)
    if disp_seleccionado == "Otro (Escribir manualmente)":
        dispositivo = st.text_input("Escriba el nombre del dispositivo:").strip()
    else:
        dispositivo = disp_seleccionado
        
    marcas_disponibles = mapeo_dispositivos_marcas[disp_seleccionado]
    marca_seleccionada = st.selectbox("Seleccione la Marca", marcas_disponibles)
    if marca_seleccionada == "Otro (Escribir manualmente)":
        marca = st.text_input("Escriba la marca:").strip()
    else:
        marca = marca_seleccionada

with col2:
    potencia_marcada = st.number_input(
        "Potencia de la Etiqueta (Watts)",
        min_value=0.0,
        step=1.0,
        format="%.1f",
        help="Digite los Watts (W) que vienen impresos en la placa o etiqueta técnica del aparato."
    )
    
    # CÁLCULO Y VISUALIZACIÓN DEL FACTOR DE UTILIZACIÓN
    factor_sugerido, explicacion_factor = obtener_factor_sugerido(dispositivo if dispositivo else disp_seleccionado)
    
    # Campo desplegable opcional para ver o ajustar el factor de utilización
    with st.expander("⚙️ Factor de Utilización Sugerido", expanded=True):
        st.caption(f"**Valor estimado:** `{factor_sugerido * 100:.0f}%` ({explicacion_factor})")
        
        # Permitir ajuste personalizado si el usuario es técnico/avanzado
        factor_personalizado = st.slider(
            "Ajustar Factor de Utilización si lo deseas:",
            min_value=0.10,
            max_value=1.00,
            value=factor_sugerido,
            step=0.05,
            help="1.00 = El aparato consume el 100% de la potencia de la etiqueta todo el tiempo."
        )

with col3:
    uso_mes = st.number_input(
        "Horas de conexión/uso al mes",
        min_value=0.0,
        step=1.0,
        help="¿Cuántas horas aproximadas en total al mes está el aparato encendido o conectado?"
    )
    
    cantidad = st.number_input(
        "Cantidad de aparatos iguales",
        min_value=1,
        step=1
    )
    
    zona = st.selectbox(
        "Ubicación en el Hogar", 
        ["Habitación 1", "Habitación 2", "Habitación 3", "Sala", "Cocina", "Patio", "Baño", "General"]
    )
    
    enviado = st.button("➕ Calcular mediante Watts")

# --- LÓGICA DE INGENIERÍA ELÉCTRICA ---
if enviado and dispositivo:
    if potencia_marcada > 0 and uso_mes > 0:
        
        factor_utilizacion = factor_personalizado

        consumo_mensual_kwh = (potencia_marcada / 1000.0) * uso_mes * cantidad * factor_utilizacion
        costo_mensual_cop = consumo_mensual_kwh * PRECIO_KWH_COP
        
        st.session_state.dispositivos.append({
            "Dispositivo": dispositivo,
            "Marca": marca,
            "Potencia Etiqueta (W)": potencia_marcada,
            "Factor de Utilización": factor_utilizacion,  # Guardamos el decimal
            "Horas/Mes": uso_mes,
            "Cantidad": cantidad,
            "Zona": zona,
            "Consumo Mensual (kWh)": round(consumo_mensual_kwh, 4),
            "Costo Mensual (COP)": round(costo_mensual_cop, 0)
        })
        st.success(f"¡{dispositivo} calculado (Factor aplicativo: {factor_utilizacion * 100:.0f}%) y agregado!")
    else:
        st.warning("Por favor, introduzca una potencia en Watts y horas de uso mayores a cero.")

# --- SECCIÓN DE RESULTADOS ---
if st.session_state.dispositivos:
    df = pd.DataFrame(st.session_state.dispositivos)
    
    st.write("### 📋 Tabla de Cargas y Consumos Teóricos")
    
    df_visual = df.copy()
    
    # Formatear columnas para visualización clara de cara al usuario
    df_visual["Factor de Utilización"] = df_visual["Factor de Utilización"].apply(lambda x: f"{x * 100:.0f}%")
    df_visual["Costo Mensual (COP)"] = df_visual["Costo Mensual (COP)"].apply(lambda x: f"{x:,.0f} COP")
    
    st.dataframe(df_visual, use_container_width=True)
    
    total_consumo = df["Consumo Mensual (kWh)"].sum()
    total_dinero = df["Costo Mensual (COP)"].sum()
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="🔌 Energía Total Demandada al Mes", value=f"{total_consumo:.2f} kWh")
    with col_m2:
        st.metric(label="💰 Costo Total Estimado en Factura", value=f"{total_dinero:,.0f} COP")
    
    st.write("### 🧠 Diagnóstico de Eficiencia y Auditoría de Consumo")
    
    ranking = df.sort_values(by="Consumo Mensual (kWh)", ascending=False)
    
    for _, fila in ranking.iterrows():
        nombre = fila["Dispositivo"].lower()
        kwh_calculado = fila["Consumo Mensual (kWh)"]
        watts_etiqueta = fila["Potencia Etiqueta (W)"]
        horas_digitadas = fila["Horas/Mes"]
        factor_usado = fila["Factor de Utilización"]
        ubicacion = fila["Zona"]
        info_aparato = f"**{fila['Dispositivo']} ({fila['Marca']})** en **{ubicacion}**"
        
        # Filtro de Seguridad Global por fila
        if kwh_calculado >= 400.0 or watts_etiqueta > 8000.0:
            st.error(
                f"🚨 **ALERTA CRÍTICA DE SOBRECARGA EN {info_aparato}:** "
                f"Los valores ingresados ({watts_etiqueta} W por {horas_digitadas} horas) superan cualquier límite residencial lógico."
            )
            continue

        with st.expander(f"🔍 Análisis Detallado: {fila['Dispositivo']} — {kwh_calculado:.1f} kWh/mes (Factor: {factor_usado * 100:.0f}%)", expanded=True):
            
            # --- NEVERAS Y NEVECONES ---
            if "nevera" in nombre or "nevecon" in nombre:
                if watts_etiqueta > 400.0:
                    st.error(f"❌ **Potencia Crítica:** {watts_etiqueta} W es excesivo para refrigeración residencial.")
                elif 220.0 < watts_etiqueta <= 400.0:
                    st.warning(f"⚠️ **Potencia Regular:** {watts_etiqueta} W. Consumo estándar para un Nevecon grande antiguo.")
                else:
                    st.success(f"✅ **Potencia Eficiente:** {watts_etiqueta} W. Excelente rango para una nevera de alta eficiencia.")
                
                st.markdown(f"""
                * **ℹ️ Factor de Trabajo Aplicado:** Dado que la nevera cicla su motor, se calculó considerando un factor del **{factor_usado*100:.0f}%** del tiempo efectivo de consumo de pico.
                * **⚠️ Derroche Evitable:** Abrir la puerta constantemente fuerza al motor un 20% más, gastando **{(kwh_calculado * 0.20):.2f} kWh/mes** extra (~{((kwh_calculado * 0.20) * PRECIO_KWH_COP):,.0f} COP).
                """)
                    
            # --- TELEVISORES ---
            elif "televisor" in nombre or "tv" in nombre:
                if watts_etiqueta > 250.0:
                    st.error(f"❌ **Potencia Excesiva:** Un TV doméstico moderno jamás consume {watts_etiqueta} W.")
                else:
                    st.success(f"✅ **Potencia Registrada:** {watts_etiqueta} W.")

                st.markdown(f"""
                * **ℹ️ Factor de Trabajo Aplicado:** Se proyectó al **{factor_usado*100:.0f}%** teniendo en cuenta la fluctuación de brillo del panel.
                * **⚠️ Derroche Evitable:** Dejar el TV encendido de fondo sin que nadie lo vea por 3 horas al día genera un gasto fantasma de **{((watts_etiqueta/1000)*90*factor_usado):.2f} kWh/mes**.
                """)

            # --- CASO GENERAL / OTROS ---
            else:
                st.info(f"⚡ **Parámetros:** {watts_etiqueta} W analizados con un Factor de Utilización del **{factor_usado*100:.0f}%**.")

    # --- GUÍA DE AHORRO ENERGÉTICO PERSONALIZADA ---
    st.write("---")
    st.write("### 📉 Guía de Ahorro y Plan de Mitigación Personalizado")
    
    mayor_dispositivo = ranking.iloc[0]["Dispositivo"]
    mayor_consumo_kwh = ranking.iloc[0]["Consumo Mensual (kWh)"]
    mayor_costo = ranking.iloc[0]["Costo Mensual (COP)"]

    st.info(f"🎯 **Tu prioridad número 1 es:** el/la **{mayor_dispositivo}**, ya que representa un consumo de **{mayor_consumo_kwh:.2f} kWh/mes** (~ {mayor_costo:,.0f} COP). Atacar el uso de este aparato tendrá el mayor impacto financiero.")

    tab1, tab2, tab3 = st.tabs(["🔥 Cargas Térmicas (Alto Impacto)", "🕒 Cargas Fantasma e Iluminación", "📊 Metas de Reducción"])

    with tab1:
        st.markdown("#### Estrategias para Electrodomésticos de Alto Consumo")
        st.markdown("""
        * **Air Fryer y Microondas:** Reducir tan solo **10 minutos diarios** de uso en aparatos de 1500W genera un ahorro directo aproximado de **7.5 kWh al mes** (~6,300 COP).
        * **Neveras y Refrigeración:** Asegúrate de que los empaques magnéticos de las puertas sellen herméticamente. Separar la nevera al menos 15 cm de la pared reduce el esfuerzo del compresor hasta en un **15%**.
        """)

    with tab2:
        st.markdown("#### Control de Consumos Silenciosos")
        st.markdown("""
        * **Vampiros Eléctricos:** Los cargadores conectados sin dispositivo y los modos 'Stand-By' devoran energía las 24 horas del día. Usar un multitoma con interruptor puede reducir hasta un **5% de la factura total**.
        """)

    with tab3:
        st.markdown("#### Simulación de Metas (¿Cuánto podrías ahorrar?)")
        porcentaje_ahorro = st.slider("Selecciona un porcentaje de reducción de tiempo de uso diario:", 5, 30, 15, step=5)
        
        ahorro_kwh = total_consumo * (porcentaje_ahorro / 100.0)
        ahorro_cop = total_dinero * (porcentaje_ahorro / 100.0)
        nuevo_total = total_dinero - ahorro_cop

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.metric(label=f"📉 Ahorro Estimado ({porcentaje_ahorro}%)", value=f"- {ahorro_kwh:.2f} kWh", delta=f"- {ahorro_cop:,.0f} COP")
        with col_a2:
            st.metric(label="💰 Nueva Factura Proyectada", value=f"{nuevo_total:,.0f} COP")

    if st.button("🗑️ Limpiar todas las proyecciones"):
        st.session_state.dispositivos = []
        st.rerun()
else:
    st.info("💡 Ingrese la potencia en Watts (W) que sacó de la etiqueta trasera del aparato para ejecutar el algoritmo de cálculo.")

# --- SECCIÓN DE RECOMENDACIONES GENERALES ---
st.write("---")
st.write("### 📌 Conceptos Clave Explicados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.expander("🔌 ¿Por qué usamos la Potencia de la Etiqueta?", expanded=True):
        st.markdown("**La Potencia Nominal (W):** Es la capacidad instalada. Sirve para calcular las protecciones de la vivienda (Breakers/Tacos).")
        st.markdown("Multiplicar los Watts de la etiqueta por las horas te da la demanda teórica máxima de energía eléctrica.")

with col_g2:
    with st.expander("📉 ¿Qué es el Factor de Utilización?", expanded=True):
        st.markdown("Es la relación entre el consumo real medio y la potencia nominal máxima. Por ejemplo, una nevera no consume su potencia máxima las 24 horas porque el termostato apaga el motor cuando alcanza la temperatura deseada (Factor ~ 40%).")
