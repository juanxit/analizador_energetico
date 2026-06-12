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
        
        nombre_min = dispositivo.lower()
        factor_utilizacion = 1.0  
        
        if "nevera" in nombre_min or "nevecon" in nombre_min:
            factor_utilizacion = 0.40  
        elif "televisor" in nombre_min or "tv" in nombre_min:
            factor_utilizacion = 0.70  
        elif "computador" in nombre_min or "portátil" in nombre_min or "portatil" in nombre_min:
            factor_utilizacion = 0.60  
        elif "cargador" in nombre_min:
            factor_utilizacion = 0.25  

        consumo_mensual_kwh = (potencia_marcada / 1000.0) * uso_mes * cantidad * factor_utilizacion
        costo_mensual_cop = consumo_mensual_kwh * PRECIO_KWH_COP
        
        st.session_state.dispositivos.append({
            "Dispositivo": dispositivo,
            "Marca": marca,
            "Potencia Etiqueta (W)": potencia_marcada,
            "Factor de Uso Aplicado": factor_utilizacion,
            "Horas/Mes": uso_mes,
            "Cantidad": cantidad,
            "Zona": zona,
            "Consumo Mensual (kWh)": round(consumo_mensual_kwh, 4),
            "Costo Mensual (COP)": round(costo_mensual_cop, 0)
        })
        st.success(f"¡{dispositivo} calculado teóricamente y agregado al inventario!")
    else:
        st.warning("Por favor, introduzca una potencia en Watts y horas de uso mayores a cero.")

