"""
energia_solar.py — Módulo de análise energética solar do OrbitalCore (SER).

Este módulo implementa as funções de análise aprofundada do sistema de
energia renovável (SER) do data center orbital OrbitalCore. Importa os
dados de simulação de dados_missao.py e fornece:

- Cálculo de irradiância efetiva com lei do cosseno
- Análise de eficiência térmica para diferentes tipos de célula solar
- Balanço energético completo da missão
- Análise por órbita individual
- Métricas de sustentabilidade e pegada de carbono
- Comparação detalhada entre operação orbital e terrestre
- Geração de relatório energético formatado para terminal

Autores: Equipe OrbitalCore — FIAP Global Solution 2026
"""

import math
from typing import Dict, List

from dados_missao import (
    ALTITUDE_ORBITAL_KM,
    CAPACIDADE_BATERIA_WH,
    IRRADIANCIA_SOLAR,
    PERIODO_ORBITAL_MIN,
    TEMP_REF_PAINEL,
    TEMPO_SOL_MIN,
    TEMPO_SOMBRA_MIN,
    RegistroTelemetria,
)

# =============================================================================
# CONSTANTES DO MÓDULO DE ANÁLISE ENERGÉTICA
# =============================================================================

# Eficiências base por tipo de célula solar
_EFICIENCIA_POR_TIPO: Dict[str, float] = {
    "GaAs": 0.30,  # Arseneto de Gálio — tripla junção (padrão espacial)
    "Si": 0.20,  # Silício monocristalino (padrão terrestre)
    "Perovskita": 0.25,  # Perovskita — tecnologia emergente
}

# Coeficientes de temperatura por tipo de célula (%/°C)
_COEF_TEMP_POR_TIPO: Dict[str, float] = {
    "GaAs": -0.003,
    "Si": -0.004,
    "Perovskita": -0.002,
}

# Constantes para comparação terrestre
_CONSUMO_TERRESTRE_W: float = 1000.0  # Consumo base de um DC terrestre (W)
_COOLING_TERRESTRE_W: float = 400.0  # Custo de refrigeração terrestre (W)
_PUE_TERRESTRE: float = 1.6  # PUE típico de data center terrestre
_PUE_ORBITAL: float = 1.05  # PUE do OrbitalCore (sem HVAC)
_CO2_POR_KWH_GRID: float = 0.5  # kg CO₂ por kWh na rede elétrica
_FATOR_ATENUACAO_ATMOSFERA: float = 0.7  # Fator de atenuação atmosférica


# =============================================================================
# FUNÇÕES DE ANÁLISE ENERGÉTICA
# =============================================================================


def calcular_irradiancia_efetiva(
    angulo_incidencia: float,
    em_sombra: bool,
    atmosfera: bool = False,
) -> float:
    """
    Calcula a irradiância solar efetiva sobre o painel.

    Aplica a lei do cosseno ao ângulo de incidência para determinar
    a irradiância efetiva. Quando em sombra, retorna zero.
    Opcionalmente aplica atenuação atmosférica para comparação
    com instalações terrestres.

    Args:
        angulo_incidencia: Ângulo entre a normal do painel e a direção
                           do Sol em graus (0° = perpendicular ao Sol).
        em_sombra: True se o satélite está na sombra da Terra.
        atmosfera: Se True, aplica atenuação atmosférica (~30% de perda)
                   para simular condições terrestres. Padrão: False.

    Returns:
        Irradiância efetiva em W/m².
    """
    # Sem irradiância quando em sombra da Terra
    if em_sombra:
        return 0.0

    # Lei do cosseno: componente perpendicular da irradiância
    angulo_rad = math.radians(angulo_incidencia)
    fator_angular = max(0.0, math.cos(angulo_rad))

    irradiancia = IRRADIANCIA_SOLAR * fator_angular

    # Atenuação atmosférica para comparação com superfície terrestre
    if atmosfera:
        irradiancia *= _FATOR_ATENUACAO_ATMOSFERA

    return round(irradiancia, 2)


