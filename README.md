# SIMULADOR DE PARTÍCULAS INERCIAIS
Projeto de simulação desenvolvido para o estudo da trajetória de partículas com diferentes números de Stokes submetido a escoamento em tubos (Pipe Flow).

O código foi desenvolvido para operar em ambientes cluster com múltiplos processadores,  também necessita de uma base de dados auxiliar representando
o campo vetorial do escoamento. Com isso em mente, uma versão de demonstração foi incluída no projeto, utilizando uma solução analítica das equações de Navier-Stokes.

A demo utiliza um escoamento em regime permanente e inclui uma visualização simples da trajetória das partículas. 

## Como Rodar
### Clone o repositório:

```bash
git clone https://github.com/seu-user/pipeflow-particle-simulation.git
cd pipeflow-particle-simulation
```
### Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # linux/mac
venv\Scripts\activate     # windows
pip install -r requirements.txt
```
### Execute a main:
```bash
python main.py
```

### Base de dados:
O código utiliza chunks com dados de um campo vetorial (escoamento) para simular as partículas.

Os chunks têm o formato `(3, 300, 300, 1010)`  
- 3 → componentes da velocidade  
- x, y → seção transversal do tubo  
- z → direção axial (comprimento)

Os dados devem ser fornecidos em formato `.h5`.

## Referências

### Solução analítica das equações de Navier-Stokes:

WEDIN, H. *Exact coherent structures in pipe flow: travelling wave solutions*. Cambridge University Press, (2004) 
