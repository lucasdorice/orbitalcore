#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Códigos de cor ANSI para o terminal
#define RESET "\033[0m"
#define RED "\033[0;31m"
#define GREEN "\033[0;32m"
#define YELLOW "\033[0;33m"
#define BLUE "\033[0;34m"
#define CYAN "\033[0;36m"
#define BOLD "\033[1m"

#define MAX_LEITURAS 100

// ============================================================================
// ESTRUTURAS DE DADOS
// ============================================================================

// Struct que representa um pacote de telemetria (leitura do satélite)
typedef struct {
    int id;
    float temperatura;
    float energia_pct;     // 0 a 100%
    int comunicacao_ok;    // 1 = OK, 0 = Falha
    char timestamp[20];
} LeituraSensor;

// Variáveis globais para gerenciar o histórico
LeituraSensor historico[MAX_LEITURAS];
int total_leituras = 0;

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

// Pega a hora atual do sistema em formato string
void obter_hora_atual(char* buffer) {
    time_t rawtime;
    struct tm * timeinfo;
    time(&rawtime);
    timeinfo = localtime(&rawtime);
    strftime(buffer, 20, "%H:%M:%S", timeinfo);
}

// Analisa uma única leitura e exibe alertas coloridos
void analisar_leitura(LeituraSensor l) {
    printf("\n" CYAN "--- ANALISANDO LEITURA #%d [%s] ---" RESET "\n", l.id, l.timestamp);
    
    int tudo_ok = 1;

    // 1. Verificação de Temperatura
    if (l.temperatura > 80.0) {
        printf(RED BOLD "[!] ALERTA DE SUPERAQUECIMENTO:" RESET RED " Temp atual = %.1f C\n" RESET, l.temperatura);
        tudo_ok = 0;
    } else {
        printf(GREEN "[OK] Temperatura normal (%.1f C)\n" RESET, l.temperatura);
    }

    // 2. Verificação de Energia
    if (l.energia_pct < 20.0) {
        printf(YELLOW BOLD "[!] ECONOMIA DE ENERGIA ATIVADA:" RESET YELLOW " Energia = %.1f%%\n" RESET, l.energia_pct);
        tudo_ok = 0;
    } else {
        printf(GREEN "[OK] Energia estavel (%.1f%%)\n" RESET, l.energia_pct);
    }

    // 3. Verificação de Comunicação
    if (l.comunicacao_ok == 0) {
        printf(RED BOLD "[!] FALHA DE COMUNICACAO:" RESET RED " Sem conexao com a base.\n" RESET);
        tudo_ok = 0;
    } else {
        printf(GREEN "[OK] Comunicacao operante\n" RESET);
    }

    if (tudo_ok) {
        printf(GREEN BOLD ">>> STATUS GERAL: NORMAL <<<\n" RESET);
    } else {
        printf(RED BOLD ">>> STATUS GERAL: ALERTA/CRITICO <<<\n" RESET);
    }
    printf(CYAN "------------------------------------" RESET "\n");
}

// ============================================================================
// FUNÇÕES DO MENU
// ============================================================================

// Opção 1: Inserir dados manualmente
void inserir_dados_manuais() {
    if (total_leituras >= MAX_LEITURAS) {
        printf(RED "Memoria cheia! Nao e possivel armazenar mais leituras.\n" RESET);
        return;
    }

    LeituraSensor nova;
    nova.id = total_leituras + 1;
    obter_hora_atual(nova.timestamp);

    printf("\n" BOLD "=== INSERIR LEITURA MANUAL ===" RESET "\n");
    
    printf("Temperatura da nave (C): ");
    scanf("%f", &nova.temperatura);
    
    printf("Nivel de energia (%%): ");
    scanf("%f", &nova.energia_pct);
    
    printf("Comunicacao (1=OK, 0=FALHA): ");
    scanf("%d", &nova.comunicacao_ok);

    historico[total_leituras] = nova;
    total_leituras++;
    
    printf(GREEN "Dados salvos com sucesso!\n" RESET);
    analisar_leitura(nova); // Avalia imediatamente após inserir
}

