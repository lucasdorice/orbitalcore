"""
monitoramento.py — Módulo de Monitoramento Inteligente do OrbitalCore

Este módulo implementa o sistema de monitoramento em tempo real da missão
espacial OrbitalCore em órbita LEO. Realiza avaliação contínua de telemetria,
geração automática de alertas, tomada de decisões autônomas e produção de
relatórios formatados para terminal.

Funcionalidades principais:
    - Avaliação de registros de telemetria com classificação de status
    - Geração automática de alertas por condição (bateria, temperatura, energia)
    - Tomada de decisões autônomas para preservação da missão
    - Histórico completo de alertas e decisões
    - Estatísticas consolidadas da missão
    - Relatório resumido formatado com caracteres de desenho de caixa

Autor: OrbitalCore Team — FIAP Global Solution
"""

from typing import List, Dict, Any
from collections import Counter

from dados_missao import (
    RegistroTelemetria,
    Alerta,
    StatusModulo,
    TipoAlerta,
    ModuloEspacial,
    CONSUMO_MODULOS,
    SOC_MIN_SEGURO,
    SOC_CRITICO,
    TEMP_ALERTA_MIN,
    TEMP_ALERTA_MAX,
    TEMP_MIN_OPERACIONAL,
    TEMP_MAX_OPERACIONAL,
    CONSUMO_BASE_W,
    POTENCIA_MAX_PAINEL_W,
)

# ─── Códigos ANSI para saída colorida no terminal ───────────────────────────
COR_VERDE = "\033[92m"
COR_AMARELO = "\033[93m"
COR_VERMELHO = "\033[91m"
COR_CIANO = "\033[96m"
COR_BRANCO = "\033[97m"
COR_NEGRITO = "\033[1m"
COR_RESET = "\033[0m"


