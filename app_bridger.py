import streamlit as st
import pandas as pd
import altair as alt
from modelo_bridger import (
    resolver, ANALISTAS, NOMBRES, OPERACIONES,
    TIEMPOS, BLOQUEADO, RAZONES_BLOQUEO
)

# ── Configuración ────────────────────────────────────────────
st.set_page_config(
    page_title="Bridger — Asignación de Operaciones",
    page_icon="🏦",
    layout="wide",
)

# ── Tema rosado oscuro ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600;700&display=swap');

*, body, .stApp { font-family: 'DM Sans', sans-serif; }
h1, h2, h3     { font-family: 'DM Serif Display', serif !important; }

.stApp { background-color: #1a000d; }
[data-testid="stSidebar"] { background-color: #2a0016; }
[data-testid="stSidebar"] * { color: #f8bbd0 !important; }

.stTabs [data-baseweb="tab-list"]  { background: #2a0016; border-radius: 12px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"]       { color: #f48fb1; font-weight: 600; border-radius: 8px; }
.stTabs [aria-selected="true"]     { background: #880e4f !important; color: #fff !important; }

.stApp, .stApp p, .stApp label, .stApp span, .stApp div { color: #f8bbd0; }
h1, h2, h3 { color: #f48fb1 !important; }

[data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #f48fb1; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #f8bbd0; font-weight: 600; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #3d0022 0%, #2a0016 100%);
    border: 1px solid #880e4f;
    border-radius: 14px;
    padding: 16px 20px;
}

.stButton > button {
    background: linear-gradient(135deg, #880e4f, #c2185b);
    color: white; border: none; border-radius: 10px;
    font-weight: 700; font-size: 1rem;
    padding: 0.55rem 1.5rem;
    transition: all 0.2s;
}
.stButton > button:hover { background: linear-gradient(135deg, #ad1457, #e91e8c); transform: translateY(-1px); }

hr { border-color: #880e4f; opacity: 0.5; }

.stSuccess { background: #3d0022 !important; border-left: 4px solid #f48fb1 !important; color: #f8bbd0 !important; }
.stInfo    { background: #2a0016 !important; border-left: 4px solid #880e4f !important; color: #f8bbd0 !important; }
.stWarning { background: #3d0022 !important; border-left: 4px solid #f48fb1 !important; }
.stError   { background: #3d0022 !important; border-left: 4px solid #c2185b !important; }

[data-testid="stDataFrame"] { background: #2a0016; border-radius: 10px; }
[data-testid="stDataFrame"] * { color: #f8bbd0 !important; }

.block-container { padding-top: 1.8rem; max-width: 1200px; }

/* Tabla compliance personalizada */
.compliance-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
.compliance-table th {
    background: #880e4f; color: #fff;
    padding: 10px 14px; font-weight: 700; font-size: 0.85rem;
    text-align: center; letter-spacing: 0.05em;
}
.compliance-table td { padding: 9px 14px; text-align: center; font-size: 0.9rem; border-bottom: 1px solid #3d0022; }
.compliance-table tr:nth-child(even) td { background: #2a0016; }
.compliance-table tr:nth-child(odd)  td { background: #1a000d; }
.celda-bloqueada { background: #4a0028 !important; color: #f48fb1 !important; font-weight: 700; border-radius: 6px; }
.celda-libre     { color: #f8bbd0; }
.badge-bloq { background: #880e4f; color: #fff; border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700; }
.badge-asig { background: #e91e8c; color: #fff; border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.title("🏦 Bridger — Asignación Óptima de Operaciones")
st.caption("Programación Entera Binaria · Minimiza tiempo total de ejecución · Compliance incluido")

# ── Resolver ─────────────────────────────────────────────────
resultado = resolver()
r         = resultado
ok        = r["estado"] == 1

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📋 Asignación Óptima",
    "📐 Modelo Matemático",
    "📊 Análisis de Tiempos",
])

# ════════════════════════════════════════════════════════════
# TAB 1 — ASIGNACIÓN ÓPTIMA
# ════════════════════════════════════════════════════════════
with tab1:
    if not ok:
        st.error("❌ No se encontró solución factible.")
    else:
        asig = r["asignaciones"]

        st.success(f"✅ Solución óptima encontrada — Tiempo total mínimo: **{int(r['tiempo_total'])} minutos**")
        st.markdown("---")

        # Métricas resumen
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Tiempo total",       f"{int(r['tiempo_total'])} min")
        col2.metric("👥 Analistas",           f"{len(ANALISTAS)}")
        col3.metric("⚙️ Operaciones",         f"{len(OPERACIONES)}")
        col4.metric("🚫 Celdas bloqueadas",   f"{len(BLOQUEADO)}")

        st.markdown("---")
        st.subheader("✅ Asignación óptima")

        # Tabla de asignación resultado
        filas_asig = []
        for a in ANALISTAS:
            if a in asig:
                info = asig[a]
                filas_asig.append({
                    "Analista":       f"{info['nombre']} ({a})",
                    "Operación":      info["operacion"],
                    "Tiempo (min)":   info["tiempo"],
                })

        df_asig = pd.DataFrame(filas_asig)
        st.dataframe(df_asig, use_container_width=True, hide_index=True)

        # Mapa visual de tiempos con asignación marcada
        st.markdown("---")
        st.subheader("🗺️ Mapa de tiempos — solución resaltada")

        html_rows = ""
        for a in ANALISTAS:
            nombre = NOMBRES[a]
            html_rows += f"<tr><td style='font-weight:700;color:#f48fb1;text-align:left;padding:9px 14px'>{nombre} ({a})</td>"
            for o in OPERACIONES:
                es_bloq = (a, o) in BLOQUEADO
                es_asig = (a in asig and asig[a]["operacion"] == o)
                t = TIEMPOS[a, o]
                if es_asig:
                    html_rows += f"<td><span class='badge-asig'>✓ {t}</span></td>"
                elif es_bloq:
                    html_rows += f"<td class='celda-bloqueada'>🚫</td>"
                else:
                    html_rows += f"<td class='celda-libre'>{t}</td>"
            html_rows += "</tr>"

        headers = "".join(f"<th>{o}</th>" for o in OPERACIONES)
        st.markdown(f"""
<table class='compliance-table'>
  <thead><tr><th style='text-align:left'>Analista</th>{headers}</tr></thead>
  <tbody>{html_rows}</tbody>
</table>
""", unsafe_allow_html=True)
        st.caption("✓ = asignación óptima &nbsp;|&nbsp; 🚫 = bloqueado por compliance &nbsp;|&nbsp; número = tiempo disponible (min)")

        # Restricciones de compliance
        st.markdown("---")
        st.subheader("🚫 Restricciones de compliance")
        filas_comp = []
        for (a, o), razon in RAZONES_BLOQUEO.items():
            filas_comp.append({
                "Analista":   f"{NOMBRES[a]} ({a})",
                "Operación":  o,
                "Razón":      razon,
            })
        st.dataframe(pd.DataFrame(filas_comp), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — MODELO MATEMÁTICO
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📐 Formulación del Modelo")
    st.markdown("---")

    col_m, col_a = st.columns([1, 1], gap="large")

    with col_m:
        st.markdown("### Variables de decisión")
        st.markdown(
            "Para cada par (analista $a$, operación $o$) se define una variable binaria:"
        )
        st.latex(r"x_{a,o} \in \{0,\,1\} \quad \forall\, a \in A,\; o \in O")
        st.markdown("donde $x_{a,o} = 1$ si el analista $a$ ejecuta la operación $o$.")

        st.markdown("---")
        st.markdown("### Función objetivo")
        st.markdown("Minimizar el tiempo total de ejecución de todas las operaciones:")
        st.latex(
            r"\min Z = \sum_{a \in A}\sum_{o \in O} t_{a,o} \cdot x_{a,o}"
        )

        st.markdown("---")
        st.markdown("### Restricciones")

        st.markdown("**R1 — Cada operación asignada a exactamente un analista:**")
        st.latex(r"\sum_{a \in A} x_{a,o} = 1 \qquad \forall\, o \in O \quad (5 \text{ restricciones})")

        st.markdown("**R2 — Cada analista ejecuta exactamente una operación:**")
        st.latex(r"\sum_{o \in O} x_{a,o} = 1 \qquad \forall\, a \in A \quad (5 \text{ restricciones})")

        st.markdown("**R3 — Compliance (celdas bloqueadas = 0):**")
        st.latex(r"x_{a,o} = 0 \quad \forall\,(a,o) \in \mathcal{B} \quad (5 \text{ restricciones})")
        st.markdown(
            "donde $\\mathcal{B} = \\{(A,MT700),(A,MT760),(D,MT760),(E,MT103),(E,MT202)\\}$"
        )

        st.markdown("**R4 — Integralidad y no negatividad:**")
        st.latex(r"x_{a,o} \in \{0,1\} \qquad \forall\, a \in A,\; o \in O")

        st.markdown("---")
        st.markdown("### Modelo completo")
        st.latex(
            r"\min Z = \sum_{a \in A}\sum_{o \in O} t_{a,o} \cdot x_{a,o}"
            r"\\ \text{s.a.:}"
            r"\\ \sum_{a \in A} x_{a,o} = 1 \quad \forall\, o"
            r"\\ \sum_{o \in O} x_{a,o} = 1 \quad \forall\, a"
            r"\\ x_{a,o} = 0 \quad \forall\,(a,o) \in \mathcal{B}"
            r"\\ x_{a,o} \in \{0,1\}"
        )

    with col_a:
        st.markdown("### Código AMPL — bridger.mod")
        st.code("""# ── CONJUNTOS ──
set ANALISTAS;
set OPERACIONES;

# ── PARÁMETROS ──
param tiempo{ANALISTAS, OPERACIONES} >= 0;
param bloqueado{ANALISTAS, OPERACIONES} binary default 0;

# ── VARIABLES ──
var x{a in ANALISTAS, o in OPERACIONES} binary;

# ── FUNCIÓN OBJETIVO ──
minimize TiempoTotal:
  sum{a in ANALISTAS, o in OPERACIONES}
    tiempo[a,o] * x[a,o];

# ── RESTRICCIONES ──
# R1: una asignación por operación
subject to Una_por_operacion{o in OPERACIONES}:
  sum{a in ANALISTAS} x[a,o] = 1;

# R2: un trabajo por analista
subject to Una_por_analista{a in ANALISTAS}:
  sum{o in OPERACIONES} x[a,o] = 1;

# R3: compliance
subject to Compliance
  {a in ANALISTAS, o in OPERACIONES:
   bloqueado[a,o] = 1}:
  x[a,o] = 0;""", language="ampl")

        st.markdown("### Código AMPL — bridger.dat")
        st.code("""set ANALISTAS   := A B C D E;
set OPERACIONES := MT103 MT202 MT700 MT760 MT940;

param tiempo :
         MT103 MT202 MT700 MT760 MT940 :=
  A        25    30     0     0    20
  B        35    28    40    45    22
  C        40    45    35    30    25
  D        30    32    50     0    18
  E         0     0    30    28    30 ;

param bloqueado :
         MT103 MT202 MT700 MT760 MT940 :=
  A        0     0     1     1     0
  B        0     0     0     0     0
  C        0     0     0     0     0
  D        0     0     0     1     0
  E        1     1     0     0     0 ;""", language="ampl")

        st.markdown("### Script de ejecución — bridger.run")
        st.code("""model bridger.mod;
data  bridger.dat;
option solver cbc;
solve;

printf "Tiempo total: %g min\\n", TiempoTotal;
for {a in ANALISTAS, o in OPERACIONES: x[a,o] > 0.5} {
  printf "%s → %s: %g min\\n", a, o, tiempo[a,o];
}""", language="ampl")

        if ok:
            st.markdown("### ✅ Solución verificada")
            asig = r["asignaciones"]
            terminos = " + ".join(
                f"{info['tiempo']}" for info in asig.values()
            )
            st.latex(rf"Z = {terminos} = {int(r['tiempo_total'])}\text{{ min}}")

# ════════════════════════════════════════════════════════════
# TAB 3 — ANÁLISIS DE TIEMPOS
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📊 Análisis comparativo de tiempos")
    st.markdown("---")

    if ok:
        asig = r["asignaciones"]

        # Gráfico de barras: tiempo asignado por analista
        df_bar = pd.DataFrame([
            {
                "Analista":   f"{NOMBRES[a]} ({a})",
                "Operación":  asig[a]["operacion"],
                "Tiempo":     asig[a]["tiempo"],
            }
            for a in ANALISTAS if a in asig
        ])

        bar = (
            alt.Chart(df_bar)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Analista:N", axis=alt.Axis(labelAngle=-20), title=None),
                y=alt.Y("Tiempo:Q", title="Tiempo (min)"),
                color=alt.Color("Operación:N", scale=alt.Scale(
                    range=["#e91e8c", "#f48fb1", "#ad1457", "#f06292", "#880e4f"]
                )),
                tooltip=["Analista:N", "Operación:N", "Tiempo:Q"]
            )
            .properties(height=300, title="Tiempo por analista en la solución óptima")
        )
        st.altair_chart(bar, use_container_width=True)

        st.markdown("---")

        # Heatmap de tiempos completo
        st.subheader("🗺️ Heatmap de tiempos disponibles")
        filas_heat = []
        for a in ANALISTAS:
            for o in OPERACIONES:
                es_bloq = (a, o) in BLOQUEADO
                es_asig = (a in asig and asig[a]["operacion"] == o)
                filas_heat.append({
                    "Analista":   NOMBRES[a],
                    "Operación":  o,
                    "Tiempo":     TIEMPOS[a, o] if not es_bloq else None,
                    "Estado":     "Óptimo" if es_asig else ("Bloqueado" if es_bloq else "Disponible"),
                })

        df_heat = pd.DataFrame(filas_heat).dropna(subset=["Tiempo"])

        heat = (
            alt.Chart(df_heat)
            .mark_rect(cornerRadius=4)
            .encode(
                x=alt.X("Operación:N", title=None),
                y=alt.Y("Analista:N",  title=None),
                color=alt.Color("Tiempo:Q", scale=alt.Scale(
                    scheme="magma", reverse=True
                ), title="min"),
                stroke=alt.condition(
                    alt.datum.Estado == "Óptimo",
                    alt.value("#f8bbd0"),
                    alt.value("transparent")
                ),
                strokeWidth=alt.condition(
                    alt.datum.Estado == "Óptimo",
                    alt.value(3),
                    alt.value(0)
                ),
                tooltip=["Analista:N", "Operación:N", "Tiempo:Q", "Estado:N"]
            )
            .properties(height=260, title="Más oscuro = más rápido · Borde blanco = asignado")
        )
        st.altair_chart(heat, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Tabla completa de tiempos")
        tabla_completa = {}
        for a in ANALISTAS:
            fila = {}
            for o in OPERACIONES:
                if (a, o) in BLOQUEADO:
                    fila[o] = "🚫"
                else:
                    asignado = (a in asig and asig[a]["operacion"] == o)
                    fila[o] = f"✓ {TIEMPOS[a,o]}" if asignado else str(TIEMPOS[a, o])
            tabla_completa[NOMBRES[a]] = fila
        df_full = pd.DataFrame(tabla_completa).T
        st.dataframe(df_full, use_container_width=True)
        st.caption("✓ = asignado en la solución óptima &nbsp;|&nbsp; 🚫 = bloqueado por compliance")