// Opção 2: Simular sensores automaticamente
void simular_sensores() {
    if (total_leituras >= MAX_LEITURAS - 3) {
        printf(RED "Espaco insuficiente para gerar lote de simulacao.\n" RESET);
        return;
    }

    printf("\n" BLUE ">> Gerando dados simulados..." RESET "\n");

    // Mock 1: Tudo Normal
    LeituraSensor l1 = {total_leituras+1, 45.0, 85.0, 1, ""};
    obter_hora_atual(l1.timestamp);
    historico[total_leituras++] = l1;
    analisar_leitura(l1);

    // Mock 2: Superaquecimento + Bateria Baixa
    LeituraSensor l2 = {total_leituras+1, 86.5, 15.0, 1, ""};
    obter_hora_atual(l2.timestamp);
    historico[total_leituras++] = l2;
    analisar_leitura(l2);

    // Mock 3: Falha de Comunicacao
    LeituraSensor l3 = {total_leituras+1, 20.0, 50.0, 0, ""};
    obter_hora_atual(l3.timestamp);
    historico[total_leituras++] = l3;
    analisar_leitura(l3);

    printf(GREEN "3 leituras simuladas adicionadas e analisadas no historico.\n" RESET);
}

// Opção 3: Visualizar Status Atual (Última Leitura)
void visualizar_status() {
    if (total_leituras == 0) {
        printf(YELLOW "Nenhum dado cadastrado ainda.\n" RESET);
        return;
    }
    printf("\n" BOLD "=== STATUS ATUAL (Ultima Leitura) ===" RESET "\n");
    analisar_leitura(historico[total_leituras - 1]);
}

// Opção 4: Mostrar todo o histórico
void mostrar_historico() {
    if (total_leituras == 0) {
        printf(YELLOW "Nenhum dado cadastrado ainda.\n" RESET);
        return;
    }
    
    printf("\n" BOLD "=== HISTORICO DE LEITURAS ===" RESET "\n");
    printf("%-5s | %-10s | %-8s | %-8s | %-12s | %-15s\n", "ID", "HORA", "TEMP(C)", "ENERGIA", "COMUNICACAO", "STATUS");
    printf("---------------------------------------------------------------------------\n");
    
    for (int i = 0; i < total_leituras; i++) {
        char comm_str[10];
        strcpy(comm_str, historico[i].comunicacao_ok ? "OK" : "FALHA");
        
        int tudo_ok = (historico[i].temperatura <= 80.0 && historico[i].energia_pct >= 20.0 && historico[i].comunicacao_ok == 1);
        
        printf("%-5d | %-10s | %-8.1f | %-7.1f%% | %-12s | ", 
               historico[i].id, 
               historico[i].timestamp, 
               historico[i].temperatura, 
               historico[i].energia_pct, 
               comm_str);
               
        if (tudo_ok) {
            printf(GREEN "NORMAL" RESET "\n");
        } else {
            printf(RED "ALERTA/CRITICO" RESET "\n");
        }
    }
}

// ============================================================================
// MAIN (Loop Principal)
// ============================================================================

int main() {
    int opcao;

    printf(BLUE BOLD "===============================================\n" RESET);
    printf(BLUE BOLD "  ORBITALCORE - FIRMWARE DE MONITORAMENTO (C)  \n" RESET);
    printf(BLUE BOLD "===============================================\n" RESET);

    do {
        printf("\n" BOLD "MENU PRINCIPAL:" RESET "\n");
        printf("1. Inserir dados manuais\n");
        printf("2. Simular sensores automaticamente\n");
        printf("3. Visualizar status atual\n");
        printf("4. Historico das leituras\n");
        printf("0. Encerrar sistema\n");
        printf("Escolha uma opcao: ");
        
        // Proteção contra loop infinito em caso de entrada não-inteira
        if (scanf("%d", &opcao) != 1) {
            printf(RED "Entrada invalida! Saindo...\n" RESET);
            break;
        }

        switch(opcao) {
            case 1:
                inserir_dados_manuais();
                break;
            case 2:
                simular_sensores();
                break;
            case 3:
                visualizar_status();
                break;
            case 4:
                mostrar_historico();
                break;
            case 0:
                printf(YELLOW "Encerrando sistemas de monitoramento... Bye!\n" RESET);
                break;
            default:
                printf(RED "Opcao invalida. Tente novamente.\n" RESET);
        }
    } while (opcao != 0);

    return 0;
}
