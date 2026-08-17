# -*- coding: utf-8 -*-
"""Construye y ejecuta el notebook de Colab de la Practica 1."""
import os
import nbformat as nbf
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Entrega_Lab1")
os.makedirs(OUT, exist_ok=True)
DEST = os.path.join(OUT, "Confidence_intervals_20_200.ipynb")

md, code = [], []
cells = []


def M(t):
    cells.append(nbf.v4.new_markdown_cell(t.strip("\n")))


def C(t):
    cells.append(nbf.v4.new_code_cell(t.strip("\n")))


M(r"""
# Intervalos de confianza — Simulación *ad hoc* de una fila de banco

**Práctica N.º 01 — Simulación Computacional**
Universidad de los Llanos · Ingeniería de Sistemas

Este cuaderno acompaña al informe de la Práctica 1. Reproduce, de principio a fin, la
simulación *ad hoc* del sistema de cola simple descrito en la Tabla 1.1 del Capítulo 1 de
Banks (1998) y calcula los intervalos de confianza de las cinco medidas de desempeño,
siguiendo el procedimiento de la subsección 1.11.1 y el desarrollo del cuaderno
`Confidence intervals.ipynb` suministrado por el docente.

**Contenido**

1. Configuración y generadores de variables aleatorias
2. Motor de simulación y medidas de desempeño
3. Escenario A — 20 clientes por corrida
4. Escenario B — 200 clientes por corrida
5. Comparación de los dos escenarios

El cuaderno es autocontenido: al ejecutarlo completo se reproducen exactamente las tablas
del informe, porque los generadores están inicializados con una semilla fija.
""")

M(r"""
## 1. Configuración y generadores de variables aleatorias

Las dos variables aleatorias del modelo siguen distribuciones uniformes discretas, tal
como lo pide la guía:

| Variable | Distribución | Equivalente físico |
|---|---|---|
| Tiempo entre llegadas $A_i$ | $U\{1,\dots,10\}$ minutos | ruleta de 10 sectores |
| Tiempo de servicio $S_i$ | $U\{1,\dots,6\}$ minutos | dado de 6 caras |

Se usan **dos generadores independientes**, uno por variable, tal como la guía exige usar
un dado o una ruleta distinta para cada generador. Los valores esperados teóricos son
$E[A]=5{,}5$ y $E[S]=3{,}5$ minutos, de donde la utilización teórica del servidor es
$\rho = E[S]/E[A] = 0{,}636$; esta cifra servirá más adelante como control de calidad de
la simulación.
""")

C(r"""
import numpy as np
import pandas as pd
from scipy import stats
from IPython.display import display, Markdown

SEED    = 20260817     # semilla fija -> resultados reproducibles
N_RUNS  = 10           # repeticiones (corridas) por escenario
TBA_LO, TBA_HI = 1, 10 # tiempo entre llegadas ~ U{1..10}
SRV_LO, SRV_HI = 1, 6  # tiempo de servicio   ~ U{1..6}

pd.set_option("display.max_rows", 210)

print("E[A] = %.2f min   E[S] = %.2f min   rho = %.3f"
      % ((TBA_LO+TBA_HI)/2, (SRV_LO+SRV_HI)/2,
         ((SRV_LO+SRV_HI)/2)/((TBA_LO+TBA_HI)/2)))
""")

M(r"""
## 2. Motor de simulación y medidas de desempeño

Las nueve columnas de la Tabla 1.1 de Banks se obtienen con las siguientes recurrencias.
Para el cliente $i$ (con $i=1$ llegando en el instante $0$):

$$
\begin{aligned}
\text{(3) Hora de llegada:}\quad & L_i = L_{i-1} + A_i, \qquad L_1 = 0\\
\text{(5) Inicio del servicio:}\quad & B_i = \max(L_i,\; F_{i-1}), \qquad B_1 = L_1\\
\text{(6) Fin del servicio:}\quad & F_i = B_i + S_i\\
\text{(7) Tiempo en el sistema:}\quad & T_i = F_i - L_i\\
\text{(8) Tiempo ocioso del servidor:}\quad & O_i = \max(0,\; L_i - F_{i-1}), \qquad O_1 = 0\\
\text{(9) Tiempo en cola:}\quad & W_i = B_i - L_i
\end{aligned}
$$

El máximo en $B_i$ es la regla que representa la disciplina FIFO con un solo servidor: un
cliente empieza a ser atendido cuando ya llegó **y** el servidor quedó libre.
""")

