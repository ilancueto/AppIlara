import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ilara Beauty", layout="wide", page_icon="💄")

# --- CONEXIÓN A SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("❌ Error de conexión: Revisa tus secretos (.streamlit/secrets.toml).")
    st.stop()

# --- FUNCIONES ---
def cargar_datos(tabla):
    try:
        response = supabase.table(tabla).select("*").execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            if tabla == "inventario": 
                return pd.DataFrame(columns=["id", "producto", "marca", "categoria", "stock", "precio_venta", "precio_costo"])
            if tabla == "finanzas": 
                return pd.DataFrame(columns=["id", "fecha", "tipo", "descripcion", "monto"])
        return df
    except Exception as e:
        st.error(f"Error cargando {tabla}: {e}")
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("💅 Bienvenida, Mara")

# Cargar datos frescos
df_inv = cargar_datos("inventario")
df_fin = cargar_datos("finanzas")

# --- BLINDAJE DE DATOS ---
if not df_inv.empty:
    df_inv['producto'] = df_inv['producto'].astype(str)
    df_inv['marca'] = df_inv['marca'].astype(str)
    # Etiqueta única para identificar productos en los selectores
    df_inv['display'] = df_inv['producto'] + " - " + df_inv['marca']

if not df_fin.empty:
    df_fin['descripcion'] = df_fin['descripcion'].astype(str)
    df_fin['monto'] = df_fin['monto'].astype(float)

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventario", "💰 Nueva Venta", "💸 Nuevo Gasto", "📊 Finanzas"])

