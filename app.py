import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import time

# =========================
# CONFIG PÁGINA
# =========================
st.set_page_config(page_title="Ilara Beauty", layout="wide", page_icon="💄")

# =========================
# CONEXIÓN SUPABASE (CACHEADA)
# =========================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    @st.cache_resource
    def init_connection():
        return create_client(url, key)

    supabase: Client = init_connection()

except Exception:
    st.error("❌ Error de conexión: Revisa tus secretos (.streamlit/secrets.toml).")
    st.stop()

# =========================
# CARGA DE DATOS (CACHEADA)
# =========================
@st.cache_data(ttl=60)
def cargar_inventario():
    try:
        resp = supabase.table("inventario").select("*").execute()
        return pd.DataFrame(resp.data)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cargar_finanzas():
    try:
        resp = supabase.table("finanzas").select("*").execute()
        return pd.DataFrame(resp.data)
    except:
        return pd.DataFrame()

def limpiar_cache():
    st.cache_data.clear()

# =========================
# UI HEADER
# =========================
st.title("💅 Ilara Beauty — Gestión de Stock y Ventas")

# =========================
# DATA LOAD
# =========================
df_inv = cargar_inventario()
df_fin = cargar_finanzas()

# =========================
# BLINDAJE / NORMALIZACIÓN (DFs)
# =========================
if not df_inv.empty:
    for col in ["producto", "marca", "categoria"]:
        if col not in df_inv.columns:
            df_inv[col] = ""

    df_inv["producto"] = df_inv["producto"].astype(str)
    df_inv["marca"] = df_inv["marca"].astype(str)
    df_inv["categoria"] = df_inv["categoria"].astype(str)

    if "stock" not in df_inv.columns:
        df_inv["stock"] = 0
    if "precio_costo" not in df_inv.columns:
        df_inv["precio_costo"] = 0.0
    if "precio_venta" not in df_inv.columns:
        df_inv["precio_venta"] = 0.0

    df_inv["stock"] = pd.to_numeric(df_inv["stock"], errors="coerce").fillna(0).astype(int)
    df_inv["precio_costo"] = pd.to_numeric(df_inv["precio_costo"], errors="coerce").fillna(0.0)
    df_inv["precio_venta"] = pd.to_numeric(df_inv["precio_venta"], errors="coerce").fillna(0.0)

    df_inv["display"] = df_inv["producto"].str.strip() + " - " + df_inv["marca"].str.strip()

    # key normalizada para detectar duplicados localmente
    df_inv["key"] = df_inv["producto"].str.strip().str.lower() + "_" + df_inv["marca"].str.strip().str.lower()

if not df_fin.empty:
    for col in ["descripcion", "tipo", "fecha", "monto"]:
        if col not in df_fin.columns:
            df_fin[col] = None

    df_fin["descripcion"] = df_fin["descripcion"].astype(str)
    df_fin["tipo"] = df_fin["tipo"].astype(str)
    df_fin["fecha"] = df_fin["fecha"].astype(str)
    df_fin["monto"] = pd.to_numeric(df_fin["monto"], errors="coerce").fillna(0.0)

    # columnas nuevas (si existen)
    for col in ["producto_id", "cantidad", "metodo_pago", "cliente_nota"]:
        if col not in df_fin.columns:
            df_fin[col] = None

# =========================
# TABS PRINCIPALES
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Inventario", "💰 Nueva Venta", "💸 Nuevo Gasto", "📊 Finanzas", "💌 About"])

