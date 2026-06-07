# 🛰️ OrbitalCore — Sistema de Monitoramento Energético Espacial

## Soluções em Energias Renováveis e Sustentáveis (SER)

> **Global Solution FIAP 2026** — Ciência da Computação

---

## 📋 Descrição

O **OrbitalCore** é um sistema inteligente de monitoramento energético para uma missão espacial experimental em órbita baixa terrestre (LEO — _Low Earth Orbit_). O sistema simula e analisa o balanço energético entre painéis solares e o consumo de um data center orbital, aplicando conceitos de **energia renovável**, **sustentabilidade** e **eficiência energética**.

### Conceitos de Energia Renovável Aplicados

| Conceito                        | Aplicação no OrbitalCore                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Energia Solar Fotovoltaica**  | Painéis GaAs de tripla-junção com 30% de eficiência captando irradiância solar (1361 W/m²) em LEO |
| **Balanço Energético**          | Análise de geração vs. consumo por ciclo orbital (68 min sol + 35 min sombra)                     |
| **Armazenamento de Energia**    | Bateria Li-Ion de 2000 Wh com gerenciamento inteligente de carga/descarga                         |
| **Eficiência Energética (PUE)** | OrbitalCore PUE ~1.05 vs. Data Center terrestre PUE ~1.6                                          |
| **Sustentabilidade**            | 100% energia renovável, zero emissão de CO₂, resfriamento passivo no espaço                       |
| **Smart Grid Espacial**         | Tomada de decisão automatizada para otimização de consumo                                         |

---

## 🚀 Funcionalidades

- **Simulação Orbital Completa**: Simula múltiplas órbitas com dados realistas de geração solar, consumo por módulo, temperatura e bateria.
- **Monitoramento Inteligente**: Sistema de alertas automáticos com classificação `NOMINAL`, `ALERTA` e `CRÍTICO`.
- **Tomada de Decisão Automatizada**: Respostas automáticas a situações críticas (ex: desligar módulos não-essenciais quando bateria baixa).
- **Dashboard Energético**: Visualização completa com gráficos de energia, bateria, temperatura e balanço orbital.
- **Análise de Sustentabilidade**: Métricas de eficiência, CO₂ evitado, PUE e comparativo com data centers terrestres.
- **Relatório Exportável**: Geração de relatório detalhado em formato texto.

---

## 🏗️ Arquitetura do Sistema

```
SER/
├── main.py              # Sistema principal com menu interativo
├── dados_missao.py      # Constantes, dataclasses e simulação orbital
├── energia_solar.py     # Cálculos energéticos e análise de sustentabilidade
├── monitoramento.py     # Sistema de alertas e tomada de decisão
├── visualizacao.py      # Gráficos (Matplotlib + Plotly)
├── requirements.txt     # Dependências Python
├── graficos/            # Gráficos gerados (auto-criado)
└── relatorios/          # Relatórios exportados (auto-criado)
```

---

## 📊 Parâmetros da Missão

| Parâmetro            | Valor         | Descrição                                                |
| -------------------- | ------------- | -------------------------------------------------------- |
| Altitude             | 900 km        | Órbita LEO (T = 2π√(r³/μ), r=7271km)                     |
| Período orbital      | 103 min       | 68 min sol + 35 min sombra                               |
| Potência máx. painel | 1500 W        | Painel GaAs 4m², 30% eficiência                          |
| Irradiância solar    | 1361 W/m²     | Constante solar em LEO                                   |
| Consumo base         | 350 W         | 4 módulos: comunicação, processamento, sensores, térmico |
| Consumo pico         | 450 W         | Carga máxima de processamento                            |
| Bateria              | 2000 Wh       | Li-Ion com eficiência de 95% carga / 98% descarga        |
| Faixa térmica        | -40°C a +85°C | Limites operacionais dos módulos                         |

---

## ⚙️ Como Executar

### Pré-requisitos

- Python 3.10+
- pip (gerenciador de pacotes Python)

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/isaiasg09/orbitalcore-SERS
cd orbitalcore-SERS

# Instalar dependências
pip install -r requirements.txt
```

### Execução

```bash
python main.py
```

### Menu Principal

```
  ┌────────────────────────────────────────────┐
  │         MENU PRINCIPAL                     │
  ├────────────────────────────────────────────┤
  │  [1] 🚀 Executar Simulação Completa        │
  │  [2] 📊 Ver Parâmetros da Missão           │
  │  [3] 📈 Gerar Dashboard de Gráficos        │
  │  [4] 📋 Relatório Energético Detalhado     │
  │  [5] 🌱 Análise de Sustentabilidade        │
  │  [6] 🔄 Comparativo Terrestre vs Orbital   │
  │  [7] ⚙️  Alternar Plotly/Matplotlib         │
  │  [8] 💾 Exportar Relatório                 │
  │  [0] 🚪 Sair                               │
  └────────────────────────────────────────────┘
```

### Alternando entre Matplotlib e Plotly

O sistema suporta dois modos de visualização:

- **Matplotlib** (padrão): Gráficos estáticos de alta qualidade, salvos como PNG.
- **Plotly**: Gráficos interativos que abrem no navegador.

Para alternar, use a opção `[7]` no menu principal, ou edite a variável no topo de `visualizacao.py`:

```python
USAR_PLOTLY = False  # Trocar para True para Plotly
```

---

## 🌱 Sustentabilidade: Por que um Data Center no Espaço?

O OrbitalCore demonstra que data centers orbitais podem ser mais sustentáveis que terrestres:

1. **Energia 100% Solar**: Sem dependência de combustíveis fósseis.
2. **Resfriamento Passivo**: O vácuo espacial elimina a necessidade de sistemas HVAC (que consomem 30-40% da energia de um data center terrestre).
3. **PUE Superior**: ~1.05 no espaço vs. ~1.6 na Terra (quanto mais próximo de 1.0, mais eficiente).
4. **Zero Emissão de CO₂**: Toda energia é renovável e gerada in-situ.

---

## 👥 Integrantes

| RM     | Nome                    |
| ------ | ----------------------- |
| 568990 | Isaías Hörlle Sobral    |
| 570556 | Leandro Cavaccini Brito |
| 568692 | Lucas Dorice Dos Santos |

---

## 📹 Vídeo

[Link do vídeo no YouTube — _não listado_]()

---

## 📄 Licença

Projeto acadêmico — FIAP 2026 — Global Solution
