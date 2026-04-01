from multiprocessing import Pool
from src.loader import Loader
from src.simulation import simular
import numpy as np
import matplotlib.pyplot as plt
import os

def get_config():
    demo = input("Demo? (y/n)\n").lower()
    salvar_dados = input("Save Data? (y/n)\n").lower()
    save = salvar_dados == "y"


    if demo == "y":
        return {
            "demo": True,
            "n_processos": 2,
            "n_threads": 5,
            "primeira_snapshot": 0,
            "t_max": int(input("t_max?\n")),
            "st": int(input("Stokes Number?\n")),
            "m": int(input("Vortex Number?(2-5)\n")),
            "r_max": 100,
            "chunk_size": 390,
            "salvar_dados": save
        }
    else:
        return {
            "demo": False,
            "n_processos": int(input("numero de processos?\n")),
            "n_threads": int(input("numero de threads?\n")),
            "primeira_snapshot": int(input("primeiro snapshot?\n")),
            "t_max": int(input("t_max?\n")),
            "st": int(input("numero de stokes?\n")),
            "m": None,
            "r_max": 150,
            "chunk_size": 1010,
            "salvar_dados": save
        }


def gerar_particulas(config, base):

    angulos = np.arange(0, 2*np.pi, np.radians(base["delta_angulo"]))
    raios = np.arange(base["menor_raio"], base["r_max"], base["delta_raio"])  

    n_snapshots0 = max(1, int(config["n_processos"]/base["n_raios"]))

    lista_simulacoes = []

    for k in range(n_snapshots0):      
        for i in range(base["n_raios"]):

            s0_local = base["s0"].copy()

            for j in range(base["n_angulos"]):                
                raio = raios[i]
                angulo = angulos[j]

                s0_local[j,1] = base["r_max"] + raio*np.cos(angulo)
                s0_local[j,2] = base["r_max"] + raio*np.sin(angulo)

            lista_simulacoes.append((
                s0_local,
                base["v0"].copy(),
                base["a0"].copy(),
                base["t0"].copy(),
                base["primeira_snapshot_arr"].copy(),
                base["loader"],
                base["n_threads"],
                base["st_star"].copy(),
                base["estado_thread"].copy(),
                base["colidiu"].copy(),
                base["fator_dt"],
                base["chunk_size"],
                base["snapshot_max"],
                config["t_max"],
                base["dt"],
                base["r_max"],
                base["demo"],
                base["st"].copy(),
                base["salvar_dados"]
            ))

        base["primeira_snapshot_arr"] += 1000

    return lista_simulacoes


if __name__ == "__main__":

    config = get_config()
    

    n_threads = config["n_threads"]

    loader = Loader(n_threads, config["demo"], config["m"])

    # ===== campo =====
    Re = 5329.3
    D = 299
    nu = 0.0032
    u_lbm = Re*nu/D
    fator_dt = int(1/u_lbm)
    u_star = 0.00388
    fator_st = nu/u_star**2

    # ===== partículas =====
    id_thread = np.arange(0, n_threads)
    estado_thread = np.full(n_threads, True, dtype=bool)
    colidiu = np.full(n_threads, False, dtype=bool)

    st = np.ones(n_threads) * config["st"]
    st_star = st * fator_st
    dt = 1

    s0 = np.ones((n_threads, 3))
    s0[:, 0] = 0
    v0 = np.zeros((n_threads, 3))
    a0 = np.zeros((n_threads, 3))
    t0 = np.zeros(n_threads)

    # ===== config geométrica =====
    n_angulos = n_threads
    delta_angulo = int(360 / n_angulos)
    n_raios = config["n_processos"]
    menor_raio = 10
    delta_raio = int((150 - menor_raio) / n_raios)

    primeira_snapshot_arr = np.ones(n_threads, dtype=int) * config["primeira_snapshot"]
    snapshot_max = 1150000
    chunk_size = 1000

    # junta tudo
    base = {
        "s0": s0,
        "v0": v0,
        "a0": a0,
        "t0": t0,
        "estado_thread": estado_thread,
        "loader": loader,
        "colidiu": colidiu,
        "st_star": st_star,
        "st": st,
        "fator_dt": fator_dt,
        "chunk_size": config["chunk_size"],
        "snapshot_max": snapshot_max,
        "dt": dt,
        "n_angulos": n_angulos,
        "delta_angulo": delta_angulo,
        "n_raios": n_raios,
        "menor_raio": menor_raio,
        "delta_raio": delta_raio,
        "primeira_snapshot_arr": primeira_snapshot_arr,
        "n_threads": n_threads,
        "demo": config["demo"],
        "r_max": config["r_max"],
        "salvar_dados": config["salvar_dados"]
        
    }

    print("INICIANDO")

    os.makedirs("./data/outputs", exist_ok=True)
    os.makedirs("./data/chunks", exist_ok=True)

    lista_simulacoes = gerar_particulas(config, base)

    with Pool(processes=config["n_processos"]) as pool:
        resultados = pool.starmap(simular, lista_simulacoes)
    
    if config["demo"]:
        xaux = np.arange(0, 2*config["r_max"], 1)
        yaux = np.arange(0, 2*config["r_max"], 1)

        theta = np.linspace(0, 2*np.pi, 1000)
        x1 = 100 +100*np.cos(theta)
        y1 = 100 +100*np.sin(theta)

        

        x, y = np.meshgrid(xaux, yaux)
        fig, ax = plt.subplots(figsize = (10,10))
        ax.set_aspect('equal')
        loader.load(0)
        plt.quiver(x[::8, ::8], y[::8, ::8], loader.cache[0][1][::8, ::8, 0], loader.cache[0][2][::8, ::8, 0])

        for traj in resultados:
            for p in range(n_threads):
                plt.plot(traj[p][1], traj[p][2])
        plt.plot(x1, y1)
        plt.show()
        