def calcular_eficiencia_termica(
    temperatura_painel: float,
    tipo_celula: str = "GaAs",
) -> float:
    """
    Calcula a eficiência do painel solar considerando efeitos térmicos.

    Células solares perdem eficiência com o aumento de temperatura.
    Cada tipo de célula possui um coeficiente de temperatura diferente.
    A eficiência retornada já inclui o efeito térmico.

    Tipos de célula suportados:
        - 'GaAs': Arseneto de Gálio tripla junção (30% base) — padrão espacial
        - 'Si': Silício monocristalino (20% base) — padrão terrestre
        - 'Perovskita': Perovskita (25% base) — tecnologia emergente

    Args:
        temperatura_painel: Temperatura atual do painel em °C.
        tipo_celula: Tipo da célula solar ('GaAs', 'Si' ou 'Perovskita').

    Returns:
        Eficiência efetiva do painel (0.0 a 1.0).

    Raises:
        ValueError: Se o tipo de célula não é suportado.
    """
    if tipo_celula not in _EFICIENCIA_POR_TIPO:
        tipos_validos = ", ".join(_EFICIENCIA_POR_TIPO.keys())
        raise ValueError(
            f"Tipo de célula '{tipo_celula}' não suportado. "
            f"Tipos válidos: {tipos_validos}"
        )

    eficiencia_base = _EFICIENCIA_POR_TIPO[tipo_celula]
    coef_temp = _COEF_TEMP_POR_TIPO[tipo_celula]

    # Efeito da temperatura: eficiência diminui acima da referência
    delta_temp = temperatura_painel - TEMP_REF_PAINEL
    fator_temperatura = 1.0 + coef_temp * delta_temp

    # Garante que a eficiência não fique negativa
    eficiencia_efetiva = eficiencia_base * max(0.0, fator_temperatura)

    return round(eficiencia_efetiva, 4)


def analisar_balanco_energetico(
    registros: List[RegistroTelemetria],
) -> Dict[str, float]:
    """
    Analisa o balanço energético completo a partir dos registros de telemetria.

    Calcula totais de geração e consumo, balanço líquido, superávit
    percentual, autonomia estimada e valores médios/pico.

    Args:
        registros: Lista de registros de telemetria da simulação.

    Returns:
        Dicionário com as métricas de balanço energético:
            - energia_total_gerada_wh: Total gerado em Wh
            - energia_total_consumida_wh: Total consumido em Wh
            - balanco_total_wh: Diferença geração - consumo em Wh
            - superavit_percentual: Superávit como % do consumo
            - autonomia_estimada_h: Horas de autonomia com bateria cheia
            - media_potencia_gerada: Potência média gerada (W)
            - media_consumo: Consumo médio (W)
            - pico_geracao: Potência máxima gerada (W)
            - pico_consumo: Consumo máximo registrado (W)
    """
    if not registros:
        return {
            "energia_total_gerada_wh": 0.0,
            "energia_total_consumida_wh": 0.0,
            "balanco_total_wh": 0.0,
            "superavit_percentual": 0.0,
            "autonomia_estimada_h": 0.0,
            "media_potencia_gerada": 0.0,
            "media_consumo": 0.0,
            "pico_geracao": 0.0,
            "pico_consumo": 0.0,
        }

    # Calcula o intervalo entre registros (em horas)
    if len(registros) > 1:
        intervalo_min = registros[1].tempo_min - registros[0].tempo_min
    else:
        intervalo_min = 5.0  # Padrão de 5 minutos
    intervalo_h = intervalo_min / 60.0

    # Acumula energia (potência × tempo)
    energia_gerada = sum(r.potencia_gerada_w for r in registros) * intervalo_h
    energia_consumida = sum(r.consumo_total_w for r in registros) * intervalo_h
    balanco = energia_gerada - energia_consumida

    # Médias de potência
    media_geracao = sum(r.potencia_gerada_w for r in registros) / len(registros)
    media_consumo = sum(r.consumo_total_w for r in registros) / len(registros)

    # Picos
    pico_geracao = max(r.potencia_gerada_w for r in registros)
    pico_consumo = max(r.consumo_total_w for r in registros)

    # Superávit percentual relativo ao consumo
    superavit_pct = (
        (balanco / energia_consumida * 100.0) if energia_consumida > 0 else 0.0
    )

    # Autonomia estimada: capacidade da bateria / consumo médio
    autonomia_h = CAPACIDADE_BATERIA_WH / media_consumo if media_consumo > 0 else 0.0

    return {
        "energia_total_gerada_wh": round(energia_gerada, 2),
        "energia_total_consumida_wh": round(energia_consumida, 2),
        "balanco_total_wh": round(balanco, 2),
        "superavit_percentual": round(superavit_pct, 2),
        "autonomia_estimada_h": round(autonomia_h, 2),
        "media_potencia_gerada": round(media_geracao, 2),
        "media_consumo": round(media_consumo, 2),
        "pico_geracao": round(pico_geracao, 2),
        "pico_consumo": round(pico_consumo, 2),
    }


