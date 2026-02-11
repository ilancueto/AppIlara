import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import pytz

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Ilara Beauty",
    page_icon="💄",
    layout="wide"
)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }

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
       DATAFRAME (zebra + hover)
       ========================= */
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: rgba(255, 240, 246, 0.65) !important;
    }
    div[data-testid="stDataFrame"] tbody tr:hover {
        background-color: rgba(255, 182, 193, 0.65) !important;
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
# CONSTANTES
# =========================================================
DEFAULT_CATEGORIAS = ["Labios", "Ojos", "Rostro", "Skincare", "Accesorios"]
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
def queue_toast(msg: str, icon: str = "✅"):
    """Queue a toast to be shown after st.rerun()."""
    st.session_state["_toast"] = {"msg": msg, "icon": icon}

# Show queued toast (survives rerun)
if "_toast" in st.session_state:
    t = st.session_state.pop("_toast")
    try:
        st.toast(t.get("msg",""), icon=t.get("icon","✅"))
    except Exception:
        pass

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


@st.cache_data(ttl=60)
def cargar_categorias():
    try:
        res = supabase.table("categorias").select("*").order("nombre").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# =========================================================
# UI HEADER + FOOTER
# =========================================================

# Footer fijo (premium)
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
        opacity: 0.78;
        background: rgba(0,0,0,0.0);
        z-index: 999;
        pointer-events: none;
    }
    </style>
    <div class="footer-fixed">by Ilan con amor · v3.6.1</div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DATA (con spinner)
# =========================================================
with st.spinner("Cargando Ilara Beauty..."):
    df_inv = cargar_inventario()
    df_fin = cargar_finanzas()
    df_cats = cargar_categorias()

# Header marca (premium)

# =========================================================
# CATEGORÍAS (dinámicas desde Supabase)
# =========================================================
if "df_cats" not in locals() or df_cats is None:
    df_cats = pd.DataFrame()

if not df_cats.empty:
    df_cats["id"] = pd.to_numeric(df_cats.get("id", None), errors="coerce")
    df_cats["nombre"] = df_cats.get("nombre", "").astype(str).str.strip()
    df_cats = df_cats.dropna(subset=["id"]).copy()
    df_cats["id"] = df_cats["id"].astype(int)
    df_cats = df_cats[df_cats["nombre"] != ""].copy()

cat_name_to_id = {r["nombre"]: int(r["id"]) for _, r in df_cats.iterrows()} if not df_cats.empty else {}
cat_id_to_name = {int(r["id"]): r["nombre"] for _, r in df_cats.iterrows()} if not df_cats.empty else {}

categorias_list = sorted(cat_name_to_id.keys()) if cat_name_to_id else DEFAULT_CATEGORIAS

stock_crit = 0
if not df_inv.empty and "stock" in df_inv.columns:
    try:
        stock_crit = int((pd.to_numeric(df_inv["stock"], errors="coerce").fillna(0) <= 3).sum())
    except Exception:
        stock_crit = 0

st.markdown(
    f"""
    <div style="
      display:flex;
      align-items:center;
      gap:16px;
      background: linear-gradient(90deg,#ff66b2,#ff99cc);
      padding:16px 20px;
      border-radius:18px;
      box-shadow: 0 12px 30px rgba(0,0,0,.14);
      margin-bottom: 12px;">

      <img src="https://raw.githubusercontent.com/ilancueto/AppIlara/main/assets/logo_ilara.png" style="
        height:128px;
        border-radius:50%;
        background:white;
        padding:6px;
      "/>

      <div style="flex:1;">
        <div style="font-weight:700;font-size:22px;color:white;">
          Ilara Beauty
        </div>
        <div style="font-size:14px;opacity:.9;color:white;">
          Stock, Ventas y Finanzas
        </div>
      </div>

      <div style="font-weight:600;font-size:14px;color:white;">
        ⚠️ Stock bajo: {stock_crit}
      </div>

    </div>
    """,
    unsafe_allow_html=True
)

