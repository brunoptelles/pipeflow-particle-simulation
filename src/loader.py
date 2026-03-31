import numpy as np
import h5py
from src.field_genarator import criar_wedin_3d

class Loader:
    def __init__(self, n_threads, demo, m):
        self.demo = demo
        self.cache = {}
        self.processos = np.zeros(n_threads)

        if demo:
            self.campo_demo = criar_wedin_3d(m)
            

    def load(self, id_chunk):

        path = f'./data/chunks/t={id_chunk}.h5'

        #retorna se o chunk ja foi aberto
        if id_chunk in self.cache:  
            return
        
        if self.demo:
            self.cache[id_chunk] = self.campo_demo
            return

        #abre o chunk caso nao tenha sido aberto ainda       
        with h5py.File(path, 'r') as f:
            chunk = f['chunk'][:]

        self.cache[id_chunk] = chunk

        print(f"Abriu o {id_chunk}")               
        return

    def clear(self):  

        for id_chunk in list(self.cache):            
            if id_chunk not in self.processos:
                del self.cache[id_chunk]
                print(f"Limpou o {id_chunk}")