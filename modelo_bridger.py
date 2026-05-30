from pulp import (
    LpProblem, LpMinimize, LpVariable, lpSum, value, PULP_CBC_CMD, constants
)

# ── Datos del problema ──────────────────────────────────────
ANALISTAS   = ["A", "B", "C", "D", "E"]
NOMBRES     = {"A": "Andrea", "B": "Beatriz", "C": "Carlos", "D": "Daniel", "E": "Esteban"}
OPERACIONES = ["MT103", "MT202", "MT700", "MT760", "MT940"]

TIEMPOS = {
    ("A", "MT103"): 25, ("A", "MT202"): 30, ("A", "MT700"):  0, ("A", "MT760"):  0, ("A", "MT940"): 20,
    ("B", "MT103"): 35, ("B", "MT202"): 28, ("B", "MT700"): 40, ("B", "MT760"): 45, ("B", "MT940"): 22,
    ("C", "MT103"): 40, ("C", "MT202"): 45, ("C", "MT700"): 35, ("C", "MT760"): 30, ("C", "MT940"): 25,
    ("D", "MT103"): 30, ("D", "MT202"): 32, ("D", "MT700"): 50, ("D", "MT760"):  0, ("D", "MT940"): 18,
    ("E", "MT103"):  0, ("E", "MT202"):  0, ("E", "MT700"): 30, ("E", "MT760"): 28, ("E", "MT940"): 30,
}

# 1 = bloqueado por compliance
BLOQUEADO = {
    ("A", "MT700"), ("A", "MT760"),
    ("D", "MT760"),
    ("E", "MT103"), ("E", "MT202"),
}

RAZONES_BLOQUEO = {
    ("A", "MT700"): "LC — Andrea",
    ("A", "MT760"): "Garantía — Andrea",
    ("D", "MT760"): "Garantía — Daniel",
    ("E", "MT103"): "Re-certificación — Esteban",
    ("E", "MT202"): "Re-certificación — Esteban",
}


def resolver() -> dict:
    """Resuelve el modelo binario de asignación de operaciones Bridger."""
    modelo = LpProblem("Bridger_Asignacion", LpMinimize)

    # Variables binarias x[a][o]
    x = {
        (a, o): LpVariable(f"x_{a}_{o}", cat="Binary")
        for a in ANALISTAS for o in OPERACIONES
    }

    # Función objetivo: minimizar tiempo total
    modelo += lpSum(TIEMPOS[a, o] * x[a, o] for a in ANALISTAS for o in OPERACIONES), "TiempoTotal"

    # R1: cada operación asignada a exactamente 1 analista
    for o in OPERACIONES:
        modelo += lpSum(x[a, o] for a in ANALISTAS) == 1, f"op_{o}"

    # R2: cada analista realiza exactamente 1 operación
    for a in ANALISTAS:
        modelo += lpSum(x[a, o] for o in OPERACIONES) == 1, f"analista_{a}"

    # R3: compliance — celdas bloqueadas = 0
    for (a, o) in BLOQUEADO:
        modelo += x[a, o] == 0, f"compliance_{a}_{o}"

    modelo.solve(PULP_CBC_CMD(msg=0))

    asignaciones = {}
    for a in ANALISTAS:
        for o in OPERACIONES:
            if x[a, o].varValue is not None and x[a, o].varValue > 0.5:
                asignaciones[a] = {
                    "operacion": o,
                    "tiempo":    TIEMPOS[a, o],
                    "nombre":    NOMBRES[a],
                }

    return {
        "estado":        modelo.status,
        "tiempo_total":  value(modelo.objective),
        "asignaciones":  asignaciones,
    }
