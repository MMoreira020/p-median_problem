"""
Heurística Construtiva Greedy Addition para o Problema P-Median
================================================================
Disciplina: SIN-492 - Inteligência Computacional
Universidade Federal de Viçosa - Campus Rio Paranaíba

Referência:
    Resende, M.G.C. and Werneck, R.F. (2004).
    A Hybrid Heuristic for the p-Median Problem.
    Journal of Heuristics, 10(1), 59-88.

Datasets:
    OR-Library - J.E. Beasley (1985)
    http://people.brunel.ac.uk/~mastjjb/jeb/orlib/pmedinfo.html

Aluno(a): <seu nome>
Matrícula: <sua matrícula>
"""

import os
import time
import math


# =============================================================================
# LEITURA DA INSTÂNCIA
# =============================================================================

def ler_instancia(caminho_arquivo):
    """
    Lê uma instância do p-median no formato da OR-Library.

    Formato do arquivo:
        Linha 1: n  m  p
            n = número de vértices
            m = número de arestas
            p = número de facilidades a abrir
        Linhas seguintes: i  j  custo
            i, j = vértices da aresta (indexados a partir de 1)
            custo = custo da aresta

    Parâmetros:
        caminho_arquivo (str): caminho para o arquivo da instância

    Retorna:
        n (int): número de vértices
        p (int): número de facilidades
        dist (list[list[float]]): matriz de adjacência n×n com custos diretos
    """
    with open(caminho_arquivo, 'r') as f:
        tokens = f.read().split()

    idx = 0
    n = int(tokens[idx]); idx += 1
    m = int(tokens[idx]); idx += 1
    p = int(tokens[idx]); idx += 1

    # Inicializa matriz de distâncias com infinito
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]

    # Distância de cada vértice para si mesmo é 0
    for i in range(n):
        dist[i][i] = 0.0

    # Lê cada aresta e preenche a matriz (grafo não-direcionado)
    for _ in range(m):
        i = int(tokens[idx]) - 1; idx += 1   # converte para índice 0-based
        j = int(tokens[idx]) - 1; idx += 1
        custo = float(tokens[idx]); idx += 1

        # Mantém apenas o menor custo em caso de arestas múltiplas
        if custo < dist[i][j]:
            dist[i][j] = custo
            dist[j][i] = custo

    return n, p, dist


# =============================================================================
# FLOYD-WARSHALL
# =============================================================================

def floyd_warshall(dist, n):
    """
    Aplica o algoritmo de Floyd-Warshall para calcular as menores distâncias
    entre todos os pares de vértices do grafo.

    Necessário porque a OR-Library fornece apenas arestas diretas (grafo
    esparso), e a heurística precisa da distância entre qualquer par de nós.

    Parâmetros:
        dist (list[list[float]]): matriz de adjacência n×n (modificada in-place)
        n (int): número de vértices

    Complexidade: O(n³)
    """
    for k in range(n):
        for i in range(n):
            if dist[i][k] == math.inf:
                continue                      # poda: sem caminho i→k
            for j in range(n):
                novo = dist[i][k] + dist[k][j]
                if novo < dist[i][j]:
                    dist[i][j] = novo


# =============================================================================
# CÁLCULO DO CUSTO DE UMA SOLUÇÃO
# =============================================================================

def calcular_custo(dist, n, facilidades):
    """
    Calcula o custo total de uma solução do p-median.

    O custo é a soma, para cada vértice u, da distância de u até
    a facilidade mais próxima pertencente ao conjunto 'facilidades'.

    Parâmetros:
        dist (list[list[float]]): matriz de distâncias completa (pós Floyd)
        n (int): número de vértices
        facilidades (set): conjunto de vértices onde facilidades estão abertas

    Retorna:
        custo_total (float): soma das distâncias mínimas de todos os vértices
    """
    custo_total = 0.0
    for u in range(n):
        dist_min = min(dist[u][f] for f in facilidades)
        custo_total += dist_min
    return custo_total


# =============================================================================
# HEURÍSTICA CONSTRUTIVA — GREEDY ADDITION (MYOPIC)
# =============================================================================

