from src.physics import a

def RK4(t0, s0, v0, chunk_atual, st_star_p, estado, processo, snapshot, snapshot0, loader, fator_dt, chunk_size, dt):   
    if not estado: #para particulas q colidiram
        return("pause")

    if snapshot > (chunk_atual + chunk_size): #para particulas q ja excederam esse chunk e tao esperando
        return("pause")

    try:
        k1 = v0
        l1 = a(t0, s0, v0, chunk_atual, st_star_p, snapshot0, loader, fator_dt)
        l1_2 = l1/2

        k2 = v0 + l1_2
        l2 = a(t0, s0 + k1/2, v0 + l1_2, chunk_atual, st_star_p, snapshot0, loader, fator_dt)
        l2_2 = l2/2

        k3 = v0 + l2_2
        l3 = a(t0, s0 + k2/2, v0 + l2_2, chunk_atual, st_star_p, snapshot0, loader, fator_dt)

        k4 = v0 + l3
        l4 = a(t0, s0 + k3, v0 + l3, chunk_atual, st_star_p, snapshot0, loader, fator_dt)

        t1 = t0 + dt
        s1 = s0 + (1/6)*(k1 + 2*k2 + 2*k3 + k4)
        v1 = v0 + (1/6)*(l1 + 2*l2 + 2*l3 + l4)

        return(t1, v1, s1, l1)

    except Exception as e:
        return("colidiu") #serve para lidar com particulas que colidem entre as etapas do rk4