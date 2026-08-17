"""
Motor de simulacion ad hoc de una fila de banco (M/M/1 discreto, un servidor, FIFO).
Practica 1 - Simulacion Computacional - Universidad de los Llanos.

Reglas identicas a la Tabla 1.1 del Capitulo 1 de [Banks1998]:
  arrival_1      = 0
  arrival_i      = arrival_{i-1} + tba_i
  begin_i        = max(arrival_i, end_{i-1}),  begin_1 = arrival_1
  end_i          = begin_i + service_i
  system_i       = end_i - arrival_i
  idle_i         = max(0, arrival_i - end_{i-1}), idle_1 = 0
  queue_i        = begin_i - arrival_i
"""
import numpy as np
from scipy import stats

SEED = 20260817
TBA_LO, TBA_HI = 1, 10      # uniforme discreta 1..10 (ruleta de 10 sectores)
SRV_LO, SRV_HI = 1, 6       # uniforme discreta 1..6  (dado de 6 caras)
N_RUNS = 10

MEASURE_KEYS = ["avg_system", "pct_idle", "avg_wait_all", "frac_wait", "avg_wait_waiters"]
MEASURE_ES = {
    "avg_system":       "Tiempo promedio en el sistema",
    "pct_idle":         "Porcentaje de tiempo ocioso",
    "avg_wait_all":     "Tiempo de espera promedio por cliente",
    "frac_wait":        "Fraccion de clientes que espero",
    "avg_wait_waiters": "Tiempo de espera promedio de quienes esperaron",
}
MEASURE_SHORT = {
    "avg_system":       "Tiempo prom. en el sistema",
    "pct_idle":         "Porcentaje de tiempo ocioso",
    "avg_wait_all":     "Espera prom. por cliente",
    "frac_wait":        "Fraccion que espero",
    "avg_wait_waiters": "Espera prom. de quienes esperaron",
}


def simulate(tba, service):
    """tba[0] se ignora (el cliente 1 llega en t=0). Devuelve dict de columnas."""
    n = len(service)
    arrival = np.zeros(n, dtype=int)
    begin = np.zeros(n, dtype=int)
    end = np.zeros(n, dtype=int)
    system = np.zeros(n, dtype=int)
    idle = np.zeros(n, dtype=int)
    queue = np.zeros(n, dtype=int)

    arrival[0] = 0
    begin[0] = 0
    end[0] = service[0]
    system[0] = end[0] - arrival[0]
    idle[0] = 0
    queue[0] = 0

    for i in range(1, n):
        arrival[i] = arrival[i - 1] + tba[i]
        begin[i] = max(arrival[i], end[i - 1])
        end[i] = begin[i] + service[i]
        system[i] = end[i] - arrival[i]
        idle[i] = max(0, arrival[i] - end[i - 1])
        queue[i] = begin[i] - arrival[i]

    return dict(tba=tba, arrival=arrival, service=service, begin=begin,
                end=end, system=system, idle=idle, queue=queue)


def measures(t):
    n = len(t["service"])
    total_time = int(t["end"][-1])
    n_waiters = int(np.sum(t["queue"] > 0))
    return {
        "avg_system": t["system"].sum() / n,
        "pct_idle": t["idle"].sum() / total_time,
        "avg_wait_all": t["queue"].sum() / n,
        "frac_wait": n_waiters / n,
        "avg_wait_waiters": (t["queue"].sum() / n_waiters) if n_waiters else 0.0,
        "_n_waiters": n_waiters,
        "_total_time": total_time,
        "_sum_system": int(t["system"].sum()),
        "_sum_idle": int(t["idle"].sum()),
        "_sum_queue": int(t["queue"].sum()),
    }


def make_runs(n_customers, n_runs=N_RUNS, seed=SEED):
    """Ruletas independientes: un generador para llegadas y otro para servicio."""
    rng_tba = np.random.default_rng(seed)
    rng_srv = np.random.default_rng(seed + 1)
    runs = []
    for _ in range(n_runs):
        tba = rng_tba.integers(TBA_LO, TBA_HI + 1, size=n_customers)
        srv = rng_srv.integers(SRV_LO, SRV_HI + 1, size=n_customers)
        tba[0] = 0  # el primer cliente llega en el instante 0
        t = simulate(tba, srv)
        runs.append({"table": t, "meas": measures(t)})
    return runs


def confidence(sample, alpha):
    x = np.asarray(sample, dtype=float)
    n = len(x)
    mean = float(np.mean(x))
    s = float(np.sqrt(np.var(x, ddof=1)))
    tval = float(stats.t.ppf(1 - alpha / 2, n - 1))
    h = tval * s / np.sqrt(n)
    return {"n": n, "mean": mean, "s": s, "t": tval, "h": h,
            "lo": mean - h, "hi": mean + h, "range": 2 * h}