class SistemaMonitoramento:
    """Sistema central de monitoramento da missão OrbitalCore.

    Realiza avaliação contínua dos registros de telemetria, gera alertas
    automáticos, toma decisões autônomas para preservar a integridade da
    missão e mantém histórico completo de todos os eventos.

    Attributes:
        historico_alertas (List[Alerta]): Histórico acumulado de todos os alertas.
        log_eventos (List[dict]): Log cronológico de eventos relevantes.
        log_decisoes (List[dict]): Log de decisões autônomas tomadas.
        leituras_consumo_excedente (int): Contador de leituras consecutivas
            em que o consumo superou a geração de energia.
        total_avaliacoes (int): Quantidade total de avaliações realizadas.
        avaliacoes_alerta (int): Quantidade de avaliações com status ALERTA.
        avaliacoes_critico (int): Quantidade de avaliações com status CRITICO.
    """

    def __init__(self) -> None:
        """Inicializa o sistema de monitoramento com históricos vazios."""
        self.historico_alertas: List[Alerta] = []
        self.log_eventos: List[Dict[str, Any]] = []
        self.log_decisoes: List[Dict[str, Any]] = []
        self.leituras_consumo_excedente: int = 0
        self.total_avaliacoes: int = 0
        self.avaliacoes_alerta: int = 0
        self.avaliacoes_critico: int = 0

    # ── Avaliação principal ──────────────────────────────────────────────

    def avaliar_registro(self, registro: RegistroTelemetria) -> dict:
        """Avalia um único registro de telemetria e retorna a avaliação completa.

        Realiza a classificação de status geral, geração de alertas e
        tomada de decisões autônomas para o instante de tempo representado
        pelo registro.

        Args:
            registro: Registro de telemetria a ser avaliado.

        Returns:
            Dicionário contendo:
                - status_geral (str): 'NOMINAL', 'ALERTA' ou 'CRITICO'.
                - alertas_ativos (List[Alerta]): Alertas gerados neste instante.
                - decisoes_tomadas (List[dict]): Decisões autônomas executadas.
                - resumo (str): Resumo textual formatado da avaliação.
        """
        self.total_avaliacoes += 1

        # Atualizar contador de consumo excedente consecutivo
        if registro.consumo_total_w > registro.potencia_gerada_w:
            self.leituras_consumo_excedente += 1
        else:
            self.leituras_consumo_excedente = 0

        status_geral = self.classificar_status_geral(registro)
        alertas = self.gerar_alertas(registro)
        decisoes = self.tomar_decisoes(registro, alertas)

        # Registrar alertas no histórico
        self.historico_alertas.extend(alertas)

        # Registrar decisões no log
        for decisao in decisoes:
            self.log_decisoes.append({
                "tempo_min": registro.tempo_min,
                **decisao,
            })

        # Contabilizar avaliações por status
        if status_geral == StatusModulo.CRITICO:
            self.avaliacoes_critico += 1
        elif status_geral == StatusModulo.ALERTA:
            self.avaliacoes_alerta += 1

        # Registrar evento
        self.log_eventos.append({
            "tempo_min": registro.tempo_min,
            "status": status_geral.name,
            "num_alertas": len(alertas),
            "num_decisoes": len(decisoes),
        })

        # Montar resumo textual
        resumo = self._formatar_resumo(registro, status_geral, alertas, decisoes)

        return {
            "status_geral": status_geral.name,
            "alertas_ativos": alertas,
            "decisoes_tomadas": decisoes,
            "resumo": resumo,
        }

    # ── Classificação de status ──────────────────────────────────────────

    def classificar_status_geral(self, registro: RegistroTelemetria) -> StatusModulo:
        """Determina o status geral da missão com base em todos os subsistemas.

        A classificação segue hierarquia de prioridade: se qualquer condição
        crítica for detectada o status será CRITICO; se houver condições de
        alerta sem críticas, será ALERTA; caso contrário, NOMINAL.

        Args:
            registro: Registro de telemetria atual.

        Returns:
            StatusModulo indicando o nível geral: NOMINAL, ALERTA ou CRITICO.
        """
        # ── Condições CRÍTICAS ───────────────────────────────────────────
        if registro.soc_bateria < SOC_CRITICO:
            return StatusModulo.CRITICO

        for nome, temp in registro.temperaturas.items():
            if temp < TEMP_MIN_OPERACIONAL or temp > TEMP_MAX_OPERACIONAL:
                return StatusModulo.CRITICO

        # Consumo excedente prolongado (> 3 leituras consecutivas)
        if self.leituras_consumo_excedente > 3:
            return StatusModulo.CRITICO

        # ── Condições de ALERTA ──────────────────────────────────────────
        if registro.soc_bateria < SOC_MIN_SEGURO:
            return StatusModulo.ALERTA

        for nome, temp in registro.temperaturas.items():
            if temp < TEMP_ALERTA_MIN or temp > TEMP_ALERTA_MAX:
                return StatusModulo.ALERTA

        if registro.consumo_total_w > registro.potencia_gerada_w:
            return StatusModulo.ALERTA

        # Verificar status dos módulos individuais
        if registro.status_modulos:
            for nome_modulo, status in registro.status_modulos.items():
                status_str = status.value if hasattr(status, 'value') else str(status)
                if status_str == StatusModulo.CRITICO.value:
                    return StatusModulo.CRITICO
                if status_str == StatusModulo.ALERTA.value:
                    return StatusModulo.ALERTA

        return StatusModulo.NOMINAL

    # ── Geração de alertas ───────────────────────────────────────────────

    def gerar_alertas(self, registro: RegistroTelemetria) -> List[Alerta]:
        """Gera alertas com base nas condições atuais de telemetria.

        Verifica condições de bateria, temperatura, balanço energético e
        comunicação, gerando alertas com severidade e tipo apropriados.

        Args:
            registro: Registro de telemetria atual.

        Returns:
            Lista de alertas gerados para este instante.
        """
        alertas: List[Alerta] = []

        # ── Alertas de bateria ───────────────────────────────────────────
        if registro.soc_bateria < SOC_CRITICO:
            alertas.append(Alerta(
                tipo=TipoAlerta.BATERIA_CRITICA,
                mensagem=f"Bateria em nível CRÍTICO: {registro.soc_bateria:.1%}",
                severidade="CRITICO",
                tempo_min=registro.tempo_min,
                modulo="bateria",
                valor=registro.soc_bateria,
            ))
        elif registro.soc_bateria < SOC_MIN_SEGURO:
            alertas.append(Alerta(
                tipo=TipoAlerta.BATERIA_BAIXA,
                mensagem=f"Bateria em nível baixo: {registro.soc_bateria:.1%}",
                severidade="ALERTA",
                tempo_min=registro.tempo_min,
                modulo="bateria",
                valor=registro.soc_bateria,
            ))

        # ── Alertas de temperatura ───────────────────────────────────────
        for nome_modulo, temp in registro.temperaturas.items():
            if temp > TEMP_MAX_OPERACIONAL:
                alertas.append(Alerta(
                    tipo=TipoAlerta.TEMPERATURA_ALTA,
                    mensagem=(
                        f"Temperatura CRÍTICA em {nome_modulo}: {temp:.1f}°C "
                        f"(máx operacional: {TEMP_MAX_OPERACIONAL}°C)"
                    ),
                    severidade="CRITICO",
                    tempo_min=registro.tempo_min,
                    modulo=nome_modulo,
                    valor=temp,
                ))
            elif temp > TEMP_ALERTA_MAX:
                alertas.append(Alerta(
                    tipo=TipoAlerta.TEMPERATURA_ALTA,
                    mensagem=(
                        f"Temperatura ALTA em {nome_modulo}: {temp:.1f}°C "
                        f"(alerta: {TEMP_ALERTA_MAX}°C)"
                    ),
                    severidade="ALERTA",
                    tempo_min=registro.tempo_min,
                    modulo=nome_modulo,
                    valor=temp,
                ))
            elif temp < TEMP_MIN_OPERACIONAL:
                alertas.append(Alerta(
                    tipo=TipoAlerta.TEMPERATURA_BAIXA,
                    mensagem=(
                        f"Temperatura CRÍTICA BAIXA em {nome_modulo}: {temp:.1f}°C "
                        f"(mín operacional: {TEMP_MIN_OPERACIONAL}°C)"
                    ),
                    severidade="CRITICO",
                    tempo_min=registro.tempo_min,
                    modulo=nome_modulo,
                    valor=temp,
                ))
            elif temp < TEMP_ALERTA_MIN:
                alertas.append(Alerta(
                    tipo=TipoAlerta.TEMPERATURA_BAIXA,
                    mensagem=(
                        f"Temperatura BAIXA em {nome_modulo}: {temp:.1f}°C "
                        f"(alerta: {TEMP_ALERTA_MIN}°C)"
                    ),
                    severidade="ALERTA",
                    tempo_min=registro.tempo_min,
                    modulo=nome_modulo,
                    valor=temp,
                ))

        # ── Alertas de balanço energético ────────────────────────────────
        if registro.balanco_w < 0:
            severidade = "CRITICO" if abs(registro.balanco_w) > 200 else "ALERTA"
            tipo = TipoAlerta.ENERGIA_CRITICA if severidade == "CRITICO" else TipoAlerta.ENERGIA_BAIXA
            alertas.append(Alerta(
                tipo=tipo,
                mensagem=(
                    f"Balanço energético negativo: {registro.balanco_w:.1f}W "
                    f"(geração: {registro.potencia_gerada_w:.1f}W, "
                    f"consumo: {registro.consumo_total_w:.1f}W)"
                ),
                severidade=severidade,
                tempo_min=registro.tempo_min,
                modulo="energia",
                valor=registro.balanco_w,
            ))

        # ── Alertas de sobrecarga ────────────────────────────────────────
        if registro.consumo_total_w > POTENCIA_MAX_PAINEL_W:
            alertas.append(Alerta(
                tipo=TipoAlerta.SOBRECARGA,
                mensagem=(
                    f"Consumo ({registro.consumo_total_w:.1f}W) excede "
                    f"capacidade máxima dos painéis ({POTENCIA_MAX_PAINEL_W}W)"
                ),
                severidade="ALERTA",
                tempo_min=registro.tempo_min,
                modulo="energia",
                valor=registro.consumo_total_w,
            ))

        # ── Alertas de consumo excedente prolongado ──────────────────────
        if self.leituras_consumo_excedente > 3:
            alertas.append(Alerta(
                tipo=TipoAlerta.ENERGIA_CRITICA,
                mensagem=(
                    f"Consumo excede geração por {self.leituras_consumo_excedente} "
                    f"leituras consecutivas — risco de esgotamento de bateria"
                ),
                severidade="CRITICO",
                tempo_min=registro.tempo_min,
                modulo="energia",
                valor=self.leituras_consumo_excedente,
            ))

        # ── Alertas de comunicação (baseado em status de módulo) ─────────
        if registro.status_modulos:
            status_comms = registro.status_modulos.get("comunicacao")
            status_str = status_comms.value if hasattr(status_comms, 'value') else str(status_comms) if status_comms else ""
            if status_str == StatusModulo.CRITICO.value:
                alertas.append(Alerta(
                    tipo=TipoAlerta.COMUNICACAO_FALHA,
                    mensagem="Falha no módulo de comunicação — enlace comprometido",
                    severidade="CRITICO",
                    tempo_min=registro.tempo_min,
                    modulo="comunicacao",
                    valor=0,
                ))
            elif status_str == StatusModulo.DESLIGADO.value:
                alertas.append(Alerta(
                    tipo=TipoAlerta.COMUNICACAO_FALHA,
                    mensagem="Módulo de comunicação DESLIGADO",
                    severidade="ALERTA",
                    tempo_min=registro.tempo_min,
                    modulo="comunicacao",
                    valor=0,
                ))

        return alertas

    # ── Tomada de decisões autônomas ─────────────────────────────────────

    def tomar_decisoes(
        self, registro: RegistroTelemetria, alertas: List[Alerta]
    ) -> List[Dict[str, Any]]:
        """Tomada de decisões autônomas para preservação da missão.

        Com base no estado atual da telemetria e nos alertas gerados,
        determina ações corretivas automáticas priorizadas.

        Regras de decisão:
            - Bateria < 10%: DESLIGAR módulos não-essenciais (sensores, reduzir comms)
            - Bateria < 20%: REDUZIR carga de processamento
            - Temperatura > 70°C em qualquer módulo: ATIVAR gestão térmica
            - Temperatura < -20°C: AUMENTAR potência do aquecedor
            - Consumo > geração por >3 leituras: ENTRAR em modo economia
            - Cada decisão é um dict com: acao, motivo, modulo_afetado, prioridade

        Args:
            registro: Registro de telemetria atual.
            alertas: Lista de alertas gerados para este instante.

        Returns:
            Lista de decisões, cada uma como dicionário com chaves:
            acao, motivo, modulo_afetado, prioridade (1=máxima).
        """
        decisoes: List[Dict[str, Any]] = []

        # ── Bateria crítica (< 10%) — desligar não-essenciais ────────────
        if registro.soc_bateria < SOC_CRITICO:
            decisoes.append({
                "acao": "DESLIGAR módulos não-essenciais",
                "motivo": (
                    f"Bateria em nível crítico ({registro.soc_bateria:.1%}). "
                    f"Desligando sensores e reduzindo comunicações para "
                    f"preservar energia vital."
                ),
                "modulo_afetado": "sensores, comunicacao",
                "prioridade": 1,
            })

        # ── Bateria baixa (< 20%) — reduzir processamento ───────────────
        elif registro.soc_bateria < SOC_MIN_SEGURO:
            decisoes.append({
                "acao": "REDUZIR carga de processamento",
                "motivo": (
                    f"Bateria em nível baixo ({registro.soc_bateria:.1%}). "
                    f"Reduzindo processamento para economizar energia."
                ),
                "modulo_afetado": "processamento",
                "prioridade": 2,
            })

        # ── Temperatura alta (> 70°C) — ativar gestão térmica ────────────
        for nome_modulo, temp in registro.temperaturas.items():
            if temp > TEMP_ALERTA_MAX:
                decisoes.append({
                    "acao": "ATIVAR gestão térmica",
                    "motivo": (
                        f"Temperatura elevada em {nome_modulo}: {temp:.1f}°C "
                        f"(limite: {TEMP_ALERTA_MAX}°C). Ativando dissipação "
                        f"térmica de emergência."
                    ),
                    "modulo_afetado": nome_modulo,
                    "prioridade": 2,
                })

        # ── Temperatura baixa (< -20°C) — aumentar aquecedor ────────────
        for nome_modulo, temp in registro.temperaturas.items():
            if temp < TEMP_ALERTA_MIN:
                decisoes.append({
                    "acao": "AUMENTAR potência do aquecedor",
                    "motivo": (
                        f"Temperatura baixa em {nome_modulo}: {temp:.1f}°C "
                        f"(limite: {TEMP_ALERTA_MIN}°C). Incrementando "
                        f"aquecimento para proteção de componentes."
                    ),
                    "modulo_afetado": nome_modulo,
                    "prioridade": 2,
                })

        # ── Consumo excedente prolongado — modo economia ─────────────────
        if self.leituras_consumo_excedente > 3:
            decisoes.append({
                "acao": "ENTRAR em modo economia de energia",
                "motivo": (
                    f"Consumo excede geração por "
                    f"{self.leituras_consumo_excedente} leituras consecutivas. "
                    f"Ativando modo de economia para estabilizar balanço "
                    f"energético."
                ),
                "modulo_afetado": "todos",
                "prioridade": 1,
            })

        # Ordenar decisões por prioridade (1 = mais urgente)
        decisoes.sort(key=lambda d: d["prioridade"])

        return decisoes

    # ── Consultas ao histórico ───────────────────────────────────────────

    def obter_historico_alertas(self) -> List[Alerta]:
        """Retorna o histórico completo de todos os alertas registrados.

        Returns:
            Lista cronológica de todos os alertas acumulados desde o início
            do monitoramento.
        """
        return list(self.historico_alertas)

    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas consolidadas do monitoramento.

        Returns:
            Dicionário com:
                - total_alertas (int): Total de alertas registrados.
                - alertas_por_tipo (dict): Contagem de alertas por TipoAlerta.
                - alertas_por_severidade (dict): Contagem por severidade.
                - total_decisoes (int): Total de decisões autônomas tomadas.
                - tempo_em_alerta_pct (float): Percentual de tempo em ALERTA.
                - tempo_em_critico_pct (float): Percentual de tempo em CRITICO.
        """
        alertas_por_tipo: Dict[str, int] = Counter(
            alerta.tipo.name if hasattr(alerta.tipo, "name") else str(alerta.tipo)
            for alerta in self.historico_alertas
        )
        alertas_por_severidade: Dict[str, int] = Counter(
            alerta.severidade for alerta in self.historico_alertas
        )

        total_aval = max(self.total_avaliacoes, 1)  # evitar divisão por zero

        return {
            "total_alertas": len(self.historico_alertas),
            "alertas_por_tipo": dict(alertas_por_tipo),
            "alertas_por_severidade": dict(alertas_por_severidade),
            "total_decisoes": len(self.log_decisoes),
            "tempo_em_alerta_pct": (self.avaliacoes_alerta / total_aval) * 100,
            "tempo_em_critico_pct": (self.avaliacoes_critico / total_aval) * 100,
        }

    # ── Relatório de missão ──────────────────────────────────────────────

    def gerar_resumo_missao(self, registros: List[RegistroTelemetria]) -> str:
        """Gera um relatório resumido e formatado da missão para terminal.

        Processa todos os registros de telemetria fornecidos e produz um
        resumo completo utilizando caracteres de desenho de caixa e códigos
        ANSI para visualização no terminal.

        Args:
            registros: Lista completa de registros de telemetria da missão.

        Returns:
            String formatada pronta para impressão no terminal.
        """
        if not registros:
            return f"{COR_AMARELO}⚠ Nenhum registro de telemetria disponível.{COR_RESET}"

        # ── Processar todos os registros ─────────────────────────────────
        for reg in registros:
            self.avaliar_registro(reg)

        stats = self.obter_estatisticas()

        # ── Cálculos agregados ───────────────────────────────────────────
        tempo_total_min = registros[-1].tempo_min - registros[0].tempo_min
        tempo_total_h = tempo_total_min / 60 if tempo_total_min > 0 else 1

        soc_min = min(r.soc_bateria for r in registros)
        soc_max = max(r.soc_bateria for r in registros)
        soc_media = sum(r.soc_bateria for r in registros) / len(registros)

        pot_gerada_media = sum(r.potencia_gerada_w for r in registros) / len(registros)
        consumo_medio = sum(r.consumo_total_w for r in registros) / len(registros)
        balanco_medio = sum(r.balanco_w for r in registros) / len(registros)

        orbitas = set(r.orbita for r in registros)
        num_orbitas = len(orbitas)

        tempo_sombra = sum(1 for r in registros if r.em_sombra)
        pct_sombra = (tempo_sombra / len(registros)) * 100

        # Temperaturas extremas
        temp_min_global = float("inf")
        temp_max_global = float("-inf")
        modulo_temp_max = ""
        modulo_temp_min = ""
        for reg in registros:
            for nome, temp in reg.temperaturas.items():
                if temp < temp_min_global:
                    temp_min_global = temp
                    modulo_temp_min = nome
                if temp > temp_max_global:
                    temp_max_global = temp
                    modulo_temp_max = nome

        # ── Determinação do status final ─────────────────────────────────
        status_final = self.classificar_status_geral(registros[-1])
        if status_final == StatusModulo.CRITICO:
            cor_status = COR_VERMELHO
            icone_status = "🔴"
        elif status_final == StatusModulo.ALERTA:
            cor_status = COR_AMARELO
            icone_status = "🟡"
        else:
            cor_status = COR_VERDE
            icone_status = "🟢"

        # ── Montagem do relatório ────────────────────────────────────────
        largura = 68
        linha_h = "─" * largura
        linha_d = "═" * largura

        linhas = [
            "",
            f"{COR_CIANO}{COR_NEGRITO}╔{linha_d}╗{COR_RESET}",
            f"{COR_CIANO}{COR_NEGRITO}║{'OrbitalCore — Resumo da Missão':^{largura}}║{COR_RESET}",
            f"{COR_CIANO}{COR_NEGRITO}╚{linha_d}╝{COR_RESET}",
            "",
            f"{COR_NEGRITO}┌{linha_h}┐{COR_RESET}",
            f"{COR_NEGRITO}│{'  INFORMAÇÕES GERAIS':<{largura}}│{COR_RESET}",
            f"{COR_NEGRITO}├{linha_h}┤{COR_RESET}",
            f"│  Duração total:        {tempo_total_min:.0f} min ({tempo_total_h:.1f} h){' ' * (largura - 46)}│",
            f"│  Órbitas completadas:  {num_orbitas}{' ' * (largura - 27 - len(str(num_orbitas)))}│",
            f"│  Tempo em sombra:      {pct_sombra:.1f}%{' ' * (largura - 28 - len(f'{pct_sombra:.1f}'))}│",
            f"│  Status final:         {cor_status}{icone_status} {status_final.name}{COR_RESET}{' ' * max(0, largura - 30 - len(status_final.name))}│",
            f"{COR_NEGRITO}└{linha_h}┘{COR_RESET}",
            "",
            f"{COR_NEGRITO}┌{linha_h}┐{COR_RESET}",
            f"{COR_NEGRITO}│{'  ENERGIA':<{largura}}│{COR_RESET}",
            f"{COR_NEGRITO}├{linha_h}┤{COR_RESET}",
            f"│  Geração média:        {COR_VERDE}{pot_gerada_media:>8.1f} W{COR_RESET}{' ' * (largura - 35)}│",
            f"│  Consumo médio:        {COR_VERMELHO}{consumo_medio:>8.1f} W{COR_RESET}{' ' * (largura - 35)}│",
            f"│  Balanço médio:        {COR_AMARELO}{balanco_medio:>+8.1f} W{COR_RESET}{' ' * (largura - 35)}│",
            f"{COR_NEGRITO}└{linha_h}┘{COR_RESET}",
            "",
            f"{COR_NEGRITO}┌{linha_h}┐{COR_RESET}",
            f"{COR_NEGRITO}│{'  BATERIA':<{largura}}│{COR_RESET}",
            f"{COR_NEGRITO}├{linha_h}┤{COR_RESET}",
            f"│  SOC mínimo:           {soc_min:>8.1%}{' ' * (largura - 33)}│",
            f"│  SOC máximo:           {soc_max:>8.1%}{' ' * (largura - 33)}│",
            f"│  SOC médio:            {soc_media:>8.1%}{' ' * (largura - 33)}│",
            f"{COR_NEGRITO}└{linha_h}┘{COR_RESET}",
            "",
            f"{COR_NEGRITO}┌{linha_h}┐{COR_RESET}",
            f"{COR_NEGRITO}│{'  TEMPERATURAS':<{largura}}│{COR_RESET}",
            f"{COR_NEGRITO}├{linha_h}┤{COR_RESET}",
            f"│  Mín global:           {temp_min_global:>+8.1f}°C ({modulo_temp_min}){' ' * max(0, largura - 42 - len(modulo_temp_min))}│",
            f"│  Máx global:           {temp_max_global:>+8.1f}°C ({modulo_temp_max}){' ' * max(0, largura - 42 - len(modulo_temp_max))}│",
            f"{COR_NEGRITO}└{linha_h}┘{COR_RESET}",
            "",
            f"{COR_NEGRITO}┌{linha_h}┐{COR_RESET}",
            f"{COR_NEGRITO}│{'  ALERTAS E DECISÕES':<{largura}}│{COR_RESET}",
            f"{COR_NEGRITO}├{linha_h}┤{COR_RESET}",
            f"│  Total de alertas:     {stats['total_alertas']:>8}{' ' * (largura - 33)}│",
            f"│  Total de decisões:    {stats['total_decisoes']:>8}{' ' * (largura - 33)}│",
            f"│  Tempo em ALERTA:      {stats['tempo_em_alerta_pct']:>7.1f}%{' ' * (largura - 33)}│",
            f"│  Tempo em CRÍTICO:     {stats['tempo_em_critico_pct']:>7.1f}%{' ' * (largura - 33)}│",
            f"{COR_NEGRITO}└{linha_h}┘{COR_RESET}",
        ]

        # ── Detalhamento dos alertas por tipo ────────────────────────────
        if stats["alertas_por_tipo"]:
            linhas.append("")
            linhas.append(f"{COR_NEGRITO}┌{linha_h}┐{COR_RESET}")
            linhas.append(
                f"{COR_NEGRITO}│{'  ALERTAS POR TIPO':<{largura}}│{COR_RESET}"
            )
            linhas.append(f"{COR_NEGRITO}├{linha_h}┤{COR_RESET}")
            for tipo, qtd in sorted(
                stats["alertas_por_tipo"].items(), key=lambda x: -x[1]
            ):
                texto_tipo = f"  {tipo}:"
                linhas.append(
                    f"│{texto_tipo:<40}{qtd:>6}{' ' * (largura - 46)}│"
                )
            linhas.append(f"{COR_NEGRITO}└{linha_h}┘{COR_RESET}")

        linhas.append("")

        return "\n".join(linhas)

    # ── Métodos auxiliares internos ───────────────────────────────────────

    def _formatar_resumo(
        self,
        registro: RegistroTelemetria,
        status: StatusModulo,
        alertas: List[Alerta],
        decisoes: List[Dict[str, Any]],
    ) -> str:
        """Formata resumo textual de uma única avaliação de telemetria.

        Args:
            registro: Registro avaliado.
            status: Status geral classificado.
            alertas: Alertas gerados.
            decisoes: Decisões tomadas.

        Returns:
            String formatada para impressão no terminal.
        """
        if status == StatusModulo.CRITICO:
            cor = COR_VERMELHO
            icone = "🔴"
        elif status == StatusModulo.ALERTA:
            cor = COR_AMARELO
            icone = "🟡"
        else:
            cor = COR_VERDE
            icone = "🟢"

        partes = [
            f"{cor}{COR_NEGRITO}{icone} [{registro.tempo_min:.0f} min] "
            f"Status: {status.name}{COR_RESET}",
            f"  ⚡ Geração: {registro.potencia_gerada_w:.1f}W | "
            f"Consumo: {registro.consumo_total_w:.1f}W | "
            f"Balanço: {registro.balanco_w:+.1f}W",
            f"  🔋 Bateria: {registro.soc_bateria:.1%} | "
            f"Sombra: {'Sim' if registro.em_sombra else 'Não'}",
        ]

        if alertas:
            partes.append(f"  {COR_AMARELO}⚠ Alertas ({len(alertas)}):{COR_RESET}")
            for alerta in alertas:
                partes.append(f"    • {alerta.mensagem}")

        if decisoes:
            partes.append(f"  {COR_CIANO}🤖 Decisões ({len(decisoes)}):{COR_RESET}")
            for dec in decisoes:
                partes.append(
                    f"    → {dec['acao']} [{dec['modulo_afetado']}] "
                    f"(P{dec['prioridade']})"
                )

        return "\n".join(partes)
