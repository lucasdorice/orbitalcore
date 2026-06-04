# Fluxograma do Sistema DSA (Firmware C)

Abaixo o diagrama lógico da arquitetura do `firmware.c`, explicando a dinâmica de menus, estruturas e análise condicional.

```mermaid
flowchart TD
    A([Início do Sistema]) --> B{Menu Principal\n(do-while)}
    
    B -->|Opção 1| C[Inserir Dados Manuais]
    B -->|Opção 2| D[Simular Sensores]
    B -->|Opção 3| E[Visualizar Status Atual]
    B -->|Opção 4| F[Histórico de Leituras]
    B -->|Opção 0| G([Fim / Encerrar])
    
    C --> H[Preencher Struct LeituraSensor\nscanf()]
    H --> I[Salvar no Vetor historico[]]
    I --> J[Analisar Leitura]
    
    D --> K[Criar 3 Mocks Automáticos]
    K --> L[Salvar no Vetor historico[]]
    L --> B
    
    E --> M{Vetor está vazio?}
    M -->|Sim| N[Aviso: Nenhum Dado]
    M -->|Não| O[Recuperar historico[total_leituras - 1]]
    O --> J
    N --> B
    
    F --> P{Vetor está vazio?}
    P -->|Sim| Q[Aviso: Nenhum Dado]
    P -->|Não| R[Laço FOR do índice 0 até total_leituras]
    R --> S[Imprimir Tabela Formatada]
    S --> B
    Q --> B
    
    %% Bloco de Análise Detalhada
    J --> T{Temp > 80?}
    T -->|Sim| U[Print Alerta Vermelho]
    T -->|Não| V[Print OK Verde]
    
    U --> W{Energia < 20?}
    V --> W
    
    W -->|Sim| X[Print Economia Amarelo]
    W -->|Não| Y[Print OK Verde]
    
    X --> Z{Comunicação == 0?}
    Y --> Z
    
    Z -->|Sim| AA[Print Falha Vermelho]
    Z -->|Não| AB[Print OK Verde]
    
    AA --> AC[Exibir STATUS GERAL]
    AB --> AC
    AC --> B
```

### Explicação da Lógica Utilizada (Critério de Avaliação 3)

1. **Laço Principal (`do-while`)**: Garante que o menu continue aparecendo até que o usuário decida explicitamente encerrar (Opção 0).
2. **Estrutura de Dados (`struct`)**: A telemetria foi agrupada em um pacote único (`id, temp, energia, comm, timestamp`). Isso mantém os dados concisos e evita usar variáveis soltas espalhadas pelo código.
3. **Vetor (`historico[]`)**: Armazena sequencialmente as estruturas inseridas (tanto manualmente quanto por simulação). Como na linguagem C arrays não possuem métodos nativos `.push()` (como em JS), o índice é controlado pela variável `total_leituras`.
4. **Análise Sequencial (`if-else`)**: A função `analisar_leitura()` processa regras de negócios preestabelecidas (T>80, E<20, C=0) sequencialmente sem o uso de `else-if` encadeados na mesma condicional, garantindo que TODOS os parâmetros (temperatura, bateria E comunicação) sejam verificados para cada pacote.