def analisar_por_orbita(
    registros: List[RegistroTelemetria],
) -> List[Dict[str, float]]:
    """
    Realiza análise energética por órbita individual.

    Agrupa os registros de telemetria por número de órbita e calcula
    métricas energéticas e térmicas para cada uma.

    Args:
        registros: Lista de registros de telemetria da simulação.

    Returns:
        Lista de dicionários, um por órbita, contendo:
            - orbita: Número da órbita
            - energia_gerada_wh: Energia gerada nesta órbita (Wh)
            - energia_consumida_wh: Energia consumida nesta órbita (Wh)
            - balanco_wh: Balanço energético da órbita (Wh)
            - soc_min: SOC mínimo registrado na órbita
            - soc_max: SOC máximo registrado na órbita
            - temperatura_media: Temperatura média dos módulos (°C)
    """
    if not registros:
        return []

    # Calcula intervalo entre registros (em horas)
    if len(registros) > 1:
        intervalo_min = registros[1].tempo_min - registros[0].tempo_min
    else:
        intervalo_min = 5.0
    intervalo_h = intervalo_min / 60.0

    # Agrupa registros por órbita
    orbitas: Dict[int, List[RegistroTelemetria]] = {}
    for r in registros:
        if r.orbita not in orbitas:
            orbitas[r.orbita] = []
        orbitas[r.orbita].append(r)

    resultados: List[Dict[str, float]] = []

    for num_orbita in sorted(orbitas.keys()):
        regs = orbitas[num_orbita]

        energia_gerada = sum(r.potencia_gerada_w for r in regs) * intervalo_h
        energia_consumida = sum(r.consumo_total_w for r in regs) * intervalo_h
        balanco = energia_gerada - energia_consumida

        soc_min = min(r.soc_bateria for r in regs)
        soc_max = max(r.soc_bateria for r in regs)

        # Temperatura média de todos os módulos em todos os registros
        todas_temps = []
        for r in regs:
            todas_temps.extend(r.temperaturas.values())
        temp_media = sum(todas_temps) / len(todas_temps) if todas_temps else 0.0

        resultados.append(
            {
                "orbita": num_orbita,
                "energia_gerada_wh": round(energia_gerada, 2),
                "energia_consumida_wh": round(energia_consumida, 2),
                "balanco_wh": round(balanco, 2),
                "soc_min": round(soc_min, 4),
                "soc_max": round(soc_max, 4),
                "temperatura_media": round(temp_media, 2),
            }
        )

    return resultados