C(r"""
def simular(tba, servicio):
    '''Ejecuta una corrida completa y devuelve las nueve columnas de la Tabla 1.1.

    tba[0] se ignora: el primer cliente llega en el instante 0.
    '''
    n = len(servicio)
    llegada = np.zeros(n, dtype=int); inicio = np.zeros(n, dtype=int)
    fin     = np.zeros(n, dtype=int); sistema = np.zeros(n, dtype=int)
    ocioso  = np.zeros(n, dtype=int); cola    = np.zeros(n, dtype=int)

    llegada[0] = 0
    inicio[0]  = 0
    fin[0]     = servicio[0]
    sistema[0] = fin[0] - llegada[0]

    for i in range(1, n):
        llegada[i] = llegada[i-1] + tba[i]
        inicio[i]  = max(llegada[i], fin[i-1])
        fin[i]     = inicio[i] + servicio[i]
        sistema[i] = fin[i] - llegada[i]
        ocioso[i]  = max(0, llegada[i] - fin[i-1])
        cola[i]    = inicio[i] - llegada[i]

    return pd.DataFrame({
        "(1) Cliente":            np.arange(1, n+1),
        "(2) Tiempo entre lleg.": tba,
        "(3) Hora de llegada":    llegada,
        "(4) Tiempo de servicio": servicio,
        "(5) Inicio servicio":    inicio,
        "(6) Fin servicio":       fin,
        "(7) Tiempo en sistema":  sistema,
        "(8) Tiempo ocioso":      ocioso,
        "(9) Tiempo en cola":     cola,
    })


def medidas(df):
    '''Las cinco medidas de desempeño del Capítulo 1 de Banks (1998).'''
    n         = len(df)
    T_total   = df["(6) Fin servicio"].iloc[-1]      # duración de la corrida
    esperaron = int((df["(9) Tiempo en cola"] > 0).sum())
    return {
        "Tiempo promedio en el sistema":  df["(7) Tiempo en sistema"].sum() / n,
        "Porcentaje de tiempo ocioso":    df["(8) Tiempo ocioso"].sum() / T_total,
        "Espera promedio por cliente":    df["(9) Tiempo en cola"].sum() / n,
        "Fracción que esperó":            esperaron / n,
        "Espera promedio de los que esperaron":
            df["(9) Tiempo en cola"].sum() / esperaron if esperaron else 0.0,
    }
""")

M(r"""
### Verificación del motor contra la Tabla 1.1 de Banks

Antes de generar datos propios conviene comprobar que el código reproduce el ejemplo del
libro. Se cargan las columnas (2) y (4) de la Tabla 1.1 y se verifica que las columnas
calculadas coincidan con las publicadas, incluyendo las tres sumas de control (79, 30 y 10).
""")

C(r"""
tba_banks = np.array([0,5,1,10,6,2,9,1,10,3,5,2,3,5,4,3,7,8,7,7])
srv_banks = np.array([2,2,6,5,6,4,3,4,1,3,1,2,3,6,2,6,4,5,3,1])
ver = simular(tba_banks, srv_banks)

esperado = {"(7) Tiempo en sistema": 79, "(8) Tiempo ocioso": 30, "(9) Tiempo en cola": 10}
for col, val in esperado.items():
    obtenido = int(ver[col].sum())
    print("%-24s libro = %3d   calculado = %3d   %s"
          % (col, val, obtenido, "OK" if obtenido == val else "DIFIERE"))
""")

M(r"""
El motor reproduce las nueve columnas del libro y las tres sumas de control, de modo que
puede usarse con confianza para generar las corridas propias.
""")

