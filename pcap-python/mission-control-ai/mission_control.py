'''
Mission Control AI - Sistema Inteligente de Monitoramento de Missão Espacial
GS2026.1: Pensamento Computacional e Automação com Python

Requisitos implementados:
1.  Nome da missão
2.  Nome da equipe
3.  Matriz dados_missao com 6 ciclos
4.  Cada ciclo com 5 informações: temperatura, comunicação, bateria, oxigênio, estabilidade
5.  Lista com as áreas monitoradas
6.  10 funções definidas e utilizadas
7.  Estrutura de repetição para percorrer os ciclos
8.  Estruturas condicionais para gerar alertas
9.  Cálculo de risco por ciclo
10. Classificação de cada ciclo
11. Análise da tendência da missão
12. Identificação da área mais afetada
13. Relatório final exibido no terminal

Regras de alerta utilizadas:
  Temperatura: < 18°C → ATENÇÃO | 18–30°C → NORMAL | 30–35°C → ATENÇÃO | > 35°C → CRÍTICO
  Comunicação: < 30% → CRÍTICO | 30–59% → ATENÇÃO | >= 60% → NORMAL
  Bateria:     < 20% → CRÍTICO | 20–49% → ATENÇÃO | >= 50% → NORMAL
  Oxigênio:   < 80% → CRÍTICO | 80–89% → ATENÇÃO | >= 90% → NORMAL
  Estabilidade:< 40% → CRÍTICO | 40–69% → ATENÇÃO | >= 70% → NORMAL

Pontuação de risco: NORMAL = 0 | ATENÇÃO = 1 | CRÍTICO = 2
Classificação do ciclo: 0–2 pts → MISSÃO ESTÁVEL | 3–5 pts → MISSÃO EM ATENÇÃO | 6–10 pts → MISSÃO CRÍTICA
'''

# ============================================================
# FUNÇÕES DE ANÁLISE
# ============================================================

def analisar_temperatura(valor):
    '''Analisa a temperatura e retorna (classificação, pontuação, descrição).'''
    if valor < 18:
        return 'ATENÇÃO', 1, 'Temperatura abaixo do ideal'
    elif valor <= 30:
        return 'NORMAL', 0, 'Temperatura estável'
    elif valor <= 35:
        return 'ATENÇÃO', 1, 'Temperatura elevada'
    else:
        return 'CRÍTICO', 2, 'Risco de superaquecimento'


def analisar_comunicacao(valor):
    '''Analisa a comunicação e retorna (classificação, pontuação, descrição).'''
    if valor < 30:
        return 'CRÍTICO', 2, 'Comunicação com a base em nível crítico'
    elif valor < 60:
        return 'ATENÇÃO', 1, 'Comunicação instável'
    else:
        return 'NORMAL', 0, 'Comunicação estável'


def analisar_bateria(valor):
    '''Analisa a bateria e retorna (classificação, pontuação, descrição).'''
    if valor < 20:
        return 'CRÍTICO', 2, 'Bateria em nível crítico'
    elif valor < 50:
        return 'ATENÇÃO', 1, 'Bateria abaixo do recomendado'
    else:
        return 'NORMAL', 0, 'Energia estável'


def analisar_oxigenio(valor):
    '''Analisa o oxigênio e retorna (classificação, pontuação, descrição).'''
    if valor < 80:
        return 'CRÍTICO', 2, 'Oxigênio em nível crítico'
    elif valor < 90:
        return 'ATENÇÃO', 1, 'Oxigênio abaixo do ideal'
    else:
        return 'NORMAL', 0, 'Oxigênio adequado'


def analisar_estabilidade(valor):
    '''Analisa a estabilidade e retorna (classificação, pontuação, descrição).'''
    if valor < 40:
        return 'CRÍTICO', 2, 'Estabilidade operacional crítica'
    elif valor < 70:
        return 'ATENÇÃO', 1, 'Estabilidade operacional reduzida'
    else:
        return 'NORMAL', 0, 'Estabilidade operacional adequada'


def calcular_risco_ciclo(ciclo):
    '''Calcula a pontuação de risco total de um ciclo e retorna lista de análises e pontuação.'''
    temperatura, comunicacao, bateria, oxigenio, estabilidade = ciclo

    analises = [
        analisar_temperatura(temperatura),
        analisar_comunicacao(comunicacao),
        analisar_bateria(bateria),
        analisar_oxigenio(oxigenio),
        analisar_estabilidade(estabilidade)
    ]

    pontuacao = sum(a[1] for a in analises)
    return analises, pontuacao


def classificar_ciclo(pontuacao):
    '''Classifica o ciclo com base na pontuação de risco.'''
    if pontuacao <= 2:
        return 'MISSÃO ESTÁVEL'
    elif pontuacao <= 5:
        return 'MISSÃO EM ATENÇÃO'
    else:
        return 'MISSÃO CRÍTICA'


