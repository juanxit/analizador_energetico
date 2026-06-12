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
    # Solicitud estricta de la potencia de etiqueta requerida por el profesor
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

# --- LÓGICA DE INGENIERÍA ELÉCTRICA (POTENCIA NOMINAL Y FACTOR DE UTILIZACIÓN) ---
if enviado and dispositivo:
    if potencia_marcada > 0 and uso_mes > 0:
        
        # FACTOR DE UTILIZACIÓN MODERADO (Evita que la nevera o TV simulen un consumo falso del 100% todo el tiempo)
        nombre_min = dispositivo.lower()
        factor_utilizacion = 1.0  # Por defecto consumen lo que dice la etiqueta (planchas, resistencias, bombillos)
        
        if "nevera" in nombre_min or "nevecon" in nombre_min:
            factor_utilizacion = 0.40  # Una nevera real solo tiene el compresor activo el 40% del tiempo conectado
        elif "televisor" in nombre_min or "tv" in nombre_min:
            factor_utilizacion = 0.70  # Los televisores rara vez operan al brillo máximo de etiqueta
        elif "computador" in nombre_min or "portátil" in pointer_min if "portátil" in nombre_min or "portatil" in nombre_min:
            factor_utilizacion = 0.60  # Consumo variable según el procesamiento
        elif "cargador" in nombre_min:
            factor_utilizacion = 0.25  # Un cargador conectado sin celular consume casi 0 (consumo vampiro)

        # Fórmula Física Fundamental: Energía (kWh) = (Potencia(W) / 1000) * Horas * Cantidad * Factor
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
        st.rerun()
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
        costo_calculado = fila["Costo Mensual (COP)"]
        horas_digitadas = fila["Horas/Mes"]
        watts_etiqueta = fila["Potencia Etiqueta (W)"]
        ubicacion = fila["Zona"]
        info_aparato = f"**{fila['Dispositivo']} ({fila['Marca']})** en **{ubicacion}**"
        
        # 1. FILTRO DE SEGURIDAD GLOBAL
        if kwh_calculado >= 250.0:
            st.error(
                f"🚨 **Alerta de Sobrecarga Teórica en {info_aparato}:** "
                f"La potencia de {watts_etiqueta} W multiplicada por las horas arroja un consumo exagerado de {kwh_calculado:.2f} kWh al mes. "
                f"Verifica si calculaste mal las horas mensuales o si los Watts corresponden a la etiqueta técnica."
            )
            continue

        # 2. ALERTAS BASADAS EN POTENCIA (W)
        
        # Neveras, Nevecones y Refrigeradores
        if "nevera" in nombre or "nevecon" in nombre:
            if watts_etiqueta > 350.0:
                st.error(
                    f"❄️ **{info_aparato}:** La potencia de etiqueta ({watts_etiqueta} W) es alta para estándares modernos de eficiencia. "
                    f"Aunque el motor se apaga intermitentemente, cuando arranca exige un pico alto de corriente. "
                    f"Se recomienda verificar si cuenta con tecnología Inverter."
                )
            else:
                st.success(f"❄️ **{info_aparato}:** Potencia nominal balanceada de {watts_etiqueta} W. Buen comportamiento de la carga inductiva.")
                
        # Routers, Internet y Módems
        elif "internet" in nombre or "router" in nombre or "modem" in nombre:
            if watts_etiqueta > 30.0:
                st.warning(f"🌐 **{info_aparato}:** Un módem no debería superar los 15-20 Watts en su etiqueta. Tus {watts_etiqueta} W sugieren un transformador ineficiente que desperdicia energía en forma de calor.")
            else:
                st.info(f"🌐 **{info_aparato}:** Carga permanente pequeña ({watts_etiqueta} W). Aunque es baja potencia, al operar 24/7 (720 horas) acumula un consumo fijo notable.")

        # Consolas de Videojuegos
        elif "xbox" in nombre or "play" in nombre or "consola" in nombre:
            if watts_etiqueta > 150.0:
                st.warning(
                    f"🎮 **{info_aparato}:** Potencia de procesamiento alta ({watts_etiqueta} W). "
                    f"A nivel normativo, asegúrate de activar el apagado automático. Si se queda encendida sin usarse, destruye la eficiencia del hogar."
                )
            else:
                st.success(f"🎮 **{info_aparato}:** Potencia controlada de {watts_etiqueta} W.")

        # Aparatos térmicos de cocina (Microondas, Air Fryer, Hornos)
        elif "microondas" in nombre or "air fryer" in nombre or "horno" in nombre:
            st.warning(
                f"🍳 **{info_aparato}:** Posee una potencia masiva de **{watts_etiqueta} W**. "
                f"Al ser una carga resistiva pura de alto impacto, el secreto de su ahorro no es modificar el aparato, "
                f"sino mitigar estrictamente el tiempo de uso diario."
            )

        # Cuidado personal (Secadores y Planchas)
        elif "secador" in nombre or "plancha" in nombre:
            if watts_etiqueta > 1200.0:
                st.warning(
                    f"💇 **{info_aparato}:** Alerta de alta demanda de potencia instantánea ({watts_etiqueta} W). "
                    f"Evita encender este aparato al mismo tiempo que la Air Fryer o el microondas para no disparar las protecciones del tablero eléctrico."
                )

        # Iluminación
        elif "lampara" in nombre or "led" in nombre or "bombill" in nombre:
            if watts_etiqueta > 25.0:
                st.error(f"💡 **{info_aparato}:** Una potencia de {watts_etiqueta} W es excesiva para tecnología LED actual. Podría tratarse de iluminación halógena o incandescente antigua. ¡Sustitúyela!")
            else:
                st.success(f"💡 **{info_aparato}:** Excelente potencia lumínica de {watts_etiqueta} W. Uso óptimo de tecnología LED.")

        # Computadores
        elif "computador" in nombre or "portátil" in nombre or "portatil" in nombre:
            if watts_etiqueta > 250.0:
                st.warning(f"💻 **{info_aparato}:** Tu fuente de poder de {watts_etiqueta} W corresponde a un equipo Gaming o de diseño pesado. Configura perfiles de ahorro de energía en el software.")
            else:
                st.success(f"💻 **{info_aparato}:** Potencia de operación estándar ({watts_etiqueta} W).")

        # Lavadoras
        elif "lavadora" in nombre:
            if watts_etiqueta > 500.0:
                st.error(f"🧺 **{info_aparato}:** Los {watts_etiqueta} W nominales indican que el motor realiza un esfuerzo considerable o usa agua caliente. Lava siempre con agua fría para desactivar las resistencias internas.")
            else:
                st.success(f"🧺 **{info_aparato}:** Consumo del motor de {watts_etiqueta} W dentro del estándar verde.")

        # Por defecto
        else:
            st.info(f"✅ **{info_aparato}:** Potencia de {watts_etiqueta} W analizada y registrada en la base de datos.")

    if st.button("🗑️ Limpiar todas las proyecciones"):
        st.session_state.dispositivos = []
        st.rerun()
else:
    st.info("💡 Ingrese la potencia en Watts (W) que sacó de la etiqueta trasera del aparato para ejecutar el algoritmo de cálculo.")

# --- SECCIÓN DE RECOMENDACIONES GENERALES ---
st.write("---")
st.write("### 📌 Conceptos Clave de Ingeniería Eléctrica Explicados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.expander("🔌 ¿Por qué usamos la Potencia de la Etiqueta?", expanded=True):
        st.markdown("**La Potencia Nominal (W):** Es la capacidad instalada. Sirve para calcular las protecciones de la vivienda (Breakers/Tacos).")
        st.markdown("Multiplicar los Watts de la etiqueta por las horas te da la demanda teórica máxima de energía eléctrica.")
        
with col_g2:
    with st.expander("📉 ¿Qué es el Factor de Utilización?", expanded=True):
        st.markdown("Los electrodomésticos no consumen su potencia máxima el 100% del tiempo. El software aplica automáticamente un factor de corrección técnico para ajustar la simulación a la realidad de las facturas en Colombia.")