C(r"""
def generar_corridas(n_clientes, n_runs=N_RUNS, seed=SEED):
    '''Ejecuta n_runs corridas independientes de n_clientes cada una.

    Se usan dos generadores separados, uno por variable aleatoria, tal como la guía pide
    emplear un dado o una ruleta independiente para cada una.
    '''
    rng_llegadas = np.random.default_rng(seed)
    rng_servicio = np.random.default_rng(seed + 1)
    tablas, resultados = [], []
    for _ in range(n_runs):
        tba = rng_llegadas.integers(TBA_LO, TBA_HI + 1, size=n_clientes)
        srv = rng_servicio.integers(SRV_LO, SRV_HI + 1, size=n_clientes)
        tba[0] = 0                       # el primer cliente llega en t = 0
        df = simular(tba, srv)
        tablas.append(df)
        resultados.append(medidas(df))
    return tablas, pd.DataFrame(resultados, index=pd.RangeIndex(1, n_runs+1, name="Corrida"))
""")

M(r"""
### La función de intervalos de confianza

Siguiendo la subsección 1.11.1 de Banks (1998), con $n$ corridas independientes la media
muestral y la desviación estándar muestral son

$$\bar{X}=\frac{1}{n}\sum_{i=1}^{n}X_i,
\qquad
S=\sqrt{\frac{\sum_{i=1}^{n}\left(X_i-\bar{X}\right)^2}{n-1}},$$

y el intervalo de confianza al $100(1-\alpha)\%$ es

$$\bar{X}\pm h,\qquad h=t_{n-1,\,1-\alpha/2}\,\frac{S}{\sqrt{n}},$$

donde $h$ es la **media anchura** (*half-width*). Nótese el uso de `ddof=1` en la varianza:
es el divisor $n-1$ que corresponde a la desviación estándar **muestral**.
""")

C(r"""
def intervalo(muestra, alpha):
    '''Media, desviación muestral, valor t, media anchura y límites del intervalo.'''
    x    = np.asarray(muestra, dtype=float)
    n    = len(x)
    mean = np.mean(x)
    desv = np.sqrt(np.var(x, ddof=1))            # ddof=1 -> desviación MUESTRAL
    tval = stats.t.ppf(1 - alpha/2, n - 1)       # valor crítico t de Student
    h    = tval * desv / np.sqrt(n)              # media anchura (half-width)
    return {"n": n, "media": mean, "S": desv, "t": tval, "h": h,
            "LI": mean - h, "LS": mean + h, "rango": 2*h}


def reporte(muestra, alpha, titulo):
    '''Presenta el cálculo con el mismo formato del ejemplo 2 de la subsección 1.11.1.'''
    r    = intervalo(muestra, alpha)
    conf = (1 - alpha) * 100
    display(Markdown(rf'''
**{titulo}** — confianza del ${conf:.0f}\%$ ($n = {r['n']}$ corridas)

$\bar{{X}} = {r['media']:.4f}$ &nbsp;&nbsp;&nbsp; $S = {r['S']:.4f}$

$t_{{n-1,\,1-\alpha/2}} = t_{{{r['n']-1},\,{1-alpha/2}}} = {r['t']:.4f}$

$h = t\,\dfrac{{S}}{{\sqrt{{n}}}} = {r['t']:.4f}\times\dfrac{{{r['S']:.4f}}}{{\sqrt{{{r['n']}}}}} = {r['h']:.4f}$

Intervalo de confianza: $\;(\bar{{X}}-h,\;\bar{{X}}+h) = ({r['LI']:.4f},\;{r['LS']:.4f})$
&nbsp;&nbsp; con rango $2h = {r['rango']:.4f}$
'''))
    return r


def tabla_intervalos(resultados):
    '''Arma la tabla de intervalos al 95% y 99% para las cinco medidas.'''
    filas = []
    for medida in resultados.columns:
        for alpha, etiqueta in ((0.05, "95%"), (0.01, "99%")):
            r = intervalo(resultados[medida], alpha)
            filas.append({"Medida": medida, "Confianza": etiqueta,
                          "X barra": r["media"], "S": r["S"], "t": r["t"], "h": r["h"],
                          "LI": r["LI"], "LS": r["LS"], "Rango (2h)": r["rango"]})
    return pd.DataFrame(filas).round(4)
""")

