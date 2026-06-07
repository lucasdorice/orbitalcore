"""
visualizacao.py — Módulo de Visualização Dual do OrbitalCore

Este módulo oferece um sistema de visualização com suporte duplo a
**matplotlib** e **Plotly**, controlado pela variável global `USAR_PLOTLY`.

- Quando `USAR_PLOTLY = False` (padrão): gráficos estáticos com matplotlib
  em tema escuro "espacial", salvos como PNG.
- Quando `USAR_PLOTLY = True`: gráficos interativos com Plotly em tema
  escuro, salvos como HTML.

Cada função pública verifica `USAR_PLOTLY` e delega para a implementação
interna correspondente (_*_matplotlib ou _*_plotly).

Funções disponíveis:
    - grafico_energia: Geração vs Consumo de Energia ao longo do tempo
    - grafico_bateria: Nível de Bateria (SOC) ao longo do tempo
    - grafico_temperaturas: Temperatura dos módulos ao longo do tempo
    - grafico_balanco_orbital: Balanço energético por órbita
    - grafico_comparativo_terrestre: OrbitalCore vs Data Center Terrestre
    - dashboard_completo: Dashboard consolidado com todos os gráficos

Autor: OrbitalCore Team — FIAP Global Solution
"""

import os
from typing import List, Dict, Any, Optional

from dados_missao import (
    RegistroTelemetria,
    SOC_MIN_SEGURO,
    SOC_CRITICO,
    TEMP_ALERTA_MIN,
    TEMP_ALERTA_MAX,
    TEMP_MIN_OPERACIONAL,
    TEMP_MAX_OPERACIONAL,
)

# ─── Controle de motor gráfico ──────────────────────────────────────────────
USAR_PLOTLY: bool = False  # Trocar para True para usar Plotly

# ─── Paleta de cores tema espacial ──────────────────────────────────────────
COR_VERDE = "#00ff88"
COR_VERMELHO = "#ff4444"
COR_AMARELO = "#ffaa00"
COR_AZUL = "#00aaff"
COR_ROSA = "#ff66ff"
COR_BRANCO = "#ffffff"

CORES_MODULOS = {
    "comunicacao": COR_VERDE,
    "processamento": COR_AZUL,
    "sensores": COR_AMARELO,
    "termico": COR_ROSA,
    "painel": COR_BRANCO,
}


# ═══════════════════════════════════════════════════════════════════════════
#  FUNÇÕES PÚBLICAS (dispatch dual)
# ═══════════════════════════════════════════════════════════════════════════


def grafico_energia(
    registros: List[RegistroTelemetria],
    salvar: bool = False,
    caminho: str = "graficos/",
) -> None:
    """Gráfico de linhas: Geração vs Consumo de Energia ao longo do tempo.

    Exibe a potência gerada e consumida com faixas de fundo indicando
    períodos de sol (amarelo claro) e sombra (azul/cinza escuro).

    Args:
        registros: Lista de registros de telemetria ordenados por tempo.
        salvar: Se True, salva o gráfico em arquivo.
        caminho: Diretório para salvar os arquivos gerados.
    """
    if USAR_PLOTLY:
        _grafico_energia_plotly(registros, salvar, caminho)
    else:
        _grafico_energia_matplotlib(registros, salvar, caminho)


def grafico_bateria(
    registros: List[RegistroTelemetria],
    salvar: bool = False,
    caminho: str = "graficos/",
) -> None:
    """Gráfico de linhas: Nível de Bateria (State of Charge) ao longo do tempo.

    A linha é colorida conforme o status: verde (>20%), amarelo (10–20%),
    vermelho (<10%). Linhas horizontais indicam limiares de segurança e
    crítico. Faixas de fundo para sol/sombra.

    Args:
        registros: Lista de registros de telemetria ordenados por tempo.
        salvar: Se True, salva o gráfico em arquivo.
        caminho: Diretório para salvar os arquivos gerados.
    """
    if USAR_PLOTLY:
        _grafico_bateria_plotly(registros, salvar, caminho)
    else:
        _grafico_bateria_matplotlib(registros, salvar, caminho)


def grafico_temperaturas(
    registros: List[RegistroTelemetria],
    salvar: bool = False,
    caminho: str = "graficos/",
) -> None:
    """Gráfico de múltiplas linhas: Temperatura dos módulos ao longo do tempo.

    Uma linha por módulo (comunicacao, processamento, sensores, termico,
    painel) com faixas horizontais indicando zonas críticas de temperatura.

    Args:
        registros: Lista de registros de telemetria ordenados por tempo.
        salvar: Se True, salva o gráfico em arquivo.
        caminho: Diretório para salvar os arquivos gerados.
    """
    if USAR_PLOTLY:
        _grafico_temperaturas_plotly(registros, salvar, caminho)
    else:
        _grafico_temperaturas_matplotlib(registros, salvar, caminho)


def grafico_balanco_orbital(
    analise_orbitas: List[Dict[str, Any]],
    salvar: bool = False,
    caminho: str = "graficos/",
) -> None:
    """Gráfico de barras: Balanço energético por órbita.

    Barras verdes para superávit e vermelhas para déficit energético em
    cada órbita completada.

    Args:
        analise_orbitas: Lista de dicionários com chaves: orbita,
            energia_gerada_wh, energia_consumida_wh, balanco_wh.
        salvar: Se True, salva o gráfico em arquivo.
        caminho: Diretório para salvar os arquivos gerados.
    """
    if USAR_PLOTLY:
        _grafico_balanco_orbital_plotly(analise_orbitas, salvar, caminho)
    else:
        _grafico_balanco_orbital_matplotlib(analise_orbitas, salvar, caminho)


