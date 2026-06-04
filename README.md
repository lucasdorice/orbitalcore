# 🛰️ OrbitalCore

> **Data Center Espacial em Órbita Baixa (LEO)**  
> Global Solution — Space Connect | FIAP · 1º Semestre · Ciência da Computação · 2026

---

## 🌐 Visão Geral

**OrbitalCore** é uma plataforma de Data Center Espacial que propõe transferir infraestrutura de processamento e armazenamento de dados para satélites em órbita baixa terrestre (LEO, ~550 km de altitude).

A solução ataca três problemas estruturais dos data centers terrestres atuais:

| Problema (DC Terrestre) | Solução (OrbitalCore) |
|---|---|
| Refrigeração representa ~40% do custo energético | Resfriamento passivo pelo vácuo espacial — custo zero |
| Dependência da rede elétrica convencional | Painéis solares em LEO, até 8× mais eficientes (sem atmosfera) |
| Ocupação de espaço físico urbano | Infraestrutura em órbita — zero impacto territorial |

> Data centers consomem cerca de 1% de toda a eletricidade mundial. O OrbitalCore propõe uma alternativa sustentável, escalável e alinhada ao futuro da computação em nuvem.

---

## 🏗️ Arquitetura

O sistema é dividido em três camadas:

```
┌─────────────────────────────────────────────┐
│              CAMADA 1 — ESPAÇO (LEO)        │
│  Painéis solares · Servidores embarcados    │
│  Resfriamento passivo · Sensores IoT        │
│  Mission Control AI · Modelo ML             │
└──────────────────┬──────────────────────────┘
                   │ Laser óptico (~5 ms)
┌──────────────────▼──────────────────────────┐
│           CAMADA 2 — COMUNICAÇÃO            │
│     Downlink (telemetria) / Uplink (cmds)   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            CAMADA 3 — TERRA                 │
│  Ground Station · Dashboard Python          │
│  Failover DC · Análise estatística          │
│  Modelagem matricial · Usuários finais      │
└─────────────────────────────────────────────┘
```

---

## 📁 Estrutura do Repositório

```
orbitalcore/
├── README.md                        # Este arquivo
│
├── coa-iot/                         # COA — Simulação IoT (Wokwi/Tinkercad)
│   └── wokwi_link.md                # Link da simulação + prints
│
├── dsa-c/                           # DSA — Sistema de monitoramento em C
│   ├── mission_control.c
│   └── README.md
│
├── cs-jupyter/                      # CS — Pipeline de Ciência de Dados
│   ├── orbitalcore_pipeline.ipynb
│   └── dataset_simulado.csv
│
├── pcap-python/                     # PCAP — Central de missão em Python
│   ├── central_missao.py
│   └── README.md
│
├── pai-ai/                          # PAI — Análise inteligente com LLM
│   ├── mission_ai.py
│   └── prompts/
│
├── mlam-estatistica/                # MLAM — Análise estatística descritiva
│   └── analise_eficiencia.ipynb
│
├── mmc-matematica/                  # MMC — Transformação linear matricial
│   └── transformacao_orbital.ipynb
│
├── ser-energia/                     # SER — Balanço energético orbital
│   └── balanco_energetico.py
│
└── simulacao-3d/                    # Visualização interativa do sistema
    └── index.html
```

---

## 🔬 Módulos por Disciplina

### 🖥️ COA — Computer Organization and Architecture
Simulação IoT do satélite no **Wokwi/Tinkercad**. O microcontrolador representa o computador de bordo da cápsula, com sensores de temperatura (servidores), luminosidade (painéis solares) e vibração (giroscópio), exibindo dados em tempo real em um display.

### ⚙️ DSA — Data Structures and Algorithms
Núcleo de monitoramento em **C**. Recebe dados dos sensores via structs e vetores, classifica o estado operacional (normal / alerta / crítico) e exibe análise em tempo real — o "firmware" do satélite.

### 📊 CS — Computer Science
Pipeline completo de ciência de dados em **Jupyter Notebook (Python)**. Inclui EDA, pré-processamento, treinamento de modelo de classificação (Random Forest / KNN) e simulação de deploy para classificar o estado operacional do DC orbital.

### 🐍 PCAP — Pensamento Computacional e Automação com Python
Central de missão em **Python puro**. Organiza os 5 parâmetros do DC (temperatura, comunicação, energia solar, processamento, latência) em uma matriz de ciclos de missão, gera alertas automáticos e calcula o índice de risco operacional.

```python
ciclos = [
    # [temp_C, comunicacao_%, energia_%, processamento_%, latencia_ms]
    [45, 98, 87, 60, 4.2],
    [72, 95, 81, 88, 5.1],  # alerta de temperatura
    [38, 99, 92, 45, 3.9],
]
```

### 🤖 PAI — Prompt and Artificial Intelligence
Sistema de análise inteligente que usa engenharia de prompts com um **LLM (Llama / open source)** para gerar diagnósticos em linguagem natural a partir da telemetria — previsão de falhas e recomendações de ação automáticas.

### 📈 MLAM — Modelagem Linear para Aprendizado de Máquina
Análise estatística descritiva em **Python**: distribuição de frequência, histogramas, boxplots, scatter plots e medidas descritivas (média, mediana, desvio padrão, percentis) comparando o DC orbital com data centers terrestres.

### 🔢 MMC — Modelagem Matemática e Computacional
Transformação linear matricial aplicada aos dados do satélite em **Python**: normalização de leituras, ajuste de painéis solares por ângulo de incidência e modelagem de eficiência energética por região orbital.

### ⚡ SER — Soluções em Energias Renováveis e Sustentáveis
Modelagem do sistema energético orbital em **Python**: potência gerada pelos painéis em LEO, consumo dos servidores, balanço energético e comparativo de sustentabilidade com DCs terrestres convencionais.

---

## 🎯 Simulação Visual

O diretório `simulacao-3d/` contém uma aplicação web interativa que demonstra o DC orbital em funcionamento, com telemetria simulada em tempo real e o painel de controle da ground station.

---

## 👥 Equipe

Trio de estudantes do **1º semestre de Ciência da Computação** — FIAP, São Paulo, Brasil.

---

## 📅 Prazo de Entrega

**09 de junho de 2026 às 23h55** — Portal do Aluno (entrega por disciplina + pitch para o Scrum Master)

---

## 🔗 Referências e Inspirações

- [Lonestar Data Holdings](https://www.lonestar.io/) — Data center na Lua
- [OrbitsEdge](https://orbitsedge.com/) — Infraestrutura de borda orbital
- FIAP Global Solution 2026 — Case *Mission Control AI / Space Connect*
