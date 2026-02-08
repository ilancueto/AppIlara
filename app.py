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
    st.error("❌ Error de conexión: revisá .streamlit/secrets.toml")
    st.stop()

# =========================
# HELPERS
# =========================
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def clear_data_cache():
    # Streamlit no permite limpiar 1 sola función fácil: limpiamos cache_data entero.
    st.cache_data.clear()

def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

# =========================
# CARGA DE DATOS (CACHE GRANULAR)
# =========================
@st.cache_data(ttl=60)
def cargar_inventario():
    try:
        res = supabase.table("inventario").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cargar_finanzas():
    try:
        # Traemos todo (si existen columnas nuevas, vienen)
        res = supabase.table("finanzas").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception:
        return pd.DataFrame()

# =========================
# UI HEADER
# =========================
st.title("💅 Ilara Beauty — Stock & Caja")

df_inv = cargar_inventario()
df_fin = cargar_finanzas()

# =========================
# BLINDAJE + CAMPOS DERIVADOS
# =========================
if not df_inv.empty:
    # strings
    df_inv["producto"] = df_inv.get("producto", "").astype(str)
    df_inv["marca"] = df_inv.get("marca", "").astype(str)
    df_inv["categoria"] = df_inv.get("categoria", "").astype(str)

    # display único para UI
    df_inv["display"] = df_inv["producto"].str.strip() + " - " + df_inv["marca"].str.strip()

    # key normalizada para detectar duplicados (case-insensitive)
    df_inv["key"] = df_inv["producto"].str.strip().str.lower() + "_" + df_inv["marca"].str.strip().str.lower()

    # numéricos
    df_inv["id"] = pd.to_numeric(df_inv.get("id", None), errors="coerce")
    df_inv["stock"] = pd.to_numeric(df_inv.get("stock", 0), errors="coerce").fillna(0).astype(int)
    df_inv["precio_costo"] = pd.to_numeric(df_inv.get("precio_costo", 0), errors="coerce").fillna(0.0).astype(float)
    df_inv["precio_venta"] = pd.to_numeric(df_inv.get("precio_venta", 0), errors="coerce").fillna(0.0).astype(float)

if not df_fin.empty:
    df_fin["id"] = pd.to_numeric(df_fin.get("id", None), errors="coerce")
    df_fin["fecha"] = df_fin.get("fecha", "").astype(str)
    df_fin["tipo"] = df_fin.get("tipo", "").astype(str)
    df_fin["descripcion"] = df_fin.get("descripcion", "").astype(str)
    df_fin["monto"] = pd.to_numeric(df_fin.get("monto", 0), errors="coerce").fillna(0.0).astype(float)

    # columnas nuevas (si no existen en la tabla aún, las creamos para no romper UI)
    if "producto_id" not in df_fin.columns:
        df_fin["producto_id"] = None
    if "cantidad" not in df_fin.columns:
        df_fin["cantidad"] = None
    if "metodo_pago" not in df_fin.columns:
        df_fin["metodo_pago"] = None
    if "nota" not in df_fin.columns:
        df_fin["nota"] = None

# =========================
# TABS PRINCIPALES
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventario", "💰 Nueva Venta", "💸 Nuevo Gasto", "📊 Finanzas"])