def greedy_addition(dist, n, p):
    """
    Heurística construtiva Greedy Addition (também chamada de Myopic) para
    o Problema P-Median.

    Ideia:
        Partindo de um conjunto vazio de facilidades, em cada iteração
        adiciona a facilidade que mais reduz o custo total da solução,
        até que p facilidades sejam abertas.

    Estruturas de dados:
        - facilidades (set): conjunto atual de facilidades abertas
        - dist_min_cliente (list): dist_min_cliente[u] = distância mínima
          do vértice u à facilidade mais próxima no conjunto atual.
          Mantida incrementalmente para evitar recalcular do zero a cada passo.

    Parâmetros:
        dist (list[list[float]]): matriz de distâncias completa (pós Floyd)
        n (int): número de vértices
        p (int): número de facilidades a abrir

    Retorna:
        facilidades (set): conjunto com os p vértices escolhidos como facilidades
        custo_final (float): custo total da solução encontrada

    Complexidade: O(p × n²)
        - p iterações externas
        - n candidatos avaliados por iteração
        - n vértices para calcular o ganho de cada candidato
    """
    facilidades = set()

    # dist_min_cliente[u] = menor distância de u a alguma facilidade aberta.
    # Antes de abrir qualquer facilidade, todas as distâncias são infinito.
    dist_min_cliente = [math.inf] * n

    custo_atual = math.inf

    for _ in range(p):
        melhor_v = -1
        melhor_ganho = -math.inf

        # Avalia cada vértice candidato a ser a próxima facilidade
        for v in range(n):
            if v in facilidades:
                continue

            # Calcula o novo custo se v fosse adicionado ao conjunto
            ganho = 0.0
            for u in range(n):
                nova_dist = min(dist_min_cliente[u], dist[u][v])
                ganho += dist_min_cliente[u] - nova_dist

            if ganho > melhor_ganho:
                melhor_ganho = ganho
                melhor_v = v

        # Adiciona a melhor facilidade encontrada
        facilidades.add(melhor_v)

        # Atualiza dist_min_cliente incrementalmente com a nova facilidade
        for u in range(n):
            if dist[u][melhor_v] < dist_min_cliente[u]:
                dist_min_cliente[u] = dist[u][melhor_v]

        custo_atual -= melhor_ganho

    # Recalcula o custo final com precisão (evita acúmulo de erro numérico)
    custo_final = sum(dist_min_cliente)

    return facilidades, custo_final


# =============================================================================
# LEITURA DOS VALORES ÓTIMOS
# =============================================================================

def ler_otimos(caminho_pmedopt):
    """
    Lê o arquivo pmedopt.txt com os valores ótimos de cada instância.

    Formato do arquivo:
        Data file   Optimal solution value   <- cabeçalho (ignorado)
        pmed1       5819
        pmed2       4093
        ...

    Parâmetros:
        caminho_pmedopt (str): caminho para o arquivo pmedopt.txt

    Retorna:
        otimos (dict): {índice_instancia: valor_ótimo}
    """
    otimos = {}
    with open(caminho_pmedopt, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('Data'):
                continue                          # ignora cabeçalho e vazios
            partes = linha.split()
            if len(partes) >= 2:
                nome = partes[0]                  # ex: "pmed1"
                valor = float(partes[1])
                idx = int(nome.replace('pmed', ''))  # extrai o número
                otimos[idx] = valor
    return otimos


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

def main():
    """
    Executa a heurística Greedy Addition em todas as instâncias pmed1 a pmed40
    e exibe uma tabela comparativa com os valores ótimos da OR-Library.
    """

    # --- Configurações de caminho ---
    # Ajuste este caminho para a pasta onde estão seus arquivos pmedX.txt
    pasta_instancias = "dataset"
    arquivo_otimos   = os.path.join(pasta_instancias, "pmedopt.txt")

    # Lê os valores ótimos
    otimos = ler_otimos(arquivo_otimos)

    # Cabeçalho da tabela de resultados
    print("=" * 75)
    print(f"{'Inst':>5} {'n':>5} {'p':>5} {'Ótimo':>10} "
          f"{'Heurística':>12} {'Gap (%)':>9} {'Tempo (s)':>10}")
    print("=" * 75)

    soma_gap  = 0.0
    num_inst  = 0

    for i in range(1, 41):
        arquivo = os.path.join(pasta_instancias, f"pmed{i}.txt")

        if not os.path.exists(arquivo):
            print(f"  Arquivo {arquivo} não encontrado. Pulando.")
            continue

        # --- Leitura e pré-processamento ---
        n, p, dist = ler_instancia(arquivo)
        floyd_warshall(dist, n)

        # --- Execução da heurística ---
        t0 = time.time()
        _, custo = greedy_addition(dist, n, p)
        tempo = time.time() - t0

        # --- Cálculo do gap ---
        otimo = otimos.get(i, None)
        if otimo is not None and otimo > 0:
            gap = 100.0 * (custo - otimo) / otimo
        else:
            gap = float('nan')

        soma_gap += gap
        num_inst  += 1

        print(f"  {i:>3}  {n:>5}  {p:>5}  {otimo:>10.1f}  "
              f"{custo:>12.1f}  {gap:>8.2f}%  {tempo:>9.3f}s")

    # --- Resumo ---
    print("=" * 75)
    if num_inst > 0:
        print(f"  Gap médio: {soma_gap / num_inst:.2f}%  "
              f"({num_inst} instâncias)")
    print("=" * 75)


if __name__ == "__main__":
    main()
