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
    
    # --- CAMBIO DE TÍTULO SOLICITADO ---
    st.write("### 🧠 Diagnóstico de Eficiencia y Auditoría de Consumo")
    
    ranking = df.sort_values(by="Consumo Mensual (kWh)", ascending=False)
    
    for _, fila in ranking.iterrows():
        nombre = fila["Dispositivo"].lower()
        kwh_calculado = fila["Consumo Mensual (kWh)"]
        watts_etiqueta = fila["Potencia Etiqueta (W)"]
        horas_digitadas = fila["Horas/Mes"]
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

        # 2. DETALLE ULTRA-ESPECÍFICO POR DISPOSITIVO (CON AUDITORÍA DE USO NUEVA)
        with st.expander(f"🔍 Análisis Detallado: {fila['Dispositivo']} — {kwh_calculado:.1f} kWh/mes", expanded=True):
            
            # --- NEVERAS Y NEVECONES ---
            if "nevera" in nombre or "nevecon" in nombre:
                if watts_etiqueta > 350.0:
                    st.error(f"❌ **Evaluación de Potencia:** {watts_etiqueta} W es críticamente alto. Indica que el motor no es de alta eficiencia.")
                else:
                    st.success(f"✅ **Evaluación de Potencia:** {watts_etiqueta} W está en el rango verde para tecnologías eficientes.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Guardar alimentos calientes o tener los empaques dañados obliga al compresor a trabajar un **20% más**. Esto representa un consumo innecesario de aproximadamente **{(kwh_calculado * 0.20):.2f} kWh/mes** (~{((kwh_calculado * 0.20) * PRECIO_KWH_COP):,.0f} COP desperdiciados).
                * **Dato Curioso:** Cada vez que abres la puerta de la nevera por 10 segundos, se pierde hasta el 30% del aire frío acumulado, requiriendo energía extra para estabilizarse.
                * **Recomendación:** Separa la nevera al menos 15 cm de la pared para facilitar la ventilación del condensador.
                """)
                    
            # --- ROUTERS Y MÓDEMS ---
            elif "internet" in nombre or "router" in nombre or "modem" in nombre:
                st.info(f"⚡ **Evaluación de Potencia:** Operación permanente estándar.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar el módem encendido durante madrugadas o jornadas laborales ausentes (ej. 12 horas muertas al día) desperdicia el **50% de su energía**. Apagarlo en esos lapsos te ahorraría **{(kwh_calculado * 0.50):.2f} kWh/mes** (~{((kwh_calculado * 0.50) * PRECIO_KWH_COP):,.0f} COP).
                * **Dato Curioso:** Aunque consume poca potencia, al operar 720 horas continuas al mes se convierte en un peso invisible pero fijo en la base de la factura.
                * **Recomendación:** Desconéctalo por completo cuando salgas de viaje los fines de semana.
                """)

            # --- CONSOLAS DE VIDEOJUEGOS ---
            elif "xbox" in nombre or "play" in nombre or "consola" in nombre:
                st.success(f"🎮 **Evaluación de Potencia:** {watts_etiqueta} W bajo análisis de carga variable.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** El modo "Inicio Rápido" o reposo mal configurado mantiene la consola consumiendo hasta 40W sin que juegues. Si pasa 20 horas al día en este estado latente, gasta de más **24.0 kWh/mes** (~20,400 COP adicionales por descuido).
                * **Dato Curioso:** Una consola descargando actualizaciones en modo reposo ineficiente gasta casi la misma energía que ejecutando un juego simple.
                * **Recomendación:** Activa el modo de ahorro de energía estricto en los ajustes del sistema para que baje a menos de 1W en espera.
                """)

            # --- COCINA DE ALTA POTENCIA (Air Fryer, Microondas, Hornos) ---
            elif "microondas" in nombre or "air fryer" in nombre or "horno" in nombre:
                st.warning(f"🔥 **Carga Térmica Pesada:** Alta absorción de corriente instantánea.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Precalentar la Air Fryer de más o abrir constantemente la bandeja durante la cocción disipa el calor bruscamente. Cada apertura prolongada puede alargar la cocción un **15%**, sumando un gasto evitable de **{(kwh_calculado * 0.15):.2f} kWh/mes** por cada ciclo alterado.
                * **Dato Curioso:** La resistencia de estos aparatos gasta en 10 minutos lo equivalente a usar una TV por más de 3 horas.
                * **Recomendación:** Reduce el uso limpiando los residuos de grasa internos, ya que actúan como un aislante térmico defectuoso.
                """)

            # --- CUIDADO PERSONAL (Secadores y Planchas) ---
            elif "secador" in nombre or "plancha" in nombre:
                st.warning(f"⚠️ **Demanda Instantánea Alta:** Resistencia pura de alto consumo.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar la plancha de pelo encendida sobre la mesa mientras haces otra actividad por solo 15 minutos innecesarios al día genera un derroche directo de aproximadamente **4.5 kWh/mes** (~3,825 COP individuales).
                * **Dato Curioso:** Las planchas consumen su pico máximo al calentar desde cero; mantenerlas calientes consume menos energía que apagarlas y volverlas a calentar de inmediato.
                * **Recomendación:** Segmenta bien tus tareas y utilízala solo cuando estés listo para el procedimiento de forma continua.
                """)

            # --- ILUMINACIÓN (Lámparas, LED, Bombillos) ---
            elif "lampara" in nombre or "led" in nombre or "bombill" in nombre:
                if watts_etiqueta > 25.0:
                    st.error(f"❌ **Alerta de Ineficiencia:** Potencia excesiva para iluminación habitacional moderna.")
                else:
                    st.success(f"✅ **Luminaria Eficiente:** Consumo adecuado de baja potencia.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar encendido un set de bombillas por olvido en habitaciones vacías durante 5 horas al día representa un consumo extra de **{(kwh_calculado * 0.30):.2f} kWh/mes** que desaparece apagando el interruptor.
                * **Dato Curioso:** Reemplazar un bombillo antiguo incandescente por uno LED reduce la demanda en un **85%** manteniendo el mismo nivel de iluminación.
                * **Recomendación:** Aprovecha al máximo la luz natural y limpia las cubiertas de los bombillos para no bloquear los lúmenes de salida.
                """)

            # --- COMPUTADORES Y PORTÁTILES ---
            elif "computador" in nombre or "portátil" in nombre or "portatil" in nombre:
                st.success(f"💻 **Procesamiento Registrado:** Parámetros dentro del estándar.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Configurar la pantalla al 100% de brillo y dejar protectores de pantalla animados en vez de suspender el equipo, incrementa el gasto un **25%**. En un equipo de escritorio esto puede representar **{(kwh_calculado * 0.25):.2f} kWh/mes** de consumo fantasma.
                * **Dato Curioso:** Un computador portátil consume hasta un 70% menos que uno de escritorio debido a la arquitectura optimizada de sus microprocesadores.
                * **Recomendación:** Activa la suspensión automática a los 5 minutos de inactividad.
                """)

            # --- LAVADORAS ---
            elif "lavadora" in nombre:
                st.info(f"🧺 **Carga Inductiva:** Consumo supeditado al torque mecánico.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Utilizar agua caliente en los ciclos de lavado dispara el consumo un **90%**, debido a las resistencias de calentamiento internas. Lavar con agua caliente añade innecesariamente hasta **15.0 kWh/mes** adicionales por carga semanal.
                * **Dato Curioso:** El motor encargado de girar el tambor solo usa el 10% de la energía de la lavadora; la gran pérdida económica está en la temperatura del agua.
                * **Recomendación:** Configura siempre programas en agua fría y utiliza la capacidad máxima de llenado sugerida.
                """)

            # --- CARGADORES ---
            elif "cargador" in nombre:
                st.info(f"🔌 **Consumo Vampiro:** Carga residual pasiva.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar el cargador pegado a la toma sin conectar el celular consume cerca de 0.5W permanentes. Mantenerlo así todo el mes causa un gasto acumulado fantasma que, sumado por varios cargadores en el hogar, puede agregar **1.5 kWh/mes** directos a la factura por desatención.
                * **Dato Curioso:** A este fenómeno los ingenieros eléctricos lo denominan "energía de reposo" o "no-carga".
                * **Recomendación:** Retira el adaptador de la pared tan pronto finalice el ciclo de carga.
                """)

            # --- POR DEFECTO ---
            else:
                st.info(f"✅ **Registro Exitoso:** Datos de potencia analizados y procesados.")

    # --- GUÍA DE AHORRO ENERGÉTICO PERSONALIZADA ---
    st.write("---")
    st.write("### 📉 Guía de Ahorro y Plan de Mitigación Personalizado")
    st.write("Basado en tu inventario actual, este es el plan de acción prioritario para reducir el costo de tu factura:")

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
st.write("### 📌 Conceptos Clave de Ingeniería Eléctrica Explicados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.expander("🔌 ¿Por qué usamos la Potencia de la Etiqueta?", expanded=True):
        st.markdown("**La Potencia Nominal (W):** Es la capacidad instalada. Sirve para calcular las protecciones de la vivienda (Breakers/Tacos).")
        st.markdown("Multiplicar los Watts de la etiqueta por las horas te da la demanda teórica máxima de energía eléctrica.")
        
with col_g2:
    with st.expander("📉 ¿Qué es el Factor de Utilización?", expanded=True):
        st.markdown("Los electrodomésticos no consumen su potencia máxima el 100% del tiempo. El software aplica automáticamente un factor de corrección técnico para ajustar la simulación a la realidad de las facturas en Colombia.")