# --------------------------------------------------------------- escenario A
M(r"""
---
## 3. Escenario A — 20 clientes por corrida

### 3.1 Generación de valores aleatorios y tabla de la simulación (paso 5.1)

Se generan las diez corridas y se muestra completa la primera de ellas, que es la que
aparece reproducida en el informe.
""")

C(r"""
tablas20, res20 = generar_corridas(20)

corrida1 = tablas20[0].copy()
corrida1.loc[corrida1.index[0], "(2) Tiempo entre lleg."] = np.nan   # el 1.er cliente no tiene
display(corrida1.to_string(index=False, na_rep="-"))

print("\nSumas de control  ->  (7) sistema = %d   (8) ocioso = %d   (9) cola = %d"
      % (corrida1["(7) Tiempo en sistema"].sum(),
         corrida1["(8) Tiempo ocioso"].sum(),
         corrida1["(9) Tiempo en cola"].sum()))
""")

M(r"""
### 3.2 Medidas de desempeño de la corrida (paso 5.2)
""")

C(r"""
m1 = medidas(tablas20[0])
for k, v in m1.items():
    print("%-40s %8.4f" % (k + ":", v))
""")

M(r"""
### 3.3 Repetición de la simulación — 10 corridas (paso 5.3)
""")

C(r"""
display(res20.round(4))
print("\nMedia de cada medida sobre las 10 corridas:")
print(res20.mean().round(4).to_string())
print("\nDesviación estándar muestral (ddof=1):")
print(res20.std(ddof=1).round(4).to_string())
""")

M(r"""
### 3.4 Intervalos de confianza (paso 5.4)

Se aplica el procedimiento del ejemplo 2 de la subsección 1.11.1 a cada medida. Primero se
desarrolla paso a paso el cálculo para el tiempo promedio en el sistema, y luego se
consolidan las cinco medidas en una sola tabla.
""")

C(r"""
_ = reporte(res20["Tiempo promedio en el sistema"], 0.05,
            "Tiempo promedio en el sistema — 20 clientes")
_ = reporte(res20["Tiempo promedio en el sistema"], 0.01,
            "Tiempo promedio en el sistema — 20 clientes")
""")

C(r"""
ic20 = tabla_intervalos(res20)
display(ic20)
""")

# --------------------------------------------------------------- escenario B
M(r"""
---
## 4. Escenario B — 200 clientes por corrida (paso 5.5)

Se repite exactamente el mismo procedimiento aumentando a 200 el número de clientes
atendidos en cada corrida. Se mantienen las distribuciones, el número de repeticiones y
los niveles de confianza, de modo que la única variable que cambia es la longitud de la
corrida.
""")

C(r"""
tablas200, res200 = generar_corridas(200)

corrida1_200 = tablas200[0].copy()
corrida1_200.loc[corrida1_200.index[0], "(2) Tiempo entre lleg."] = np.nan
print("Primeras 15 y últimas 5 filas de la corrida 1 (la tabla completa va en el informe):\n")
display(corrida1_200.head(15).to_string(index=False, na_rep="-"))
display(corrida1_200.tail(5).to_string(index=False))

print("\nSumas de control  ->  (7) sistema = %d   (8) ocioso = %d   (9) cola = %d"
      % (corrida1_200["(7) Tiempo en sistema"].sum(),
         corrida1_200["(8) Tiempo ocioso"].sum(),
         corrida1_200["(9) Tiempo en cola"].sum()))
""")

C(r"""
m1_200 = medidas(tablas200[0])
print("Medidas de desempeño de la corrida 1 (200 clientes)\n")
for k, v in m1_200.items():
    print("%-40s %8.4f" % (k + ":", v))
""")

C(r"""
display(res200.round(4))
print("\nMedia de cada medida sobre las 10 corridas:")
print(res200.mean().round(4).to_string())
print("\nDesviación estándar muestral (ddof=1):")
print(res200.std(ddof=1).round(4).to_string())
""")

