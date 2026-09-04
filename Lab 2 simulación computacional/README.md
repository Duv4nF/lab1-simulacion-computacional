# Lab 2 — Simulación Computacional

Práctica N.º 02: **Números (pseudo)aleatorios y generación de variables aleatorias**.
Generadores pseudoaleatorios con sus pruebas de periodo, uniformidad y aleatoriedad;
integración Monte Carlo; generación de variables aleatorias discretas; y una simulación
*ad hoc* de cola simple alimentada con variables Poisson y Binomiales.

Universidad de los Llanos · Ingeniería de Sistemas · Curso: Simulación Computacional
Guía FO-DOC-112 · Duván Felipe Baquero · Código 160005002

---

## Qué hay en cada numeral

### 5.1 Generación de números pseudoaleatorios

Doce secuencias de $n = 100$ números, con su periodo y sus tres pruebas:

| Método | Casos | Resultado |
|---|---|---|
| MidSquare | 5 semillas | 2 de 5 pasan las tres pruebas, y las dos degeneran si se extiende la secuencia |
| Congruencial mixto | 5 juegos de parámetros | El de `m = 2^48` es el mejor de todo el laboratorio |
| Shift-Register (LFSR, k=7) | 1 | Periodo máximo 127, pasa las tres |
| Congruencia inversa (m=101) | 1 | El más uniforme de todos y aun así **falla** el test de rachas |

Dos hallazgos que quedaron documentados:

- Un generador con periodo menor que la muestra pasa la prueba de uniformidad de forma
  **artificial**, porque recorre su ciclo completo y produce un histograma plano. Le pasa a los
  congruenciales con `m = 128` y `m = 48`.
- **Uniformidad y aleatoriedad son propiedades distintas.** El de congruencia inversa dio
  χ² = 0,0 (exactamente 10 observaciones en cada una de las 10 clases) y falló el test de
  rachas con Z = 2,31 por alternar valores altos y bajos.

### 5.2 Integración Monte Carlo

Ejercicios 3 a 9 del capítulo 3 de Ross, con las sustituciones de la sección 3.2. Con
100 000 números los siete estimadores quedan por debajo del 0,5 % de error relativo.

| Ejercicio | k = 100 | k = 100 000 |
|---|---|---|
| 3 · ∫₀¹ exp(eˣ) dx | 2,35 % | 0,041 % |
| 5 · ∫₋₂² e^(x+x²) dx | **68,63 %** | 0,487 % |
| 7 · ∫₋∞^∞ e^(−x²) dx | 8,24 % | 0,187 % |
| 9 · ∫₀^∞∫₀ˣ e^(−(x+y)) dy dx | 12,51 % | 0,174 % |

El ejercicio 5 es el peor caso porque su integrando va de 0,78 a 403,4 sobre `[-2, 2]`, y con
100 puntos casi nunca cae uno cerca del extremo derecho.

### 5.3 Variables aleatorias discretas

Transformada inversa con el generador `X0 = 2391, a = 25214903917, c = 11, m = 2^48`. Los
cuatro literales pasan la prueba χ². Dos resultados propios:

- Los literales a) y b) usan **los mismos 100 números** `u_i` y aun así 51 de los 100 valores
  generados son distintos, solo porque cambió la partición de (0,1).
- El **método de composición** del literal d) bajó el costo de generar un valor de 6,48
  comparaciones (transformada inversa directa) a **1,15**, porque el 59,8 % de las veces
  resuelve el sorteo con `Ent(10·U₂) + 1` sin ninguna búsqueda.

### 5.4 Simulación *ad hoc* con Poisson y Binomial

Se repiten las secciones 5.1 y 5.2 del Laboratorio 1 cambiando las distribuciones de entrada:

| | Laboratorio 1 | Laboratorio 2 |
|---|---|---|
| Tiempo entre llegadas | `U{1..10}`, media 5,5 | `Poisson(10)`, media 10 |
| Tiempo de servicio | `U{1..6}`, media 3,5 | `Binomial(10; 0,40)`, media 4 |
| Intensidad de tráfico ρ | 0,636 | 0,400 |

Promedio de 10 corridas de 200 clientes:

| Medida | Lab 1 | Lab 2 | Cambio |
|---|---|---|---|
| Tiempo promedio en el sistema | 4,6470 | 3,9980 | −14,0 % |
| Porcentaje de tiempo ocioso | 0,3745 | 0,6034 | +61,1 % |
| Espera promedio por cliente | 1,1890 | 0,0385 | −96,8 % |
| Fracción que esperó | 0,3505 | 0,0225 | −93,6 % |
| Espera de quienes esperaron | 3,3477 | 1,5500 | −53,7 % |

El tiempo ocioso medido reproduce el valor teórico `1 − ρ` en los dos modelos (0,3745 contra
0,3636 y 0,6034 contra 0,6000), lo que valida el motor de simulación y los dos generadores.

En la corrida de 20 clientes solo **un** cliente esperó, y esperó 1 minuto. Con el modelo del
Lab 2 y 20 clientes, 9 de 10 corridas terminan sin nadie en cola, así que hubo que subir a 200
clientes para poder medir la espera de quienes esperaron.

## Estructura

```
├── Lab2_Simulacion_Duvan_Baquero_160005002.ipynb   Cuaderno ejecutado (78 celdas)
├── Informe_Practica2_Numeros_Aleatorios.pdf        Informe compilado (18 páginas)
├── Informe_LaTeX/                                  Fuente: main.tex + 8 tablas + 3 figuras
├── Informe_LaTeX_Overleaf.zip                      Listo para subir a Overleaf
├── Entrega_Lab2_160005002.zip                      PDF + cuaderno, para la plataforma
└── LEEME.txt
```

## Reproducibilidad

Los generadores están escritos a mano siguiendo los algoritmos de los capítulos 3 y 4 de Ross.
De `scipy` solo se usan valores críticos, funciones de masa teóricas y una cuadratura numérica
como referencia en tres de las siete integrales. Todas las semillas están fijas en el código,
así que cualquier ejecución del cuaderno reproduce exactamente las tablas del informe.

El cuaderno corre tal cual en Google Colab, sin instalar nada. Para el PDF, subir
`Informe_LaTeX_Overleaf.zip` a Overleaf y compilar `main.tex`.

## Referencias

- Ross, S. (1999). *Simulación*, 2.ª edición. Pearson Press. Capítulos 3 y 4.
- Banks, J. (1998). *Handbook of Simulation*. John Wiley & Sons. Capítulo 1.
- Mancilla Herrera, A. M. (2000). *Números aleatorios. Historia, teoría y aplicaciones*.
  Ingeniería y Desarrollo, núm. 8, pp. 49-69. Universidad del Norte.