def calcular_sustentabilidade(
    registros: List[RegistroTelemetria],
) -> Dict[str, float]:
    """
    Calcula métricas de sustentabilidade do sistema OrbitalCore.

    Avalia o desempenho ambiental e energético do data center orbital
    comparado a alternativas terrestres, incluindo emissões de CO₂
    evitadas, percentual de energia renovável e eficiência energética.

    O OrbitalCore opera 100% com energia solar e não necessita de
    refrigeração ativa (HVAC), pois utiliza radiação térmica no vácuo
    espacial para dissipação de calor (0W de consumo para cooling).

    Args:
        registros: Lista de registros de telemetria da simulação.

    Returns:
        Dicionário com métricas de sustentabilidade:
            - fator_sustentabilidade: Razão geração/consumo (>1 = sustentável)
            - co2_evitado_kg: CO₂ equivalente evitado vs DC terrestre
            - autonomia_horas: Horas de autonomia com bateria cheia
            - percentual_renovavel: % de energia de fontes renováveis
            - consumo_cooling_orbital_w: Consumo de refrigeração orbital (0W)
            - consumo_cooling_terrestre_w: Consumo de refrigeração terrestre
            - economia_cooling_percentual: % de economia em refrigeração
            - pue_orbital: PUE do OrbitalCore
            - pue_terrestre: PUE de DC terrestre típico
            - ganho_pue_percentual: Ganho percentual de PUE
    """
    balanco = analisar_balanco_energetico(registros)

    # Fator de sustentabilidade: quanto gera vs quanto consome
    media_geracao = balanco["media_potencia_gerada"]
    media_consumo = balanco["media_consumo"]
    fator_sust = media_geracao / media_consumo if media_consumo > 0 else 0.0

    # Duração total da simulação em horas
    if registros:
        duracao_h = (registros[-1].tempo_min - registros[0].tempo_min) / 60.0
    else:
        duracao_h = 0.0

    # CO₂ evitado: o que um DC terrestre emitiria para fornecer o mesmo consumo
    # OrbitalCore emite 0 kg CO₂ (100% solar)
    energia_consumida_kwh = balanco["energia_total_consumida_wh"] / 1000.0
    co2_evitado = energia_consumida_kwh * _CO2_POR_KWH_GRID

    # Autonomia com bateria cheia
    autonomia_h = CAPACIDADE_BATERIA_WH / media_consumo if media_consumo > 0 else 0.0

    # Economia de cooling: OrbitalCore usa 0W (radiação no vácuo)
    # Data center terrestre usa ~30-40% da energia para refrigeração
    economia_cooling_pct = 100.0  # OrbitalCore economiza 100% em cooling

    # Ganho de PUE
    ganho_pue_pct = (_PUE_TERRESTRE - _PUE_ORBITAL) / _PUE_TERRESTRE * 100.0

    return {
        "fator_sustentabilidade": round(fator_sust, 4),
        "co2_evitado_kg": round(co2_evitado, 4),
        "autonomia_horas": round(autonomia_h, 2),
        "percentual_renovavel": 100.0,
        "consumo_cooling_orbital_w": 0.0,
        "consumo_cooling_terrestre_w": _COOLING_TERRESTRE_W,
        "economia_cooling_percentual": round(economia_cooling_pct, 2),
        "pue_orbital": _PUE_ORBITAL,
        "pue_terrestre": _PUE_TERRESTRE,
        "ganho_pue_percentual": round(ganho_pue_pct, 2),
    }


def comparar_terrestre_vs_orbital(
    registros: List[RegistroTelemetria],
) -> Dict[str, Dict[str, float]]:
    """
    Compara detalhadamente o OrbitalCore com um data center terrestre.

    Realiza uma comparação lado a lado entre o data center orbital
    OrbitalCore e um data center terrestre equivalente em termos de:
    consumo energético, refrigeração, PUE, pegada de carbono e
    percentual de energia renovável.

    Premissas do data center terrestre de referência:
        - Consumo base: 1000W
        - Refrigeração (HVAC): 400W (40% do consumo base)
        - PUE: 1.6 (média do setor)
        - Fonte de energia: rede elétrica (0.5 kg CO₂/kWh)
        - Energia renovável: ~20% (média global do grid)

    Args:
        registros: Lista de registros de telemetria da simulação.

    Returns:
        Dicionário com duas chaves ('orbital' e 'terrestre'), cada uma
        contendo um dicionário de métricas comparáveis:
            - consumo_it_w: Consumo dos equipamentos de TI (W)
            - consumo_cooling_w: Consumo de refrigeração (W)
            - consumo_total_w: Consumo total (W)
            - pue: Power Usage Effectiveness
            - co2_por_hora_kg: Emissão de CO₂ por hora (kg)
            - percentual_renovavel: % de energia renovável
            - custo_energia_relativo: Custo relativo normalizado
    """
    balanco = analisar_balanco_energetico(registros)

    # --- Métricas Orbitais (OrbitalCore) ---
    consumo_it_orbital = balanco["media_consumo"]
    consumo_cooling_orbital = 0.0  # Sem HVAC — radiação no vácuo
    consumo_total_orbital = consumo_it_orbital + consumo_cooling_orbital
    pue_orbital = (
        consumo_total_orbital / consumo_it_orbital
        if consumo_it_orbital > 0
        else _PUE_ORBITAL
    )
    # OrbitalCore é 100% solar, zero emissões diretas
    co2_orbital = 0.0

    # --- Métricas Terrestres (referência) ---
    consumo_it_terrestre = _CONSUMO_TERRESTRE_W
    consumo_cooling_terrestre = _COOLING_TERRESTRE_W
    consumo_total_terrestre = consumo_it_terrestre + consumo_cooling_terrestre
    pue_terrestre = consumo_total_terrestre / consumo_it_terrestre
    # Emissão de CO₂ baseada no grid elétrico
    co2_terrestre = (consumo_total_terrestre / 1000.0) * _CO2_POR_KWH_GRID

    # Custo relativo normalizado (terrestre = 1.0)
    custo_terrestre = 1.0
    custo_orbital = (
        consumo_total_orbital / consumo_total_terrestre
        if consumo_total_terrestre > 0
        else 0.0
    )

    return {
        "orbital": {
            "consumo_it_w": round(consumo_it_orbital, 2),
            "consumo_cooling_w": round(consumo_cooling_orbital, 2),
            "consumo_total_w": round(consumo_total_orbital, 2),
            "pue": round(pue_orbital, 4),
            "co2_por_hora_kg": round(co2_orbital, 4),
            "percentual_renovavel": 100.0,
            "custo_energia_relativo": round(custo_orbital, 4),
        },
        "terrestre": {
            "consumo_it_w": round(consumo_it_terrestre, 2),
            "consumo_cooling_w": round(consumo_cooling_terrestre, 2),
            "consumo_total_w": round(consumo_total_terrestre, 2),
            "pue": round(pue_terrestre, 4),
            "co2_por_hora_kg": round(co2_terrestre, 4),
            "percentual_renovavel": 20.0,
            "custo_energia_relativo": round(custo_terrestre, 4),
        },
    }


