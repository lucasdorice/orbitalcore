"""
OrbitalCore - Sistema Principal de Monitoramento Energético Espacial
=====================================================================
Módulo principal que integra todos os subsistemas para monitoramento
inteligente de energia em uma missão espacial experimental.

Projeto: OrbitalCore - Global Solution FIAP 2026
Disciplina: SERS - Soluções em Energias Renováveis e Sustentáveis
"""

import os
import time

import visualizacao

# Importações dos módulos do projeto
from dados_missao import (
    ALTITUDE_ORBITAL_KM,
    AREA_PAINEL_M2,
    CAPACIDADE_BATERIA_WH,
    CONSUMO_BASE_W,
    CONSUMO_PICO_W,
    EFICIENCIA_PAINEL,
    IRRADIANCIA_SOLAR,
    PERIODO_ORBITAL_MIN,
    POTENCIA_MAX_PAINEL_W,
    TEMPO_SOL_MIN,
    TEMPO_SOMBRA_MIN,
    StatusModulo,
    simular_missao,
)
from energia_solar import (
    analisar_por_orbita,
    calcular_sustentabilidade,
    comparar_terrestre_vs_orbital,
    gerar_relatorio_energetico,
)
from monitoramento import SistemaMonitoramento


# ============================================================
# CORES ANSI PARA TERMINAL
# ============================================================
class Cores:
    """Códigos ANSI para colorir saída no terminal."""

    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    DIM = "\033[2m"
    VERDE = "\033[92m"
    VERMELHO = "\033[91m"
    AMARELO = "\033[93m"
    AZUL = "\033[94m"
    CIANO = "\033[96m"
    MAGENTA = "\033[95m"
    BRANCO = "\033[97m"
    BG_VERDE = "\033[42m"
    BG_VERMELHO = "\033[41m"
    BG_AMARELO = "\033[43m"
    BG_AZUL = "\033[44m"


def limpar_tela():
    """Limpa a tela do terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def exibir_banner():
    """Exibe o banner do sistema."""
    banner = f"""
{Cores.CIANO}{Cores.NEGRITO}
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║      ◉  O R B I T A L C O R E  ◉                                 ║
    ║      Sistema de Monitoramento Energético Espacial                ║
    ║                                                                  ║
    ║      🛰️  Missão LEO - Órbita Baixa Terrestre                      ║
    ║      ☀️  Soluções em Energias Renováveis e Sustentáveis           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
{Cores.RESET}"""
    print(banner)


def exibir_parametros_missao():
    """Exibe os parâmetros configurados da missão."""
    print(f"""
{Cores.AZUL}{"═" * 60}
  📋 PARÂMETROS DA MISSÃO
{"═" * 60}{Cores.RESET}

  {Cores.CIANO}Órbita:{Cores.RESET}
    • Altitude:          {ALTITUDE_ORBITAL_KM} km (LEO)
    • Período orbital:   {PERIODO_ORBITAL_MIN} min
    • Tempo ao sol:      {TEMPO_SOL_MIN} min
    • Tempo em sombra:   {TEMPO_SOMBRA_MIN} min

  {Cores.AMARELO}Painel Solar:{Cores.RESET}
    • Área:              {AREA_PAINEL_M2} m²
    • Eficiência:        {EFICIENCIA_PAINEL * 100:.0f}% (GaAs Tripla-Junção)
    • Irradiância:       {IRRADIANCIA_SOLAR} W/m²
    • Potência máxima:   {POTENCIA_MAX_PAINEL_W} W

  {Cores.VERDE}Energia:{Cores.RESET}
    • Consumo base:      {CONSUMO_BASE_W} W
    • Consumo pico:      {CONSUMO_PICO_W} W
    • Capacidade bateria:{CAPACIDADE_BATERIA_WH} Wh

