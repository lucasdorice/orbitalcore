"""
dados_missao.py — Módulo de dados fundamentais da missão OrbitalCore.

Este módulo contém todas as constantes, estruturas de dados e funções
de simulação necessárias para modelar o sistema de energia renovável (SER)
de um data center orbital em LEO (Low Earth Orbit).

A missão OrbitalCore opera a ~900 km de altitude, completando uma órbita
a cada ~103 minutos (fórmula de Kepler: T = 2π√(r³/μ), r=7271km,
μ=398600 km³/s²), com ~68 minutos de exposição solar e ~35 minutos
em sombra da Terra (fração eclipse = arcsin(6371/7271)/π ≈ 34%).

Autores: Equipe OrbitalCore — FIAP Global Solution 2026
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# =============================================================================
# CONSTANTES ORBITAIS
# =============================================================================

# Altitude da órbita LEO em quilômetros
ALTITUDE_ORBITAL_KM: int = 900

# Período orbital completo em minutos
# Fórmula de Kepler: T = 2π√(r³/μ), r = 6371 + 900 = 7271 km, μ = 398600 km³/s²
PERIODO_ORBITAL_MIN: int = 103

# Tempo de exposição solar por órbita em minutos
# Fração iluminada = 1 - ρ/π, onde ρ = arcsin(6371/7271) = 61.1° → ~66%
TEMPO_SOL_MIN: int = 68

# Tempo em sombra da Terra por órbita em minutos
# Fração eclipse = ρ/π = 61.1/180 ≈ 34%
TEMPO_SOMBRA_MIN: int = 35

# =============================================================================
# CONSTANTES DO PAINEL SOLAR
# =============================================================================

# Área total dos painéis solares em metros quadrados (4)
AREA_PAINEL_M2: float = 4.0

# Eficiência das células solares GaAs de tripla junção (30%)
EFICIENCIA_PAINEL: float = 0.30

# Irradiância solar no topo da atmosfera em W/m² (constante solar em LEO)
IRRADIANCIA_SOLAR: float = 1361.0

# Potência máxima que o painel pode fornecer em Watts (limite do hardware)
POTENCIA_MAX_PAINEL_W: float = 1500.0

# Taxa de degradação anual dos painéis solares (2% ao ano)
DEGRADACAO_ANUAL: float = 0.02

# Coeficiente de temperatura do painel (%/°C acima da referência)
COEF_TEMP_PAINEL: float = -0.003

# Temperatura de referência do painel para cálculos de eficiência (°C)
TEMP_REF_PAINEL: float = 25.0

# =============================================================================
# CONSTANTES DA BATERIA
# =============================================================================

# Capacidade total da bateria em Watt-hora
CAPACIDADE_BATERIA_WH: float = 2000.0

# Eficiência de carga da bateria (95%)
EFICIENCIA_CARGA: float = 0.95

# Eficiência de descarga da bateria (98%)
EFICIENCIA_DESCARGA: float = 0.98

# Estado de carga (SOC) mínimo seguro — abaixo disso gera alerta
SOC_MIN_SEGURO: float = 0.20

# Estado de carga (SOC) crítico — abaixo disso é emergência
SOC_CRITICO: float = 0.10

# =============================================================================
# CONSTANTES DE CONSUMO
# =============================================================================

# Consumo energético dos módulos operacionais do OrbitalCore (em Watts)
# Cada módulo possui três modos: nominal, pico e standby
CONSUMO_MODULOS: Dict[str, Dict[str, float]] = {
    "comunicacao": {
        "nominal": 80.0,   # Comunicação padrão com estação terrestre
        "pico": 120.0,     # Transmissão de dados em alta velocidade
        "standby": 15.0,   # Apenas escuta passiva
    },
    "processamento": {
        "nominal": 150.0,  # Processamento de dados padrão
        "pico": 200.0,     # Cargas computacionais intensivas
        "standby": 30.0,   # Modo de espera mínimo
    },
    "sensores": {
        "nominal": 60.0,   # Coleta contínua de dados ambientais
        "pico": 90.0,      # Aquisição de dados em alta frequência
        "standby": 10.0,   # Sensores desligados, apenas monitoramento
    },
    "termico": {
        "nominal": 60.0,   # Controle térmico ativo (heaters/radiadores)
        "pico": 100.0,     # Compensação térmica em condições extremas
        "standby": 20.0,   # Controle térmico passivo
    },
}

# Consumo base total do sistema em operação nominal (W)
CONSUMO_BASE_W: float = 350.0

# Consumo de pico total do sistema (W)
CONSUMO_PICO_W: float = 450.0

# =============================================================================
# CONSTANTES TÉRMICAS
# =============================================================================

# Temperatura mínima operacional dos componentes (°C)
TEMP_MIN_OPERACIONAL: float = -40.0

# Temperatura máxima operacional dos componentes (°C)
TEMP_MAX_OPERACIONAL: float = 85.0

# Temperatura de alerta mínima — abaixo gera alerta de frio (°C)
TEMP_ALERTA_MIN: float = -20.0

# Temperatura de alerta máxima — acima gera alerta de calor (°C)
TEMP_ALERTA_MAX: float = 70.0

# Temperatura nominal mínima (faixa ideal de operação) (°C)
TEMP_NOMINAL_MIN: float = 5.0

# Temperatura nominal máxima (faixa ideal de operação) (°C)
TEMP_NOMINAL_MAX: float = 45.0


# =============================================================================
# ENUMERAÇÕES
# =============================================================================

class StatusModulo(Enum):
    """Status operacional de um módulo do OrbitalCore."""
    NOMINAL = "nominal"       # Operação normal dentro dos parâmetros
    ALERTA = "alerta"         # Condição anormal, requer atenção
    CRITICO = "critico"       # Condição crítica, ação imediata necessária
    DESLIGADO = "desligado"   # Módulo desativado


class TipoAlerta(Enum):
    """Tipos de alerta gerados pelo sistema de monitoramento."""
    ENERGIA_BAIXA = "energia_baixa"           # SOC abaixo do mínimo seguro
    ENERGIA_CRITICA = "energia_critica"       # SOC abaixo do nível crítico
    TEMPERATURA_ALTA = "temperatura_alta"     # Temperatura acima do alerta
    TEMPERATURA_BAIXA = "temperatura_baixa"   # Temperatura abaixo do alerta
    COMUNICACAO_FALHA = "comunicacao_falha"   # Falha no link de comunicação
    BATERIA_BAIXA = "bateria_baixa"           # Bateria em nível baixo
    BATERIA_CRITICA = "bateria_critica"       # Bateria em nível crítico
    SOBRECARGA = "sobrecarga"                 # Consumo excede a geração + bateria


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class ModuloEspacial:
    """
    Representa um módulo operacional do OrbitalCore.

    Cada módulo possui três modos de consumo (nominal, pico, standby)
    e pode ser monitorado quanto à temperatura e status operacional.

    Atributos:
        nome: Nome identificador do módulo.
        consumo_nominal: Consumo em operação normal (W).
        consumo_pico: Consumo máximo sob carga (W).
        consumo_standby: Consumo em modo de espera (W).
        consumo_atual: Consumo atual calculado (W).
        temperatura: Temperatura atual do módulo (°C).
        status: Status operacional atual.
        ativo: Se o módulo está ligado.
    """
    nome: str
    consumo_nominal: float
    consumo_pico: float
    consumo_standby: float
    consumo_atual: float = 0.0
    temperatura: float = 20.0
    status: StatusModulo = StatusModulo.NOMINAL
    ativo: bool = True

    def atualizar_consumo(self, fator_carga: float) -> float:
        """
        Atualiza o consumo atual do módulo com base no fator de carga.

        O fator de carga varia de 0.0 (standby) a 1.0 (pico).
        Valores intermediários interpolam linearmente entre nominal e pico.

        Args:
            fator_carga: Fator de carga entre 0.0 e 1.0.

        Returns:
            O consumo atual calculado em Watts.
        """
        if not self.ativo:
            self.consumo_atual = 0.0
            return self.consumo_atual

        # Limita o fator entre 0 e 1
        fator_carga = max(0.0, min(1.0, fator_carga))

        if fator_carga < 0.1:
            # Modo standby para fatores muito baixos
            self.consumo_atual = self.consumo_standby
        else:
            # Interpolação linear entre nominal e pico
            self.consumo_atual = (
                self.consumo_nominal
                + (self.consumo_pico - self.consumo_nominal) * fator_carga
            )

        return self.consumo_atual


@dataclass
class PainelSolar:
    """
    Representa o sistema de painéis solares do OrbitalCore.

    Modela a geração de energia considerando ângulo de incidência,
    degradação temporal, efeitos de temperatura e período de sombra.

    Atributos:
        area: Área total dos painéis (m²).
        eficiencia: Eficiência base das células (0 a 1).
        potencia_atual: Potência sendo gerada no momento (W).
        temperatura: Temperatura atual do painel (°C).
        degradacao: Fator de degradação acumulada (0 a 1, onde 1 = novo).
    """
    area: float = AREA_PAINEL_M2
    eficiencia: float = EFICIENCIA_PAINEL
    potencia_atual: float = 0.0
    temperatura: float = 25.0
    degradacao: float = 1.0

    def calcular_potencia(
        self,
        angulo_incidencia: float,
        em_sombra: bool,
    ) -> float:
        """
        Calcula a potência gerada pelo painel solar.

        Utiliza a lei do cosseno para o ângulo de incidência,
        aplica degradação por temperatura e envelhecimento do painel.

        Args:
            angulo_incidencia: Ângulo entre a normal do painel e a
                               direção do Sol em graus (0° = perpendicular).
            em_sombra: True se a nave está na sombra da Terra.

        Returns:
            Potência gerada em Watts (0.0 se em sombra).
        """
        # Sem geração quando em sombra da Terra
        if em_sombra:
            self.potencia_atual = 0.0
            return 0.0

        # Lei do cosseno: potência proporcional ao cos(ângulo)
        angulo_rad = math.radians(angulo_incidencia)
        fator_angular = max(0.0, math.cos(angulo_rad))

        # Efeito da temperatura na eficiência
        # Coeficiente negativo: eficiência cai com aumento de temperatura
        delta_temp = self.temperatura - TEMP_REF_PAINEL
        fator_temperatura = 1.0 + COEF_TEMP_PAINEL * delta_temp

        # Garante que o fator de temperatura não seja negativo
        fator_temperatura = max(0.0, fator_temperatura)

        # Cálculo da potência: irradiância × área × eficiência × fatores
        potencia = (
            IRRADIANCIA_SOLAR
            * self.area
            * self.eficiencia
            * fator_angular
            * fator_temperatura
            * self.degradacao
        )

        # Limita à potência máxima do hardware
        potencia = min(potencia, POTENCIA_MAX_PAINEL_W)

        self.potencia_atual = potencia
        return potencia


@dataclass
class Bateria:
    """
    Representa o sistema de armazenamento de energia (bateria) do OrbitalCore.

    Modela carregamento e descarregamento com eficiências distintas,
    e fornece monitoramento do estado de carga (SOC).

    Atributos:
        capacidade_wh: Capacidade total da bateria (Wh).
        energia_atual_wh: Energia armazenada no momento (Wh).
    """
    capacidade_wh: float = CAPACIDADE_BATERIA_WH
    energia_atual_wh: float = field(default=None)

    def __post_init__(self):
        """Inicializa a bateria com 85% de carga se não especificado."""
        if self.energia_atual_wh is None:
            self.energia_atual_wh = self.capacidade_wh * 0.85

    @property
    def soc(self) -> float:
        """
        Retorna o estado de carga (State of Charge) como fração (0.0 a 1.0).
        """
        return self.energia_atual_wh / self.capacidade_wh

    @property
    def soc_percentual(self) -> float:
        """
        Retorna o estado de carga como porcentagem (0.0 a 100.0).
        """
        return self.soc * 100.0

    @property
    def status(self) -> StatusModulo:
        """
        Retorna o status da bateria com base no SOC atual.

        Returns:
            StatusModulo.CRITICO se SOC < SOC_CRITICO,
            StatusModulo.ALERTA se SOC < SOC_MIN_SEGURO,
            StatusModulo.NOMINAL caso contrário.
        """
        if self.soc < SOC_CRITICO:
            return StatusModulo.CRITICO
        elif self.soc < SOC_MIN_SEGURO:
            return StatusModulo.ALERTA
        return StatusModulo.NOMINAL

    def carregar(self, potencia_w: float, duracao_min: float) -> float:
        """
        Carrega a bateria com a potência fornecida durante um intervalo.

        A energia efetivamente armazenada é multiplicada pela eficiência
        de carga. A bateria não ultrapassa sua capacidade máxima.

        Args:
            potencia_w: Potência de carga em Watts.
            duracao_min: Duração do carregamento em minutos.

        Returns:
            Energia efetivamente armazenada em Wh.
        """
        # Converte minutos para horas e calcula energia
        duracao_h = duracao_min / 60.0
        energia_bruta = potencia_w * duracao_h
        energia_efetiva = energia_bruta * EFICIENCIA_CARGA

        # Não ultrapassa a capacidade máxima
        energia_anterior = self.energia_atual_wh
        self.energia_atual_wh = min(
            self.capacidade_wh,
            self.energia_atual_wh + energia_efetiva,
        )

        return self.energia_atual_wh - energia_anterior

    def descarregar(self, potencia_w: float, duracao_min: float) -> float:
        """
        Descarrega a bateria para suprir a demanda de potência.

        A energia fornecida considera a eficiência de descarga.
        A bateria não desce abaixo de 0 Wh.

        Args:
            potencia_w: Potência demandada em Watts.
            duracao_min: Duração da demanda em minutos.

        Returns:
            Energia efetivamente fornecida em Wh.
        """
        duracao_h = duracao_min / 60.0
        energia_necessaria = potencia_w * duracao_h

        # Energia retirada da bateria (com perda por eficiência)
        energia_retirada = energia_necessaria / EFICIENCIA_DESCARGA

        energia_anterior = self.energia_atual_wh
        self.energia_atual_wh = max(0.0, self.energia_atual_wh - energia_retirada)

        return energia_anterior - self.energia_atual_wh


@dataclass
class Alerta:
    """
    Representa um alerta gerado pelo sistema de monitoramento do OrbitalCore.

    Atributos:
        tipo: Tipo do alerta (enum TipoAlerta).
        mensagem: Descrição legível do alerta.
        severidade: Nível de severidade (1=info, 2=aviso, 3=crítico).
        tempo_min: Momento da missão em que o alerta foi gerado (minutos).
        modulo: Nome do módulo que gerou o alerta (se aplicável).
        valor: Valor numérico associado ao alerta (se aplicável).
    """
    tipo: TipoAlerta
    mensagem: str
    severidade: int
    tempo_min: float
    modulo: Optional[str] = None
    valor: Optional[float] = None


@dataclass
class RegistroTelemetria:
    """
    Registro completo de telemetria de um instante da missão.

    Contém todos os dados relevantes do sistema de energia e
    módulos operacionais para um determinado ponto no tempo.

    Atributos:
        tempo_min: Tempo decorrido desde o início da missão (minutos).
        orbita: Número da órbita atual (1-indexado).
        em_sombra: True se a nave está na sombra da Terra.
        angulo_solar: Ângulo de incidência solar no painel (graus).
        potencia_gerada_w: Potência gerada pelos painéis solares (W).
        consumo_total_w: Consumo total de todos os módulos (W).
        balanco_w: Balanço energético: geração - consumo (W).
        soc_bateria: Estado de carga da bateria (0.0 a 1.0).
        energia_bateria_wh: Energia armazenada na bateria (Wh).
        temperaturas: Temperaturas dos módulos {nome: temp_°C}.
        status_modulos: Status dos módulos {nome: StatusModulo}.
        alertas: Lista de alertas gerados neste instante.
    """
    tempo_min: float
    orbita: int
    em_sombra: bool
    angulo_solar: float
    potencia_gerada_w: float
    consumo_total_w: float
    balanco_w: float
    soc_bateria: float
    energia_bateria_wh: float
    temperaturas: Dict[str, float] = field(default_factory=dict)
    status_modulos: Dict[str, str] = field(default_factory=dict)
    alertas: List[Alerta] = field(default_factory=list)


# =============================================================================
# FUNÇÕES
# =============================================================================

def criar_modulos() -> Dict[str, ModuloEspacial]:
    """
    Cria e retorna os quatro módulos operacionais do OrbitalCore.

    Cada módulo é inicializado com seus valores de consumo definidos
    nas constantes CONSUMO_MODULOS e começa no estado NOMINAL.

    Returns:
        Dicionário mapeando nome do módulo para instância de ModuloEspacial.
    """
    modulos: Dict[str, ModuloEspacial] = {}

    for nome, consumos in CONSUMO_MODULOS.items():
        modulos[nome] = ModuloEspacial(
            nome=nome,
            consumo_nominal=consumos["nominal"],
            consumo_pico=consumos["pico"],
            consumo_standby=consumos["standby"],
            consumo_atual=consumos["nominal"],
            temperatura=20.0,
            status=StatusModulo.NOMINAL,
            ativo=True,
        )

    return modulos


def simular_temperatura(
    tempo_min: float,
    em_sombra: bool,
    modulo: str,
    temp_anterior: float,
) -> float:
    """
    Simula a temperatura de um módulo com inércia térmica realista.

    No espaço, a temperatura varia drasticamente entre sol e sombra,
    mas a inércia térmica do satélite suaviza essas transições.
    Módulos internos (processamento) geram mais calor,
    enquanto módulos externos (sensores) são mais afetados pelo ambiente.

    Args:
        tempo_min: Tempo atual da missão em minutos.
        em_sombra: True se a nave está na sombra da Terra.
        modulo: Nome do módulo ('comunicacao', 'processamento', etc.).
        temp_anterior: Temperatura do módulo no passo anterior (°C).

    Returns:
        Nova temperatura do módulo em °C.
    """
    # Temperaturas-alvo dependendo da condição solar/sombra
    # e do tipo de módulo (cada um tem comportamento térmico distinto)
    temp_alvo_sol = {
        "comunicacao": 35.0,
        "processamento": 55.0,   # CPUs geram muito calor
        "sensores": 25.0,
        "termico": 30.0,
        "painel": 65.0,          # Painéis expostos diretamente ao Sol
    }

    temp_alvo_sombra = {
        "comunicacao": 5.0,
        "processamento": 25.0,   # Calor residual do processamento
        "sensores": -10.0,       # Sensores externos esfriam rápido
        "termico": 10.0,
        "painel": -30.0,         # Painéis expostos ao frio espacial
    }

    # Constante de inércia térmica (quanto maior, mais lenta a mudança)
    # Módulos com mais massa térmica mudam de temperatura mais devagar
    inertia = {
        "comunicacao": 0.08,
        "processamento": 0.06,
        "sensores": 0.12,
        "termico": 0.10,
        "painel": 0.15,
    }

    # Seleciona temperatura-alvo com base na condição solar
    if em_sombra:
        alvo = temp_alvo_sombra.get(modulo, 10.0)
    else:
        alvo = temp_alvo_sol.get(modulo, 30.0)

    # Adiciona variação aleatória para simular perturbações (±2°C)
    variacao = random.uniform(-2.0, 2.0)
    alvo += variacao

    # Aplica inércia térmica: temperatura se aproxima do alvo gradualmente
    taxa = inertia.get(modulo, 0.10)
    nova_temp = temp_anterior + taxa * (alvo - temp_anterior)

    return round(nova_temp, 2)


def simular_missao(
    num_orbitas: int = 10,
    intervalo_min: float = 5.0,
    seed: int = 42,
) -> List[RegistroTelemetria]:
    """
    Simula a missão completa do OrbitalCore por um número de órbitas.

    A simulação percorre cada passo de tempo, calculando:
    - Posição orbital (sol/sombra)
    - Ângulo de incidência solar
    - Temperatura dos módulos e painéis
    - Geração de energia solar
    - Consumo dos módulos com variação realista
    - Estado da bateria (carga/descarga)
    - Geração de alertas quando limites são ultrapassados

    Args:
        num_orbitas: Número de órbitas a simular (padrão: 10).
        intervalo_min: Intervalo entre registros de telemetria em minutos
                       (padrão: 5.0).
        seed: Semente para o gerador aleatório, garantindo
              reprodutibilidade (padrão: 42).

    Returns:
        Lista de RegistroTelemetria com todos os dados da simulação.
    """
    random.seed(seed)

    # Inicializa componentes do sistema
    modulos = criar_modulos()
    painel = PainelSolar()
    bateria = Bateria()
    registros: List[RegistroTelemetria] = []

    # Tempo total da simulação
    tempo_total = num_orbitas * PERIODO_ORBITAL_MIN
    tempo_atual = 0.0

    # Temperaturas iniciais dos módulos
    temperaturas = {nome: 20.0 for nome in modulos}
    temperaturas["painel"] = 25.0

    while tempo_atual < tempo_total:
        # =====================================================================
        # 1. Determina posição orbital (sol/sombra)
        # =====================================================================
        posicao_na_orbita = tempo_atual % PERIODO_ORBITAL_MIN
        em_sombra = posicao_na_orbita >= TEMPO_SOL_MIN
        orbita_atual = int(tempo_atual // PERIODO_ORBITAL_MIN) + 1

        # =====================================================================
        # 2. Calcula ângulo de incidência solar
        # =====================================================================
        if em_sombra:
            angulo_solar = 90.0  # Sem incidência direta
        else:
            # Ângulo varia sinusoidalmente durante o período solar
            # 0° no meio do período solar (máxima eficiência)
            fracao_solar = posicao_na_orbita / TEMPO_SOL_MIN
            angulo_solar = abs(math.sin(math.pi * fracao_solar)) * 30.0
            # Adiciona variação por orientação do satélite (±5°)
            angulo_solar += random.uniform(-5.0, 5.0)
            angulo_solar = max(0.0, min(85.0, angulo_solar))

        # =====================================================================
        # 3. Atualiza temperaturas com inércia térmica
        # =====================================================================
        for nome in modulos:
            temperaturas[nome] = simular_temperatura(
                tempo_atual, em_sombra, nome, temperaturas[nome]
            )
            modulos[nome].temperatura = temperaturas[nome]

        # Temperatura do painel solar
        temperaturas["painel"] = simular_temperatura(
            tempo_atual, em_sombra, "painel", temperaturas["painel"]
        )
        painel.temperatura = temperaturas["painel"]

        # =====================================================================
        # 4. Calcula geração de energia solar
        # =====================================================================
        potencia_gerada = painel.calcular_potencia(angulo_solar, em_sombra)

        # =====================================================================
        # 5. Calcula consumo dos módulos
        # =====================================================================
        consumo_total = 0.0
        for nome, modulo in modulos.items():
            # Fator de carga varia com o tempo para simular atividade real
            fator_base = 0.5 + 0.3 * math.sin(tempo_atual / 30.0)
            fator_variacao = random.uniform(-0.15, 0.15)
            fator_carga = max(0.1, min(1.0, fator_base + fator_variacao))

            modulo.atualizar_consumo(fator_carga)
            consumo_total += modulo.consumo_atual

        # =====================================================================
        # 6. Balanço energético e atualização da bateria
        # =====================================================================
        balanco = potencia_gerada - consumo_total

        if balanco > 0:
            # Excedente vai para a bateria
            bateria.carregar(balanco, intervalo_min)
        else:
            # Déficit é suprido pela bateria
            bateria.descarregar(abs(balanco), intervalo_min)

        # =====================================================================
        # 7. Atualiza status dos módulos
        # =====================================================================
        for nome, modulo in modulos.items():
            temp = modulo.temperatura
            if temp < TEMP_ALERTA_MIN or temp > TEMP_ALERTA_MAX:
                modulo.status = StatusModulo.ALERTA
            elif temp < TEMP_MIN_OPERACIONAL or temp > TEMP_MAX_OPERACIONAL:
                modulo.status = StatusModulo.CRITICO
            else:
                modulo.status = StatusModulo.NOMINAL

        # =====================================================================
        # 8. Geração de alertas
        # =====================================================================
        alertas: List[Alerta] = []

        # Alertas de bateria
        if bateria.soc < SOC_CRITICO:
            alertas.append(Alerta(
                tipo=TipoAlerta.BATERIA_CRITICA,
                mensagem=(
                    f"⚠️ CRÍTICO: Bateria em {bateria.soc_percentual:.1f}% "
                    f"— abaixo do limite crítico de "
                    f"{SOC_CRITICO * 100:.0f}%!"
                ),
                severidade=3,
                tempo_min=tempo_atual,
                modulo="bateria",
                valor=bateria.soc_percentual,
            ))
        elif bateria.soc < SOC_MIN_SEGURO:
            alertas.append(Alerta(
                tipo=TipoAlerta.BATERIA_BAIXA,
                mensagem=(
                    f"⚡ ALERTA: Bateria em {bateria.soc_percentual:.1f}% "
                    f"— abaixo do mínimo seguro de "
                    f"{SOC_MIN_SEGURO * 100:.0f}%."
                ),
                severidade=2,
                tempo_min=tempo_atual,
                modulo="bateria",
                valor=bateria.soc_percentual,
            ))

        # Alertas de temperatura por módulo
        for nome, modulo in modulos.items():
            temp = modulo.temperatura
            if temp > TEMP_ALERTA_MAX:
                alertas.append(Alerta(
                    tipo=TipoAlerta.TEMPERATURA_ALTA,
                    mensagem=(
                        f"🌡️ ALERTA: {nome} a {temp:.1f}°C "
                        f"— acima do limite de {TEMP_ALERTA_MAX}°C."
                    ),
                    severidade=2,
                    tempo_min=tempo_atual,
                    modulo=nome,
                    valor=temp,
                ))
            elif temp < TEMP_ALERTA_MIN:
                alertas.append(Alerta(
                    tipo=TipoAlerta.TEMPERATURA_BAIXA,
                    mensagem=(
                        f"❄️ ALERTA: {nome} a {temp:.1f}°C "
                        f"— abaixo do limite de {TEMP_ALERTA_MIN}°C."
                    ),
                    severidade=2,
                    tempo_min=tempo_atual,
                    modulo=nome,
                    valor=temp,
                ))

        # Alerta de sobrecarga (consumo excede geração e bateria está baixa)
        if balanco < 0 and bateria.soc < SOC_MIN_SEGURO:
            alertas.append(Alerta(
                tipo=TipoAlerta.SOBRECARGA,
                mensagem=(
                    f"⚠️ SOBRECARGA: Consumo ({consumo_total:.0f}W) excede "
                    f"geração ({potencia_gerada:.0f}W) com bateria baixa "
                    f"({bateria.soc_percentual:.1f}%)."
                ),
                severidade=3,
                tempo_min=tempo_atual,
                modulo=None,
                valor=balanco,
            ))

        # =====================================================================
        # 9. Registra telemetria
        # =====================================================================
        registro = RegistroTelemetria(
            tempo_min=round(tempo_atual, 2),
            orbita=orbita_atual,
            em_sombra=em_sombra,
            angulo_solar=round(angulo_solar, 2),
            potencia_gerada_w=round(potencia_gerada, 2),
            consumo_total_w=round(consumo_total, 2),
            balanco_w=round(balanco, 2),
            soc_bateria=round(bateria.soc, 4),
            energia_bateria_wh=round(bateria.energia_atual_wh, 2),
            temperaturas={k: round(v, 2) for k, v in temperaturas.items()},
            status_modulos={
                nome: modulo.status.value for nome, modulo in modulos.items()
            },
            alertas=alertas,
        )
        registros.append(registro)

        tempo_atual += intervalo_min

    return registros


# =============================================================================
# EXECUÇÃO DIRETA (para testes rápidos)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  OrbitalCore — Simulação de Dados da Missão")
    print("=" * 60)
    print()

    registros = simular_missao(num_orbitas=2, intervalo_min=5.0)

    print(f"Total de registros gerados: {len(registros)}")
    print(f"Órbitas simuladas: {registros[-1].orbita}")
    print()

    # Exibe alguns registros de exemplo
    for r in registros[:5]:
        sombra_str = "🌑 Sombra" if r.em_sombra else "☀️ Sol"
        print(
            f"  t={r.tempo_min:6.1f}min | Órbita {r.orbita} | {sombra_str} | "
            f"Geração={r.potencia_gerada_w:6.1f}W | "
            f"Consumo={r.consumo_total_w:6.1f}W | "
            f"SOC={r.soc_bateria * 100:5.1f}%"
        )
        for alerta in r.alertas:
            print(f"    → {alerta.mensagem}")

    print()
    print("  ... (registros omitidos)")
    print()

    # Contagem de alertas
    total_alertas = sum(len(r.alertas) for r in registros)
    print(f"Total de alertas gerados: {total_alertas}")