def gerar_relatorio_energetico(
    registros: List[RegistroTelemetria],
) -> str:
    """
    Gera um relatório energético completo formatado para terminal.

    O relatório inclui cinco seções principais:
    1. Resumo da Missão — parâmetros gerais e duração
    2. Balanço Energético — geração, consumo e balanço
    3. Sustentabilidade — métricas ambientais e eficiência
    4. Comparação Orbital vs Terrestre — análise lado a lado
    5. Recomendações — sugestões baseadas nos resultados

    Utiliza caracteres de desenho de caixa (box-drawing) para
    formatação visual e códigos ANSI para cores no terminal.

    Args:
        registros: Lista de registros de telemetria da simulação.

    Returns:
        String formatada com o relatório completo pronto para impressão.
    """
    # Códigos ANSI para cores no terminal
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO = "\033[91m"
    CIANO = "\033[96m"
    NEGRITO = "\033[1m"
    RESET = "\033[0m"

    # Obtém todas as análises
    balanco = analisar_balanco_energetico(registros)
    orbitas = analisar_por_orbita(registros)
    sustentabilidade = calcular_sustentabilidade(registros)
    comparacao = comparar_terrestre_vs_orbital(registros)

    # Caracteres de desenho de caixa
    H = "═"
    V = "║"
    TL = "╔"
    TR = "╗"
    BL = "╚"
    BR = "╝"
    ML = "╠"
    MR = "╣"

    largura = 64
    linha_dupla = H * largura

    linhas: List[str] = []

    def titulo_secao(titulo: str) -> None:
        """Adiciona um título de seção ao relatório."""
        linhas.append("")
        linhas.append(f"{TL}{linha_dupla}{TR}")
        linhas.append(f"{V} {NEGRITO}{CIANO}{titulo:<{largura - 1}}{RESET}{V}")
        linhas.append(f"{BL}{linha_dupla}{BR}")

    def linha_dado(rotulo: str, valor: str) -> None:
        """Adiciona uma linha de dado formatada."""
        conteudo = f"  {rotulo:<36} {valor}"
        linhas.append(conteudo)

    def separador() -> None:
        """Adiciona uma linha separadora simples."""
        linhas.append(f"  {'─' * (largura - 2)}")

    # =========================================================================
    # CABEÇALHO
    # =========================================================================
    linhas.append("")
    linhas.append(f"{NEGRITO}{CIANO}")
    linhas.append(f"  {'=' * 60}")
    linhas.append("   ☀️  ORBITALCORE — RELATÓRIO ENERGÉTICO SER")
    linhas.append(
        "   🛰️  Sistema de Energia Renovável — LEO " + str(ALTITUDE_ORBITAL_KM) + "km"
    )
    linhas.append(f"  {'=' * 60}")
    linhas.append(f"{RESET}")

    # =========================================================================
    # SEÇÃO 1: RESUMO DA MISSÃO
    # =========================================================================
    titulo_secao("1. RESUMO DA MISSÃO")

    if registros:
        duracao_total_min = registros[-1].tempo_min - registros[0].tempo_min
        num_orbitas_real = registros[-1].orbita
        num_registros = len(registros)
        total_alertas = sum(len(r.alertas) for r in registros)
    else:
        duracao_total_min = 0.0
        num_orbitas_real = 0
        num_registros = 0
        total_alertas = 0

    linha_dado("Altitude orbital:", f"{ALTITUDE_ORBITAL_KM} km (LEO)")
    linha_dado("Período orbital:", f"{PERIODO_ORBITAL_MIN} min")
    linha_dado(
        "Tempo no sol:",
        f"{TEMPO_SOL_MIN} min ({TEMPO_SOL_MIN / PERIODO_ORBITAL_MIN * 100:.0f}%)",
    )
    linha_dado(
        "Tempo na sombra:",
        f"{TEMPO_SOMBRA_MIN} min ({TEMPO_SOMBRA_MIN / PERIODO_ORBITAL_MIN * 100:.0f}%)",
    )
    separador()
    linha_dado("Órbitas simuladas:", f"{num_orbitas_real}")
    linha_dado(
        "Duração total:",
        f"{duracao_total_min:.0f} min ({duracao_total_min / 60:.1f} h)",
    )
    linha_dado("Registros de telemetria:", f"{num_registros}")
    linha_dado("Alertas gerados:", f"{total_alertas}")

    # =========================================================================
    # SEÇÃO 2: BALANÇO ENERGÉTICO
    # =========================================================================
    titulo_secao("2. BALANÇO ENERGÉTICO")

    cor_balanco = VERDE if balanco["balanco_total_wh"] >= 0 else VERMELHO
    cor_superavit = VERDE if balanco["superavit_percentual"] >= 0 else VERMELHO

    linha_dado(
        "Energia total gerada:",
        f"{VERDE}{balanco['energia_total_gerada_wh']:.1f} Wh{RESET}",
    )
    linha_dado(
        "Energia total consumida:",
        f"{AMARELO}{balanco['energia_total_consumida_wh']:.1f} Wh{RESET}",
    )
    linha_dado(
        "Balanço líquido:",
        f"{cor_balanco}{balanco['balanco_total_wh']:+.1f} Wh{RESET}",
    )
    linha_dado(
        "Superávit:",
        f"{cor_superavit}{balanco['superavit_percentual']:+.1f}%{RESET}",
    )
    separador()
    linha_dado(
        "Potência média gerada:",
        f"{balanco['media_potencia_gerada']:.1f} W",
    )
    linha_dado(
        "Consumo médio:",
        f"{balanco['media_consumo']:.1f} W",
    )
    linha_dado(
        "Pico de geração:",
        f"{balanco['pico_geracao']:.1f} W",
    )
    linha_dado(
        "Pico de consumo:",
        f"{balanco['pico_consumo']:.1f} W",
    )
    linha_dado(
        "Autonomia estimada (bateria):",
        f"{balanco['autonomia_estimada_h']:.1f} h",
    )

    # =========================================================================
    # SEÇÃO 3: ANÁLISE POR ÓRBITA
    # =========================================================================
    titulo_secao("3. ANÁLISE POR ÓRBITA")

    linhas.append(
        f"  {'Órbita':>6} │ {'Gerado(Wh)':>10} │ {'Consumo(Wh)':>11} │ "
        f"{'Balanço(Wh)':>11} │ {'SOC Min':>7} │ {'SOC Max':>7}"
    )
    linhas.append(
        f"  {'─' * 6}─┼─{'─' * 10}─┼─{'─' * 11}─┼─{'─' * 11}─┼─{'─' * 7}─┼─{'─' * 7}"
    )

    for orb in orbitas:
        cor = VERDE if orb["balanco_wh"] >= 0 else VERMELHO
        linhas.append(
            f"  {orb['orbita']:>6} │ {orb['energia_gerada_wh']:>10.1f} │ "
            f"{orb['energia_consumida_wh']:>11.1f} │ "
            f"{cor}{orb['balanco_wh']:>+11.1f}{RESET} │ "
            f"{orb['soc_min'] * 100:>6.1f}% │ {orb['soc_max'] * 100:>6.1f}%"
        )

    # =========================================================================
    # SEÇÃO 4: SUSTENTABILIDADE
    # =========================================================================
    titulo_secao("4. SUSTENTABILIDADE")

    sust = sustentabilidade
    cor_fator = VERDE if sust["fator_sustentabilidade"] >= 1.0 else VERMELHO

    linha_dado(
        "Fator de sustentabilidade:",
        f"{cor_fator}{sust['fator_sustentabilidade']:.2f}x{RESET}",
    )
    linha_dado(
        "Energia renovável:",
        f"{VERDE}{sust['percentual_renovavel']:.0f}%{RESET} (100% solar)",
    )
    linha_dado(
        "CO₂ evitado vs terrestre:",
        f"{VERDE}{sust['co2_evitado_kg']:.3f} kg{RESET}",
    )
    separador()
    linha_dado(
        "Cooling orbital (OrbitalCore):",
        f"{VERDE}{sust['consumo_cooling_orbital_w']:.0f} W{RESET} (radiação no vácuo)",
    )
    linha_dado(
        "Cooling terrestre (referência):",
        f"{VERMELHO}{sust['consumo_cooling_terrestre_w']:.0f} W{RESET} (HVAC)",
    )
    linha_dado(
        "Economia em refrigeração:",
        f"{VERDE}{sust['economia_cooling_percentual']:.0f}%{RESET}",
    )
    separador()
    linha_dado(
        "PUE OrbitalCore:",
        f"{VERDE}{sust['pue_orbital']:.2f}{RESET}",
    )
    linha_dado(
        "PUE terrestre (referência):",
        f"{AMARELO}{sust['pue_terrestre']:.2f}{RESET}",
    )
    linha_dado(
        "Ganho de eficiência PUE:",
        f"{VERDE}{sust['ganho_pue_percentual']:.1f}%{RESET}",
    )

    # =========================================================================
    # SEÇÃO 5: COMPARAÇÃO ORBITAL vs TERRESTRE
    # =========================================================================
    titulo_secao("5. COMPARAÇÃO: ORBITAL vs TERRESTRE")

    orb = comparacao["orbital"]
    ter = comparacao["terrestre"]

    linhas.append(f"  {'Métrica':<30} │ {'OrbitalCore':>14} │ {'Terrestre':>14}")
    linhas.append(f"  {'─' * 30}─┼─{'─' * 14}─┼─{'─' * 14}")

    linhas.append(
        f"  {'Consumo TI (W)':<30} │ "
        f"{orb['consumo_it_w']:>14.1f} │ {ter['consumo_it_w']:>14.1f}"
    )
    linhas.append(
        f"  {'Cooling (W)':<30} │ "
        f"{VERDE}{orb['consumo_cooling_w']:>14.1f}{RESET} │ "
        f"{VERMELHO}{ter['consumo_cooling_w']:>14.1f}{RESET}"
    )
    linhas.append(
        f"  {'Consumo Total (W)':<30} │ "
        f"{orb['consumo_total_w']:>14.1f} │ {ter['consumo_total_w']:>14.1f}"
    )
    linhas.append(
        f"  {'PUE':<30} │ "
        f"{VERDE}{orb['pue']:>14.2f}{RESET} │ "
        f"{AMARELO}{ter['pue']:>14.2f}{RESET}"
    )
    linhas.append(
        f"  {'CO₂/hora (kg)':<30} │ "
        f"{VERDE}{orb['co2_por_hora_kg']:>14.4f}{RESET} │ "
        f"{VERMELHO}{ter['co2_por_hora_kg']:>14.4f}{RESET}"
    )
    linhas.append(
        f"  {'Energia Renovável (%)':<30} │ "
        f"{VERDE}{orb['percentual_renovavel']:>13.0f}%{RESET} │ "
        f"{AMARELO}{ter['percentual_renovavel']:>13.0f}%{RESET}"
    )
    linhas.append(
        f"  {'Custo Relativo':<30} │ "
        f"{orb['custo_energia_relativo']:>14.4f} │ "
        f"{ter['custo_energia_relativo']:>14.4f}"
    )

    # =========================================================================
    # SEÇÃO 6: RECOMENDAÇÕES
    # =========================================================================
    titulo_secao("6. RECOMENDAÇÕES")

    recomendacoes: List[str] = []

    # Recomendações baseadas nos dados
    fator = sust["fator_sustentabilidade"]
    if fator >= 1.0:
        recomendacoes.append(
            f"  {VERDE}✅ Sistema energeticamente sustentável "
            f"(fator {fator:.2f}x).{RESET}"
        )
    else:
        recomendacoes.append(
            f"  {VERMELHO}❌ Sistema com déficit energético "
            f"(fator {fator:.2f}x). Considerar aumento da "
            f"área de painéis ou redução de consumo.{RESET}"
        )

    if balanco["autonomia_estimada_h"] < 2.0:
        recomendacoes.append(
            f"  {AMARELO}⚠️ Autonomia baixa ({balanco['autonomia_estimada_h']:.1f}h). "
            f"Considerar aumento da capacidade da bateria.{RESET}"
        )
    else:
        recomendacoes.append(
            f"  {VERDE}✅ Autonomia adequada "
            f"({balanco['autonomia_estimada_h']:.1f}h).{RESET}"
        )

    # Verifica se houve alertas de temperatura
    alertas_temp = []
    for r in registros:
        for a in r.alertas:
            if a.tipo.value in ("temperatura_alta", "temperatura_baixa"):
                alertas_temp.append(a)

    if alertas_temp:
        recomendacoes.append(
            f"  {AMARELO}⚠️ {len(alertas_temp)} alertas de temperatura "
            f"registrados. Revisar sistema de controle térmico.{RESET}"
        )
    else:
        recomendacoes.append(
            f"  {VERDE}✅ Nenhum alerta de temperatura. "
            f"Controle térmico operando nominalmente.{RESET}"
        )

    # Verifica alertas de bateria
    alertas_bateria = []
    for r in registros:
        for a in r.alertas:
            if a.tipo.value in ("bateria_baixa", "bateria_critica"):
                alertas_bateria.append(a)

    if alertas_bateria:
        recomendacoes.append(
            f"  {VERMELHO}⚠️ {len(alertas_bateria)} alertas de bateria. "
            f"Otimizar gestão de carga ou aumentar capacidade.{RESET}"
        )
    else:
        recomendacoes.append(
            f"  {VERDE}✅ Bateria estável durante toda a missão.{RESET}"
        )

    # PUE excelente
    recomendacoes.append(
        f"  {VERDE}🌍 PUE de {sust['pue_orbital']:.2f} — "
        f"{sust['ganho_pue_percentual']:.0f}% mais eficiente "
        f"que data centers terrestres (PUE {sust['pue_terrestre']:.1f}).{RESET}"
    )

    # Emissões zero
    recomendacoes.append(
        f"  {VERDE}🌱 Zero emissões diretas de CO₂ — 100% energia solar.{RESET}"
    )

    for rec in recomendacoes:
        linhas.append(rec)

    # =========================================================================
    # RODAPÉ
    # =========================================================================
    linhas.append("")
    linhas.append(f"  {'─' * 60}")
    linhas.append(f"  {CIANO}Relatório gerado pelo módulo SER — OrbitalCore{RESET}")
    linhas.append(f"  {CIANO}FIAP Global Solution 2026{RESET}")
    linhas.append(f"  {'─' * 60}")
    linhas.append("")

    return "\n".join(linhas)