{Cores.AZUL}{"═" * 60}{Cores.RESET}
""")


def exibir_menu():
    """Exibe o menu principal."""
    print(f"""
{Cores.NEGRITO}{Cores.BRANCO}
  ┌────────────────────────────────────────────┐
  │         MENU PRINCIPAL                     │
  ├────────────────────────────────────────────┤
  │                                            │
  │  [1] 🚀 Executar Simulação Completa        │
  │  [2] 📊 Ver Parâmetros da Missão           │
  │  [3] 📈 Gerar Dashboard de Gráficos        │
  │  [4] 📋 Relatório Energético Detalhado     │
  │  [5] 🌱 Análise de Sustentabilidade        │
  │  [6] 🔄 Comparativo Terrestre vs Orbital   │
  │  [7] ⚙️  Alternar Plotly/Matplotlib         │
  │  [8] 💾 Exportar Relatório                 │
  │  [0] 🚪 Sair                               │
  │                                            │
  └────────────────────────────────────────────┘
{Cores.RESET}""")


def aguardar_enter():
    """Aguarda o usuário pressionar Enter."""
    input(f"\n  {Cores.DIM}Pressione Enter para continuar...{Cores.RESET}")


def exibir_progresso_simulacao(registros):
    """Exibe um resumo rápido da simulação com indicadores visuais."""
    total = len(registros)
    ultimo = registros[-1]
    alertas_total = sum(len(r.alertas) for r in registros)
    alertas_criticos = sum(
        1
        for r in registros
        for a in r.alertas
        if a.severidade == 3 or str(a.severidade).upper() == "CRITICO"
    )

    # Barra de SOC (soc_bateria é fração 0.0-1.0)
    soc = ultimo.soc_bateria
    soc_pct = soc * 100 if soc <= 1.0 else soc  # compatibilidade
    barra_len = 30
    preenchido = int(soc_pct / 100 * barra_len)
    if soc_pct > 20:
        cor_barra = Cores.VERDE
    elif soc_pct > 10:
        cor_barra = Cores.AMARELO
    else:
        cor_barra = Cores.VERMELHO
    barra = f"{cor_barra}{'█' * preenchido}{Cores.DIM}{'░' * (barra_len - preenchido)}{Cores.RESET}"

    print(f"""
{Cores.VERDE}{"═" * 60}
  ✅ SIMULAÇÃO CONCLUÍDA COM SUCESSO
{"═" * 60}{Cores.RESET}

  📡 Registros coletados: {Cores.NEGRITO}{total}{Cores.RESET}
  🔄 Órbitas simuladas:  {Cores.NEGRITO}{ultimo.orbita}{Cores.RESET}
  ⏱️  Tempo total:        {Cores.NEGRITO}{ultimo.tempo_min:.0f} min ({ultimo.tempo_min / 60:.1f}h){Cores.RESET}

  🔋 Bateria final:      {barra} {soc_pct:.1f}%
  ⚡ Geração final:      {Cores.VERDE}{ultimo.potencia_gerada_w:.0f} W{Cores.RESET}
  🔌 Consumo final:      {Cores.VERMELHO}{ultimo.consumo_total_w:.0f} W{Cores.RESET}

  ⚠️  Total de alertas:   {Cores.AMARELO}{alertas_total}{Cores.RESET}
  🚨 Alertas críticos:   {Cores.VERMELHO}{alertas_criticos}{Cores.RESET}