# ==========================================
# 1. INVENTARIO (CON SEMÁFORO DE STOCK)
# ==========================================
with tab1:
    st.header("Gestión de Productos")
    
    # --- ALERTA DE STOCK BAJO (NUEVO) ---
    if not df_inv.empty:
        criticos = df_inv[df_inv['stock'] <= 3] # Umbral de alerta
        if not criticos.empty:
            st.warning(f"⚠️ ¡Atención! Hay {len(criticos)} productos con poco stock (3 o menos).")
            with st.expander("Ver lista de reposición"):
                st.dataframe(criticos[["producto", "marca", "stock"]], use_container_width=True, hide_index=True)
    
    col_izq, col_der = st.columns(2)
    
    with col_izq.expander("➕ Agregar o Reponer Stock", expanded=True):
        with st.form("nuevo_prod"):
            st.caption("Si el nombre y marca coinciden, se suma al stock actual.")
            col1, col2 = st.columns(2)
            
            nom = col1.text_input("Nombre").strip()
            marca = col2.text_input("Marca").strip()
            marca_final = marca if marca else "Genérico"
            
            cat = col1.selectbox("Categoría", ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"])
            stk_input = col2.number_input("Cantidad", min_value=1, value=1)
            
            costo = col1.number_input("Costo Unitario ($)", min_value=0.0, value=None, placeholder="0.00")
            venta = col2.number_input("Precio Venta ($)", min_value=0.0, value=None, placeholder="0.00")
            
            if st.form_submit_button("Guardar"):
                if not nom or costo is None or venta is None:
                    st.error("⚠️ Faltan datos obligatorios (Nombre, Costo, Venta).")
                else:
                    try:
                        # Buscar coincidencia exacta (Nombre + Marca)
                        query = supabase.table("inventario").select("*").eq("producto", nom).eq("marca", marca_final).execute()
                        existe = query.data
                        
                        if existe:
                            prod_viejo = existe[0]
                            nuevo_id = prod_viejo['id']
                            nuevo_stock = prod_viejo['stock'] + stk_input
                            
                            supabase.table("inventario").update({
                                "stock": nuevo_stock, "precio_costo": costo, "precio_venta": venta, "categoria": cat
                            }).eq("id", nuevo_id).execute()
                            st.success(f"🔄 Stock actualizado: {prod_viejo['stock']} ➝ {nuevo_stock}")
                        else:
                            nuevo = {
                                "producto": nom, "marca": marca_final, "categoria": cat, 
                                "stock": stk_input, "precio_costo": costo, "precio_venta": venta
                            }
                            supabase.table("inventario").insert(nuevo).execute()
                            st.success(f"✅ Nuevo producto creado: {nom}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    with col_der.expander("🗑️ Eliminar Producto"):
        if df_inv.empty:
            st.info("Lista vacía.")
        else:
            lista_eliminar = df_inv["display"].tolist()
            elegido_eliminar = st.selectbox("Seleccionar para borrar", lista_eliminar)
            
            if st.button("Eliminar definitivamente", type="primary"):
                try:
                    fila_a_borrar = df_inv[df_inv["display"] == elegido_eliminar]
                    if not fila_a_borrar.empty:
                        id_borrar = int(fila_a_borrar.iloc[0]['id'])
                        supabase.table("inventario").delete().eq("id", id_borrar).execute()
                        st.success("🗑️ Producto eliminado.")
                        st.rerun()
                    else:
                        st.error("No se encontró el producto.")
                except Exception as e:
                    st.error(f"Error al borrar: {e}")

    st.divider()
    if not df_inv.empty:
        df_inv["precio_costo"] = df_inv.get("precio_costo", 0).fillna(0)
        df_inv["Ganancia"] = df_inv["precio_venta"] - df_inv["precio_costo"]
        
        # Tabla visual limpia
        df_view = df_inv[["producto", "marca", "categoria", "stock", "precio_costo", "precio_venta", "Ganancia"]]
        df_view.columns = ["Producto", "Marca", "Categoría", "Stock", "Costo", "Venta", "Ganancia"]
        st.dataframe(df_view, use_container_width=True, hide_index=True)

# ==========================================
# 2. REGISTRAR VENTA
# ==========================================
with tab2:
    st.header("Registrar Venta")
    if df_inv.empty:
        st.warning("Carga productos primero en la pestaña Inventario.")
    else:
        opciones = df_inv['display'].unique()
        seleccion = st.selectbox("Producto a vender", opciones)
        
        if seleccion:
            filtro = df_inv[df_inv['display'] == seleccion]
            
            if not filtro.empty:
                fila = filtro.iloc[0]
                
                # Datos seguros
                precio_unit = float(fila.get('precio_venta', 0))
                stock_disp = int(fila.get('stock', 0))
                id_prod = int(fila.get('id', 0))
                nombre_real = fila.get('producto', 'Desconocido')
                marca_real = fila.get('marca', 'Genérico')

                c1, c2 = st.columns(2)
                c1.metric("Precio Unitario", f"${precio_unit:,.0f}")
                c2.metric("Stock Disponible", f"{stock_disp} u.")

                if stock_disp > 0:
                    col_cant, col_total = st.columns(2)
                    # Tope dinámico para no vender más de lo que hay
                    cantidad = col_cant.number_input("Cantidad", min_value=1, max_value=stock_disp, value=1)
                    total_calc = precio_unit * cantidad
                    total_cobrado = col_total.number_input("Total a Cobrar ($)", min_value=0.0, value=total_calc)

                    if st.button("✅ Confirmar Venta", use_container_width=True):
                        # 1. Descuento stock
                        supabase.table("inventario").update({"stock": stock_disp - cantidad}).eq("id", id_prod).execute()
                        
                        # 2. Registro plata (IMPORTANTE: Guardamos Marca en formato (Marca) para poder leerlo después)
                        venta = {
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "tipo": "Ingreso",
                            "descripcion": f"Venta: {cantidad}x {nombre_real} ({marca_real})",
                            "monto": total_cobrado
                        }
                        supabase.table("finanzas").insert(venta).execute()
                        st.success(f"¡Venta registrada! Cobraste ${total_cobrado}")
                        st.rerun()
                else:
                    st.error("❌ Producto agotado (Stock 0).")

# ==========================================
# 3. GASTOS
# ==========================================
with tab3:
    st.header("Registrar Gasto")
    with st.form("gasto"):
        desc = st.text_input("Descripción")
        monto = st.number_input("Monto ($)", min_value=0.0, value=None, placeholder="0.00")
        if st.form_submit_button("Guardar Gasto"):
            if monto:
                gasto = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tipo": "Gasto",
                    "descripcion": desc,
                    "monto": -monto 
                }
                supabase.table("finanzas").insert(gasto).execute()
                st.success("✅ Gasto registrado.")
                st.rerun()
            else:
                st.error("Falta el monto.")

# ==========================================
# 4. FINANZAS (CON FILTRO Y RESTITUCIÓN)
# ==========================================
with tab4:
    st.header("Resumen Financiero")
    
    # --- FILTRO POR MES (NUEVO) ---
    df_filtrado = df_fin
    filtro_texto = "Todos los tiempos"

    if not df_fin.empty:
        # Convertimos fecha string a objeto fecha real
        df_fin["fecha_dt"] = pd.to_datetime(df_fin["fecha"], errors='coerce')
        df_fin["mes"] = df_fin["fecha_dt"].dt.strftime("%Y-%m") # Ej: 2026-02
        
        # Lista de meses disponibles
        opciones_mes = ["Todos los tiempos"] + sorted(df_fin["mes"].dropna().unique().tolist(), reverse=True)
        
        col_filtro, _ = st.columns([1, 3])
        filtro_texto = col_filtro.selectbox("📅 Filtrar por Mes:", opciones_mes)
        
        if filtro_texto != "Todos los tiempos":
            df_filtrado = df_fin[df_fin["mes"] == filtro_texto]

    # --- MÉTRICAS ---
    if not df_filtrado.empty:
        ingresos = df_filtrado[df_filtrado["monto"] > 0]["monto"].sum()
        gastos = df_filtrado[df_filtrado["monto"] < 0]["monto"].sum()
        balance = ingresos + gastos
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ingresos:,.0f}")
        c2.metric("Gastos", f"${abs(gastos):,.0f}")
        c3.metric("Ganancia Neta", f"${balance:,.0f}", 
                  delta_color="normal" if balance >= 0 else "inverse")
    else:
        st.info("No hay movimientos en este período.")

    st.divider()

    # --- HERRAMIENTA DE CORRECCIÓN ---
    with st.expander("🗑️ Corregir / Eliminar Movimiento (Devuelve Stock)"):
        if not df_fin.empty:
            # Usamos el DF completo para poder borrar cosas viejas aunque filtremos el mes
            df_fin["label"] = df_fin["fecha"] + " | " + df_fin["descripcion"] + " | $" + df_fin["monto"].astype(str)
            lista_movimientos = df_fin.sort_values("id", ascending=False)["label"]
            
            borrar_seleccion = st.selectbox("Selecciona movimiento a borrar:", lista_movimientos)
            
            if st.button("Borrar y Restituir", type="primary"):
                try:
                    fila = df_fin[df_fin["label"] == borrar_seleccion].iloc[0]
                    id_borrar = int(fila["id"])
                    desc = fila["descripcion"]
                    tipo = fila["tipo"]

                    # Lógica de Restitución EXACTA
                    if tipo == "Ingreso" and "Venta:" in desc:
                        try:
                            # 1. Parsear cantidad "Venta: 2x ..."
                            parte_cantidad = desc.split("x ")[0] 
                            cantidad_reponer = int(parte_cantidad.split(": ")[1])
                            
                            # 2. Parsear Nombre y Marca "... Nombre (Marca)"
                            parte_resto = desc.split("x ")[1]
                            
                            nombre_prod = ""
                            marca_prod = ""

                            if "(" in parte_resto and parte_resto.endswith(")"):
                                # Separa desde la derecha para evitar líos si el nombre tiene parentesis
                                nombre_prod = parte_resto.rsplit(" (", 1)[0]
                                marca_prod = parte_resto.rsplit(" (", 1)[1].replace(")", "")
                            else:
                                nombre_prod = parte_resto
                                marca_prod = "Genérico"

                            # 3. Buscar Producto exacto
                            q = supabase.table("inventario").select("*").eq("producto", nombre_prod).eq("marca", marca_prod).execute()
                            
                            if q.data:
                                prod = q.data[0]
                                supabase.table("inventario").update({"stock": prod["stock"] + cantidad_reponer}).eq("id", prod["id"]).execute()
                                st.toast(f"✅ Stock devuelto: {cantidad_reponer}u a {nombre_prod}")
                            else:
                                st.warning(f"⚠️ Producto '{nombre_prod}' no encontrado, no se pudo devolver stock.")
                        except:
                            pass # Si falla el parseo, igual borra la plata

                    # Borrar registro financiero
                    supabase.table("finanzas").delete().eq("id", id_borrar).execute()
                    st.success("Registro eliminado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al borrar: {e}")

    # --- TABLA DETALLE ---
    st.subheader(f"Detalle: {filtro_texto}")
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado.sort_values("id", ascending=False)[["fecha", "tipo", "descripcion", "monto"]], 
            use_container_width=True, 
            hide_index=True
        )