# =========================================================
# TAB 1 — INVENTARIO
# =========================================================
with tab1:
    st.header("📦 Inventario")

    if df_inv.empty:
        st.info("Todavía no hay productos cargados.")
    else:
        col_rep1, col_rep2 = st.columns([3, 1])
        with col_rep1:
            umbral = st.slider("⚠️ Umbral de alerta de stock bajo", 1, 20, 3)
        criticos = df_inv[df_inv["stock"] <= umbral].sort_values("stock")

        if not criticos.empty:
            st.warning(f"⚠️ Hay {len(criticos)} productos con stock bajo ({umbral} o menos).")
            with st.expander("Ver lista crítica"):
                st.dataframe(criticos[["producto", "marca", "categoria", "stock"]], use_container_width=True, hide_index=True)
                csv = criticos.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Descargar CSV", csv, "stock_bajo.csv", "text/csv")

    st.divider()

    subtab_ver, subtab_add, subtab_edit, subtab_ajuste, subtab_del = st.tabs(
        ["🔍 Ver/Buscar", "➕ Agregar/Reponer", "✏️ Editar", "📉 Ajuste", "🗑️ Eliminar"]
    )

    # -------------------------
    # VER / BUSCAR
    # -------------------------
    with subtab_ver:
        if df_inv.empty:
            st.info("Inventario vacío.")
        else:
            col_search, col_filter = st.columns([2, 1])
            search_term = col_search.text_input("🔍 Buscar por nombre o marca:", placeholder="Ej: Rimel")
            cats = sorted([c for c in df_inv["categoria"].dropna().unique().tolist() if c.strip() != ""])
            cat_filter = col_filter.multiselect("Filtrar categoría", cats)

            df_view = df_inv.copy()
            if search_term:
                df_view = df_view[df_view["display"].str.contains(search_term, case=False, na=False)]
            if cat_filter:
                df_view = df_view[df_view["categoria"].isin(cat_filter)]

            df_view["Ganancia"] = df_view["precio_venta"] - df_view["precio_costo"]
            st.dataframe(
                df_view[["producto", "marca", "categoria", "stock", "precio_costo", "precio_venta", "Ganancia"]]
                .sort_values(["categoria", "producto"], ascending=True),
                use_container_width=True,
                hide_index=True,
            )

    # -------------------------
    # AGREGAR / REPONER
    # -------------------------
    with subtab_add:
        with st.form("nuevo_prod"):
            st.caption("Si el nombre y marca coinciden, suma stock al existente.")
            c1, c2 = st.columns(2)

            nom = c1.text_input("Nombre").strip()
            marca = c2.text_input("Marca").strip()
            marca_final = marca if marca else "Genérico"

            cat = c1.selectbox("Categoría", ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"])
            stk_input = c2.number_input("Cantidad", min_value=1, value=1)

            costo = c1.number_input("Costo ($)", min_value=0.0, value=None, placeholder="0.00")
            venta = c2.number_input("Venta ($)", min_value=0.0, value=None, placeholder="0.00")

            if st.form_submit_button("Guardar"):
                if not nom or costo is None or venta is None:
                    st.error("⚠️ Faltan datos: Nombre, Costo y Venta son obligatorios.")
                else:
                    try:
                        key_input = nom.lower().strip() + "_" + marca_final.lower().strip()

                        if not df_inv.empty and "key" in df_inv.columns:
                            match = df_inv[df_inv["key"] == key_input]
                        else:
                            match = pd.DataFrame()

                        if not match.empty:
                            prod = match.iloc[0]
                            nuevo_stock = int(prod["stock"]) + int(stk_input)

                            supabase.table("inventario").update({
                                "stock": nuevo_stock,
                                "precio_costo": float(costo),
                                "precio_venta": float(venta),
                                "categoria": cat
                            }).eq("id", int(prod["id"])).execute()

                            st.toast(f"🔄 Stock sumado a {nom}", icon="✅")

                        else:
                            supabase.table("inventario").insert({
                                "producto": nom,
                                "marca": marca_final,
                                "categoria": cat,
                                "stock": int(stk_input),
                                "precio_costo": float(costo),
                                "precio_venta": float(venta)
                            }).execute()

                            st.toast(f"✅ Nuevo producto: {nom}", icon="✨")

                        limpiar_cache()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    # -------------------------
    # EDITAR
    # -------------------------
    with subtab_edit:
        if df_inv.empty:
            st.info("Primero cargá productos.")
        else:
            opciones_edit = df_inv["display"].tolist()
            seleccion_edit = st.selectbox("Producto a editar:", options=opciones_edit)

            fila_edit = df_inv[df_inv["display"] == seleccion_edit].iloc[0]

            with st.form("form_editar"):
                c1, c2 = st.columns(2)

                new_nom = c1.text_input("Nombre", value=str(fila_edit["producto"])).strip()
                new_marca = c2.text_input("Marca", value=str(fila_edit["marca"])).strip()

                cats = ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"]
                try:
                    cat_idx = cats.index(str(fila_edit["categoria"]))
                except:
                    cat_idx = 0

                new_cat = c1.selectbox("Categoría", cats, index=cat_idx)
                new_costo = c1.number_input("Costo ($)", min_value=0.0, value=float(fila_edit["precio_costo"]))
                new_venta = c2.number_input("Venta ($)", min_value=0.0, value=float(fila_edit["precio_venta"]))

                if st.form_submit_button("💾 Guardar cambios"):
                    try:
                        id_actual = int(fila_edit["id"])
                        new_key = new_nom.lower().strip() + "_" + new_marca.lower().strip()

                        dup = df_inv[(df_inv["key"] == new_key) & (df_inv["id"] != id_actual)]
                        if not dup.empty:
                            st.error("❌ Ya existe otro producto con ese Nombre+Marca.")
                        else:
                            supabase.table("inventario").update({
                                "producto": new_nom,
                                "marca": new_marca,
                                "categoria": new_cat,
                                "precio_costo": float(new_costo),
                                "precio_venta": float(new_venta)
                            }).eq("id", id_actual).execute()

                            st.toast("✅ Producto editado.", icon="💾")
                            limpiar_cache()
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error al editar: {e}")

    # -------------------------
    # AJUSTE DE STOCK
    # -------------------------
    with subtab_ajuste:
        if df_inv.empty:
            st.info("Sin productos.")
        else:
            with st.form("form_ajuste"):
                prod_ajuste = st.selectbox("Producto:", df_inv["display"].unique())
                tipo_ajuste = st.radio("Tipo:", ["Resta (Pérdida/Regalo)", "Suma (Encontré stock)"])
                cant_ajuste = st.number_input("Cantidad", min_value=1, value=1)
                motivo = st.text_input("Motivo (obligatorio)", placeholder="Ej: Se rompió / Regalo").strip()

                if st.form_submit_button("Aplicar ajuste"):
                    if not motivo:
                        st.error("⚠️ Falta el motivo.")
                    else:
                        try:
                            fila = df_inv[df_inv["display"] == prod_ajuste].iloc[0]
                            id_prod = int(fila["id"])
                            stock_actual = int(fila["stock"])

                            nuevo_stock = stock_actual - int(cant_ajuste) if "Resta" in tipo_ajuste else stock_actual + int(cant_ajuste)
                            if nuevo_stock < 0:
                                st.error(f"❌ No podés restar {cant_ajuste}. Solo hay {stock_actual}.")
                            else:
                                supabase.table("inventario").update({"stock": nuevo_stock}).eq("id", id_prod).execute()

                                signo = "-" if "Resta" in tipo_ajuste else "+"
                                desc_ajuste = f"Ajuste: {signo}{int(cant_ajuste)}x {fila['producto']} ({fila['marca']}) | Motivo: {motivo}"

                                supabase.table("finanzas").insert({
                                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "tipo": "Ajuste",
                                    "descripcion": desc_ajuste,
                                    "monto": 0.0
                                }).execute()

                                st.toast("✅ Ajuste registrado.", icon="📉")
                                limpiar_cache()
                                st.rerun()

                        except Exception as e:
                            st.error(f"Error en ajuste: {e}")

    # -------------------------
    # ELIMINAR PRODUCTO
    # -------------------------
    with subtab_del:
        if df_inv.empty:
            st.info("Nada para eliminar.")
        else:
            st.warning("⚠️ Esto borra el producto del inventario. (Las ventas pasadas quedan en finanzas).")
            elegido = st.selectbox("Producto a eliminar:", df_inv["display"].tolist())
            confirmado = st.checkbox("Estoy seguro de eliminar este producto", key="chk_del_producto")

            if st.button("Eliminar definitivamente", type="primary", disabled=not confirmado):
                try:
                    fila = df_inv[df_inv["display"] == elegido].iloc[0]
                    supabase.table("inventario").delete().eq("id", int(fila["id"])).execute()
                    st.toast("🗑️ Producto eliminado.", icon="👋")
                    limpiar_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

# =========================================================
# TAB 2 — REGISTRAR VENTA (CON CAMPOS ESTRUCTURADOS)
# =========================================================
with tab2:
    st.header("💰 Registrar Venta")

    if df_inv.empty:
        st.warning("Primero cargá productos en Inventario.")
    else:
        opciones = df_inv["display"].unique()
        seleccion = st.selectbox("Producto a vender", opciones)

        fila_local = df_inv[df_inv["display"] == seleccion].iloc[0]
        precio_unit = float(fila_local.get("precio_venta", 0))
        stock_local = int(fila_local.get("stock", 0))
        id_prod = int(fila_local.get("id", 0))
        nombre_real = str(fila_local.get("producto", "Desconocido"))
        marca_real = str(fila_local.get("marca", "Genérico"))

        c1, c2 = st.columns(2)
        c1.metric("Precio Unitario", f"${precio_unit:,.0f}")
        c2.metric("Stock (estimado)", f"{stock_local} u.")

        if stock_local <= 0:
            st.error("❌ Producto agotado (stock 0).")
        else:
            col_cant, col_total = st.columns(2)

            # cantidad: key única para que no “se pegue” raro entre productos
            cantidad = col_cant.number_input(
                "Cantidad",
                min_value=1,
                max_value=max(1, stock_local),
                value=1,
                key=f"cant_vta_{id_prod}"
            )

            total_calc = precio_unit * int(cantidad)

            # total: key única por producto
            total_cobrado = col_total.number_input(
                "Total a cobrar ($)",
                min_value=0.0,
                value=float(total_calc),
                key=f"total_vta_{id_prod}"
            )

            c_pago, c_nota = st.columns(2)
            metodo_pago = c_pago.selectbox(
                "Método de Pago",
                ["Efectivo", "Transferencia", "Cuenta Corriente (Fiado)", "Otro"],
                key=f"pago_vta_{id_prod}"
            )
            cliente_nota = c_nota.text_input(
                "Cliente / Nota",
                placeholder="Ej: María",
                key=f"nota_vta_{id_prod}"
            ).strip()

            if st.button("✅ Confirmar Venta", use_container_width=True):
                try:
                    # 1) Chequear stock REAL en DB
                    check = supabase.table("inventario").select("stock").eq("id", id_prod).single().execute()
                    stock_real = int(check.data.get("stock", 0))

                    if stock_real < int(cantidad):
                        st.error(f"❌ Stock insuficiente. Quedan {stock_real} reales.")
                        st.stop()

                    # 2) Descontar stock
                    supabase.table("inventario").update({"stock": stock_real - int(cantidad)}).eq("id", id_prod).execute()

                    # 3) Descripción humana (pero ya NO dependemos de esto)
                    desc_final = f"Venta: {int(cantidad)}x {nombre_real} ({marca_real})"
                    extras = [f"Pago: {metodo_pago}"]
                    if cliente_nota:
                        extras.append(f"Nota: {cliente_nota}")
                    desc_final += " | " + " | ".join(extras)

                    # 4) Insert finanzas con columnas estructuradas
                    try:
                        supabase.table("finanzas").insert({
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "tipo": "Ingreso",
                            "descripcion": desc_final,
                            "monto": float(total_cobrado),
                            "producto_id": int(id_prod),
                            "cantidad": int(cantidad),
                            "metodo_pago": metodo_pago,
                            "cliente_nota": cliente_nota if cliente_nota else None
                        }).execute()
                    except Exception as e_insert:
                        # rollback manual
                        supabase.table("inventario").update({"stock": stock_real}).eq("id", int(id_prod)).execute()
                        raise e_insert

                    st.toast(f"💰 Venta registrada: ${float(total_cobrado):,.0f}", icon="✅")
                    limpiar_cache()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error al procesar venta: {e}")

# =========================================================
# TAB 3 — GASTOS
# =========================================================
with tab3:
    st.header("💸 Registrar Gasto")

    with st.form("form_gasto"):
        desc = st.text_input("Descripción").strip()
        monto = st.number_input("Monto ($)", min_value=0.0, value=None, placeholder="0.00")
        if st.form_submit_button("Guardar Gasto"):
            if not desc or monto is None or float(monto) <= 0:
                st.error("Faltan datos: descripción y monto válido.")
            else:
                try:
                    supabase.table("finanzas").insert({
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "tipo": "Gasto",
                        "descripcion": desc,
                        "monto": -float(monto)
                    }).execute()
                    st.toast("✅ Gasto registrado.", icon="💸")
                    limpiar_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error guardando gasto: {e}")

# =========================================================
# TAB 4 — FINANZAS (FILTRO + BORRADO CON RESTITUCIÓN)
# =========================================================
with tab4:
    st.header("📊 Finanzas")

    df_work = df_fin.copy() if not df_fin.empty else pd.DataFrame(columns=["id", "fecha", "tipo", "descripcion", "monto"])

    filtro_texto = "Todos los tiempos"
    if not df_work.empty:
        df_work["fecha_dt"] = pd.to_datetime(df_work["fecha"], errors="coerce")
        df_work["mes"] = df_work["fecha_dt"].dt.strftime("%Y-%m")
        meses = ["Todos los tiempos"] + sorted(df_work["mes"].dropna().unique().tolist(), reverse=True)

        col_f, _ = st.columns([1, 3])
        filtro_texto = col_f.selectbox("📅 Filtrar por mes:", meses)

        df_filtrado = df_work[df_work["mes"] == filtro_texto] if filtro_texto != "Todos los tiempos" else df_work
    else:
        df_filtrado = df_work

    if not df_filtrado.empty:
        ingresos = df_filtrado[df_filtrado["monto"] > 0]["monto"].sum()
        gastos = df_filtrado[df_filtrado["monto"] < 0]["monto"].sum()
        balance = ingresos + gastos

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ingresos:,.0f}")
        c2.metric("Gastos", f"${abs(gastos):,.0f}")
        c3.metric("Neto", f"${balance:,.0f}", delta_color="normal" if balance >= 0 else "inverse")
    else:
        st.info("No hay movimientos en este período.")

    st.divider()

    with st.expander("🗑️ Corregir / Eliminar Movimiento (Devuelve Stock)"):
        if df_work.empty:
            st.info("Nada para borrar.")
        else:
            # limpieza de ids
            df_work["id"] = pd.to_numeric(df_work.get("id", None), errors="coerce")
            df_clean = df_work.dropna(subset=["id"]).copy()
            df_clean["id"] = df_clean["id"].astype(int)

            busqueda = st.text_input("🔍 Buscar movimiento (texto o monto):", key="buscar_mov").strip()

            if busqueda:
                m_desc = df_clean["descripcion"].str.contains(busqueda, case=False, na=False)
                m_num = False
                try:
                    val = float(busqueda.replace(",", "."))
                    m_num = df_clean["monto"].round(2) == round(val, 2)
                except:
                    m_num = False
                df_sel = df_clean[m_desc | m_num].sort_values("id", ascending=False)
            else:
                df_sel = df_clean.sort_values("id", ascending=False)

            if df_sel.empty:
                st.info("No se encontraron movimientos.")
            else:
                ids = df_sel["id"].tolist()

                def pretty_label(_id: int):
                    r = df_sel[df_sel["id"] == _id].iloc[0]
                    return f"{r['fecha']} | {r['tipo']} | {r['descripcion']} | ${float(r['monto']):,.2f} | (ID:{_id})"

                id_borrar = st.selectbox("Seleccioná movimiento:", options=ids, format_func=pretty_label)
                confirmado = st.checkbox("Confirmo borrar y (si aplica) devolver stock", key="chk_del_fin")

                if st.button("Borrar ahora", type="primary", disabled=not confirmado):
                    try:
                        fila = df_sel[df_sel["id"] == int(id_borrar)].iloc[0]
                        desc = str(fila.get("descripcion", ""))
                        tipo = str(fila.get("tipo", ""))

                        msg_stock = ""

                        # Restitución (primero por ID)
                        if tipo == "Ingreso":
                            restituido = False
                            try:
                                pid = fila.get("producto_id", None)
                                qty = fila.get("cantidad", None)

                                if pd.notna(pid) and pd.notna(qty):
                                    pid = int(pid)
                                    qty = int(qty)

                                    check = supabase.table("inventario").select("stock").eq("id", pid).single().execute()
                                    curr_stock = int(check.data.get("stock", 0))

                                    supabase.table("inventario").update({"stock": curr_stock + qty}).eq("id", pid).execute()
                                    msg_stock = f" (Stock devuelto +{qty} por ID)"
                                    restituido = True
                            except:
                                pass

                            # Fallback legacy (texto)
                            if not restituido and "Venta:" in desc:
                                try:
                                    desc_pura = desc.split(" | ", 1)[0]
                                    parte_cantidad = desc_pura.split("x ", 1)[0]
                                    cantidad_reponer = int(parte_cantidad.split(": ")[1])

                                    parte_resto = desc_pura.split("x ", 1)[1]
                                    if "(" in parte_resto and parte_resto.endswith(")"):
                                        nombre_prod = parte_resto.rsplit(" (", 1)[0]
                                        marca_prod = parte_resto.rsplit(" (", 1)[1].replace(")", "")
                                    else:
                                        nombre_prod = parte_resto
                                        marca_prod = "Genérico"

                                    q = supabase.table("inventario").select("*").eq("producto", nombre_prod).eq("marca", marca_prod).execute()
                                    if q.data:
                                        prod = q.data[0]
                                        supabase.table("inventario").update({"stock": int(prod["stock"]) + cantidad_reponer}).eq("id", int(prod["id"])).execute()
                                        msg_stock = f" (Stock devuelto +{cantidad_reponer} por texto)"
                                except:
                                    pass

                        supabase.table("finanzas").delete().eq("id", int(id_borrar)).execute()
                        st.toast(f"✅ Movimiento eliminado.{msg_stock}", icon="🗑️")
                        limpiar_cache()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error al borrar: {e}")

    st.subheader(f"Detalle: {filtro_texto}")
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado.sort_values("id", ascending=False)[["fecha", "tipo", "descripcion", "monto"]],
            use_container_width=True,
            hide_index=True,
        )

# =========================================================
# TAB 5 — ABOUT (DEDICATORIA)
# =========================================================
with tab5:
    st.header("💌 About")
    st.write("Esta app está hecha para ordenar stock, ventas y gastos de **Ilara Beauty**.")
    st.divider()

    with st.expander("Para Mara ❤️"):
        st.markdown("""
**Mara**,  
esta app es un pedacito de tus ganas y tu laburo convertido en orden y progreso.  
Que cada venta te acerque a lo que soñás, y que nunca te falten motivos para sonreír.

**Te amo.**  
— Ilan
""")

# =========================================================
# FOOTER FIJO
# =========================================================
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(255,255,255,0.88);
        padding: 8px 12px;
        text-align: center;
        font-size: 13px;
        color: #555;
        border-top: 1px solid rgba(0,0,0,0.08);
        z-index: 9999;
    }
    </style>
    <div class="footer">by ChadGpt e Ilan con amor · v2</div>
    """,
    unsafe_allow_html=True
)
