import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import pytz

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Ilara Beauty", layout="wide", page_icon="💄")
st.markdown(
    """
    <style>
    /* =========================
       BASE (Ilara Beauty)
       ========================= */

    /* Fondo general */
    .stApp {
        background-color: #ffb6c1;
    }

    /* Texto general */
    * {
        color: #660033 !important;
    }

    /* =========================
       BOTONES
       ========================= */
    button {
        background-color: #ffb6c1 !important;
        color: #b30059 !important;
        border-radius: 11px !important;
        border: none !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        transition: all .15s ease-in-out !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
    }

    button:hover {
        background-color: #ffffff !important;
        color: #b30059 !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.14);
    }

    /* Botón primario */
    button[kind="primary"] {
        background-color: #e60073 !important;
        color: white !important;
    }

    button[kind="primary"]:hover {
        background-color: #b8005a !important;
        color: white !important;
    }

    /* =========================
       CARDS / CONTENEDORES
       ========================= */
    .block-container {
        padding-top: 1.8rem;
    }

    div[data-testid="stMetric"],
    div[data-testid="stExpander"],
    div[data-testid="stForm"],
    div[data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.65);
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    div[data-testid="stDataFrame"] {
        overflow: hidden;
    }

    /* =========================
       TABS
       ========================= */
    div[data-testid="stTabs"] button {
        border-radius: 14px !important;
        padding: 10px 18px !important;
        font-weight: 700 !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        box-shadow: 0 10px 28px rgba(230,0,115,0.20) !important;
        transform: translateY(-1px);
    }

    /* =========================
       INPUTS / TEXTBOX / NUMBER INPUT (BaseWeb) ✅ FIX
       ========================= */

    /* Contenedor de inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #ff66b2 !important;
        box-shadow: none !important;
    }

    /* El input real (texto dentro) */
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        background-color: transparent !important;
        color: #660033 !important;
        caret-color: #e60073 !important;
        font-weight: 600 !important;
    }

    /* Placeholder */
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder {
        color: rgba(102,0,51,0.55) !important;
    }

    /* Focus glow */
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border: 2px solid #e60073 !important;
        box-shadow: 0 0 0 4px rgba(230,0,115,0.18) !important;
    }

    /* Botoncitos + / - (number_input) */
    div[data-baseweb="input"] button {
        background-color: #ffb6c1 !important;
        color: #660033 !important;
        box-shadow: none !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
    }

    div[data-baseweb="input"] button:hover {
        background-color: #ff99cc !important;
        color: #660033 !important;
        transform: none !important;
    }

    /* =========================
       SELECT / DROPDOWN (BaseWeb) ✅
       ========================= */

    /* Caja del select (control) */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #ff66b2 !important;
    }

    /* Texto dentro del select */
    div[data-baseweb="select"] * {
        color: #660033 !important;
    }

    /* Popover del dropdown */
    div[data-baseweb="popover"] {
        background-color: transparent !important;
    }

    /* Lista desplegable */
    div[data-baseweb="popover"] ul {
        background-color: #fff0f6 !important;
        border: 1px solid #ff99cc !important;
        border-radius: 12px !important;
        padding: 6px !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.18) !important;
    }

    /* Opciones */
    div[data-baseweb="popover"] li {
        background-color: #fff0f6 !important;
        color: #660033 !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
    }

    /* Hover */
    div[data-baseweb="popover"] li:hover {
        background-color: #ffb6c1 !important;
        color: #660033 !important;
    }

    /* Seleccionada */
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background-color: #ff99cc !important;
        color: #660033 !important;
        font-weight: 700 !important;
    }

    /* Martillazo extra por si algún tema oscuro se mete */
    [role="listbox"] {
        background-color: #fff0f6 !important;
        border: 1px solid #ff99cc !important;
        border-radius: 12px !important;
    }

    [role="option"] {
        color: #660033 !important;
    }

    [role="option"]:hover {
        background-color: #ffb6c1 !important;
    }

    /* =========================
       HEADER STREAMLIT (OCULTO)
       ========================= */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* =========================
       MOBILE
       ========================= */
    @media (max-width: 768px) {
        button {
            width: 100% !important;
        }
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
TZ_AR = pytz.timezone("America/Argentina/Buenos_Aires")

# =========================================================
# CONEXIÓN SUPABASE (cacheada)
# =========================================================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    @st.cache_resource
    def init_connection():
        return create_client(url, key)

    supabase: Client = init_connection()

except Exception:
    st.error("❌ Error de conexión: Revisá tus secretos (.streamlit/secrets.toml).")
    st.stop()

# =========================================================
# HELPERS
# =========================================================
def limpiar_cache():
    st.cache_data.clear()

def now_ar_str():
    # Fecha “linda” AR (si tu columna fecha es string)
    return datetime.now(TZ_AR).strftime("%d/%m/%Y %H:%M")

def formatear_monto_ars(x):
    try:
        return f"${float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(x)

def formatear_fecha_arg(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte timestamps (UTC o ISO) a hora Argentina y formatea.
    Si ya viniera como string, intenta parsear.
    Devuelve columnas: fecha_dt y fecha_fmt.
    """
    if df.empty or "fecha" not in df.columns:
        return df

    out = df.copy()

    out["fecha_dt"] = pd.to_datetime(out["fecha"], errors="coerce", utc=True)

    mask_na = out["fecha_dt"].isna()
    if mask_na.any():
        out.loc[mask_na, "fecha_dt"] = pd.to_datetime(out.loc[mask_na, "fecha"], errors="coerce")

    try:
        out["fecha_dt"] = out["fecha_dt"].dt.tz_convert(TZ_AR)
    except Exception:
        pass

    out["fecha_fmt"] = out["fecha_dt"].dt.strftime("%d/%m/%Y %H:%M")
    out["fecha_fmt"] = out["fecha_fmt"].fillna(out["fecha"].astype(str))
    return out

# =========================================================
# CARGA DE DATOS (cache)
# =========================================================
@st.cache_data(ttl=60)
def cargar_inventario():
    try:
        res = supabase.table("inventario").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cargar_finanzas():
    try:
        res = supabase.table("finanzas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# =========================================================
# UI HEADER + FOOTER
# =========================================================
st.title("💅 Ilara Beauty — Stock, Ventas y Finanzas")

# Footer fijo
st.markdown(
    """
    <style>
    .footer-fixed {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        padding: 8px 0;
        text-align: center;
        font-size: 12px;
        opacity: 0.75;
        background: rgba(0,0,0,0.0);
        z-index: 999;
        pointer-events: none;
    }
    </style>
    <div class="footer-fixed">by Ilan con amor · v3.1.0</div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DATA
# =========================================================
df_inv = cargar_inventario()
df_fin = cargar_finanzas()

# Blindajes inventario
if not df_inv.empty:
    for col in ["producto", "marca", "categoria"]:
        if col not in df_inv.columns:
            df_inv[col] = ""
        df_inv[col] = df_inv[col].astype(str)

    df_inv["display"] = df_inv["producto"] + " - " + df_inv["marca"]

    df_inv["stock"] = pd.to_numeric(df_inv.get("stock", 0), errors="coerce").fillna(0).astype(int)
    df_inv["precio_costo"] = pd.to_numeric(df_inv.get("precio_costo", 0), errors="coerce").fillna(0.0)
    df_inv["precio_venta"] = pd.to_numeric(df_inv.get("precio_venta", 0), errors="coerce").fillna(0.0)

    # key local robusta (para duplicados)
    df_inv["key"] = df_inv["producto"].str.strip().str.lower() + "_" + df_inv["marca"].str.strip().str.lower()

# Blindajes finanzas
if not df_fin.empty:
    if "descripcion" not in df_fin.columns:
        df_fin["descripcion"] = ""
    df_fin["descripcion"] = df_fin["descripcion"].astype(str)
    df_fin["monto"] = pd.to_numeric(df_fin.get("monto", 0), errors="coerce").fillna(0.0)

    for col in ["producto_id", "cantidad", "metodo_pago"]:
        if col not in df_fin.columns:
            df_fin[col] = None

# =========================================================
# TABS (tradicional)
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📦 Inventario", "💰 Nueva Venta", "💸 Nuevo Gasto", "📊 Finanzas", "💌 About"]
)

# =========================================================
# TAB 1: INVENTARIO
# =========================================================
with tab1:
    st.header("📦 Gestión de Productos")

    if df_inv.empty:
        st.info("Inventario vacío. Agregá el primer producto.")
    else:
        col_rep1, col_rep2 = st.columns([3, 1])
        with col_rep1:
            umbral = st.slider("⚠️ Umbral de alerta de stock", 1, 10, 3)

        criticos = df_inv[df_inv["stock"] <= umbral].sort_values("stock")
        if not criticos.empty:
            st.warning(f"⚠️ {len(criticos)} producto(s) con stock crítico ({umbral} o menos).")
            with st.expander("Ver lista crítica"):
                st.dataframe(criticos[["producto", "marca", "stock"]], use_container_width=True, hide_index=True)

    st.divider()

    sub_ver, sub_add, sub_edit, sub_ajuste, sub_del = st.tabs(
        ["🔍 Buscar", "➕ Agregar/Reponer", "✏️ Editar", "📉 Ajuste", "🗑️ Eliminar"]
    )

    # Buscar
    with sub_ver:
        if df_inv.empty:
            st.info("No hay productos.")
        else:
            c1, c2 = st.columns([2, 1])
            term = c1.text_input("🔍 Buscar por nombre o marca", placeholder="Ej: Rimel")
            cats = sorted(df_inv["categoria"].dropna().unique().tolist())
            filt_cat = c2.multiselect("Filtrar categoría", cats)

            view = df_inv.copy()
            if term:
                view = view[view["display"].str.contains(term, case=False, na=False)]
            if filt_cat:
                view = view[view["categoria"].isin(filt_cat)]

            view["ganancia"] = view["precio_venta"] - view["precio_costo"]

            view_show = view[["producto", "marca", "categoria", "stock", "precio_costo", "precio_venta", "ganancia"]].copy()
            view_show.rename(columns={
                "producto": "Producto",
                "marca": "Marca",
                "categoria": "Categoría",
                "stock": "Stock",
                "precio_costo": "Costo",
                "precio_venta": "Venta",
                "ganancia": "Ganancia"
            }, inplace=True)

            st.dataframe(view_show, use_container_width=True, hide_index=True)

    # Agregar / reponer
    with sub_add:
        with st.form("form_add"):
            st.caption("Si Nombre+Marca ya existe, suma stock.")
            a, b = st.columns(2)
            nom = a.text_input("Nombre").strip()
            marca = b.text_input("Marca").strip()
            marca_final = marca if marca else "Genérico"

            cat = a.selectbox("Categoría", ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"])
            cant = b.number_input("Cantidad", min_value=1, value=1, step=1)

            costo = a.number_input("Costo ($)", min_value=0.0, value=None, placeholder="0,00")
            venta = b.number_input("Venta ($)", min_value=0.0, value=None, placeholder="0,00")

            if st.form_submit_button("Guardar"):
                if not nom or costo is None or venta is None:
                    st.error("⚠️ Faltan datos (Nombre, Costo y Venta).")
                else:
                    try:
                        key_in = nom.lower() + "_" + marca_final.lower()
                        match = df_inv[df_inv["key"] == key_in] if not df_inv.empty else pd.DataFrame()

                        if not match.empty:
                            prod = match.iloc[0]
                            new_stock = int(prod["stock"]) + int(cant)
                            supabase.table("inventario").update({
                                "stock": new_stock,
                                "precio_costo": float(costo),
                                "precio_venta": float(venta),
                                "categoria": cat
                            }).eq("id", int(prod["id"])).execute()
                            st.toast(f"🔄 Stock actualizado: {prod['stock']} ➝ {new_stock}", icon="✅")
                        else:
                            supabase.table("inventario").insert({
                                "producto": nom,
                                "marca": marca_final,
                                "categoria": cat,
                                "stock": int(cant),
                                "precio_costo": float(costo),
                                "precio_venta": float(venta)
                            }).execute()
                            st.toast(f"✨ Nuevo producto: {nom}", icon="✅")

                        limpiar_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Editar
    with sub_edit:
        if df_inv.empty:
            st.info("Cargá productos primero.")
        else:
            sel = st.selectbox("Producto a editar", df_inv["display"].tolist())
            row = df_inv[df_inv["display"] == sel].iloc[0]

            with st.form("form_edit"):
                a, b = st.columns(2)
                new_nom = a.text_input("Nombre", value=row["producto"]).strip()
                new_marca = b.text_input("Marca", value=row["marca"]).strip()

                cats = ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"]
                idx = cats.index(row["categoria"]) if row["categoria"] in cats else 0
                new_cat = a.selectbox("Categoría", cats, index=idx)

                new_costo = a.number_input("Costo ($)", min_value=0.0, value=float(row["precio_costo"]))
                new_venta = b.number_input("Venta ($)", min_value=0.0, value=float(row["precio_venta"]))

                if st.form_submit_button("Guardar cambios"):
                    try:
                        id_actual = int(row["id"])
                        new_key = new_nom.lower() + "_" + new_marca.lower()
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

                            st.toast("💾 Producto editado.", icon="✅")
                            limpiar_cache()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Ajuste
    with sub_ajuste:
        if df_inv.empty:
            st.info("Sin productos.")
        else:
            with st.form("form_adj"):
                prod = st.selectbox("Producto", df_inv["display"].unique())
                tipo = st.radio("Tipo", ["Resta (Pérdida/Regalo)", "Suma (Encontré stock)"])
                cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
                motivo = st.text_input("Motivo (obligatorio)", placeholder="Ej: roto / regalo").strip()

                if st.form_submit_button("Aplicar ajuste"):
                    if not motivo:
                        st.error("⚠️ Motivo obligatorio.")
                    else:
                        try:
                            row = df_inv[df_inv["display"] == prod].iloc[0]
                            id_prod = int(row["id"])
                            stock_act = int(row["stock"])
                            new_stock = stock_act - int(cant) if "Resta" in tipo else stock_act + int(cant)

                            if new_stock < 0:
                                st.error(f"❌ No podés dejar stock negativo. Tenés {stock_act}.")
                            else:
                                supabase.table("inventario").update({"stock": new_stock}).eq("id", id_prod).execute()

                                signo = "-" if "Resta" in tipo else "+"
                                supabase.table("finanzas").insert({
                                    "fecha": now_ar_str(),
                                    "tipo": "Ajuste",
                                    "descripcion": f"Ajuste: {signo}{cant}x {row['producto']} ({row['marca']}) | Motivo: {motivo}",
                                    "monto": 0.0
                                }).execute()

                                st.toast("📉 Ajuste registrado.", icon="✅")
                                limpiar_cache()
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # Eliminar
    with sub_del:
        if df_inv.empty:
            st.info("Sin productos.")
        else:
            st.warning("⚠️ Borra el producto del inventario (no borra ventas pasadas).")
            prod = st.selectbox("Producto a eliminar", df_inv["display"].tolist())
            ok = st.checkbox("Estoy seguro de eliminar este producto", key="chk_del_prod")

            if st.button("Eliminar definitivamente", type="primary", disabled=not ok):
                try:
                    row = df_inv[df_inv["display"] == prod].iloc[0]
                    supabase.table("inventario").delete().eq("id", int(row["id"])).execute()
                    st.toast("🗑️ Producto eliminado.", icon="✅")
                    limpiar_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# =========================================================
# TAB 2: VENTA (FIX total sugerido + callback)
# =========================================================
with tab2:
    st.header("💰 Registrar Venta")

    if df_inv.empty:
        st.warning("Primero cargá productos en Inventario.")
    else:
        opciones = df_inv["display"].unique()
        sel = st.selectbox("Producto a vender", opciones)

        if sel:
            row = df_inv[df_inv["display"] == sel].iloc[0]
            id_prod = int(row["id"])
            stock_est = int(row["stock"])
            precio_unit = float(row["precio_venta"])

            c1, c2 = st.columns(2)
            c1.metric("Precio Unitario", formatear_monto_ars(precio_unit))
            c2.metric("Stock (estimado)", f"{stock_est} u.")

            if stock_est <= 0:
                st.error("❌ Producto agotado.")
            else:
                a, b = st.columns(2)

                cantidad = a.number_input(
                    "Cantidad",
                    min_value=1,
                    max_value=stock_est,
                    value=1,
                    step=1,
                    key=f"cant_{id_prod}"
                )

                total_calc = precio_unit * int(cantidad)

                total_key = f"total_{id_prod}"
                sug_key = f"sug_{id_prod}"

                if sug_key not in st.session_state:
                    st.session_state[sug_key] = float(total_calc)
                if total_key not in st.session_state:
                    st.session_state[total_key] = float(total_calc)

                # si cambia cantidad, arrastro el total SOLO si no lo editaron
                if float(st.session_state[sug_key]) != float(total_calc):
                    if float(st.session_state[total_key]) == float(st.session_state[sug_key]):
                        st.session_state[total_key] = float(total_calc)
                    st.session_state[sug_key] = float(total_calc)

                b.metric("Total sugerido", formatear_monto_ars(total_calc))

                # callback seguro (evita StreamlitAPIException)
                def usar_sugerido():
                    st.session_state[total_key] = float(total_calc)
                    st.session_state[sug_key] = float(total_calc)

                st.button("Usar total sugerido", key=f"use_sug_{id_prod}", on_click=usar_sugerido)

                total_cobrado = st.number_input(
                    "Total a cobrar ($)",
                    min_value=0.0,
                    value=float(st.session_state[total_key]),
                    step=100.0,
                    key=total_key
                )

                p1, p2 = st.columns(2)
                metodo = p1.selectbox("Método de pago", ["Efectivo", "Transferencia", "Cuenta Corriente", "Otro"])
                nota = p2.text_input("Cliente / Nota (opcional)", placeholder="Ej: María").strip()

                st.divider()

                if st.button("✅ Confirmar venta", use_container_width=True):
                    desc = f"Venta: {int(cantidad)}x {row['producto']} ({row['marca']}) | Pago: {metodo}"
                    if nota:
                        desc += f" | Nota: {nota}"

                    # 1) RPC (real)
                    try:
                        supabase.rpc("registrar_venta", {
                            "p_producto_id": id_prod,
                            "p_cantidad": int(cantidad),
                            "p_monto": float(total_cobrado),
                            "p_descripcion": desc,
                            "p_metodo_pago": metodo
                        }).execute()

                        st.toast("💰 Venta registrada!", icon="✅")
                        limpiar_cache()
                        st.rerun()

                    except Exception:
                        # 2) fallback (sin RPC)
                        try:
                            check = supabase.table("inventario").select("stock").eq("id", id_prod).single().execute()
                            stock_real = int(check.data.get("stock", 0))

                            if stock_real < int(cantidad):
                                st.error(f"❌ No seo se pudo registrar la venta: Stock insuficiente (real: {stock_real}).")
                            else:
                                supabase.table("inventario").update({"stock": stock_real - int(cantidad)}).eq("id", id_prod).execute()

                                supa_base = supabase.table("finanzas").insert({
                                    "fecha": now_ar_str(),
                                    "tipo": "Ingreso",
                                    "descripcion": desc,
                                    "monto": float(total_cobrado),
                                    "producto_id": id_prod,
                                    "cantidad": int(cantidad),
                                    "metodo_pago": metodo
                                }).execute()

                                st.toast("💰 Venta registrada (fallback).", icon="✅")
                                limpiar_cache()
                                st.rerun()
                        except Exception as e2:
                            st.error(f"Error: {e2}")

# =========================================================
# TAB 3: GASTO
# =========================================================
with tab3:
    st.header("💸 Registrar Gasto")

    with st.form("form_gasto"):
        desc = st.text_input("Descripción").strip()
        monto = st.number_input("Monto ($)", min_value=0.0, value=None, placeholder="0,00")
        if st.form_submit_button("Guardar gasto"):
            if not desc or monto is None or float(monto) <= 0:
                st.error("⚠️ Poné descripción y un monto válido.")
            else:
                try:
                    supabase.table("finanzas").insert({
                        "fecha": now_ar_str(),
                        "tipo": "Gasto",
                        "descripcion": desc,
                        "monto": -float(monto)
                    }).execute()

                    st.toast("💸 Gasto registrado.", icon="✅")
                    limpiar_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# =========================================================
# TAB 4: FINANZAS
# =========================================================
with tab4:
    st.header("📊 Finanzas")

    df_work = df_fin.copy() if not df_fin.empty else pd.DataFrame(
        columns=["id", "fecha", "tipo", "descripcion", "monto", "producto_id", "cantidad", "metodo_pago"]
    )

    filtro_txt = "Todos los tiempos"
    df_fil = df_work.copy()

    if not df_work.empty:
        df_work2 = formatear_fecha_arg(df_work)
        df_work2["mes"] = pd.to_datetime(df_work2["fecha_dt"], errors="coerce").dt.strftime("%Y-%m")
        meses = ["Todos los tiempos"] + sorted(df_work2["mes"].dropna().unique().tolist(), reverse=True)

        col_f, _ = st.columns([1, 3])
        filtro_txt = col_f.selectbox("📅 Filtrar por mes", meses)

        if filtro_txt != "Todos los tiempos":
            df_fil = df_work2[df_work2["mes"] == filtro_txt].copy()
        else:
            df_fil = df_work2.copy()

    if not df_fil.empty:
        ingresos = df_fil[df_fil["monto"] > 0]["monto"].sum()
        gastos = df_fil[df_fil["monto"] < 0]["monto"].sum()
        neto = ingresos + gastos

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", formatear_monto_ars(ingresos))
        c2.metric("Gastos", formatear_monto_ars(abs(gastos)))
        c3.metric("Neto", formatear_monto_ars(neto), delta_color="normal" if neto >= 0 else "inverse")
    else:
        st.info("Sin movimientos para el período.")

    st.divider()

    with st.expander("🗑️ Corregir / Eliminar movimiento (restituye stock si es venta)"):
        if df_work.empty:
            st.info("Nada para borrar.")
        else:
            base = df_work.copy()
            base["id"] = pd.to_numeric(base["id"], errors="coerce")
            base = base.dropna(subset=["id"]).copy()
            base["id"] = base["id"].astype(int)

            base_fmt = formatear_fecha_arg(base)
            base_fmt["monto_fmt"] = base_fmt["monto"].apply(formatear_monto_ars)
            base_fmt = base_fmt.sort_values("id", ascending=False)

            busq = st.text_input("🔍 Buscar", placeholder="Ej: labial / 1500 / efectivo").strip()
            show = base_fmt
            if busq:
                mask = (
                    show["descripcion"].str.contains(busq, case=False, na=False)
                    | show["tipo"].astype(str).str.contains(busq, case=False, na=False)
                )
                show = show[mask]

            if show.empty:
                st.info("No se encontró nada con ese filtro.")
            else:
                def label_row(r):
                    f = r.get("fecha_fmt", str(r.get("fecha", "")))
                    return f"{f} | {r.get('tipo','')} | {r.get('descripcion','')} | {r.get('monto_fmt','')} | (ID:{int(r['id'])})"

                options = show["id"].tolist()
                id_sel = st.selectbox(
                    "Movimiento",
                    options=options,
                    format_func=lambda _id: label_row(show[show["id"] == _id].iloc[0])
                )

                ok = st.checkbox("Confirmo borrar este movimiento", key="chk_del_mov")

                if st.button("Borrar (y restituir si aplica)", type="primary", disabled=not ok):
                    try:
                        try:
                            supabase.rpc("borrar_movimiento_y_restituir", {"p_finanzas_id": int(id_sel)}).execute()
                        except Exception:
                            supabase.table("finanzas").delete().eq("id", int(id_sel)).execute()

                        st.toast("🗑️ Movimiento eliminado.", icon="✅")
                        limpiar_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.subheader(f"Detalle: {filtro_txt}")

    if not df_fil.empty:
        df_show = df_fil.copy()
        if "fecha_fmt" not in df_show.columns:
            df_show = formatear_fecha_arg(df_show)

        df_show["monto_fmt"] = df_show["monto"].apply(formatear_monto_ars)

        tabla = df_show.sort_values("id", ascending=False)[["fecha_fmt", "tipo", "descripcion", "monto_fmt"]].copy()
        tabla.columns = ["Fecha", "Tipo", "Descripción", "Monto"]

        st.dataframe(tabla, use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos para mostrar.")

# =========================================================
# TAB 5: ABOUT
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
















