import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Energético", layout="wide")

# --- VARIABLE DE PRECIO COLOMBIA ---
PRECIO_KWH_COP = 850

st.title("⚡ Analizador Energético Residencial con Vatímetro (Colombia)")
st.write(
    f"Registre los kWh medidos con su vatímetro y las horas totales que el aparato permanece encendido al mes para proyectar el consumo real. (Tarifa: **{PRECIO_KWH_COP} COP / kWh**)."
)

# Inicializar almacenamiento en la sesión
if "dispositivos" not in st.session_state:
    st.session_state.dispositivos = []

# --- DICCIONARIO DE DISPOSITIVOS Y SUS MARCAS ---
mapeo_dispositivos_marcas = {
    "Lampara LED de techo": ["No reconocida", "Otro (Escribir manualmente)"],
    "Cargador celular/dispositivos": ["Honor x8b", "IPhone 16e", "Samsung", "No reconocida", "Otro (Escribir manualmente)"],
    "portátil": ["LENOVO", "Otro (Escribir manualmente)"],
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

# --- FORMULARIO DE INGRESO DIRECTO DE MEDICIÓN ---
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
    kwh_soltados = st.number_input(
        "Dato Vatímetro (kWh)",
        min_value=0.0,
        step=0.001,
        format="%.4f",
        help="Digite el consumo en kWh acumulado que marcó el vatímetro al terminar de medir el aparato."
    )
    
with col3:
    # Cambiado estrictamente a Horas de uso al mes
    uso_mes = st.number_input(
        "Horas de uso al mes",
        min_value=0.0,
        step=1.0,
        help="Escriba cuántas horas en TOTAL al mes permanece encendido o en uso este aparato."
    )
    
    cantidad = st.number_input(
        "Cantidad de estos mismos aparatos",
        min_value=1,
        step=1
    )
    
    zona = st.selectbox(
        "Ubicación de la casa", 
        ["Habitación 1", "Habitación 2", "Habitación 3", "Sala", "Cocina", "Patio", "Baño", "General"]
    )
    
    enviado = st.button("➕ Calcular y Agregar Proyección")

# --- LÓGICA MATEMÁTICA DIRECTA ---
if enviado and dispositivo:
    if kwh_soltados > 0 and uso_mes > 0:
        # Operación física: kWh medidos durante el periodo de prueba × horas de uso al mes × cantidad
        consumo_mensual_kwh = kwh_soltados * uso_mes * cantidad
        costo_mensual_cop = consumo_mensual_kwh * PRECIO_KWH_COP
        
        st.session_state.dispositivos.append({
            "Dispositivo": dispositivo,
            "Marca": marca,
            "kWh Medidos": kwh_soltados,
            "Horas/Mes": uso_mes,
            "Cantidad": cantidad,
            "Zona": zona,
            "Consumo Mensual (kWh)": round(consumo_mensual_kwh, 4),
            "Costo Mensual (COP)": round(costo_mensual_cop, 0)
        })
        st.success(f"¡{dispositivo} proyectado y agregado exitosamente!")
        st.rerun()
    else:
        st.warning("Por favor, introduzca un valor de kWh y las horas de uso mayores a cero.")

# --- SECCIÓN DE RESULTADOS ---
if st.session_state.dispositivos:
    df = pd.DataFrame(st.session_state.dispositivos)
    
    st.write("### 📋 Proyección Mensual Basada en Mediciones Directas")
    
    df_visual = df.copy()
    df_visual["Costo Mensual (COP)"] = df_visual["Costo Mensual (COP)"].apply(lambda x: f"{x:,.0f} COP")
    st.dataframe(df_visual, use_container_width=True)
    
    total_consumo = df["Consumo Mensual (kWh)"].sum()
    total_dinero = df["Costo Mensual (COP)"].sum()
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="🔌 Consumo Total Proyectado al Mes", value=f"{total_consumo:.2f} kWh")
    with col_m2:
        st.metric(label="💰 Costo Total Estimado en Factura", value=f"{total_dinero:,.0f} COP")
    
    st.write("### 🧠 Diagnóstico y Análisis de la Eficiencia ")
    
    ranking = df.sort_values(by="Consumo Mensual (kWh)", ascending=False)
    
    for _, fila in ranking.iterrows():
        nombre = fila["Dispositivo"].lower()
        kwh_calculado = fila["Consumo Mensual (kWh)"]
        costo_calculado = fila["Costo Mensual (COP)"]
        horas_digitadas = fila["Horas/Mes"]
        ubicacion = fila["Zona"]
        info_aparato = f"**{fila['Dispositivo']} ({fila['Marca']})** en **{ubicacion}**"
        
        # 1. FILTRO DE SEGURIDAD GLOBAL (Por si se digitan Watts en lugar de kWh por error)
        if kwh_calculado >= 176.0:
            st.error(
                f"🚨 **Alerta Crítica - Consumo Fuera de Rango en {info_aparato}:** "
                f"La proyección arroja {kwh_calculado:.2f} kWh al mes ({costo_calculado:,.0f} COP). "
                f"Esto es demasiado alto para una residencia. Por favor, verifica que el 'Dato Vatímetro (kWh)' "
                f"corresponda a la energía acumulada y no a la potencia instantánea en Watts."
            )
            continue

        # 2. ALERTAS DETALLADAS Y PERSONALIZADAS POR DISPOSITIVO
        
        # Neveras, Nevecones y Refrigeradores
        if "nevera" in nombre or "nevecon" in nombre:
            if kwh_calculado > 90.0:
                st.error(
                    f"❄️ **{info_aparato}:** Alerta de alto consumo ({kwh_calculado:.2f} kWh/mes). "
                    f"**Consejo Clave:** Evita abrir la nevera repetidamente o por aburrimiento. Al abrirla, "
                    f"entra aire caliente del entorno y el compresor se ve obligado a encenderse a máxima potencia para "
                    f"volver a enfriar, disparando la factura. Revisa que los empaques de goma sellen perfectamente."
                )
            else:
                st.success(f"❄️ **{info_aparato}:** ¡Buen rendimiento! Registra {kwh_calculado:.2f} kWh/mes ({costo_calculado:,.0f} COP). Mantienes un excelente hábito de uso continuo.")
                
        # Routers, Internet y Módems
        elif "internet" in nombre or "router" in nombre or "modem" in nombre:
            if horas_digitadas < 720:
                st.warning(f"🌐 **{info_aparato}:** Ingresaste {horas_digitadas} horas, pero recuerda que el internet en el hogar opera 24/7 (720 horas al mes).")
            if kwh_calculado > 18.0:
                st.error(f"🌐 **{info_aparato}:** Consumo elevado para telecomunicaciones. Asegúrate de que el adaptador de corriente no se esté recalentando por falta de ventilación.")
            else:
                st.info(f"🌐 **{info_aparato}:** Consumo base saludable de {kwh_calculado:.2f} kWh al mes. Es un gasto fijo necesario para el hogar.")

        # Consolas de Videojuegos (Xbox, Play 5) y Controles
        elif "xbox" in nombre or "play" in nombre or "consola" in nombre or "control" in nombre:
            if kwh_calculado > 25.0:
                st.warning(
                    f"🎮 **{info_aparato}:** Registra un consumo importante de {kwh_calculado:.2f} kWh/mes ({costo_calculado:,.0f} COP). "
                    f"**Consejo Clave:** ¡No la dejes en modo reposo o inicio instantáneo! En estos modos de espera, "
                    f"la consola sigue consumiendo energía las 24 horas del día descargando actualizaciones silenciosas. Apágala por completo."
                )
            else:
                st.success(f"🎮 **{info_aparato}:** Consumo controlado. Tus sesiones de juego y recarga están balanceadas.")

        # Aparatos térmicos de cocina (Microondas, Air Fryer, Hornos)
        elif "microondas" in nombre or "air fryer" in nombre or "horno" in nombre:
            if kwh_calculado > 35.0:
                st.error(
                    f"🍳 **{info_aparato}:** Consumo mensual excesivo ({kwh_calculado:.2f} kWh / {costo_calculado:,.0f} COP). "
                    f"**Consejo Clave:** Estos dispositivos usan resistencias de alta potencia que generan calor extremo al instante. "
                    f"Reducir solo unos minutos de uso por ciclo u optimizar las porciones reduce significativamente el impacto."
                )
            else:
                st.success(f"🍳 **{info_aparato}:** Uso óptimo de {kwh_calculado:.2f} kWh al mes. Los ciclos cortos y eficientes evitan picos de energía.")

        # Cuidado personal (Secadores y Planchas de pelo o ropa)
        elif "secador" in nombre or "plancha" in nombre:
            if kwh_calculado > 15.0:
                st.warning(
                    f"💇 **{info_aparato}:** Cuidado con la acumulación de horas de uso. Proyecta ${costo_calculado:,.0f} COP. "
                    f"**Consejo Clave:** Debido a que transforman electricidad en calor de forma directa, dejarlos encendidos mientras te peinas "
                    f"o usarlos por horas largas acumula un gasto enorme. Apágalos inmediatamente termines tu rutina."
                )
            else:
                st.success(f"💇 **{info_aparato}:** Uso inteligente. El tiempo de encendido es el adecuado.")

        # Iluminación (Lámparas de techo, paneles, bombillas, tirillas LED)
        elif "lampara" in nombre or "led" in nombre or "bombill" in nombre:
            if kwh_calculado > 12.0:
                st.warning(
                    f"💡 **{info_aparato}:** Consumo elevado de {kwh_calculado:.2f} kWh al mes. "
                    f"**Consejo Clave:** Aunque la tecnología LED gasta muy pocos vatios por hora, el problema aquí es el exceso de tiempo. "
                    f"Dejar luces encendidas en espacios donde no hay nadie o durante toda la noche acumula muchas horas e incrementa la factura."
                )
            else:
                st.success(f"💡 **{info_aparato}:** ¡Excelente! El consumo de iluminación está bajo control gracias a la tecnología LED.")

        # Computadores y Portátiles
        elif "computador" in nombre or "portátil" in nombre or "portatil" in nombre:
            if kwh_calculado > 30.0:
                st.warning(
                    f"💻 **{info_aparato}:** Consumo moderado-alto con ${costo_calculado:,.0f} COP. "
                    f"**Consejo Clave:** Activa la suspensión automática de tu sistema operativo para que el monitor y los componentes "
                    f"entren en reposo de inmediato cuando te levantes del escritorio. Disminuir un poco el brillo de pantalla también ayuda."
                )
            else:
                st.success(f"💻 **{info_aparato}:** Operación eficiente para actividades académicas o laborales.")

        # Cargadores de celulares u otros dispositivos
        elif "cargador" in nombre or "celular" in nombre:
            if horas_digitadas >= 500:
                st.warning(
                    f"🔌 **{info_aparato}:** Alerta de consumo vampiro. "
                    f"**Consejo Clave:** Dejar el cargador enchufado continuamente a la toma corriente sin tener el teléfono conectado "
                    f"sigue demandando energía de la red de forma inútil. Acostúmbrate a desconectarlo al retirar tu celular."
                )
            else:
                st.success(f"🔌 **{info_aparato}:** Carga controlada y eficiente.")

        # Licuadoras e Impresoras
        elif "licuadora" in nombre or "impresora" in nombre:
            if kwh_calculado > 10.0:
                st.warning(f"🖨️ **{info_aparato}:** Uso por encima del promedio. Verifica que los equipos queden completamente apagados y no en modo Stand-by.")
            else:
                st.success(f"✅ **{info_aparato}:** Gasto mínimo bajo control de {kwh_calculado:.2f} kWh/mes.")

        # Lavadoras
        elif "lavadora" in nombre:
            if kwh_calculado > 25.0:
                st.error(f"🧺 **{info_aparato}:** Consumo alto (${costo_calculado:,.0f} COP). Procura realizar únicamente lavadas con carga completa y agua fría para evitar activar las resistencias de calentamiento interno.")
            else:
                st.success(f"🧺 **{info_aparato}:** Ciclos de lavado eficientes y programados.")

        # Regla por defecto para cualquier otro dispositivo manual
        else:
            if kwh_calculado >= 40.0:
                st.warning(f"🔥 **{info_aparato}:** Identificado como un punto de consumo moderado-alto. Intenta optimizar sus horas de uso mensual.")
            else:
                st.success(f"✅ **{info_aparato}:** Consumo verificado y controlado de ${costo_calculado:,.0f} COP al mes.")

    if st.button("🗑️ Limpiar todas las proyecciones"):
        st.session_state.dispositivos = []
        st.rerun()
