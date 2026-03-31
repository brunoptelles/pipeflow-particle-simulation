import numpy as np
from timeit import default_timer as timer
from concurrent.futures import ThreadPoolExecutor
from src.integrator import RK4



def criar_chunk(chunk_atual, loader, n_threads):

    for i in range(n_threads):
        loader.processos[i] = chunk_atual
        loader.load(chunk_atual)

    loader.clear()

    return


def simular(s0, v0, a0, t0, snapshot0, loader, n_threads, st_star, estado_thread,
            colidiu, fator_dt, chunk_size, snapshot_max, t_max, dt, r_max, demo, st, salvar_dados):

    teta0 = np.arctan2((s0[:,2] - 150),(s0[:,1] - 150))
    teta0_graus = np.round(np.degrees(teta0)) % 360
    r0 = np.round(np.sqrt((s0[:,2] - 150)**2 + (s0[:,1] - 150)**2), 2)
    r_max_sq = r_max**2

    chunk_atual = ((snapshot0[0] / chunk_size)*chunk_size).astype(int)

    criar_chunk(chunk_atual, loader, n_threads)

    resultados = [] #[i, j, k] - i eh o indice da thread, j eh o tipo de dado (s,t,v,snapshot), k eh a iteracao

    for p in range(n_threads):
        resultados.append([[s0[p].copy()], [t0[p].copy()], [v0[p].copy()], [snapshot0[p]], [a0[p]]])

    lista_particulas = [None]*n_threads
    lista_novos_valores = [None]*n_threads

    snapshot_atual = snapshot0.copy() #para poder usar no rk4 sem dar merda

    timer_it = timer()

    parada = False
    iteracoes = 1
    while not parada:          

        #cria uma lista com tuplas para passar os parametros do RK4    
        for p in range(n_threads):
            lista_particulas[p] = (t0[p], s0[p, :], v0[p, :], chunk_atual, st_star[p], estado_thread[p], p, snapshot_atual[p], snapshot0[p], loader, fator_dt, chunk_size, dt)

        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = []
            for args in lista_particulas:
                futures.append(executor.submit(RK4, *args))

        lista_novos_valores = [f.result() for f in futures]

        #atualiza os parametros            
        for p in range(n_threads):
            if not (type(lista_novos_valores[p]) is str):
                v0[p,:] = lista_novos_valores[p][1]
                s0[p,:] = lista_novos_valores[p][2]
                t0[p] = lista_novos_valores[p][0]

        for p in range(n_threads):
            if estado_thread[p]:
                snapshot_atual[p] = (snapshot0[p] + fator_dt*s0[p,0] + t0[p]).astype(int) #encontra os snapshots que dever ser usados p simulacao, faz soma do snapshot inicial 
                                                                                        #com o quanto ele andou espacialmente (corrigido por uma cte que relaciona dt e ds)
                                                                                        #com o tempo que ja passou (movimento do fluido em si,a particula e o fluido estao em movimento)         

        #testa se colidiu ou excedeu os dados 
        for p in range(n_threads):
            if estado_thread[p]:                   
                if snapshot_atual[p] >= snapshot_max:
                    estado_thread[p] = False
                    snapshot_atual[p] = snapshot_max + 1 #serve para limpar os chunks da maneira correta e para gerar os chunks direito
                    print("\nExcedeu o numero de snapshots.")

                if t0[p] > t_max: #condicao de parada, avalia se a particula excedeu o volume
                    estado_thread[p] = False
                    snapshot_atual[p] = snapshot_max + 1 #serve para limpar os chunks da maneira correta e para gerar os chunks direito
                    print("\nConcluiu em tempo.")

                if ((s0[p,1] - r_max)**2 + (s0[p,2] - r_max)**2) > r_max_sq: #condicao de parada, avalia se a particula bateu na parede
                    estado_thread[p] = False
                    colidiu[p] = True
                    snapshot_atual[p] = snapshot_max + 1 #serve para limpar os chunks da maneira correta e para gerar os chunks direito
                    print("\nColidiu!")

                if lista_novos_valores[p] == "colidiu": #avalia se a particula colidiu dentro do rk4
                    estado_thread[p] = False
                    colidiu[p] = True
                    snapshot_atual[p] = snapshot_max + 1 #serve para limpar os chunks da maneira correta e para gerar os chunks direito
                    print("\nColidiu!")


        #atualiza  os resultados
        for p in range(n_threads):
            if (not (type(lista_novos_valores[p]) is str)) and estado_thread[p]:
                resultados[p][0].append(lista_novos_valores[p][2].copy()) #salva a posicao
                resultados[p][1].append(lista_novos_valores[p][0].copy()) #salva o tempo
                resultados[p][2].append(lista_novos_valores[p][1].copy()) #salva a velocidade
                resultados[p][3].append(snapshot_atual[p].copy())
                resultados[p][4].append(lista_novos_valores[p][3].copy()) #salva a aceleracao


        #termina a simulacao, quando todas as particulas param de simular
        if not np.any(estado_thread):
            parada = True

        #atualiza os chunks
        if np.all(snapshot_atual > (chunk_atual + chunk_size)):                                   
            chunk_atual = (chunk_atual + chunk_size).astype(int)
        

        criar_chunk(chunk_atual, loader, n_threads)


        if iteracoes % 1000 == 0:
            timer_it2 = - timer_it + timer()
            print(f"Iteracao {iteracoes}\n")
            print(f"particulas ativas = {np.sum(estado_thread)}\n")
            print(f"particulas mais longe = {np.min(t0)}\n")
            print(f"timer it = {timer_it2/iteracoes}\n")
            print("\n") 

        iteracoes += 1 #contador de iteracoes

    #SEQUENCIA DE SALVAMENTO
    resultado_demo = []
    for p in range(n_threads):     
        resultado_x = [arr[0] for arr in resultados[p][0]]
        resultado_y = [arr[1] for arr in resultados[p][0]]
        resultado_z = [arr[2] for arr in resultados[p][0]]

        resultado_u = [arr[0] for arr in resultados[p][2]]
        resultado_v = [arr[1] for arr in resultados[p][2]]
        resultado_w = [arr[2] for arr in resultados[p][2]]

        resultado_ax = [arr[0] for arr in resultados[p][4]]
        resultado_ay = [arr[1] for arr in resultados[p][4]]
        resultado_az = [arr[2] for arr in resultados[p][4]]


        trajetoria = np.array([resultado_x.copy(), resultado_y.copy(), resultado_z.copy(), 
                                resultado_u.copy(), resultado_v.copy(), resultado_w.copy(),
                                resultado_ax.copy(), resultado_ay.copy(), resultado_az.copy(),
                                resultados[p][1], resultados[p][3]])
        
        if demo:
            resultado_demo.append(trajetoria.copy())

        if salvar_dados:

            if colidiu[p]:
                nome_trajetoria = f"./data/outputs/r0={int(r0[p])}_teta={int(teta0_graus[p])}_st={int(st[p])}_c_inicio={int(snapshot0[p])}"
            else:
                nome_trajetoria = f"./data/outputs/r0={int(r0[p])}_teta={int(teta0_graus[p])}_st={int(st[p])}_nc_inicio={int(snapshot0[p])}"

            np.save(nome_trajetoria, trajetoria)
            print(f"Salvou particula {p}")

    del resultados, resultado_x, resultado_y, resultado_z, resultado_u, resultado_v, resultado_w, resultado_ax, resultado_ay, resultado_az

    print("Simulacao concluida")
    return(resultado_demo)