import numpy as np

def a(t, s, v, chunk_atual, st_star_p, snapshot0, loader, fator_dt):
    chunk = loader.cache[chunk_atual]
    
    x = snapshot0 + fator_dt*s[0] + t - chunk_atual #mesma coisa do snapshot, passa o x para o espaco dos snapshots, mas dessa vez ajusta
                                                 #para representar indiceis subtraindo o chunk atual para ficar no range (0-999)
    y = s[1]  
    z = s[2]

    x1, x2 = int(x), int(x) + 1
    y1, y2 = int(y), int(y) + 1
    z1, z2 = int(z), int(z) + 1

    x1i, x2i = int(x1), int(x2)
    y1i, y2i = int(y1), int(y2)
    z1i, z2i = int(z1), int(z2) 

    xd = (x-x1)
    yd = (y-y1)
    zd = (z-z1)

    xd_1 = 1-xd
    yd_1 = 1-yd
    zd_1 = 1-zd

    grid_x = chunk[0,:,:,:]
    grid_y = chunk[1,:,:,:]
    grid_z = chunk[2,:,:,:]

    c00_x = grid_x[z1i, y1i, x1i]*xd_1 + grid_x[z2i, y1i, x1i]*xd
    c01_x = grid_x[z1i, y1i, x2i]*xd_1 + grid_x[z2i, y1i, x2i]*xd
    c10_x = grid_x[z1i, y2i, x1i]*xd_1 + grid_x[z2i, y2i, x1i]*xd
    c11_x = grid_x[z1i, y2i, x2i]*xd_1 + grid_x[z2i, y2i, x2i]*xd    
    c0_x = c00_x*yd_1 + c10_x*yd
    c1_x = c01_x*yd_1 + c11_x*yd
    c_x = c0_x*zd_1 + c1_x*zd

    c00_y = grid_y[z1i, y1i, x1i]*xd_1 + grid_y[z2i, y1i, x1i]*xd
    c01_y = grid_y[z1i, y1i, x2i]*xd_1 + grid_y[z2i, y1i, x2i]*xd
    c10_y = grid_y[z1i, y2i, x1i]*xd_1 + grid_y[z2i, y2i, x1i]*xd
    c11_y = grid_y[z1i, y2i, x2i]*xd_1 + grid_y[z2i, y2i, x2i]*xd    
    c0_y = c00_y*yd_1 + c10_y*yd
    c1_y = c01_y*yd_1 + c11_y*yd
    c_y = c0_y*zd_1 + c1_y*zd

    c00_z = grid_z[z1i, y1i, x1i]*xd_1 + grid_z[z2i, y1i, x1i]*xd
    c01_z = grid_z[z1i, y1i, x2i]*xd_1 + grid_z[z2i, y1i, x2i]*xd
    c10_z = grid_z[z1i, y2i, x1i]*xd_1 + grid_z[z2i, y2i, x1i]*xd
    c11_z = grid_z[z1i, y2i, x2i]*xd_1 + grid_z[z2i, y2i, x2i]*xd    
    c0_z = c00_z*yd_1 + c10_z*yd
    c1_z = c01_z*yd_1 + c11_z*yd
    c_z = c0_z*zd_1 + c1_z*zd

    vf = np.array([c_x, c_y, c_z])
    a = (1/st_star_p)*(vf - v)

    return a