def grafico_comparativo_terrestre(
    dados_comparacao: Dict[str, Any],
    salvar: bool = False,
    caminho: str = "graficos/",
) -> None:
    """Gráfico de barras agrupadas: OrbitalCore vs Data Center Terrestre.

    Compara métricas de consumo, eficiência energética (PUE), emissão de
    CO₂ e percentual de energia renovável entre as duas plataformas.

    Args:
        dados_comparacao: Dicionário com chaves 'orbital' e 'terrestre',
            cada um contendo: consumo_total_w, consumo_refrigeracao_w,
            pue, co2_kg_por_hora, energia_renovavel_pct.
        salvar: Se True, salva o gráfico em arquivo.
        caminho: Diretório para salvar os arquivos gerados.
    """
    if USAR_PLOTLY:
        _grafico_comparativo_terrestre_plotly(dados_comparacao, salvar, caminho)
    else:
        _grafico_comparativo_terrestre_matplotlib(dados_comparacao, salvar, caminho)


def dashboard_completo(
    registros: List[RegistroTelemetria],
    analise_orbitas: Optional[List[Dict[str, Any]]] = None,
    dados_comparacao: Optional[Dict[str, Any]] = None,
    salvar: bool = False,
    caminho: str = "graficos/",
) -> None:
    """Dashboard consolidado com todos os gráficos da missão.

    Matplotlib: grade 2×3 de subplots com tight_layout.
    Plotly: figura com múltiplas abas interativas.

    Args:
        registros: Lista de registros de telemetria ordenados por tempo.
        analise_orbitas: Dados de balanço por órbita (opcional).
        dados_comparacao: Dados comparativos orbital vs terrestre (opcional).
        salvar: Se True, salva o gráfico em arquivo.
        caminho: Diretório para salvar os arquivos gerados.
    """
    if USAR_PLOTLY:
        _dashboard_completo_plotly(
            registros, analise_orbitas, dados_comparacao, salvar, caminho
        )
    else:
        _dashboard_completo_matplotlib(
            registros, analise_orbitas, dados_comparacao, salvar, caminho
        )


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════


def _garantir_diretorio(caminho: str) -> None:
    """Cria o diretório de saída caso não exista.

    Args:
        caminho: Caminho do diretório a ser garantido.
    """
    os.makedirs(caminho, exist_ok=True)


def _extrair_series(registros: List[RegistroTelemetria]) -> dict:
    """Extrai séries temporais dos registros de telemetria.

    Args:
        registros: Lista de registros de telemetria.

    Returns:
        Dicionário com listas: tempos, geracao, consumo, balanco,
        soc, em_sombra, e temperaturas (dict de listas por módulo).
    """
    tempos = [r.tempo_min for r in registros]
    geracao = [r.potencia_gerada_w for r in registros]
    consumo = [r.consumo_total_w for r in registros]
    balanco = [r.balanco_w for r in registros]
    soc = [r.soc_bateria for r in registros]
    em_sombra = [r.em_sombra for r in registros]

    # Extrair temperaturas por módulo
    modulos_temp: Dict[str, list] = {}
    for reg in registros:
        for nome, temp in reg.temperaturas.items():
            modulos_temp.setdefault(nome, []).append(temp)

    return {
        "tempos": tempos,
        "geracao": geracao,
        "consumo": consumo,
        "balanco": balanco,
        "soc": soc,
        "em_sombra": em_sombra,
        "temperaturas": modulos_temp,
    }


def _adicionar_faixas_sol_sombra_mpl(ax, tempos, em_sombra) -> None:
    """Adiciona faixas de fundo sol/sombra a um eixo matplotlib.

    Args:
        ax: Eixo matplotlib.
        tempos: Lista de tempos em minutos.
        em_sombra: Lista de booleanos indicando sombra.
    """
    inicio_faixa = tempos[0]
    estado_atual = em_sombra[0]

    for i in range(1, len(tempos)):
        if em_sombra[i] != estado_atual or i == len(tempos) - 1:
            fim_faixa = tempos[i]
            cor_faixa = "#1a1a3e" if estado_atual else "#3d3d00"
            alpha_faixa = 0.3 if estado_atual else 0.15
            ax.axvspan(inicio_faixa, fim_faixa, color=cor_faixa, alpha=alpha_faixa)
            inicio_faixa = tempos[i]
            estado_atual = em_sombra[i]


# ═══════════════════════════════════════════════════════════════════════════
#  IMPLEMENTAÇÕES MATPLOTLIB
# ═══════════════════════════════════════════════════════════════════════════