""")


def exibir_telemetria_tempo_real(registros, monitor):
    """Exibe a telemetria simulando tempo real (mostrando alguns pontos-chave)."""
    # Selecionar pontos-chave para exibição (a cada mudança sol/sombra + início/fim)
    pontos = []
    em_sombra_anterior = None
    for i, reg in enumerate(registros):
        if reg.em_sombra != em_sombra_anterior:
            pontos.append(i)
            em_sombra_anterior = reg.em_sombra
        elif reg.alertas:  # Pontos com alertas
            pontos.append(i)

    # Limitar a 20 pontos para não poluir o terminal
    if len(pontos) > 20:
        step = len(pontos) // 20
        pontos = pontos[::step]

    print(f"\n{Cores.CIANO}  ── Telemetria em Tempo Real ──{Cores.RESET}\n")

    for idx in pontos:
        reg = registros[idx]
        avaliacao = monitor.avaliar_registro(reg)

        # Ícone de sol/sombra
        icone = "☀️ " if not reg.em_sombra else "🌑"

        # Cor do status (status_geral é string: "NOMINAL", "ALERTA", "CRITICO")
        status = avaliacao["status_geral"]
        if status == "NOMINAL" or status == StatusModulo.NOMINAL:
            cor_status = Cores.VERDE
            txt_status = "NOMINAL"
        elif status == "ALERTA" or status == StatusModulo.ALERTA:
            cor_status = Cores.AMARELO
            txt_status = "ALERTA "
        else:
            cor_status = Cores.VERMELHO
            txt_status = "CRÍTICO"

        print(
            f"  {Cores.DIM}T={reg.tempo_min:6.0f}min{Cores.RESET} "
            f"│ Órbita {reg.orbita:2d} {icone} "
            f"│ {cor_status}[{txt_status}]{Cores.RESET} "
            f"│ ⚡{reg.potencia_gerada_w:5.0f}W "
            f"│ 🔌{reg.consumo_total_w:5.0f}W "
            f"│ 🔋{reg.soc_bateria * 100:5.1f}%"
        )

        # Mostrar alertas/decisões se houver
        for decisao in avaliacao.get("decisoes_tomadas", []):
            print(
                f"  {Cores.MAGENTA}       └─ 🤖 DECISÃO: "
                f"{decisao.get('acao', 'N/A')} → {decisao.get('motivo', '')}"
                f"{Cores.RESET}"
            )

        time.sleep(0.05)  # Pequena pausa para efeito visual


def opcao_simulacao_completa():
    """Executa a simulação completa da missão."""
    print(f"\n{Cores.CIANO}  🚀 Iniciando simulação da missão...{Cores.RESET}")
    print(f"  {Cores.DIM}Configuração: 10 órbitas | Intervalo: 5 min{Cores.RESET}\n")

    # Executar simulação
    registros = simular_missao(num_orbitas=10, intervalo_min=5.0)

    # Criar monitor e processar telemetria
    monitor = SistemaMonitoramento()
    exibir_telemetria_tempo_real(registros, monitor)

    # Resumo
    exibir_progresso_simulacao(registros)

    return registros, monitor


def opcao_dashboard(registros):
    """Gera o dashboard completo de gráficos."""
    if registros is None:
        print(
            f"\n  {Cores.VERMELHO}❌ Execute a simulação primeiro (opção 1){Cores.RESET}"
        )
        return

    print(f"\n{Cores.CIANO}  📈 Gerando dashboard...{Cores.RESET}")
    print(
        f"  {Cores.DIM}Modo: {'Plotly (interativo)' if visualizacao.USAR_PLOTLY else 'Matplotlib (estático)'}{Cores.RESET}"
    )

    analise_orbitas = analisar_por_orbita(registros)
    dados_comp = comparar_terrestre_vs_orbital(registros)

    visualizacao.dashboard_completo(
        registros,
        analise_orbitas=analise_orbitas,
        dados_comparacao=dados_comp,
        salvar=True,
        caminho="graficos/",
    )

    print(f"\n  {Cores.VERDE}✅ Dashboard gerado com sucesso!{Cores.RESET}")
    if not visualizacao.USAR_PLOTLY:
        print(f"  {Cores.DIM}Gráficos salvos em SER/graficos/{Cores.RESET}")


def opcao_relatorio(registros):
    """Exibe o relatório energético detalhado."""
    if registros is None:
        print(
            f"\n  {Cores.VERMELHO}❌ Execute a simulação primeiro (opção 1){Cores.RESET}"
        )
        return

    relatorio = gerar_relatorio_energetico(registros)
    print(relatorio)


def opcao_sustentabilidade(registros):
    """Exibe a análise de sustentabilidade."""
    if registros is None:
        print(
            f"\n  {Cores.VERMELHO}❌ Execute a simulação primeiro (opção 1){Cores.RESET}"
        )
        return

    sust = calcular_sustentabilidade(registros)

    print(f"""
{Cores.VERDE}{"═" * 60}
  🌱 ANÁLISE DE SUSTENTABILIDADE - OrbitalCore
{"═" * 60}{Cores.RESET}

  {Cores.NEGRITO}Fator de Sustentabilidade:{Cores.RESET}  {Cores.VERDE}{sust["fator_sustentabilidade"]:.2f}{Cores.RESET}
    {"✅ Sistema sustentável!" if sust["fator_sustentabilidade"] >= 1.0 else "⚠️ Sistema em déficit energético"}

  {Cores.NEGRITO}Energia Renovável:{Cores.RESET}         {Cores.VERDE}{sust["percentual_renovavel"]:.0f}%{Cores.RESET} (100% Solar)

  {Cores.NEGRITO}PUE (Power Usage Eff.):{Cores.RESET}    {Cores.VERDE}{sust["pue_orbital"]:.2f}{Cores.RESET}
    vs. Data Center Terrestre: {Cores.AMARELO}{sust["pue_terrestre"]:.2f}{Cores.RESET}

  {Cores.NEGRITO}CO₂ Evitado (total simulação):{Cores.RESET}  {Cores.VERDE}{sust["co2_evitado_kg"]:.3f} kg{Cores.RESET}

  {Cores.NEGRITO}Autonomia Estimada:{Cores.RESET}        {Cores.CIANO}{sust["autonomia_horas"]:.1f} horas{Cores.RESET}

  {Cores.NEGRITO}Economia em Refrigeração:{Cores.RESET}  {Cores.VERDE}{sust["economia_cooling_percentual"]:.0f}%{Cores.RESET}
    (Espaço = resfriamento passivo, sem HVAC)