def gerar_recomendacao(analises, pontuacao):
    '''Gera recomendação automática com base nas análises do ciclo.'''
    criticos = []
    atencoes = []

    nomes = ['Temperatura', 'Comunicação', 'Bateria', 'Oxigênio', 'Estabilidade']
    recomendacoes_critico = {
        'Temperatura':  'verificar controle térmico da missão',
        'Comunicação':  'tentar restabelecer contato com a base',
        'Bateria':      'ativar modo de economia de energia',
        'Oxigênio':     'acionar protocolo de suporte à vida',
        'Estabilidade': 'reduzir operações não essenciais'
    }

    for i, analise in enumerate(analises):
        if analise[0] == 'CRÍTICO':
            criticos.append(nomes[i])
        elif analise[0] == 'ATENÇÃO':
            atencoes.append(nomes[i])

    if not criticos and not atencoes:
        return 'Manter operação normal e continuar monitoramento.'

    if len(criticos) >= 3:
        return 'Ativar modo de segurança e priorizar suporte à vida, energia e comunicação.'

    partes = []
    for area in criticos:
        partes.append(recomendacoes_critico[area].capitalize())

    if partes:
        return '; '.join(partes) + '.'

    return f'Monitorar sistemas em atenção ({", ".join(atencoes)}) e preparar plano de contingência.'


def analisar_tendencia(riscos):
    '''Compara o risco do primeiro e último ciclo para identificar tendência.'''
    if riscos[-1] > riscos[0]:
        return 'A missão apresentou tendência de piora.'
    elif riscos[-1] < riscos[0]:
        return 'A missão apresentou tendência de melhora.'
    else:
        return 'A missão permaneceu estável em relação ao início.'


def identificar_area_mais_afetada(dados_missao, areas_monitoradas):
    '''Soma a pontuação de risco de cada área ao longo de todos os ciclos.'''
    totais = [0] * len(areas_monitoradas)
    analisadores = [
        analisar_temperatura,
        analisar_comunicacao,
        analisar_bateria,
        analisar_oxigenio,
        analisar_estabilidade
    ]

    for ciclo in dados_missao:
        for j, analisador in enumerate(analisadores):
            _, pontos, _ = analisador(ciclo[j])
            totais[j] += pontos

    indice_max = totais.index(max(totais))
    return areas_monitoradas[indice_max], totais


def gerar_relatorio_final(nome_missao, nome_equipe, dados_missao, areas_monitoradas, riscos_ciclos):
    '''Exibe o relatório final consolidado da missão.'''
    n = len(dados_missao)

    # Médias
    media_temp  = sum(c[0] for c in dados_missao) / n
    media_com   = sum(c[1] for c in dados_missao) / n
    media_bat   = sum(c[2] for c in dados_missao) / n
    media_oxi   = sum(c[3] for c in dados_missao) / n
    media_est   = sum(c[4] for c in dados_missao) / n

    ciclo_critico = riscos_ciclos.index(max(riscos_ciclos)) + 1
    maior_risco   = max(riscos_ciclos)
    risco_medio   = sum(riscos_ciclos) / n
    qtd_criticos  = sum(1 for r in riscos_ciclos if r >= 6)

    tendencia = analisar_tendencia(riscos_ciclos)
    area_afetada, totais_areas = identificar_area_mais_afetada(dados_missao, areas_monitoradas)

    risco_medio_geral = risco_medio
    classificacao_final = classificar_ciclo(round(risco_medio_geral))

    print('============================================================')
    print('RELATÓRIO FINAL DA MISSÃO')
    print('============================================================')
    print(f'Missão: {nome_missao}')
    print(f'Equipe: {nome_equipe}')
    print()
    print(f'Quantidade de ciclos analisados: {n}')
    print()
    print(f'Média de temperatura:   {media_temp:.2f} °C')
    print(f'Média de comunicação:   {media_com:.2f}%')
    print(f'Média de bateria:       {media_bat:.2f}%')
    print(f'Média de oxigênio:      {media_oxi:.2f}%')
    print(f'Média de estabilidade:  {media_est:.2f}%')
    print()
    print(f'Ciclo mais crítico:          Ciclo {ciclo_critico}')
    print(f'Maior pontuação de risco:    {maior_risco}')
    print(f'Risco médio da missão:       {risco_medio:.2f}')
    print(f'Quantidade de ciclos críticos: {qtd_criticos}')
    print()
    print(f'Tendência da missão:')
    print(f'{tendencia}')
    print()
    print('Pontuação acumulada por área:')
    for i, area in enumerate(areas_monitoradas):
        print(f'  {area}: {totais_areas[i]} ponto(s)')
    print()
    print(f'Área mais afetada:')
    print(f'  {area_afetada}')
    print()
    print(f'Classificação final da missão:')
    print(f'  {classificacao_final}')
    print()
    print('Conclusão:')
    if classificacao_final == 'MISSÃO ESTÁVEL':
        print('A missão transcorreu dentro dos parâmetros normais. '
              'Todos os sistemas operaram de forma adequada.')
    elif classificacao_final == 'MISSÃO EM ATENÇÃO':
        print('A missão apresentou instabilidade relevante durante a operação. '
              'Apesar da tentativa de recuperação no último ciclo, ainda existem '
              'sistemas em atenção e a equipe deve manter o plano de contingência ativo.')
    else:
        print('A missão atingiu níveis críticos em múltiplos sistemas. '
              'É necessária intervenção imediata para garantir a segurança da operação '
              'e dos tripulantes.')
    print('============================================================')


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