def _grafico_energia_matplotlib(
    registros: List[RegistroTelemetria], salvar: bool, caminho: str
) -> None:
    """Implementação matplotlib do gráfico de energia."""
    import matplotlib.pyplot as plt

    plt.style.use("dark_background")
    dados = _extrair_series(registros)

    fig, ax = plt.subplots(figsize=(14, 8))

    # Faixas sol/sombra
    _adicionar_faixas_sol_sombra_mpl(ax, dados["tempos"], dados["em_sombra"])

    # Linhas de geração e consumo
    ax.plot(
        dados["tempos"], dados["geracao"],
        color=COR_VERDE, linewidth=2, label="Geração (W)", zorder=3,
    )
    ax.plot(
        dados["tempos"], dados["consumo"],
        color=COR_VERMELHO, linewidth=2, label="Consumo (W)", zorder=3,
    )

    # Preenchimento entre curvas
    ax.fill_between(
        dados["tempos"], dados["geracao"], dados["consumo"],
        where=[g >= c for g, c in zip(dados["geracao"], dados["consumo"])],
        color=COR_VERDE, alpha=0.1, interpolate=True,
    )
    ax.fill_between(
        dados["tempos"], dados["geracao"], dados["consumo"],
        where=[g < c for g, c in zip(dados["geracao"], dados["consumo"])],
        color=COR_VERMELHO, alpha=0.1, interpolate=True,
    )

    ax.set_title("Geração vs Consumo de Energia", fontsize=16, fontweight="bold")
    ax.set_xlabel("Tempo (minutos)", fontsize=12)
    ax.set_ylabel("Potência (W)", fontsize=12)
    ax.legend(loc="upper right", fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if salvar:
        _garantir_diretorio(caminho)
        fig.savefig(os.path.join(caminho, "energia.png"), dpi=150, bbox_inches="tight")
    plt.show()


def _grafico_bateria_matplotlib(
    registros: List[RegistroTelemetria], salvar: bool, caminho: str
) -> None:
    """Implementação matplotlib do gráfico de bateria (SOC)."""
    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use("dark_background")
    dados = _extrair_series(registros)
    tempos = dados["tempos"]
    soc = dados["soc"]

    fig, ax = plt.subplots(figsize=(14, 8))

    # Faixas sol/sombra
    _adicionar_faixas_sol_sombra_mpl(ax, tempos, dados["em_sombra"])

    # Plotar segmentos coloridos por status
    for i in range(len(tempos) - 1):
        valor_soc = soc[i]
        if valor_soc >= SOC_MIN_SEGURO:
            cor = COR_VERDE
        elif valor_soc >= SOC_CRITICO:
            cor = COR_AMARELO
        else:
            cor = COR_VERMELHO
        ax.plot(
            [tempos[i], tempos[i + 1]],
            [soc[i] * 100, soc[i + 1] * 100],
            color=cor, linewidth=2.5, zorder=3,
        )

    # Linhas de limiar
    ax.axhline(
        y=SOC_MIN_SEGURO * 100, color=COR_AMARELO, linestyle="--",
        linewidth=1.5, alpha=0.7, label=f"SOC Mín. Seguro ({SOC_MIN_SEGURO:.0%})",
    )
    ax.axhline(
        y=SOC_CRITICO * 100, color=COR_VERMELHO, linestyle="--",
        linewidth=1.5, alpha=0.7, label=f"SOC Crítico ({SOC_CRITICO:.0%})",
    )

    # Faixas de zona de perigo
    ax.axhspan(0, SOC_CRITICO * 100, color=COR_VERMELHO, alpha=0.08)
    ax.axhspan(SOC_CRITICO * 100, SOC_MIN_SEGURO * 100, color=COR_AMARELO, alpha=0.06)

    ax.set_title("Nível de Bateria (State of Charge)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Tempo (minutos)", fontsize=12)
    ax.set_ylabel("SOC (%)", fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if salvar:
        _garantir_diretorio(caminho)
        fig.savefig(os.path.join(caminho, "bateria.png"), dpi=150, bbox_inches="tight")
    plt.show()


def _grafico_temperaturas_matplotlib(
    registros: List[RegistroTelemetria], salvar: bool, caminho: str
) -> None:
    """Implementação matplotlib do gráfico de temperaturas dos módulos."""
    import matplotlib.pyplot as plt

    plt.style.use("dark_background")
    dados = _extrair_series(registros)
    tempos = dados["tempos"]

    fig, ax = plt.subplots(figsize=(14, 8))

    # Faixas de zona crítica de temperatura
    ax.axhspan(TEMP_MAX_OPERACIONAL, TEMP_MAX_OPERACIONAL + 30, color=COR_VERMELHO, alpha=0.08)
    ax.axhspan(TEMP_ALERTA_MAX, TEMP_MAX_OPERACIONAL, color=COR_AMARELO, alpha=0.06)
    ax.axhspan(TEMP_MIN_OPERACIONAL - 30, TEMP_MIN_OPERACIONAL, color=COR_AZUL, alpha=0.08)
    ax.axhspan(TEMP_MIN_OPERACIONAL, TEMP_ALERTA_MIN, color=COR_AZUL, alpha=0.05)

    # Linhas de limiar
    ax.axhline(
        y=TEMP_ALERTA_MAX, color=COR_AMARELO, linestyle="--",
        linewidth=1, alpha=0.5, label=f"Alerta Máx ({TEMP_ALERTA_MAX}°C)",
    )
    ax.axhline(
        y=TEMP_ALERTA_MIN, color=COR_AZUL, linestyle="--",
        linewidth=1, alpha=0.5, label=f"Alerta Mín ({TEMP_ALERTA_MIN}°C)",
    )
    ax.axhline(
        y=TEMP_MAX_OPERACIONAL, color=COR_VERMELHO, linestyle=":",
        linewidth=1, alpha=0.5, label=f"Crítico Máx ({TEMP_MAX_OPERACIONAL}°C)",
    )
    ax.axhline(
        y=TEMP_MIN_OPERACIONAL, color=COR_VERMELHO, linestyle=":",
        linewidth=1, alpha=0.5, label=f"Crítico Mín ({TEMP_MIN_OPERACIONAL}°C)",
    )

    # Linha por módulo
    for nome_modulo, temps in dados["temperaturas"].items():
        cor = CORES_MODULOS.get(nome_modulo, COR_BRANCO)
        ax.plot(
            tempos, temps,
            color=cor, linewidth=2, label=nome_modulo.capitalize(), zorder=3,
        )

    ax.set_title("Temperatura dos Módulos", fontsize=16, fontweight="bold")
    ax.set_xlabel("Tempo (minutos)", fontsize=12)
    ax.set_ylabel("Temperatura (°C)", fontsize=12)
    ax.legend(loc="upper right", fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if salvar:
        _garantir_diretorio(caminho)
        fig.savefig(
            os.path.join(caminho, "temperaturas.png"), dpi=150, bbox_inches="tight"
        )
    plt.show()


def _grafico_balanco_orbital_matplotlib(
    analise_orbitas: List[Dict[str, Any]], salvar: bool, caminho: str
) -> None:
    """Implementação matplotlib do gráfico de balanço energético por órbita."""
    import matplotlib.pyplot as plt

    plt.style.use("dark_background")

    orbitas = [str(o["orbita"]) for o in analise_orbitas]
    balancos = [o["balanco_wh"] for o in analise_orbitas]
    cores = [COR_VERDE if b >= 0 else COR_VERMELHO for b in balancos]

    fig, ax = plt.subplots(figsize=(14, 8))

    barras = ax.bar(orbitas, balancos, color=cores, edgecolor=COR_BRANCO, linewidth=0.5)

    # Rótulos nas barras
    for barra, val in zip(barras, balancos):
        y_pos = barra.get_height() if val >= 0 else barra.get_height()
        va = "bottom" if val >= 0 else "top"
        ax.text(
            barra.get_x() + barra.get_width() / 2, y_pos,
            f"{val:+.1f}", ha="center", va=va, fontsize=9, color=COR_BRANCO,
        )

    ax.axhline(y=0, color=COR_BRANCO, linewidth=0.8, alpha=0.5)
    ax.set_title("Balanço Energético por Órbita", fontsize=16, fontweight="bold")
    ax.set_xlabel("Órbita", fontsize=12)
    ax.set_ylabel("Balanço (Wh)", fontsize=12)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    if salvar:
        _garantir_diretorio(caminho)
        fig.savefig(
            os.path.join(caminho, "balanco_orbital.png"), dpi=150, bbox_inches="tight"
        )
    plt.show()


def _grafico_comparativo_terrestre_matplotlib(
    dados_comparacao: Dict[str, Any], salvar: bool, caminho: str
) -> None:
    """Implementação matplotlib do gráfico comparativo orbital vs terrestre."""
    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use("dark_background")

    categorias = [
        "Consumo Total (W)",
        "Refrigeração (W)",
        "PUE",
        "CO₂ (kg/h)",
        "Energia Renovável (%)",
    ]

    orbital = dados_comparacao["orbital"]
    terrestre = dados_comparacao["terrestre"]

    valores_orbital = [
        orbital["consumo_total_w"],
        orbital["consumo_cooling_w"],
        orbital["pue"],
        orbital["co2_por_hora_kg"],
        orbital["percentual_renovavel"],
    ]
    valores_terrestre = [
        terrestre["consumo_total_w"],
        terrestre["consumo_cooling_w"],
        terrestre["pue"],
        terrestre["co2_por_hora_kg"],
        terrestre["percentual_renovavel"],
    ]

    x = np.arange(len(categorias))
    largura_barra = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))

    barras1 = ax.bar(
        x - largura_barra / 2, valores_orbital, largura_barra,
        label="OrbitalCore", color=COR_AZUL, edgecolor=COR_BRANCO, linewidth=0.5,
    )
    barras2 = ax.bar(
        x + largura_barra / 2, valores_terrestre, largura_barra,
        label="Data Center Terrestre", color=COR_AMARELO,
        edgecolor=COR_BRANCO, linewidth=0.5,
    )

    # Rótulos nas barras
    for barra in barras1:
        ax.text(
            barra.get_x() + barra.get_width() / 2, barra.get_height(),
            f"{barra.get_height():.1f}", ha="center", va="bottom",
            fontsize=8, color=COR_BRANCO,
        )
    for barra in barras2:
        ax.text(
            barra.get_x() + barra.get_width() / 2, barra.get_height(),
            f"{barra.get_height():.1f}", ha="center", va="bottom",
            fontsize=8, color=COR_BRANCO,
        )

    ax.set_title(
        "OrbitalCore vs Data Center Terrestre", fontsize=16, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, fontsize=10, rotation=15, ha="right")
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    if salvar:
        _garantir_diretorio(caminho)
        fig.savefig(
            os.path.join(caminho, "comparativo_terrestre.png"),
            dpi=150, bbox_inches="tight",
        )
    plt.show()


def _dashboard_completo_matplotlib(
    registros: List[RegistroTelemetria],
    analise_orbitas: Optional[List[Dict[str, Any]]],
    dados_comparacao: Optional[Dict[str, Any]],
    salvar: bool,
    caminho: str,
) -> None:
    """Implementação matplotlib do dashboard completo (grade 2×3)."""
    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use("dark_background")
    dados = _extrair_series(registros)
    tempos = dados["tempos"]

    fig, axes = plt.subplots(2, 3, figsize=(20, 14))
    fig.suptitle(
        "OrbitalCore — Dashboard de Monitoramento Energético",
        fontsize=20, fontweight="bold", color=COR_BRANCO, y=0.98,
    )

    # ── [0,0] Energia ────────────────────────────────────────────────────
    ax = axes[0, 0]
    _adicionar_faixas_sol_sombra_mpl(ax, tempos, dados["em_sombra"])
    ax.plot(tempos, dados["geracao"], color=COR_VERDE, linewidth=1.5, label="Geração")
    ax.plot(tempos, dados["consumo"], color=COR_VERMELHO, linewidth=1.5, label="Consumo")
    ax.set_title("Geração vs Consumo", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tempo (min)", fontsize=9)
    ax.set_ylabel("Potência (W)", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── [0,1] Bateria ────────────────────────────────────────────────────
    ax = axes[0, 1]
    _adicionar_faixas_sol_sombra_mpl(ax, tempos, dados["em_sombra"])
    soc_pct = [s * 100 for s in dados["soc"]]
    for i in range(len(tempos) - 1):
        valor = dados["soc"][i]
        if valor >= SOC_MIN_SEGURO:
            cor = COR_VERDE
        elif valor >= SOC_CRITICO:
            cor = COR_AMARELO
        else:
            cor = COR_VERMELHO
        ax.plot(
            [tempos[i], tempos[i + 1]], [soc_pct[i], soc_pct[i + 1]],
            color=cor, linewidth=2, zorder=3,
        )
    ax.axhline(y=SOC_MIN_SEGURO * 100, color=COR_AMARELO, linestyle="--", linewidth=1, alpha=0.6)
    ax.axhline(y=SOC_CRITICO * 100, color=COR_VERMELHO, linestyle="--", linewidth=1, alpha=0.6)
    ax.set_title("Bateria (SOC)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tempo (min)", fontsize=9)
    ax.set_ylabel("SOC (%)", fontsize=9)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)

    # ── [0,2] Temperaturas ───────────────────────────────────────────────
    ax = axes[0, 2]
    ax.axhline(y=TEMP_ALERTA_MAX, color=COR_AMARELO, linestyle="--", linewidth=1, alpha=0.5)
    ax.axhline(y=TEMP_ALERTA_MIN, color=COR_AZUL, linestyle="--", linewidth=1, alpha=0.5)
    for nome_modulo, temps in dados["temperaturas"].items():
        cor = CORES_MODULOS.get(nome_modulo, COR_BRANCO)
        ax.plot(tempos, temps, color=cor, linewidth=1.5, label=nome_modulo.capitalize())
    ax.set_title("Temperaturas", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tempo (min)", fontsize=9)
    ax.set_ylabel("Temp (°C)", fontsize=9)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # ── [1,0] Balanço orbital ────────────────────────────────────────────
    ax = axes[1, 0]
    if analise_orbitas:
        orbitas = [str(o["orbita"]) for o in analise_orbitas]
        balancos = [o["balanco_wh"] for o in analise_orbitas]
        cores = [COR_VERDE if b >= 0 else COR_VERMELHO for b in balancos]
        ax.bar(orbitas, balancos, color=cores, edgecolor=COR_BRANCO, linewidth=0.5)
        ax.axhline(y=0, color=COR_BRANCO, linewidth=0.5, alpha=0.5)
        ax.set_title("Balanço por Órbita", fontsize=12, fontweight="bold")
        ax.set_xlabel("Órbita", fontsize=9)
        ax.set_ylabel("Balanço (Wh)", fontsize=9)
    else:
        ax.text(
            0.5, 0.5, "Dados de órbita\nnão disponíveis",
            ha="center", va="center", fontsize=12, color=COR_AMARELO,
            transform=ax.transAxes,
        )
        ax.set_title("Balanço por Órbita", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # ── [1,1] Comparativo terrestre ──────────────────────────────────────
    ax = axes[1, 1]
    if dados_comparacao:
        categorias = ["Consumo (W)", "Refrig. (W)", "PUE", "CO₂ (kg/h)", "Renov. (%)"]
        orb = dados_comparacao["orbital"]
        ter = dados_comparacao["terrestre"]
        vals_o = [
            orb["consumo_total_w"], orb["consumo_cooling_w"],
            orb["pue"], orb["co2_por_hora_kg"], orb["percentual_renovavel"],
        ]
        vals_t = [
            ter["consumo_total_w"], ter["consumo_cooling_w"],
            ter["pue"], ter["co2_por_hora_kg"], ter["percentual_renovavel"],
        ]
        x = np.arange(len(categorias))
        w = 0.35
        ax.bar(x - w / 2, vals_o, w, label="Orbital", color=COR_AZUL)
        ax.bar(x + w / 2, vals_t, w, label="Terrestre", color=COR_AMARELO)
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, fontsize=7, rotation=20, ha="right")
        ax.legend(fontsize=8)
        ax.set_title("Orbital vs Terrestre", fontsize=12, fontweight="bold")
    else:
        ax.text(
            0.5, 0.5, "Dados comparativos\nnão disponíveis",
            ha="center", va="center", fontsize=12, color=COR_AMARELO,
            transform=ax.transAxes,
        )
        ax.set_title("Orbital vs Terrestre", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # ── [1,2] Balanço energético ao longo do tempo ───────────────────────
    ax = axes[1, 2]
    _adicionar_faixas_sol_sombra_mpl(ax, tempos, dados["em_sombra"])
    ax.plot(tempos, dados["balanco"], color=COR_AMARELO, linewidth=1.5)
    ax.fill_between(
        tempos, dados["balanco"], 0,
        where=[b >= 0 for b in dados["balanco"]],
        color=COR_VERDE, alpha=0.2, interpolate=True,
    )
    ax.fill_between(
        tempos, dados["balanco"], 0,
        where=[b < 0 for b in dados["balanco"]],
        color=COR_VERMELHO, alpha=0.2, interpolate=True,
    )
    ax.axhline(y=0, color=COR_BRANCO, linewidth=0.5, alpha=0.5)
    ax.set_title("Balanço Energético", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tempo (min)", fontsize=9)
    ax.set_ylabel("Balanço (W)", fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if salvar:
        _garantir_diretorio(caminho)
        fig.savefig(
            os.path.join(caminho, "dashboard.png"), dpi=150, bbox_inches="tight"
        )
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════
#  IMPLEMENTAÇÕES PLOTLY
# ═══════════════════════════════════════════════════════════════════════════


def _adicionar_faixas_sol_sombra_plotly(fig, tempos, em_sombra, row=None, col=None):
    """Adiciona faixas de fundo sol/sombra a uma figura Plotly.

    Args:
        fig: Figura Plotly.
        tempos: Lista de tempos em minutos.
        em_sombra: Lista de booleanos indicando sombra.
        row: Linha do subplot (opcional).
        col: Coluna do subplot (opcional).
    """
    import plotly.graph_objects as go

    inicio = tempos[0]
    estado = em_sombra[0]

    for i in range(1, len(tempos)):
        if em_sombra[i] != estado or i == len(tempos) - 1:
            fim = tempos[i]
            cor = "rgba(26,26,62,0.3)" if estado else "rgba(61,61,0,0.15)"
            shape_kwargs = dict(
                type="rect", x0=inicio, x1=fim,
                y0=0, y1=1, yref="paper" if row is None else f"y{'' if row == 1 and col == 1 else ''}",
                fillcolor=cor, line=dict(width=0), layer="below",
            )
            fig.add_vrect(
                x0=inicio, x1=fim, fillcolor=cor,
                line_width=0, layer="below",
                row=row, col=col,
            )
            inicio = tempos[i]
            estado = em_sombra[i]


def _grafico_energia_plotly(
    registros: List[RegistroTelemetria], salvar: bool, caminho: str
) -> None:
    """Implementação Plotly do gráfico de energia."""
    import plotly.graph_objects as go

    dados = _extrair_series(registros)

    fig = go.Figure()

    # Faixas sol/sombra
    _adicionar_faixas_sol_sombra_plotly(fig, dados["tempos"], dados["em_sombra"])

    fig.add_trace(go.Scatter(
        x=dados["tempos"], y=dados["geracao"],
        mode="lines", name="Geração (W)",
        line=dict(color=COR_VERDE, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=dados["tempos"], y=dados["consumo"],
        mode="lines", name="Consumo (W)",
        line=dict(color=COR_VERMELHO, width=2),
    ))

    fig.update_layout(
        title="Geração vs Consumo de Energia",
        xaxis_title="Tempo (minutos)",
        yaxis_title="Potência (W)",
        template="plotly_dark",
        font=dict(size=12),
    )

    if salvar:
        _garantir_diretorio(caminho)
        fig.write_html(os.path.join(caminho, "energia.html"))
    fig.show()


def _grafico_bateria_plotly(
    registros: List[RegistroTelemetria], salvar: bool, caminho: str
) -> None:
    """Implementação Plotly do gráfico de bateria (SOC)."""
    import plotly.graph_objects as go

    dados = _extrair_series(registros)
    soc_pct = [s * 100 for s in dados["soc"]]

    fig = go.Figure()

    # Faixas sol/sombra
    _adicionar_faixas_sol_sombra_plotly(fig, dados["tempos"], dados["em_sombra"])

    # Segmentos coloridos por status
    cores_seg = []
    for s in dados["soc"]:
        if s >= SOC_MIN_SEGURO:
            cores_seg.append(COR_VERDE)
        elif s >= SOC_CRITICO:
            cores_seg.append(COR_AMARELO)
        else:
            cores_seg.append(COR_VERMELHO)

    # Plotly não suporta cor por ponto em linhas diretamente; usamos segmentos
    # agrupados por cor para simplificar
    i = 0
    while i < len(dados["tempos"]):
        cor_atual = cores_seg[i]
        seg_t = [dados["tempos"][i]]
        seg_s = [soc_pct[i]]
        while i + 1 < len(dados["tempos"]) and cores_seg[i + 1] == cor_atual:
            i += 1
            seg_t.append(dados["tempos"][i])
            seg_s.append(soc_pct[i])
        # Incluir próximo ponto para continuidade
        if i + 1 < len(dados["tempos"]):
            seg_t.append(dados["tempos"][i + 1])
            seg_s.append(soc_pct[i + 1])
        fig.add_trace(go.Scatter(
            x=seg_t, y=seg_s,
            mode="lines", line=dict(color=cor_atual, width=2.5),
            showlegend=False,
        ))
        i += 1

    # Linhas de limiar
    fig.add_hline(
        y=SOC_MIN_SEGURO * 100, line_dash="dash",
        line_color=COR_AMARELO, opacity=0.7,
        annotation_text=f"SOC Mín. Seguro ({SOC_MIN_SEGURO:.0%})",
    )
    fig.add_hline(
        y=SOC_CRITICO * 100, line_dash="dash",
        line_color=COR_VERMELHO, opacity=0.7,
        annotation_text=f"SOC Crítico ({SOC_CRITICO:.0%})",
    )

    fig.update_layout(
        title="Nível de Bateria (State of Charge)",
        xaxis_title="Tempo (minutos)",
        yaxis_title="SOC (%)",
        yaxis_range=[0, 105],
        template="plotly_dark",
        font=dict(size=12),
    )

    if salvar:
        _garantir_diretorio(caminho)
        fig.write_html(os.path.join(caminho, "bateria.html"))
    fig.show()


def _grafico_temperaturas_plotly(
    registros: List[RegistroTelemetria], salvar: bool, caminho: str
) -> None:
    """Implementação Plotly do gráfico de temperaturas dos módulos."""
    import plotly.graph_objects as go

    dados = _extrair_series(registros)

    fig = go.Figure()

    # Linhas de limiar
    fig.add_hline(
        y=TEMP_ALERTA_MAX, line_dash="dash", line_color=COR_AMARELO, opacity=0.5,
        annotation_text=f"Alerta Máx ({TEMP_ALERTA_MAX}°C)",
    )
    fig.add_hline(
        y=TEMP_ALERTA_MIN, line_dash="dash", line_color=COR_AZUL, opacity=0.5,
        annotation_text=f"Alerta Mín ({TEMP_ALERTA_MIN}°C)",
    )
    fig.add_hline(
        y=TEMP_MAX_OPERACIONAL, line_dash="dot", line_color=COR_VERMELHO, opacity=0.5,
        annotation_text=f"Crítico Máx ({TEMP_MAX_OPERACIONAL}°C)",
    )
    fig.add_hline(
        y=TEMP_MIN_OPERACIONAL, line_dash="dot", line_color=COR_VERMELHO, opacity=0.5,
        annotation_text=f"Crítico Mín ({TEMP_MIN_OPERACIONAL}°C)",
    )

    for nome_modulo, temps in dados["temperaturas"].items():
        cor = CORES_MODULOS.get(nome_modulo, COR_BRANCO)
        fig.add_trace(go.Scatter(
            x=dados["tempos"], y=temps,
            mode="lines", name=nome_modulo.capitalize(),
            line=dict(color=cor, width=2),
        ))

    fig.update_layout(
        title="Temperatura dos Módulos",
        xaxis_title="Tempo (minutos)",
        yaxis_title="Temperatura (°C)",
        template="plotly_dark",
        font=dict(size=12),
    )

    if salvar:
        _garantir_diretorio(caminho)
        fig.write_html(os.path.join(caminho, "temperaturas.html"))
    fig.show()


def _grafico_balanco_orbital_plotly(
    analise_orbitas: List[Dict[str, Any]], salvar: bool, caminho: str
) -> None:
    """Implementação Plotly do gráfico de balanço energético por órbita."""
    import plotly.graph_objects as go

    orbitas = [str(o["orbita"]) for o in analise_orbitas]
    balancos = [o["balanco_wh"] for o in analise_orbitas]
    cores = [COR_VERDE if b >= 0 else COR_VERMELHO for b in balancos]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=orbitas, y=balancos,
        marker_color=cores,
        marker_line=dict(color=COR_BRANCO, width=0.5),
        text=[f"{b:+.1f}" for b in balancos],
        textposition="outside",
        textfont=dict(color=COR_BRANCO),
    ))

    fig.add_hline(y=0, line_color=COR_BRANCO, line_width=0.8, opacity=0.5)

    fig.update_layout(
        title="Balanço Energético por Órbita",
        xaxis_title="Órbita",
        yaxis_title="Balanço (Wh)",
        template="plotly_dark",
        font=dict(size=12),
    )

    if salvar:
        _garantir_diretorio(caminho)
        fig.write_html(os.path.join(caminho, "balanco_orbital.html"))
    fig.show()


def _grafico_comparativo_terrestre_plotly(
    dados_comparacao: Dict[str, Any], salvar: bool, caminho: str
) -> None:
    """Implementação Plotly do gráfico comparativo orbital vs terrestre."""
    import plotly.graph_objects as go

    categorias = [
        "Consumo Total (W)",
        "Refrigeração (W)",
        "PUE",
        "CO₂ (kg/h)",
        "Energia Renovável (%)",
    ]

    orbital = dados_comparacao["orbital"]
    terrestre = dados_comparacao["terrestre"]

    valores_orbital = [
        orbital["consumo_total_w"], orbital["consumo_cooling_w"],
        orbital["pue"], orbital["co2_por_hora_kg"], orbital["percentual_renovavel"],
    ]
    valores_terrestre = [
        terrestre["consumo_total_w"], terrestre["consumo_cooling_w"],
        terrestre["pue"], terrestre["co2_por_hora_kg"], terrestre["percentual_renovavel"],
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="OrbitalCore", x=categorias, y=valores_orbital,
        marker_color=COR_AZUL,
        text=[f"{v:.1f}" for v in valores_orbital],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Data Center Terrestre", x=categorias, y=valores_terrestre,
        marker_color=COR_AMARELO,
        text=[f"{v:.1f}" for v in valores_terrestre],
        textposition="outside",
    ))

    fig.update_layout(
        title="OrbitalCore vs Data Center Terrestre",
        barmode="group",
        template="plotly_dark",
        font=dict(size=12),
    )

    if salvar:
        _garantir_diretorio(caminho)
        fig.write_html(os.path.join(caminho, "comparativo_terrestre.html"))
    fig.show()


def _dashboard_completo_plotly(
    registros: List[RegistroTelemetria],
    analise_orbitas: Optional[List[Dict[str, Any]]],
    dados_comparacao: Optional[Dict[str, Any]],
    salvar: bool,
    caminho: str,
) -> None:
    """Implementação Plotly do dashboard completo (subplots multi-aba)."""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    dados = _extrair_series(registros)
    tempos = dados["tempos"]

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            "Geração vs Consumo",
            "Bateria (SOC)",
            "Temperaturas",
            "Balanço por Órbita",
            "Orbital vs Terrestre",
            "Balanço Energético",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # ── [1,1] Energia ────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=tempos, y=dados["geracao"], mode="lines",
        name="Geração", line=dict(color=COR_VERDE, width=2),
        legendgroup="energia",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=tempos, y=dados["consumo"], mode="lines",
        name="Consumo", line=dict(color=COR_VERMELHO, width=2),
        legendgroup="energia",
    ), row=1, col=1)

    # ── [1,2] Bateria ────────────────────────────────────────────────────
    soc_pct = [s * 100 for s in dados["soc"]]
    fig.add_trace(go.Scatter(
        x=tempos, y=soc_pct, mode="lines",
        name="SOC (%)", line=dict(color=COR_VERDE, width=2),
        legendgroup="bateria",
    ), row=1, col=2)

    # ── [1,3] Temperaturas ───────────────────────────────────────────────
    for nome_modulo, temps in dados["temperaturas"].items():
        cor = CORES_MODULOS.get(nome_modulo, COR_BRANCO)
        fig.add_trace(go.Scatter(
            x=tempos, y=temps, mode="lines",
            name=nome_modulo.capitalize(),
            line=dict(color=cor, width=1.5),
            legendgroup="temp",
        ), row=1, col=3)

    # ── [2,1] Balanço orbital ────────────────────────────────────────────
    if analise_orbitas:
        orbitas = [str(o["orbita"]) for o in analise_orbitas]
        balancos = [o["balanco_wh"] for o in analise_orbitas]
        cores = [COR_VERDE if b >= 0 else COR_VERMELHO for b in balancos]
        fig.add_trace(go.Bar(
            x=orbitas, y=balancos, marker_color=cores,
            name="Balanço (Wh)", legendgroup="orbita",
        ), row=2, col=1)

    # ── [2,2] Comparativo terrestre ──────────────────────────────────────
    if dados_comparacao:
        cats = ["Consumo", "Refrig.", "PUE", "CO₂", "Renov.%"]
        orb = dados_comparacao["orbital"]
        ter = dados_comparacao["terrestre"]
        vals_o = [
            orb["consumo_total_w"], orb["consumo_cooling_w"],
            orb["pue"], orb["co2_por_hora_kg"], orb["percentual_renovavel"],
        ]
        vals_t = [
            ter["consumo_total_w"], ter["consumo_cooling_w"],
            ter["pue"], ter["co2_por_hora_kg"], ter["percentual_renovavel"],
        ]
        fig.add_trace(go.Bar(
            x=cats, y=vals_o, name="Orbital",
            marker_color=COR_AZUL, legendgroup="comp",
        ), row=2, col=2)
        fig.add_trace(go.Bar(
            x=cats, y=vals_t, name="Terrestre",
            marker_color=COR_AMARELO, legendgroup="comp",
        ), row=2, col=2)

    # ── [2,3] Balanço temporal ───────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=tempos, y=dados["balanco"], mode="lines",
        name="Balanço (W)", line=dict(color=COR_AMARELO, width=1.5),
        legendgroup="balanco_t",
    ), row=2, col=3)

    fig.update_layout(
        title_text="OrbitalCore — Dashboard de Monitoramento Energético",
        template="plotly_dark",
        height=900, width=1400,
        showlegend=True,
        font=dict(size=11),
    )

    if salvar:
        _garantir_diretorio(caminho)
        fig.write_html(os.path.join(caminho, "dashboard.html"))
    fig.show()