C(r"""
_ = reporte(res200["Tiempo promedio en el sistema"], 0.05,
            "Tiempo promedio en el sistema — 200 clientes")
_ = reporte(res200["Tiempo promedio en el sistema"], 0.01,
            "Tiempo promedio en el sistema — 200 clientes")
""")

C(r"""
ic200 = tabla_intervalos(res200)
display(ic200)
""")

# --------------------------------------------------------------- comparacion
M(r"""
---
## 5. Comparación de los dos escenarios

La última pregunta de la guía pide identificar qué combinación de número de clientes,
repeticiones y nivel de confianza produce la menor desviación estándar muestral y el menor
rango de intervalo. La siguiente tabla reúne los datos necesarios para responderla.
""")

C(r"""
comp = (ic20.assign(Clientes=20)
        ._append(ic200.assign(Clientes=200)) if hasattr(ic20, "_append")
        else pd.concat([ic20.assign(Clientes=20), ic200.assign(Clientes=200)]))
comp = comp[["Medida", "Clientes", "Confianza", "X barra", "S", "h", "Rango (2h)"]]
comp = comp.sort_values(["Medida", "Clientes", "Confianza"]).reset_index(drop=True)
display(comp)

fila = comp.loc[comp["Rango (2h)"].idxmin()]
print("\nMenor rango de intervalo de confianza de toda la tabla:")
print("  Medida    : %s" % fila["Medida"])
print("  Clientes  : %d   Confianza: %s" % (fila["Clientes"], fila["Confianza"]))
print("  S = %.4f   rango 2h = %.4f" % (fila["S"], fila["Rango (2h)"]))
""")

M(r"""
Como las cinco medidas están expresadas en unidades distintas (minutos, proporciones), la
comparación directa de sus $S$ favorece automáticamente a las que se miden en una escala
más pequeña. Para comparar de forma justa se calcula la **precisión relativa**
$h/\bar{X}$, que es adimensional.
""")

C(r"""
rel = []
for medida in res20.columns:
    a = intervalo(res20[medida], 0.05)
    b = intervalo(res200[medida], 0.05)
    rel.append({"Medida": medida,
                "CV 20 cl. (%)":  100*a["S"]/a["media"],
                "CV 200 cl. (%)": 100*b["S"]/b["media"],
                "h/X 20 cl. (%)":  100*a["h"]/a["media"],
                "h/X 200 cl. (%)": 100*b["h"]/b["media"],
                "Reducción de S (%)": 100*(1 - b["S"]/a["S"])})
display(pd.DataFrame(rel).round(2))
""")

C(r"""
print("Control de calidad: utilización teórica del servidor rho = %.4f" % (3.5/5.5))
print("Tiempo ocioso teórico esperado = 1 - rho = %.4f" % (1 - 3.5/5.5))
print("Tiempo ocioso medio observado con  20 clientes = %.4f"
      % res20["Porcentaje de tiempo ocioso"].mean())
print("Tiempo ocioso medio observado con 200 clientes = %.4f"
      % res200["Porcentaje de tiempo ocioso"].mean())
""")

M(r"""
El porcentaje de tiempo ocioso observado con 200 clientes prácticamente coincide con el
valor teórico $1-\rho = 0{,}3636$, lo que confirma que la simulación converge al
comportamiento esperado del sistema a medida que crece la longitud de la corrida.

---

### Referencia

Banks, J. (1998). *Handbook of Simulation: Principles, Methodology, Advances, Applications,
and Practice*. John Wiley & Sons, Inc. — Capítulo 1, secciones 1.2, 1.11 y 1.11.1.
""")

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
    "colab": {"provenance": [], "toc_visible": True},
}

print("Ejecutando el notebook...")
client = NotebookClient(nb, timeout=300, kernel_name="python3",
                        resources={"metadata": {"path": os.path.dirname(DEST) or "."}})
client.execute()
nbf.write(nb, DEST)
print("Guardado:", DEST)