print('============================================================')
print('MISSION CONTROL AI')
print('============================================================')
print('Olá, seja bem-vindo(a) ao Mission Control AI')
print()

# 1. Nome da missão
nome_missao = input('Digite o nome da missão: ').strip()
while nome_missao == '':
    print('ERRO: O nome da missão não pode ser vazio.')
    nome_missao = input('Digite o nome da missão: ').strip()

# 2. Nome da equipe
nome_equipe = input('Digite o nome da equipe: ').strip()
while nome_equipe == '':
    print('ERRO: O nome da equipe não pode ser vazio.')
    nome_equipe = input('Digite o nome da equipe: ').strip()

print()

# 3. Matriz dados_missao com 6 ciclos
print(f'Informamos a equipe {nome_equipe} que a missão {nome_missao} será relatada')
print('por meio de 6 ciclos de monitoramento:')
print()
print('  Ciclo 1 — início da missão')
print('  Ciclo 2 — estabilização dos sistemas')
print('  Ciclo 3 — queda parcial de comunicação')
print('  Ciclo 4 — alerta de energia')
print('  Ciclo 5 — risco operacional')
print('  Ciclo 6 — tentativa de recuperação')
print()

autorizar_comeco = input('Podemos começar? (S/N)\nR: ').strip().upper()

while autorizar_comeco not in ('S', 'N'):
    print('ERRO: Digite "S" (Sim) para autorizar o início do relatório')
    print('      ou "N" (Não) para encerrar.')
    autorizar_comeco = input('Podemos começar? (S/N)\nR: ').strip().upper()

if autorizar_comeco == 'N':
    print('============================================================')
    print('Obrigado por usar o Mission Control AI!')
    print('Relatório encerrado!')

else:
    # 5. Lista com as áreas monitoradas
    areas_monitoradas = [
        'Temperatura interna',
        'Comunicação com a base',
        'Sistema de energia',
        'Suporte de oxigênio',
        'Estabilidade operacional'
    ]

    dados_missao = []

    print('============================================================')
    print()

    # 4. Coleta de dados — cada ciclo com 5 informações
    for i in range(6):
        print(f'CICLO {i + 1}')
        print('------------------------------------------------------------')

        while True:
            try:
                temperatura  = int(input('Qual é a temperatura do módulo em °C? '))
                comunicacao  = int(input('Qual é a qualidade do sinal de comunicação em %? '))
                bateria      = int(input('Qual é o nível de bateria da missão em %? '))
                oxigenio     = int(input('Qual é o nível de oxigênio disponível, em %? '))
                estabilidade = int(input('Qual é a estabilidade geral dos sistemas, em %? '))
                break
            except ValueError:
                print('ERRO: Digite apenas números inteiros.\n')

        dados_missao.append([temperatura, comunicacao, bateria, oxigenio, estabilidade])
        print()

    # ============================================================
    # CABEÇALHO DO RELATÓRIO
    # ============================================================
    print('============================================================')
    print('MISSION CONTROL AI')
    print('============================================================')
    print(f'Missão: {nome_missao}')
    print(f'Equipe: {nome_equipe}')
    print(f'Quantidade de ciclos analisados: {len(dados_missao)}')
    print('============================================================')

    riscos_ciclos = []
    categorias = ['Temperatura', 'Comunicação', 'Bateria', 'Oxigênio', 'Estabilidade']
    unidades    = ['°C', ' %', ' %', ' %', ' %']

    # 7. Estrutura de repetição para percorrer os ciclos
    for i in range(len(dados_missao)):
        ciclo = dados_missao[i]

        # 9. Cálculo de risco por ciclo + 8. estruturas condicionais nos analisadores
        analises, pontuacao = calcular_risco_ciclo(ciclo)

        # 10. Classificação de cada ciclo
        classificacao = classificar_ciclo(pontuacao)

        recomendacao = gerar_recomendacao(analises, pontuacao)

        riscos_ciclos.append(pontuacao)

        print(f'\nCICLO {i + 1}')
        print('------------------------------------------------------------')

        for j in range(len(ciclo)):
            classe, _, descricao = analises[j]
            valor   = ciclo[j]
            unidade = unidades[j]
            print(f'{categorias[j]}: {valor} {unidade} | {classe} | {descricao}')

        print()
        print(f'Pontuação de risco do ciclo: {pontuacao}')
        print(f'Classificação do ciclo: {classificacao}')
        print(f'Recomendação: {recomendacao}')

    print()

    # 11. Análise da tendência + 12. Área mais afetada + Relatório final
    gerar_relatorio_final(nome_missao, nome_equipe, dados_missao, areas_monitoradas, riscos_ciclos)