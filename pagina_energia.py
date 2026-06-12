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
    
    st.write("### 🧠 Diagnóstico de Eficiencia y Auditoría de Consumo")
    
    ranking = df.sort_values(by="Consumo Mensual (kWh)", ascending=False)
    
    for _, fila in ranking.iterrows():
        nombre = fila["Dispositivo"].lower()
        kwh_calculado = fila["Consumo Mensual (kWh)"]
        watts_etiqueta = fila["Potencia Etiqueta (W)"]
        horas_digitadas = fila["Horas/Mes"]
        ubicacion = fila["Zona"]
        info_aparato = f"**{fila['Dispositivo']} ({fila['Marca']})** en **{ubicacion}**"
        
        # Filtro de Seguridad Global por fila
        if kwh_calculado >= 400.0 or watts_etiqueta > 8000.0:
            st.error(
                f"🚨 **ALERTA CRÍTICA DE SOBRECARGA EN {info_aparato}:** "
                f"Los valores ingresados ({watts_etiqueta} W por {horas_digitadas} horas) superan cualquier límite residencial lógico. "
                f"Por favor, revisa si colocaste un cero de más o confundiste Watts con voltios."
            )
            continue

        with st.expander(f"🔍 Análisis Detallado: {fila['Dispositivo']} — {kwh_calculado:.1f} kWh/mes", expanded=True):
            
            # --- NEVERAS Y NEVECONES ---
            if "nevera" in nombre or "nevecon" in nombre:
                if watts_etiqueta > 400.0:
                    st.error(f"❌ **Potencia Crítica:** {watts_etiqueta} W es excesivo para refrigeración residencial. Indica un equipo muy viejo o comercial.")
                elif 220.0 < watts_etiqueta <= 400.0:
                    st.warning(f"⚠️ **Potencia Regular:** {watts_etiqueta} W. Consumo estándar para un Nevecon grande antiguo. Podría mejorar con tecnología Inverter.")
                else:
                    st.success(f"✅ **Potencia Eficiente:** {watts_etiqueta} W. Excelente rango para una nevera con compresor de alta eficiencia.")
                
                if horas_digitadas < 500:
                    st.warning(f"🕒 **Nota de simulación:** Digitaste {horas_digitadas} horas. Las neveras operan 720 horas/mes. Aunque el compresor cicla, se calcula sobre el tiempo de conexión eléctrica.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Abrir la puerta constantemente o guardar alimentos calientes fuerza al motor un 20% más, botando a la basura **{(kwh_calculado * 0.20):.2f} kWh/mes** (~{((kwh_calculado * 0.20) * PRECIO_KWH_COP):,.0f} COP).
                * **Dato Curioso:** La nevera es responsable de casi la tercera parte del gasto de luz de una casa en Colombia al operar sin interrupción.
                """)
                    
            # --- TELEVISORES ---
            elif "televisor" in nombre or "tv" in nombre:
                if watts_etiqueta > 250.0:
                    st.error(f"❌ **Potencia Excesiva:** Un TV doméstico moderno jamás consume {watts_etiqueta} W. ¡Esto es un error de digitación o un panel industrial!")
                elif 120.0 < watts_etiqueta <= 250.0:
                    st.warning(f"⚠️ **Potencia Regular:** {watts_etiqueta} W. Típico de pantallas gigantes antiguas de Plasma o LCD de gran formato.")
                else:
                    st.success(f"✅ **Potencia Eficiente:** {watts_etiqueta} W. Rango ideal para pantallas LED, QLED u OLED actuales.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar el TV encendido de fondo sin que nadie lo vea por 3 horas al día genera un gasto fantasma de **{((watts_etiqueta/1000)*90*0.7):.2f} kWh/mes** (~{(((watts_etiqueta/1000)*90*0.7)*PRECIO_KWH_COP):,.0f} COP).
                * **Dato Curioso:** Las pantallas LED consumen hasta un 40% menos energía que las antiguas pantallas LCD de tubos fluorescentes.
                """)

            # --- ROUTERS Y MÓDEMS ---
            elif "internet" in nombre or "router" in nombre or "modem" in nombre:
                if watts_etiqueta > 30.0:
                    st.error(f"❌ **Potencia Anómala:** {watts_etiqueta} W es demasiado para un módem de hogar. Revisa la etiqueta trasera.")
                else:
                    st.success(f"✅ **Potencia Correcta:** {watts_etiqueta} W. Consumo bajo y estabilizado para telecomunicaciones.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Al estar encendido las 24 horas del día, si no se desconecta en viajes largos de fin de semana, tira unos **3.5 kWh** por viaje directamente a la cuenta.
                * **Dato Curioso:** Aunque su potencia es mínima, al estar encendido 720 horas lineales al mes, su consumo acumulado supera al de una licuadora de alta potencia.
                """)

            # --- CONSOLAS DE VIDEOJUEGOS ---
            elif "xbox" in nombre or "play" in nombre or "consola" in nombre:
                if watts_etiqueta > 230.0:
                    st.error(f"❌ **Potencia Excesiva:** {watts_etiqueta} W sobrepasa los picos máximos de las consolas de última generación.")
                elif 140.0 < watts_etiqueta <= 230.0:
                    st.warning(f"⚠️ **Potencia Alta:** {watts_etiqueta} W. Consumo normal en juegos de gráficos exigentes (4K UHD).")
                else:
                    st.success(f"✅ **Potencia Controlada:** {watts_etiqueta} W. Consumo eficiente o juego en modo retro/menús.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar la consola en modo de 'Suspensión de inicio rápido' consume hasta 15W continuos. Al mes son **10.8 kWh** desperdiciados (~9,180 COP) solo por no apagarla por completo.
                * **Dato Curioso:** Jugar en streaming desde la nube consume menos Watts en el dispositivo local que procesar el juego directamente con la tarjeta gráfica de la consola.
                """)

            # --- AIR FRYER, MICROONDAS Y HORNOS ---
            elif "microondas" in nombre or "air fryer" in nombre or "horno" in nombre:
                if watts_etiqueta > 2200.0:
                    st.error(f"❌ **Potencia Crítica:** {watts_etiqueta} W. Excede los límites estándar para un tomacorriente residencial común (Riesgo de corto).")
                elif 1000.0 <= watts_etiqueta <= 2200.0:
                    st.warning(f"🔥 **Carga Térmica Pesada:** {watts_etiqueta} W. Es normal para este aparato ya que convierte electricidad en calor mediante resistencias puras.")
                else:
                    st.success(f"✅ **Potencia Baja:** {watts_etiqueta} W. Equipo compacto o de bajo consumo térmico.")
                
                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Precalentar el equipo innecesariamente por más de 10 minutos o abrir la bandeja en medio ciclo disipa el calor, alargando los tiempos un 15% y encareciendo la cocción.
                * **Dato Curioso:** Una freidora de aire gasta en un instante la corriente equivalente a tener entre 120 y 150 bombillas LED encendidas simultáneamente.
                """)

            # --- SECADORES Y PLANCHAS ---
            elif "secador" in nombre or "plancha" in nombre:
                if watts_etiqueta > 2400.0:
                    st.error(f"❌ **Potencia Peligrosa:** {watts_etiqueta} W es excesivo para un circuito normal de habitación. Puede derretir la toma si se usa por periodos largos.")
                elif 1000.0 < watts_etiqueta <= 2400.0:
                    st.warning(f"⚠️ **Demanda Alta:** {watts_etiqueta} W. Estándar para generación instantánea de calor. Requiere precaución.")
                else:
                    st.success(f"✅ **Potencia Moderada:** {watts_etiqueta} W. Adecuado para un uso personal eficiente.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar la plancha de pelo encendida sobre el tocador mientras haces otra actividad por 15 minutos diarios acumula **4.5 kWh/mes** de puro desperdicio.
                * **Dato Curioso:** Estos equipos consumen su pico más alto de corriente al encenderse desde frío; es más eficiente usarlos en una sola sesión continua que prenderlos y apagarlos a cada rato.
                """)

            # --- ILUMINACIÓN (Lámparas y Bombillos) ---
            elif "lampara" in nombre or "led" in nombre or "bombill" in nombre:
                if watts_etiqueta > 50.0:
                    st.error(f"❌ **Error de Tecnología:** ¡Un bombillo LED doméstico jamás consume {watts_etiqueta} W! Estás registrando una bombilla incandescente antigua o un reflector de estadio.")
                elif 18.0 < watts_etiqueta <= 50.0:
                    st.warning(f"⚠️ **Potencia Elevada:** {watts_etiqueta} W. Alto para interiores; revisa si puedes sustituirlo por lúmenes más eficientes.")
                else:
                    st.success(f"✅ **Iluminación Eficiente:** {watts_etiqueta} W. Estándar perfecto para la tecnología LED actual.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar las luces encendidas en áreas vacías por 4 horas diarias suma un **25% de gasto extra** innecesario en iluminación.
                * **Dato Curioso:** Los bombillos LED transforman el 90% de la energía en luz limpia y solo el 10% en calor, al revés que las bombillas tradicionales.
                """)

            # --- COMPUTADORES Y PORTÁTILES ---
            elif "computador" in nombre or "portátil" in nombre or "portatil" in nombre:
                if watts_etiqueta > 600.0:
                    st.error(f"❌ **Potencia Desproporcionada:** {watts_etiqueta} W supera las especificaciones de fuentes de poder residenciales comunes.")
                elif 250.0 < watts_etiqueta <= 600.0:
                    st.warning(f"⚠️ **Perfil Gaming/Diseño:** {watts_etiqueta} W. Fuente robusta para procesadores gráficos pesados. Consume bastante bajo carga.")
                else:
                    st.success(f"✅ **Consumo Ofimático Eficiente:** {watts_etiqueta} W. Consumo típico y controlado de un equipo portátil o de oficina.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar el equipo encendido toda la noche suspendido de forma incorrecta o con el brillo al máximo sin necesidad añade un gasto silencioso evitable del 15%.
                * **Dato Curioso:** Un portátil ahorra entre un 70% y un 85% de energía comparado con un computador de escritorio de similares prestaciones de pantalla.
                """)

            # --- LAVADORAS ---
            elif "lavadora" in nombre:
                if watts_etiqueta > 1200.0:
                    st.error(f"❌ **Potencia Excesiva:** {watts_etiqueta} W está fuera del rango normal de lavado doméstico.")
                elif 500.0 < watts_etiqueta <= 1200.0:
                    st.warning(f"⚠️ **Consumo Alto:** {watts_etiqueta} W. Común en lavadoras con ciclos de lavado con calentamiento interno de agua.")
                else:
                    st.success(f"✅ **Motor Eficiente:** {watts_etiqueta} W. Excelente rango para motores Direct Drive o inverter en agua fría.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** El **90% de la energía** de una lavadora se va exclusivamente en calentar el agua. Lavar siempre con agua fría evita este gasto por completo, protegiendo tus finanzas.
                * **Dato Curioso:** El motor que hace girar la tina consume solo una fracción mínima; el enemigo real de la factura es la temperatura seleccionada.
                """)

            # --- CARGADORES ---
            elif "cargador" in nombre:
                if watts_etiqueta > 120.0:
                    st.error(f"❌ **Potencia Errónea:** {watts_etiqueta} W es una potencia de electrodoméstico, no de un cargador móvil.")
                else:
                    st.success(f"✅ **Baja Potencia:** {watts_etiqueta} W. Adecuado para cargas rápidas de dispositivos electrónicos.")

                st.markdown(f"""
                * **⚠️ Derroche Evitable:** Dejar el cargador enchufado a la pared sin el celular consume energía de 'No-Carga' las 24 horas. Multiplicado por varios cargadores en casa, se traduce en kilovatios desperdiciados al año.
                * **Dato Curioso:** A este fenómeno eléctrico se le conoce técnicamente como 'Consumo Vampiro'.
                """)

            # --- CASO POR DEFECTO / OTROS ---
            else:
                if watts_etiqueta > 1500.0:
                    st.warning(f"⚡ **Aparato de Alta Potencia:** {watts_etiqueta} W requiere un control estricto de las horas de operación al mes.")
                else:
                    st.info(f"✅ **Registro Exitoso:** {watts_etiqueta} W analizados bajo parámetros generales.")

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
st.write("### 📌 Conceptos Clave Explicados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.expander("🔌 ¿Por qué usamos la Potencia de la Etiqueta?", expanded=True):
        st.markdown("**La Potencia Nominal (W):** Es la capacidad instalada. Sirve para calcular las protecciones de la vivienda (Breakers/Tacos).")
        st.markdown("Multiplicar los Watts de la etiqueta por las horas te da la demanda teórica máxima de energía eléctrica.")
        
with col_g2:
    with st.expander("📉 ¿Qué es el Factor de Utilización?", expanded=True):
        st.markdown("Los electrodomésticos no consumen su potencia máxima el 100% del tiempo. El software aplica automáticamente un factor de corrección técnico para ajustar la simulación a la realidad de las facturas en Colombia.")
