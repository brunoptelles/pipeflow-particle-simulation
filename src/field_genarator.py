import numpy as np
import scipy as sp



def U_wedin(s, m, phi, lambda_):
    return (
        sp.special.jv(m+1, lambda_[m-1]*s)
        + sp.special.jv(m-1, lambda_[m-1]*s)
        - sp.special.jv(m-1, lambda_[m-1]) * s**(m-1)
    ) * np.cos(m*phi)


def V_wedin(s, m, phi, lambda_):
    return (
        sp.special.jv(m+1, lambda_[m-1]*s)
        - sp.special.jv(m-1, lambda_[m-1]*s)
        + sp.special.jv(m-1, lambda_[m-1]) * s**(m-1)
    ) * np.sin(m*phi)


def vx_wedin(s, m, phi, lambda_):
    return U_wedin(s, m, phi, lambda_) * np.cos(phi) - V_wedin(s, m, phi, lambda_) * np.sin(phi)


def vy_wedin(s, m, phi, lambda_):
    return U_wedin(s, m, phi, lambda_) * np.sin(phi) + V_wedin(s, m, phi, lambda_) * np.cos(phi)



#cria um campo 2d com vortices
def criar_meshgrid_wedin(resolucao, m, R=100):

    lambda_ = (5.14, 6.38, 7.59, 8.77, 9.94, 11.09)


    step = np.linspace(-R, R, resolucao)

    U_grid = np.zeros((resolucao, resolucao))
    V_grid = np.zeros((resolucao, resolucao))

    for i in range(resolucao):
        for j in range(resolucao):

            x = step[j]
            y = step[i]

            r_real = np.sqrt(x**2 + y**2)
            phi = np.arctan2(y, x)

            s = r_real / R  

            # fora do tubo
            if s > 1:
                U_grid[i, j] = 0
                V_grid[i, j] = 0
            else:
                U_grid[i, j] = vx_wedin(s, m, phi, lambda_)/R
                V_grid[i, j] = vy_wedin(s, m, phi, lambda_)/R

    #ruido aleatorio para mover as particulas para frente
    Z_grid = 0.1 * np.random.randn(resolucao, resolucao)**2

    return [U_grid, V_grid, Z_grid]


#junta os snaptshot e cria um campo 3d para usar c o codigo
def criar_wedin_3d(m, resolucao=200, nz=400, R=100):

    grid_wedin = criar_meshgrid_wedin(resolucao, m, R)

    ux3d = np.zeros((resolucao, resolucao, nz))
    uy3d = np.zeros((resolucao, resolucao, nz))
    uz3d = np.zeros((resolucao, resolucao, nz))

    for i in range(nz):
        ux3d[:, :, i] = grid_wedin[2]  # componente x (ruído)
        uy3d[:, :, i] = grid_wedin[0]  # componente y
        uz3d[:, :, i] = grid_wedin[1]  # componente z

    return np.array([ux3d, uy3d, uz3d])