# --- SECCIÓN DE RESULTADOS ---
if st.session_state.dispositivos:
    df = pd.DataFrame(st.session_state.dispositivos)
    
    st.write("### 📋 Tabla de Cargas y Consumos Teóricos")
    
    df_visual = df.copy()
    df_visual["Costo Mensual (COP)"] = df_visual["Costo Mensual (COP)"].apply(lambda x: f"{x:,.0f} COP")
    st.dataframe(df_visual, use_container_width=True)
    
    total_consumo = df["Consumo Mensual (kWh)"].sum()
    total_dinero = df["Costo Mensual (COP)"].sum()
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="🔌 Energía Total Demandada al Mes", value=f"{total_consumo:.2f} kWh")
    with col_m2:
        st.metric(label="💰 Costo Total Estimado en Factura", value=f"{total_dinero:,.0f} COP")
    
    st.write("### 🧠 Diagnóstico del Profesor e Indicadores de Eficiencia")
    
    ranking = df.sort_values(by="Consumo Mensual (kWh)", ascending=False)
    
    for _, fila in ranking.iterrows():
        nombre = fila["Dispositivo"].lower()
        kwh_calculado = fila["Consumo Mensual (kWh)"]
        watts_etiqueta = fila["Potencia Etiqueta (W)"]
        ubicacion = fila["Zona"]
        info_aparato = f"**{fila['Dispositivo']} ({fila['Marca']})** en **{ubicacion}**"
        
        # Filtro de Seguridad Global
        if kwh_calculado >= 250.0:
            st.error(
                f"🚨 **Alerta de Sobrecarga Teórica en {info_aparato}:** "
                f"La potencia de {watts_etiqueta} W multiplicada por las horas arroja un consumo exagerado de {kwh_calculado:.2f} kWh al mes. "
                f"Verifica si calculaste mal las horas mensuales o si los Watts corresponden a la etiqueta técnica."
            )
            continue

        # Alertas Basadas en Potencia
        if "nevera" in nombre or "nevecon" in nombre:
            if watts_etiqueta > 350.0:
                st.error(f"❄️ **{info_aparato}:** La potencia de etiqueta ({watts_etiqueta} W) es alta para estándares modernos. Se recomienda verificar tecnología Inverter.")
            else:
                st.success(f"❄️ **{info_aparato}:** Potencia nominal balanceada de {watts_etiqueta} W.")
                
        elif "internet" in nombre or "router" in nombre or "modem" in nombre:
            if watts_etiqueta > 30.0:
                st.warning(f"🌐 **{info_aparato}:** Un módem no debería superar los 15-20 Watts. Tus {watts_etiqueta} W sugieren ineficiencia térmica.")
            else:
                st.info(f"🌐 **{info_aparato}:** Carga permanente pequeña ({watts_etiqueta} W). Al operar 24/7 acumula un consumo fijo notable.")

        elif "xbox" in nombre or "play" in nombre or "consola" in nombre:
            if watts_etiqueta > 150.0:
                st.warning(f"🎮 **{info_aparato}:** Potencia alta ({watts_etiqueta} W). Asegúrate de activar el apagado automático.")
            else:
                st.success(f"🎮 **{info_aparato}:** Potencia controlada de {watts_etiqueta} W.")

        elif "microondas" in nombre or "air fryer" in nombre or "horno" in nombre:
            st.warning(f"🍳 **{info_aparato}:** Posee una potencia masiva de **{watts_etiqueta} W**. Mitigue estrictamente el tiempo de uso diario.")

        elif "secador" in nombre or "plancha" in nombre:
            if watts_etiqueta > 1200.0:
                st.warning(f"💇 **{info_aparato}:** Alta demanda instantánea ({watts_etiqueta} W). Evita encenderlo junto a otros equipos de cocina.")

        elif "lampara" in nombre or "led" in nombre or "bombill" in nombre:
            if watts_etiqueta > 25.0:
                st.error(f"💡 **{info_aparato}:** {watts_etiqueta} W es excesivo para tecnología LED actual. ¡Sustitúyela!")
            else:
                st.success(f"💡 **{info_aparato}:** Excelente potencia lumínica de {watts_etiqueta} W.")

        elif "computador" in nombre or "portátil" in nombre or "portatil" in nombre:
            if watts_etiqueta > 250.0:
                st.warning(f"💻 **{info_aparato}:** Fuente de {watts_etiqueta} W corresponde a un equipo Gaming o pesado. Configure perfiles de ahorro.")
            else:
                st.success(f"💻 **{info_aparato}:** Potencia de operación estándar ({watts_etiqueta} W).")

        elif "lavadora" in nombre:
            if watts_etiqueta > 500.0:
                st.error(f"🧺 **{info_aparato}:** Los {watts_etiqueta} W indican alto esfuerzo o uso de agua caliente. Lava con agua fría.")
            else:
                st.success(f"🧺 **{info_aparato}:** Consumo del motor dentro del estándar verde.")
        else:
            st.info(f"✅ **{info_aparato}:** Potencia de {watts_etiqueta} W analizada y registrada.")

    # --- NUEVA SECCIÓN: GUÍA DE AHORRO ENERGÉTICO PERSONALIZADA ---
    st.write("---")
    st.write("### 📉 Guía de Ahorro y Plan de Mitigación Personalizado")
    st.write("Basado en tu inventario actual, este es el plan de acción prioritario para reducir el costo de tu factura:")

    # Identificar el mayor consumidor del inventario para dar un consejo dinámico
    mayor_dispositivo = ranking.iloc[0]["Dispositivo"]
    mayor_consumo_kwh = ranking.iloc[0]["Consumo Mensual (kWh)"]
    mayor_costo = ranking.iloc[0]["Costo Mensual (COP)"]

    st.info(f"🎯 **Tu prioridad número 1 es:** el/la **{mayor_dispositivo}**, ya que representa un consumo de **{mayor_consumo_kwh:.2f} kWh/mes** (~ {mayor_costo:,.0f} COP). Atacar el uso de este aparato tendrá el mayor impacto financiero.")

    # Pestañas de la guía estructuradas por tipo de carga
    tab1, tab2, tab3 = st.tabs(["🔥 Cargas Térmicas (Alto Impacto)", "🕒 Cargas Fantasma e Iluminación", "📊 Metas de Reducción"])

    with tab1:
        st.markdown("#### Estrategias para Electrodomésticos de Alto Consumo")
        st.markdown("""
        * **Air Fryer y Microondas:** Reducir tan solo **10 minutos diarios** de uso en aparatos de 1500W genera un ahorro directo aproximado de **7.5 kWh al mes** (~6,300 COP).
        * **Neveras y Refrigeración:** Asegúrate de que los empaques magnéticos de las puertas sellen herméticamente. Separar la nevera al menos 15 cm de la pared reduce el esfuerzo del compresor hasta en un **15%**.
        * **Planchas y Secadores:** Evita usarlos de manera intermitente. El mayor consumo ocurre mientras la resistencia se calienta desde cero; planchar toda la ropa en una sola sesión es mucho más eficiente.
        """)

    with tab2:
        st.markdown("#### Control de Consumos Silenciosos")
        st.markdown("""
        * **Vampiros Eléctricos:** Los cargadores conectados sin dispositivo y los modos 'Stand-By' de consolas y TVs devoran energía las 24 horas del día. Usar un multitoma con interruptor para apagarlos por completo por las noches puede reducir hasta un **5% de la factura total**.
        * **Módems y Routers:** Aunque consumen poca potencia (~12W), operan 720 horas al mes de forma lineal. Si tu hogar pasa periodos largos sin habitar (ej. viajes), desconectarlo es mandatorio.
        """)

    with tab3:
        st.markdown("#### Simulación de Metas (¿Cuánto podrías ahorrar?)")
        porcentaje_ahorro = st.slider("Selecciona un porcentaje de reducción de tiempo de uso diario:", 5, 30, 15, step=5, help="Simula qué pasaría si optimizas el tiempo de uso de tus aparatos.")
        
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
st.write("### 📌 Definicion de Conceptos Clave ")
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.expander("🔌 ¿Por qué usamos la Potencia de la Etiqueta?", expanded=True):
        st.markdown("**La Potencia Nominal (W):** Es la capacidad instalada. Sirve para calcular las protecciones de la vivienda (Breakers/Tacos).")
        st.markdown("Multiplicar los Watts de la etiqueta por las horas te da la demanda teórica máxima de energía eléctrica.")
        
with col_g2:
    with st.expander("📉 ¿Qué es el Factor de Utilización?", expanded=True):
        st.markdown("Los electrodomésticos no consumen su potencia máxima el 100% del tiempo. El software aplica automáticamente un factor de corrección técnico para ajustar la simulación a la realidad de las facturas en Colombia.")