# =========================================================
# TAB 1 — INVENTARIO
# =========================================================
with tab1:
    st.header("📦 Gestión de Productos")

    if df_inv.empty:
        st.info("Todavía no hay productos en inventario.")
    else:
        colA, colB = st.columns([3, 1])
        with colA:
            umbral = st.slider("⚠️ Umbral de stock bajo", 1, 20, 3)
        criticos = df_inv[df_inv["stock"] <= umbral].sort_values("stock")
        if not criticos.empty:
            st.warning(f"⚠️ {len(criticos)} productos con stock bajo (≤ {umbral}).")
            with st.expander("Ver lista + Exportar"):
                st.dataframe(criticos[["producto", "marca", "categoria", "stock"]], use_container_width=True, hide_index=True)
                csv = criticos.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Descargar CSV", csv, "stock_bajo.csv", "text/csv")

    st.divider()

    sub1, sub2, sub3, sub4, sub5 = st.tabs(["🔍 Ver/Buscar", "➕ Agregar/Reponer", "✏️ Editar", "📉 Ajuste", "🗑️ Eliminar"])

    # -------------------------
    # SUBTAB 1 — VER/BUSCAR
    # -------------------------
    with sub1:
        if df_inv.empty:
            st.info("Inventario vacío.")
        else:
            colS, colF = st.columns([2, 1])
            search_term = colS.text_input("🔍 Buscar por nombre o marca", placeholder="Ej: Rimel")
            cats = sorted([c for c in df_inv["categoria"].dropna().unique().tolist() if str(c).strip() != ""])
            cat_filter = colF.multiselect("Filtrar categoría", cats)

            view = df_inv.copy()
            if search_term.strip():
                view = view[view["display"].str.contains(search_term.strip(), case=False, na=False)]
            if cat_filter:
                view = view[view["categoria"].isin(cat_filter)]

            view["ganancia"] = view["precio_venta"] - view["precio_costo"]
            st.dataframe(
                view[["producto", "marca", "categoria", "stock", "precio_costo", "precio_venta", "ganancia"]],
                use_container_width=True,
                hide_index=True
            )

    # -------------------------
    # SUBTAB 2 — AGREGAR/REPONER
    # -------------------------
    with sub2:
        st.caption("Mismo producto + marca (ignorando mayúsc/minúsc) => suma stock.")
        with st.form("form_add"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nombre").strip()
            marca = c2.text_input("Marca").strip()
            marca_final = marca if marca else "Genérico"

            cat = c1.selectbox("Categoría", ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"])
            stk = c2.number_input("Cantidad", min_value=1, value=1, step=1)

            costo = c1.number_input("Costo unitario ($)", min_value=0.0, value=0.0, step=50.0)
            venta = c2.number_input("Precio venta ($)", min_value=0.0, value=0.0, step=50.0)

            ok = st.form_submit_button("Guardar")
            if ok:
                if not nom:
                    st.error("Falta el nombre.")
                else:
                    try:
                        key_in = nom.strip().lower() + "_" + marca_final.strip().lower()

                        if df_inv.empty:
                            match = pd.DataFrame()
                        else:
                            match = df_inv[df_inv["key"] == key_in]

                        if not match.empty:
                            prod = match.iloc[0]
                            new_stock = safe_int(prod["stock"]) + safe_int(stk)

                            supabase.table("inventario").update({
                                "stock": new_stock,
                                "precio_costo": float(costo),
                                "precio_venta": float(venta),
                                "categoria": cat,
                                "producto": nom.strip(),
                                "marca": marca_final.strip()
                            }).eq("id", int(prod["id"])).execute()

                            st.toast(f"🔄 Reposición OK (+{stk})", icon="✅")
                        else:
                            supabase.table("inventario").insert({
                                "producto": nom.strip(),
                                "marca": marca_final.strip(),
                                "categoria": cat,
                                "stock": int(stk),
                                "precio_costo": float(costo),
                                "precio_venta": float(venta)
                            }).execute()

                            st.toast("✨ Producto creado", icon="✅")

                        clear_data_cache()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error guardando: {e}")

    # -------------------------
    # SUBTAB 3 — EDITAR
    # -------------------------
    with sub3:
        if df_inv.empty:
            st.info("No hay productos para editar.")
        else:
            opciones = df_inv["display"].tolist()
            sel = st.selectbox("Producto a editar", opciones, key="edit_sel")
            fila = df_inv[df_inv["display"] == sel].iloc[0]

            with st.form("form_edit"):
                c1, c2 = st.columns(2)
                new_nom = c1.text_input("Nombre", value=str(fila["producto"])).strip()
                new_marca = c2.text_input("Marca", value=str(fila["marca"])).strip()

                cats = ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"]
                idx = cats.index(fila["categoria"]) if str(fila["categoria"]) in cats else 0
                new_cat = c1.selectbox("Categoría", cats, index=idx)

                new_costo = c1.number_input("Costo ($)", min_value=0.0, value=float(fila["precio_costo"]), step=50.0)
                new_venta = c2.number_input("Venta ($)", min_value=0.0, value=float(fila["precio_venta"]), step=50.0)

                ok = st.form_submit_button("💾 Guardar cambios")
                if ok:
                    if not new_nom:
                        st.error("El nombre no puede estar vacío.")
                    else:
                        try:
                            id_actual = int(fila["id"])
                            new_key = new_nom.lower() + "_" + (new_marca if new_marca else "Genérico").lower()
                            dup = df_inv[(df_inv["key"] == new_key) & (df_inv["id"] != id_actual)]
                            if not dup.empty:
                                st.error("❌ Ya existe otro producto con ese nombre + marca.")
                            else:
                                supabase.table("inventario").update({
                                    "producto": new_nom.strip(),
                                    "marca": (new_marca.strip() if new_marca else "Genérico"),
                                    "categoria": new_cat,
                                    "precio_costo": float(new_costo),
                                    "precio_venta": float(new_venta),
                                }).eq("id", id_actual).execute()

                                st.toast("✅ Editado", icon="💾")
                                clear_data_cache()
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error editando: {e}")

    # -------------------------
    # SUBTAB 4 — AJUSTE
    # -------------------------
    with sub4:
        if df_inv.empty:
            st.info("No hay productos para ajustar.")
        else:
            st.caption("Para roturas, regalos, pérdidas o conteo.")
            with st.form("form_ajuste"):
                prod = st.selectbox("Producto", df_inv["display"].unique().tolist())
                tipo = st.radio("Tipo", ["Resta (Pérdida/Regalo)", "Suma (Encontré stock)"], horizontal=True)
                cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
                motivo = st.text_input("Motivo (obligatorio)", placeholder="Ej: Se rompió / Regalo").strip()

                ok = st.form_submit_button("Aplicar ajuste")
                if ok:
                    if not motivo:
                        st.error("Falta el motivo.")
                    else:
                        try:
                            fila = df_inv[df_inv["display"] == prod].iloc[0]
                            idp = int(fila["id"])
                            stock_act = int(fila["stock"])

                            nuevo = stock_act - int(cant) if "Resta" in tipo else stock_act + int(cant)
                            if nuevo < 0:
                                st.error(f"No podés dejar stock negativo. Stock actual: {stock_act}.")
                            else:
                                supabase.table("inventario").update({"stock": nuevo}).eq("id", idp).execute()

                                signo = "-" if "Resta" in tipo else "+"
                                supabase.table("finanzas").insert({
                                    "fecha": now_str(),
                                    "tipo": "Ajuste",
                                    "descripcion": f"Ajuste: {signo}{cant}x {fila['producto']} ({fila['marca']}) | Motivo: {motivo}",
                                    "monto": 0.0
                                }).execute()

                                st.toast("✅ Ajuste aplicado", icon="📉")
                                clear_data_cache()
                                st.rerun()

                        except Exception as e:
                            st.error(f"Error aplicando ajuste: {e}")

    # -------------------------
    # SUBTAB 5 — ELIMINAR
    # -------------------------
    with sub5:
        if df_inv.empty:
            st.info("No hay productos para borrar.")
        else:
            st.warning("⚠️ Esto borra el producto del inventario. No borra ventas ya registradas.")
            sel = st.selectbox("Producto a eliminar", df_inv["display"].tolist(), key="del_sel")
            confirmado = st.checkbox("Estoy seguro de eliminar este producto", key="del_chk")

            if st.button("Eliminar definitivamente", type="primary", disabled=not confirmado):
                try:
                    fila = df_inv[df_inv["display"] == sel].iloc[0]
                    supabase.table("inventario").delete().eq("id", int(fila["id"])).execute()
                    st.toast("🗑️ Eliminado", icon="✅")
                    clear_data_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error borrando: {e}")

# =========================================================
# TAB 2 — NUEVA VENTA (ROBUSTA + CAMPOS ESTRUCTURADOS)
# =========================================================
with tab2:
    st.header("💰 Registrar Venta")

    if df_inv.empty:
        st.warning("Primero cargá productos en Inventario.")
    else:
        opciones = df_inv["display"].unique().tolist()
        sel = st.selectbox("Producto a vender", opciones, key="venta_sel")

        fila = df_inv[df_inv["display"] == sel].iloc[0]
        id_prod = int(fila["id"])
        precio_unit = float(fila["precio_venta"])
        stock_est = int(fila["stock"])

        c1, c2, c3 = st.columns(3)
        c1.metric("Precio unitario", f"${precio_unit:,.0f}")
        c2.metric("Stock actual", f"{stock_est} u.")
        c3.metric("Ganancia/u", f"${(fila['precio_venta'] - fila['precio_costo']):,.0f}")

        if stock_est <= 0:
            st.error("❌ Agotado.")
        else:
            col_q, col_total, col_reset = st.columns([1, 1, 0.4])

            # cantidad con tope por stock (y key única por producto)
            cantidad = col_q.number_input(
                "Cantidad",
                min_value=1,
                max_value=stock_est,
                value=1,
                step=1,
                key=f"qty_{id_prod}"
            )

            total_calc = precio_unit * int(cantidad)

            # ---- TOTAL editable: Streamlit no deja auto-seleccionar al click.
            # Solución realista: usamos session_state + botón reset.
            total_key = f"total_{id_prod}"
            if total_key not in st.session_state:
                st.session_state[total_key] = float(total_calc)

            # si cambia la cantidad, actualizamos el total sugerido SOLO si el user no lo tocó manualmente
            # (guardamos un flag)
            touched_key = f"total_touched_{id_prod}"
            if touched_key not in st.session_state:
                st.session_state[touched_key] = False

            # Si el usuario NO tocó el total, lo recalculamos en vivo
            if not st.session_state[touched_key]:
                st.session_state[total_key] = float(total_calc)

            total_cobrado = col_total.number_input(
                "Venta ($)",
                min_value=0.0,
                value=float(st.session_state[total_key]),
                step=50.0,
                key=total_key,
                help="Tip: si al click te queda el cursor al final, usá 🧹 Reset."
            )

            # marcamos touched si difiere del cálculo sugerido (o simplemente si el user lo cambia)
            if abs(total_cobrado - float(total_calc)) > 0.0001:
                st.session_state[touched_key] = True

            # Reset rápido a 0 (lo que me pediste: “clic y que quede en 0”)
            if col_reset.button("🧹 Reset", use_container_width=True):
                st.session_state[total_key] = 0.0
                st.session_state[touched_key] = True
                st.rerun()

            c_pago, c_nota = st.columns(2)
            metodo_pago = c_pago.selectbox("Método de pago", ["Efectivo", "Transferencia", "Cuenta Corriente", "Otro"], key=f"mp_{id_prod}")
            nota = c_nota.text_input("Cliente / Nota", placeholder="Ej: María", key=f"nota_{id_prod}").strip()

            if st.button("✅ Confirmar venta", use_container_width=True):
                stock_real = 0
                try:
                    # 1) Leer stock real de DB (single)
                    check = supabase.table("inventario").select("stock").eq("id", id_prod).single().execute()
                    stock_real = safe_int(check.data.get("stock", 0))

                    if stock_real < int(cantidad):
                        st.error(f"❌ Stock insuficiente. Quedan {stock_real} reales.")
                        clear_data_cache()
                        st.rerun()

                    # 2) Descontar stock
                    supabase.table("inventario").update({"stock": stock_real - int(cantidad)}).eq("id", id_prod).execute()

                    # 3) Insert finanzas (con columnas estructuradas)
                    desc = f"Venta: {int(cantidad)}x {fila['producto']} ({fila['marca']})"
                    extras = [f"Pago: {metodo_pago}"]
                    if nota:
                        extras.append(f"Nota: {nota}")
                    desc_final = desc + " | " + " | ".join(extras)

                    try:
                        supabase.table("finanzas").insert({
                            "fecha": now_str(),
                            "tipo": "Ingreso",
                            "descripcion": desc_final,
                            "monto": float(total_cobrado),
                            "producto_id": id_prod,
                            "cantidad": int(cantidad),
                            "metodo_pago": metodo_pago,
                            "nota": nota if nota else None
                        }).execute()
                    except Exception as e_ins:
                        # rollback manual del stock
                        supabase.table("inventario").update({"stock": stock_real}).eq("id", id_prod).execute()
                        raise e_ins

                    st.toast(f"💰 Venta registrada (${total_cobrado:,.0f})", icon="✅")
                    clear_data_cache()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error al registrar venta: {e}")

# =========================================================
# TAB 3 — GASTOS
# =========================================================
with tab3:
    st.header("💸 Registrar Gasto")

    with st.form("form_gasto"):
        desc = st.text_input("Descripción").strip()
        monto = st.number_input("Monto ($)", min_value=0.0, value=0.0, step=50.0)
        ok = st.form_submit_button("Guardar gasto")

        if ok:
            if not desc or monto <= 0:
                st.error("Completá descripción y monto > 0.")
            else:
                try:
                    supabase.table("finanzas").insert({
                        "fecha": now_str(),
                        "tipo": "Gasto",
                        "descripcion": desc,
                        "monto": -float(monto)
                    }).execute()
                    st.toast("✅ Gasto registrado", icon="💸")
                    clear_data_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error registrando gasto: {e}")

# =========================================================
# TAB 4 — FINANZAS (FILTRO + BORRADO + RESTITUCIÓN)
# =========================================================
with tab4:
    st.header("📊 Finanzas")

    df_work = df_fin.copy() if not df_fin.empty else pd.DataFrame(columns=["id", "fecha", "tipo", "descripcion", "monto"])

    # Filtro por mes
    filtro_texto = "Todos los tiempos"
    if not df_work.empty:
        df_work["fecha_dt"] = pd.to_datetime(df_work["fecha"], errors="coerce")
        df_work["mes"] = df_work["fecha_dt"].dt.strftime("%Y-%m")
        meses = ["Todos los tiempos"] + sorted(df_work["mes"].dropna().unique().tolist(), reverse=True)
        colF, _ = st.columns([1, 3])
        filtro_texto = colF.selectbox("📅 Filtrar por mes", meses)

        df_filtrado = df_work[df_work["mes"] == filtro_texto] if filtro_texto != "Todos los tiempos" else df_work
    else:
        df_filtrado = df_work

    # métricas
    if not df_filtrado.empty:
        ingresos = df_filtrado[df_filtrado["monto"] > 0]["monto"].sum()
        gastos = df_filtrado[df_filtrado["monto"] < 0]["monto"].sum()
        neto = ingresos + gastos
        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ingresos:,.0f}")
        c2.metric("Gastos", f"${abs(gastos):,.0f}")
        c3.metric("Neto", f"${neto:,.0f}", delta_color="normal" if neto >= 0 else "inverse")
    else:
        st.info("No hay movimientos en ese período.")

    st.divider()

    # Borrado + restitución
    with st.expander("🗑️ Corregir / Eliminar movimiento (restituye stock si corresponde)"):
        if df_work.empty:
            st.info("Nada para borrar.")
        else:
            df_work = df_work.dropna(subset=["id"]).copy()
            df_work["id"] = df_work["id"].astype(int)

            q = st.text_input("🔍 Buscar movimiento (texto o monto)", key="find_mov").strip()
            if q:
                m1 = df_work["descripcion"].str.contains(q, case=False, na=False)
                try:
                    m2 = df_work["monto"].round(2) == round(float(q.replace(",", ".")), 2)
                except Exception:
                    m2 = False
                df_sel = df_work[m1 | m2].sort_values("id", ascending=False)
            else:
                df_sel = df_work.sort_values("id", ascending=False)

            if df_sel.empty:
                st.info("No se encontraron movimientos.")
            else:
                ids = df_sel["id"].tolist()

                def label(_id: int):
                    r = df_sel[df_sel["id"] == _id].iloc[0]
                    return f"{r['fecha']} | {r['tipo']} | {r['descripcion']} | ${r['monto']:,.2f} | (ID:{_id})"

                id_del = st.selectbox("Seleccioná", ids, format_func=label)
                chk = st.checkbox("Confirmo borrar (y restituir stock si aplica)", key="chk_del_fin")

                if st.button("Borrar movimiento", type="primary", disabled=not chk):
                    try:
                        row = df_sel[df_sel["id"] == int(id_del)].iloc[0]
                        desc = str(row.get("descripcion", ""))
                        tipo = str(row.get("tipo", ""))

                        msg = ""
                        restituido = False

                        # 1) Restituir por ID/cantidad (ventas nuevas)
                        try:
                            pid = row.get("producto_id", None)
                            qty = row.get("cantidad", None)
                            if tipo == "Ingreso" and pd.notna(pid) and pd.notna(qty):
                                pid = int(pid)
                                qty = int(qty)

                                check = supabase.table("inventario").select("stock").eq("id", pid).single().execute()
                                curr = safe_int(check.data.get("stock", 0))
                                supabase.table("inventario").update({"stock": curr + qty}).eq("id", pid).execute()

                                msg = f" (Stock +{qty} restaurado por ID)"
                                restituido = True
                        except Exception:
                            pass

                        # 2) Fallback por texto (ventas viejas)
                        if (not restituido) and tipo == "Ingreso" and "Venta:" in desc:
                            try:
                                # Nos quedamos con la parte antes de los extras " | "
                                d_pura = desc.split(" | ", 1)[0]  # "Venta: 2x Prod (Marca)"
                                parts = d_pura.split("x ", 1)
                                qty = int(parts[0].split(": ")[1])
                                rest = parts[1]

                                if "(" in rest and rest.endswith(")"):
                                    nom = rest.rsplit(" (", 1)[0]
                                    mar = rest.rsplit(" (", 1)[1].replace(")", "")
                                else:
                                    nom, mar = rest, "Genérico"

                                qr = supabase.table("inventario").select("*").eq("producto", nom).eq("marca", mar).execute()
                                if qr.data:
                                    prd = qr.data[0]
                                    supabase.table("inventario").update({"stock": int(prd["stock"]) + qty}).eq("id", int(prd["id"])).execute()
                                    msg = f" (Stock +{qty} restaurado por texto)"
                            except Exception:
                                pass

                        # borrar movimiento
                        supabase.table("finanzas").delete().eq("id", int(id_del)).execute()

                        st.toast(f"✅ Borrado.{msg}", icon="🗑️")
                        clear_data_cache()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error borrando: {e}")

    st.subheader(f"Detalle: {filtro_texto}")
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado.sort_values("id", ascending=False)[["fecha", "tipo", "descripcion", "monto"]],
            use_container_width=True,
            hide_index=True
        )