{Cores.VERDE}{"═" * 60}{Cores.RESET}
""")


def opcao_comparativo(registros):
    """Exibe o comparativo terrestre vs. orbital."""
    if registros is None:
        print(
            f"\n  {Cores.VERMELHO}❌ Execute a simulação primeiro (opção 1){Cores.RESET}"
        )
        return

    comp = comparar_terrestre_vs_orbital(registros)
    orb = comp["orbital"]
    ter = comp["terrestre"]

    # Calcular economia e redução
    economia_pct = (
        (1 - orb["consumo_total_w"] / ter["consumo_total_w"]) * 100
        if ter["consumo_total_w"] > 0
        else 0
    )
    reducao_co2 = (
        (1 - orb["co2_por_hora_kg"] / ter["co2_por_hora_kg"]) * 100
        if ter["co2_por_hora_kg"] > 0
        else 100
    )

    print(f"""
{Cores.AZUL}{"═" * 60}
  🔄 COMPARATIVO: OrbitalCore vs Data Center Terrestre
{"═" * 60}{Cores.RESET}

  {Cores.NEGRITO}{"Métrica":<30} {"OrbitalCore":>12} {"Terrestre":>12}{Cores.RESET}
  {"─" * 56}
  {"Consumo Total (W)":<30} {Cores.VERDE}{orb["consumo_total_w"]:>10.0f} W{Cores.RESET}  {Cores.VERMELHO}{ter["consumo_total_w"]:>10.0f} W{Cores.RESET}
  {"Refrigeração (W)":<30} {Cores.VERDE}{orb["consumo_cooling_w"]:>10.0f} W{Cores.RESET}  {Cores.VERMELHO}{ter["consumo_cooling_w"]:>10.0f} W{Cores.RESET}
  {"PUE":<30} {Cores.VERDE}{orb["pue"]:>10.2f}  {Cores.RESET}  {Cores.VERMELHO}{ter["pue"]:>10.2f}  {Cores.RESET}
  {"CO₂ (kg/hora)":<30} {Cores.VERDE}{orb["co2_por_hora_kg"]:>10.3f}  {Cores.RESET}  {Cores.VERMELHO}{ter["co2_por_hora_kg"]:>10.3f}  {Cores.RESET}
  {"Energia Renovável":<30} {Cores.VERDE}{orb["percentual_renovavel"]:>9.0f}%  {Cores.RESET}  {Cores.VERMELHO}{ter["percentual_renovavel"]:>9.0f}%  {Cores.RESET}
  {"─" * 56}

  {Cores.VERDE}📊 Economia de energia:{Cores.RESET}  {economia_pct:.1f}%
  {Cores.VERDE}📊 Redução de CO₂:{Cores.RESET}       {reducao_co2:.1f}%