# =============================================================================
# EXECUÇÃO DIRETA (para testes e demonstração)
# =============================================================================

if __name__ == "__main__":
    from dados_missao import simular_missao

    print("Executando simulação da missão OrbitalCore...")
    print()

    # Simula 10 órbitas
    registros = simular_missao(num_orbitas=10, intervalo_min=5.0, seed=42)

    # Gera e exibe o relatório completo
    relatorio = gerar_relatorio_energetico(registros)
    print(relatorio)

    # Demonstração das funções individuais
    print("\n--- Demonstração de Funções Individuais ---\n")

    # Irradiância efetiva
    irr_orbital = calcular_irradiancia_efetiva(0.0, False, atmosfera=False)
    irr_terrestre = calcular_irradiancia_efetiva(0.0, False, atmosfera=True)
    print(f"Irradiância orbital (0°): {irr_orbital:.1f} W/m²")
    print(f"Irradiância terrestre (0°): {irr_terrestre:.1f} W/m²")
    print(f"Perda atmosférica: {(1 - irr_terrestre / irr_orbital) * 100:.0f}%")
    print()

    # Eficiência térmica
    for tipo in ["GaAs", "Si", "Perovskita"]:
        ef_25 = calcular_eficiencia_termica(25.0, tipo)
        ef_65 = calcular_eficiencia_termica(65.0, tipo)
        print(
            f"Eficiência {tipo} a 25°C: {ef_25 * 100:.1f}%  |  a 65°C: {ef_65 * 100:.1f}%"
        )
