# Lab 1 — Simulación Computacional

Práctica N.º 01: **Simulación *ad hoc*** de un sistema de cola simple (la ventanilla de un banco),
con cálculo de medidas de desempeño e intervalos de confianza para 20 y 200 clientes atendidos.

Universidad de los Llanos · Ingeniería de Sistemas · Curso: Simulación Computacional

---

## El problema

Se simula un sistema de cola de **un solo servidor** con disciplina FIFO, siguiendo la Tabla 1.1
del Capítulo 1 de Banks (1998). Las dos variables aleatorias del modelo son uniformes discretas:

| Variable | Distribución | Equivalente físico |
|---|---|---|
| Tiempo entre llegadas | `U{1..10}` minutos | ruleta de 10 sectores |
| Tiempo de servicio | `U{1..6}` minutos | dado de 6 caras |

Sobre cada corrida se calculan las cinco medidas de desempeño de la guía, y sobre 10 corridas
repetidas se construyen intervalos de confianza al 95 % y 99 % mediante la distribución *t* de
Student, según la subsección 1.11.1 de Banks.

## Resultados principales

Con 10 corridas por escenario, la media se mantiene estable mientras la dispersión cae de forma
drástica al alargar la corrida:

| Medida | 20 clientes | 200 clientes |
|---|---|---|
| Tiempo promedio en el sistema | 4,66 min (S = 1,1276) | 4,60 min (S = 0,2642) |
| Porcentaje de tiempo ocioso | 34,91 % (S = 0,0910) | 36,07 % (S = 0,0282) |
| Espera promedio por cliente | 1,1750 min (S = 0,8430) | 1,1115 min (S = 0,2428) |
| Fracción que esperó | 0,3500 (S = 0,1434) | 0,3545 (S = 0,0539) |
| Espera prom. de quienes esperaron | 3,1089 min (S = 1,0386) | 3,1079 min (S = 0,2972) |

El margen relativo del intervalo al 95 % para el tiempo en el sistema pasa de **±17,3 %** a
**±4,1 %**. Las razones de reducción de *S* se agrupan alrededor de **√10 ≈ 3,162**, que es
exactamente lo que predice la teoría al multiplicar por diez la longitud de la corrida.

Como validación independiente, el tiempo ocioso promedio observado con 200 clientes (36,07 %)
coincide con el valor teórico `1 − ρ = 36,36 %`, donde `ρ = E[S]/E[A] = 3,5/5,5`.

## Estructura

```
├── Entrega_Lab1/
│   ├── Informe_Practica1_Simulacion_AdHoc.pdf   Informe compilado (24 páginas)
│   ├── Informe_LaTeX/                           Fuente LaTeX (main.tex + tablas + figuras)
│   ├── Informe_LaTeX_Overleaf.zip               Listo para subir a Overleaf
│   ├── fila_banco_20_clientes.xlsx              Hojas "Ejemplo" y "10 runs", con fórmulas
│   ├── fila_banco_200_clientes.xlsx
│   ├── Confidence_intervals_20_200.ipynb        Cuaderno de Colab, ya ejecutado
│   └── LEEME.txt
├── scripts/
│   ├── simcore.py            Motor de simulación y estadística
│   ├── build_tablas.py       Genera las tablas .tex, las figuras y los .xlsx
│   └── make_notebook.py      Construye y ejecuta el cuaderno
├── Confidence_intervals.ipynb                   Cuaderno original de la guía
└── FO-DOC-112 Lab 1 Simulacion Ad Hoc.pdf       Guía del laboratorio
```

## Reproducibilidad

Todos los valores aleatorios provienen de dos generadores independientes con **semilla fija**
(`SEED = 20260817`), uno por variable aleatoria. Cualquier ejecución reproduce exactamente las
mismas tablas del informe.

El motor está verificado contra la Tabla 1.1 de Banks: reproduce sus nueve columnas y los tres
totales de control (79 min en el sistema, 30 de tiempo ocioso, 10 en cola). Además, una prueba
χ² de bondad de ajuste confirma que los generadores son indistinguibles de la ruleta y el dado
(p > 0,05 en los cuatro casos).

### Regenerar todo desde cero

```bash
pip install numpy scipy pandas matplotlib openpyxl nbformat nbclient ipykernel

python scripts/build_tablas.py     # tablas .tex, figuras .pdf y archivos .xlsx
python scripts/make_notebook.py    # cuaderno .ipynb ejecutado
```

Para el PDF, subir `Entrega_Lab1/Informe_LaTeX_Overleaf.zip` a Overleaf y compilar `main.tex`.
El preámbulo funciona tanto con pdfLaTeX como con XeLaTeX o LuaLaTeX.

## Referencia

Banks, J. (1998). *Handbook of Simulation: Principles, Methodology, Advances, Applications, and
Practice*. John Wiley & Sons, Inc. — Capítulo 1, secciones 1.2, 1.11 y 1.11.1.