{Cores.AZUL}{"═" * 60}{Cores.RESET}
""")


def opcao_alternar_visualizacao():
    """Alterna entre Plotly e Matplotlib."""
    visualizacao.USAR_PLOTLY = not visualizacao.USAR_PLOTLY
    modo = (
        "Plotly (interativo)" if visualizacao.USAR_PLOTLY else "Matplotlib (estático)"
    )
    print(
        f"\n  {Cores.VERDE}✅ Modo de visualização alterado para: {Cores.NEGRITO}{modo}{Cores.RESET}"
    )


def opcao_exportar(registros, monitor):
    """Exporta o relatório completo para arquivo."""
    if registros is None:
        print(
            f"\n  {Cores.VERMELHO}❌ Execute a simulação primeiro (opção 1){Cores.RESET}"
        )
        return

    os.makedirs("relatorios", exist_ok=True)
    caminho = "relatorios/relatorio_energetico_orbitalcore.txt"

    relatorio = gerar_relatorio_energetico(registros)

    # Remover códigos ANSI para o arquivo
    import re

    relatorio_limpo = re.sub(r"\033\[[0-9;]*m", "", relatorio)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(relatorio_limpo)

    print(
        f"\n  {Cores.VERDE}✅ Relatório exportado para: {Cores.NEGRITO}{caminho}{Cores.RESET}"
    )


def main():
    """Função principal do sistema."""
    registros = None
    monitor = None

    while True:
        limpar_tela()
        exibir_banner()
        exibir_menu()

        try:
            opcao = input(f"  {Cores.CIANO}Escolha uma opção: {Cores.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {Cores.AMARELO}👋 Encerrando OrbitalCore...{Cores.RESET}\n")
            break

        if opcao == "1":
            limpar_tela()
            exibir_banner()
            registros, monitor = opcao_simulacao_completa()
            aguardar_enter()

        elif opcao == "2":
            limpar_tela()
            exibir_banner()
            exibir_parametros_missao()
            aguardar_enter()

        elif opcao == "3":
            limpar_tela()
            exibir_banner()
            opcao_dashboard(registros)
            aguardar_enter()

        elif opcao == "4":
            limpar_tela()
            exibir_banner()
            opcao_relatorio(registros)
            aguardar_enter()

        elif opcao == "5":
            limpar_tela()
            exibir_banner()
            opcao_sustentabilidade(registros)
            aguardar_enter()

        elif opcao == "6":
            limpar_tela()
            exibir_banner()
            opcao_comparativo(registros)
            aguardar_enter()

        elif opcao == "7":
            opcao_alternar_visualizacao()
            aguardar_enter()

        elif opcao == "8":
            opcao_exportar(registros, monitor)
            aguardar_enter()

        elif opcao == "0":
            print(f"\n  {Cores.AMARELO}👋 Encerrando OrbitalCore...{Cores.RESET}")
            print(f"  {Cores.DIM}Missão encerrada com sucesso.{Cores.RESET}\n")
            break

        else:
            print(
                f"\n  {Cores.VERMELHO}❌ Opção inválida. Tente novamente.{Cores.RESET}"
            )
            aguardar_enter()


if __name__ == "__main__":
    main()