# Blindajes inventario
if not df_inv.empty:
    # columnas base
    for col in ["producto", "marca"]:
        if col not in df_inv.columns:
            df_inv[col] = ""
        df_inv[col] = df_inv[col].astype(str)

    # categoria_id (si existe)
    if "categoria_id" in df_inv.columns:
        df_inv["categoria_id"] = pd.to_numeric(df_inv["categoria_id"], errors="coerce")

    # categoria "nombre" (compat: si todavía existe texto en inventario)
    if "categoria" not in df_inv.columns:
        df_inv["categoria"] = ""
    df_inv["categoria"] = df_inv["categoria"].astype(str)

    # Si hay categoria_id, usamos el nombre de la tabla categorias
    if "categoria_id" in df_inv.columns and cat_id_to_name:
        df_inv["categoria"] = df_inv["categoria_id"].apply(lambda x: cat_id_to_name.get(int(x), "") if pd.notna(x) else "")                               .where(lambda s: s.astype(str).str.len() > 0, df_inv["categoria"])

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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📦 Inventario", "💰 Nueva Venta", "💸 Nuevo Gasto", "📊 Finanzas", "🏷️ Categorías", "💌 About"]
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

            # Estado (chips)
            def _estado_stock(s):
                try:
                    s = int(s)
                except Exception:
                    s = 0
                if s <= 0:
                    return "🛑 Agotado"
                if s <= 3:
                    return "⚠️ Bajo"
                return "✅ OK"

            view_show["Estado"] = view_show["Stock"].apply(_estado_stock)

            st.dataframe(view_show, use_container_width=True, hide_index=True)

            # Export CSV
            csv_inv = view_show.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Exportar inventario filtrado (CSV)",
                csv_inv,
                file_name="ilara_inventario.csv",
                mime="text/csv",
                use_container_width=True,
            )


    # Agregar / reponer
    with sub_add:
        with st.form("form_add", clear_on_submit=True):
            st.caption("Si Nombre+Marca ya existe, suma stock.")
            a, b = st.columns(2)
            nom = a.text_input("Nombre").strip()
            marca = b.text_input("Marca").strip()
            marca_final = marca if marca else "Genérico"

            cat = a.selectbox("Categoría", categorias_list)
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
                                "categoria": cat,
                                "categoria_id": int(cat_name_to_id.get(cat, 0)) if cat_name_to_id.get(cat) else None
                            }).eq("id", int(prod["id"])).execute()
                            queue_toast(f"🔄 Stock actualizado: {prod['stock']} ➝ {new_stock}", "✅")
                        else:
                            supabase.table("inventario").insert({
                                "producto": nom,
                                "marca": marca_final,
                                "categoria": cat,
                                "categoria_id": int(cat_name_to_id.get(cat, 0)) if cat_name_to_id.get(cat) else None,
                                "stock": int(cant),
                                "precio_costo": float(costo),
                                "precio_venta": float(venta)
                            }).execute()
                            queue_toast(f"✨ Producto cargado correctamente: {nom}", "💄")

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

                cats = categorias_list
                idx = cats.index(row["categoria"]) if row["categoria"] in cats else 0
                new_cat = a.selectbox("Categoría", cats, index=idx)

                stock_actual = int(row.get("stock") or 0)
                new_stock = b.number_input("Stock", min_value=0, value=stock_actual, step=1)

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
                                "categoria_id": int(cat_name_to_id.get(new_cat, 0)) if cat_name_to_id.get(new_cat) else None,
                                "precio_costo": float(new_costo),
                                "precio_venta": float(new_venta)
                                ,"stock": int(new_stock)
                            }).eq("id", id_actual).execute()

                            queue_toast("💾 Cambios guardados.", "✏️")
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
    st.header("💰 Registrar Venta (Carrito)")

    # ===== CARRITO DE VENTAS (v3.6.1) =====
    if "carrito" not in st.session_state:
        st.session_state["carrito"] = []

    carrito = st.session_state["carrito"]

    if df_inv.empty:
        st.warning("Primero cargá productos en Inventario.")
    else:
        # --------- Agregar al carrito ---------
        st.subheader("➕ Agregar productos")

        opciones = df_inv["display"].unique()
        sel = st.selectbox("Producto", opciones, key="cart_sel_prod")

        if sel:
            row = df_inv[df_inv["display"] == sel].iloc[0]
            id_prod = int(row["id"])
            stock_est = int(row["stock"])
            precio_unit = float(row["precio_venta"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Unitario", formatear_monto_ars(precio_unit))
            c2.metric("Stock (estimado)", f"{stock_est} u.")
            c3.metric("En carrito", str(sum(int(i["cantidad"]) for i in carrito if int(i["producto_id"]) == id_prod)))

            if stock_est <= 0:
                st.error("❌ Producto agotado.")
            else:
                a, b = st.columns(2)
                cant = a.number_input(
                    "Cantidad",
                    min_value=1,
                    max_value=max(1, stock_est),
                    value=1,
                    step=1,
                    key=f"cart_cant_{id_prod}",
                )

                subtotal_calc = float(precio_unit) * int(cant)
                b.metric("Subtotal sugerido", formatear_monto_ars(subtotal_calc))

                editar_subtotal = st.checkbox("Editar subtotal (descuento/recargo)", value=False, key=f"cart_edit_sub_{id_prod}")
                if editar_subtotal:
                    subtotal = st.number_input(
                        "Subtotal final ($)",
                        min_value=0.0,
                        value=float(subtotal_calc),
                        step=100.0,
                        key=f"cart_subtotal_{id_prod}",
                    )
                else:
                    subtotal = float(subtotal_calc)

                add_col1, add_col2 = st.columns([2, 1])
                if add_col1.button("➕ Agregar al carrito", type="primary", use_container_width=True):
                    # si ya está, sumamos cantidad y subtotal
                    found = False
                    for it in carrito:
                        if int(it["producto_id"]) == id_prod:
                            it["cantidad"] = int(it["cantidad"]) + int(cant)
                            it["subtotal"] = float(it.get("subtotal", 0.0)) + float(subtotal)
                            it["precio_unit"] = float(precio_unit)  # por las dudas
                            it["display"] = sel
                            found = True
                            break
                    if not found:
                        carrito.append({
                            "producto_id": id_prod,
                            "display": sel,
                            "cantidad": int(cant),
                            "precio_unit": float(precio_unit),
                            "subtotal": float(subtotal),
                        })
                    st.session_state["carrito"] = carrito
                    st.toast("🛒 Agregado al carrito.", icon="✅")
                    st.rerun()

                if add_col2.button("🗑️ Vaciar", use_container_width=True, disabled=(len(carrito) == 0)):
                    st.session_state["carrito"] = []
                    st.toast("Carrito vaciado.", icon="🗑️")
                    st.rerun()

        st.divider()

        # --------- Mostrar carrito ---------
        st.subheader("🛒 Carrito")

        if not carrito:
            st.info("Carrito vacío. Agregá productos arriba.")
        else:
            df_cart = pd.DataFrame(carrito)
            df_cart["Precio"] = df_cart["precio_unit"].apply(formatear_monto_ars)
            df_cart["Subtotal"] = df_cart["subtotal"].apply(formatear_monto_ars)
            df_cart_show = df_cart[["display", "cantidad", "Precio", "Subtotal"]].copy()
            df_cart_show.columns = ["Producto", "Cantidad", "Precio Unit.", "Subtotal"]

            st.dataframe(df_cart_show, use_container_width=True, hide_index=True)

            total_sugerido = float(sum(float(i.get("subtotal", 0.0)) for i in carrito))

            c1, c2 = st.columns([2, 1])
            c1.metric("Total sugerido", formatear_monto_ars(total_sugerido))

            editar_total = st.checkbox("Editar total final", value=False, key="cart_edit_total")
            if editar_total:
                total_final = st.number_input(
                    "Total final a cobrar ($)",
                    min_value=0.0,
                    value=float(total_sugerido),
                    step=100.0,
                    key="cart_total_final",
                )
            else:
                total_final = float(total_sugerido)

            st.divider()

            p1, p2 = st.columns(2)
            metodo_pago = p1.selectbox("Método de pago", ["Efectivo", "Transferencia", "Cuenta Corriente", "Otro"], key="cart_metodo")
            nota = p2.text_input("Cliente / Nota (opcional)", placeholder="Ej: María", key="cart_nota").strip()

            # Quitar item
            rm1, rm2 = st.columns([3, 1])
            opciones_rm = [f'{it["display"]} (x{it["cantidad"]})' for it in carrito]
            sel_rm = rm1.selectbox("Quitar ítem", opciones_rm, key="cart_rm_sel")
            if rm2.button("Quitar", use_container_width=True):
                idx = opciones_rm.index(sel_rm)
                carrito.pop(idx)
                st.session_state["carrito"] = carrito
                st.rerun()

            st.divider()

            # --------- Procesar venta (RPC) ---------
            if st.button("✅ Procesar venta (carrito)", type="primary", use_container_width=True):
                try:
                    # armado payload RPC
                    items_rpc = [{"producto_id": int(i["producto_id"]), "cantidad": int(i["cantidad"])} for i in carrito]

                    # descripción corta y útil
                    desc_items = " | ".join([f'{int(i["cantidad"])}x {str(i["display"])}' for i in carrito])
                    desc = f"Venta carrito: {desc_items} | Pago: {metodo_pago}"
                    if nota:
                        desc += f" | Nota: {nota}"

                    supabase.rpc(
                        "registrar_venta_carrito",
                        {
                            "p_items": items_rpc,
                            "p_monto_total": float(total_final),
                            "p_descripcion": desc,
                            "p_metodo_pago": metodo_pago,
                        },
                    ).execute()

                    st.toast("💰 Venta de carrito registrada!", icon="✅")
                    st.session_state["carrito"] = []
                    limpiar_cache()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al procesar la venta: {e}")


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

        # Export CSV
        csv_fin = tabla.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar finanzas (CSV)",
            csv_fin,
            file_name="ilara_finanzas.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:
        st.info("No hay movimientos para mostrar.")

# =========================================================

# =========================================================
# TAB 5: CATEGORÍAS (ABM)
# =========================================================
    st.subheader("➕ Ingreso manual")

    with st.form("form_ingreso_manual", clear_on_submit=True):
        desc_in = st.text_input("Descripción", placeholder="Ej: Regalo / Aporte personal").strip()
        monto_in = st.number_input("Monto ($)", min_value=0.0, value=0.0, step=100.0)

        ok_in = st.form_submit_button("Agregar ingreso")

    if ok_in:
        if float(monto_in) <= 0:
            st.error("⚠️ Poné un monto mayor a 0.")
        else:
            try:
                supabase.table("finanzas").insert({
                    "fecha": now_ar_str(),
                    "tipo": "Ingreso",
                    "descripcion": desc_in or "Ingreso manual",
                    "monto": float(monto_in)  # ✅ positivo
                }).execute()

                # ✅ toast que sobrevive al rerun (usa tu helper)
                try:
                    queue_toast("💰 Ingreso agregado correctamente", icon="🎁")
                except Exception:
                    st.toast("💰 Ingreso agregado correctamente", icon="🎁")

                limpiar_cache()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al agregar ingreso: {e}")

with tab5:
    st.header("🏷️ Categorías")

    st.caption("Administrá las categorías desde acá. Se usan en Inventario (Agregar/Editar).")

    # refrescar dataframe desde cache
    df_cats_view = cargar_categorias()

    if df_cats_view.empty:
        st.warning("No hay categorías cargadas. Agregá la primera.")
    else:
        show_c = df_cats_view.copy()
        if "id" in show_c.columns:
            show_c["id"] = pd.to_numeric(show_c["id"], errors="coerce")
        if "nombre" in show_c.columns:
            show_c["nombre"] = show_c["nombre"].astype(str)
        show_c = show_c.rename(columns={"id":"ID","nombre":"Categoría"})
        cols = [c for c in ["ID","Categoría"] if c in show_c.columns]
        st.dataframe(show_c[cols], use_container_width=True, hide_index=True)

    st.divider()

    c_add, c_ren, c_del = st.tabs(["➕ Agregar", "✏️ Renombrar", "🗑️ Eliminar"])

    with c_add:
        with st.form("form_cat_add"):
            nombre = st.text_input("Nueva categoría", placeholder="Ej: Uñas").strip()
            if st.form_submit_button("Guardar", type="primary"):
                if not nombre:
                    st.error("⚠️ Escribí un nombre.")
                else:
                    try:
                        supabase.table("categorias").insert({"nombre": nombre}).execute()
                        st.toast("✅ Categoría agregada.", icon="✅")
                        limpiar_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with c_ren:
        df_cats_view = cargar_categorias()
        nombres = df_cats_view["nombre"].astype(str).tolist() if (not df_cats_view.empty and "nombre" in df_cats_view.columns) else []
        if not nombres:
            st.info("Agregá categorías primero.")
        else:
            old = st.selectbox("Categoría a renombrar", nombres, key="cat_ren_old")
            with st.form("form_cat_ren"):
                new_name = st.text_input("Nuevo nombre", value=old).strip()
                if st.form_submit_button("Renombrar", type="primary"):
                    if not new_name:
                        st.error("⚠️ Nombre inválido.")
                    else:
                        try:
                            row = df_cats_view[df_cats_view["nombre"].astype(str) == old].iloc[0]
                            cat_id = int(row["id"])
                            supabase.table("categorias").update({"nombre": new_name}).eq("id", cat_id).execute()

                            # compat: si inventario aún guarda texto en 'categoria', lo mantenemos sincronizado
                            try:
                                supabase.table("inventario").update({"categoria": new_name}).eq("categoria_id", cat_id).execute()
                            except Exception:
                                pass

                            st.toast("✏️ Categoría renombrada.", icon="✅")
                            limpiar_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    with c_del:
        df_cats_view = cargar_categorias()
        nombres = df_cats_view["nombre"].astype(str).tolist() if (not df_cats_view.empty and "nombre" in df_cats_view.columns) else []
        if not nombres:
            st.info("Agregá categorías primero.")
        else:
            sel_name = st.selectbox("Categoría a eliminar", nombres, key="cat_del_sel")
            ok = st.checkbox("Confirmo eliminar esta categoría", key="cat_del_ok")

            # buscamos id
            row = df_cats_view[df_cats_view["nombre"].astype(str) == sel_name].iloc[0]
            cat_id = int(row["id"])

            # chequeo de uso (no borrar si está en inventario)
            try:
                used = supabase.table("inventario").select("id").eq("categoria_id", cat_id).execute()
                used_count = len(used.data or [])
            except Exception:
                used_count = 0

            if used_count > 0:
                st.warning(f"⚠️ No se puede borrar: está en uso por {used_count} producto(s). Renombrala o reasigná esos productos.")
                st.button("Eliminar", disabled=True, use_container_width=True)
            else:
                if st.button("Eliminar", type="primary", disabled=not ok, use_container_width=True):
                    try:
                        supabase.table("categorias").delete().eq("id", cat_id).execute()
                        st.toast("🗑️ Categoría eliminada.", icon="✅")
                        limpiar_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# TAB 6: ABOUT
# =========================================================
with tab6:
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




