else:
    st.info("💡 Mida el consumo de un aparato con su vatímetro, digite los kWh acumulados y las horas que se usa en todo el mes.")

# --- SECCIÓN DE RECOMENDACIONES GENERALES ---
st.write("---")
st.write("### 📌 Guía General de Ahorro para el Hogar (Colombia)")
st.write("Hábitos prácticos enfocados en reducir tanto los kilovatios-hora como el costo final de tu factura:")

col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.expander("🔌 El Consumo Vampiro (Dispositivos en Espera)", expanded=True):
        st.markdown("Los cargadores de celular, pantallas de TV apagadas o consolas siguen consumiendo energía silenciosamente si se quedan conectados a la toma de corriente de forma continua.")
        st.markdown(f"**El impacto medible:** Mantener 4 cargadores enchufados sin usar genera un desperdicio fantasma de **7 kWh al año** (6.000 COP). Si le sumas televisores y consolas en reposo, el gasto innecesario supera los **47 kWh anuales** (40.000 COP al año).")
        
    with st.expander("💡 Optimización de la Iluminación"):
        st.markdown("Aunque las tirillas LED y bombillas consumen poco de forma individual, al tener muchas unidades encendidas por varias horas el costo final suma en la factura.")
        st.markdown(f"**El impacto medible:** Cambiar 5 bombillos antiguos por tecnología LED moderna ahorra **25 kWh mensuales**. En Colombia, esto representa un alivio directo de **21.250 COP menos** en cada mes de facturación.")

with col_g2:
    with st.expander("❄️ Uso Inteligente de la Nevera / Nevecon", expanded=True):
        st.markdown("Es el único electrodoméstico que nunca descansa en todo el mes y puede llevarse hasta el 30% del costo total de la energía eléctrica de tu hogar.")
        st.markdown(f"**El impacto medible:** Abrir la nevera por descuido unas 10 veces al día (dejando escapar el aire frío) obliga al motor a re-enfriar con fuerza. Esto añade entre **4 kWh y 6 kWh extras al mes**, obligándote a pagar entre **3.500 COP y 5.100 COP adicionales** mensuales.")
        
    with st.expander("🖥️ Gestión de Equipos de Cómputo y Consolas"):
        st.markdown("Configura tus laptops y consolas en el Modo Ahorro de Energía para que entren en estado de suspensión de forma automática si no estás jugando o trabajando.")
        st.markdown(f"**El impacto medible:** Dejar una consola en modo de inicio instantáneo gasta corriente fantasma. Al mes, este estado genera un consumo innecesario de **9 kWh**, lo que significa pagar **7.600 COP** en tu factura sin haber jugado un solo minuto.")