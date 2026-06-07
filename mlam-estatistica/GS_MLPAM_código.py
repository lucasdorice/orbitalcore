import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. CARREGAMENTO DOS DADOS
# ==========================================
nome_arquivo = "GS_MLPAM_Base_de_Dados.csv"

if not os.path.exists(nome_arquivo):
    raise FileNotFoundError(f"ERRO: O arquivo '{nome_arquivo}' precisa estar na mesma pasta do código.")

# Leitura automatizada
df = pd.read_csv(nome_arquivo, encoding='utf-8', sep=None, engine='python')
df.columns = df.columns.str.strip()

print("✅ Dataset carregado com sucesso!")

# Mapeamento e limpeza das colunas
var_discreta = 'Number of data centre'
nome_coluna_fantasma = df.columns[3]
df = df.rename(columns={nome_coluna_fantasma: 'Consumo_Energia_MWh'})
var_continua = 'Consumo_Energia_MWh'

df[var_continua] = pd.to_numeric(df[var_continua], errors='coerce')
df[var_discreta] = pd.to_numeric(df[var_discreta], errors='coerce')
df = df.dropna(subset=[var_discreta, var_continua])

print(f"📊 Variável Discreta definida: '{var_discreta}'")
print(f"📈 Variável Contínua definida: '{var_continua}'\n")

# ==========================================
# 2. TABELAS DE DISTRIBUIÇÃO DE FREQUÊNCIAS
# ==========================================
print("--- TABELA DE FREQUÊNCIA: VARIÁVEL DISCRETA (Nº de Data Centers) ---")
freq_discreta = df[var_discreta].value_counts().sort_index().to_frame(name='Freq. Absoluta (f)')
freq_discreta['Freq. Relativa (f_r)'] = df[var_discreta].value_counts(normalize=True).sort_index()
freq_discreta['Freq. Acumulada (F)'] = freq_discreta['Freq. Absoluta (f)'].cumsum()
print(freq_discreta.head(10))
print("\n")

print("--- TABELA DE FREQUÊNCIA: VARIÁVEL CONTÍNUA (Consumo Energético) ---")
n = len(df)
k = int(1 + 3.322 * np.log10(n))  # Regra de Sturges

df['classes_continua'] = pd.cut(df[var_continua], bins=k)
freq_continua = df['classes_continua'].value_counts().sort_index().to_frame(name='Freq. Absoluta (f)')
freq_continua['Freq. Relativa (f_r)'] = df['classes_continua'].value_counts(normalize=True).sort_index()
freq_continua['Freq. Acumulada (F)'] = freq_continua['Freq. Absoluta (f)'].cumsum()
print(freq_continua)
print("\n")

# ==========================================
# 3. GERAÇÃO DOS GRÁFICOS OBRIGATÓRIOS
# ==========================================
sns.set_theme(style="whitegrid")

# Gráfico 1: Histograma
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x=var_continua, bins=k, color='royalblue', kde=True)
plt.title('Distribuição Global Estimada de Consumo dos Data Centers', fontsize=13, fontweight='bold')
plt.xlabel('Consumo de Energia (MWh)', fontsize=11)
plt.ylabel('Frequência de Ocorrência', fontsize=11)
plt.tight_layout()
plt.savefig('grafico_histograma.png')
plt.close()

# Gráfico 2: Boxplot Comparativo (Correção do Aviso aplicada aqui)
plt.figure(figsize=(11, 6))
if 'Region' in df.columns:
    top_regioes = df['Region'].value_counts().nlargest(5).index
    df_filtrado = df[df['Region'].isin(top_regioes)].copy()

    # Adicionado o parâmetro 'hue' e 'legend' para evitar o aviso de obsolescência
    sns.boxplot(data=df_filtrado, x='Region', y=var_continua, hue='Region', palette='Set2', legend=False)
    plt.title('Dispersão do Consumo de Energia por Região Geográfica', fontsize=13, fontweight='bold')
    plt.xlabel('Região Geográfica', fontsize=11)
    plt.ylabel('Consumo de Energia (MWh)', fontsize=11)
else:
    sns.boxplot(data=df, y=var_continua, color='seagreen')
    plt.title('Análise de Dispersão Geral do Consumo', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('grafico_boxplot.png')
plt.close()
print("✅ Imagens 'grafico_histograma.png' e 'grafico_boxplot.png' geradas e atualizadas!")

# ==========================================
# 4. ANÁLISE UNIVARIADA (ESTATÍSTICA DESCRITIVA)
# ==========================================
print("\n" + "=" * 50)
print(f"ANÁLISE DESCRITIVA COMPLETA: {var_continua}")
print("=" * 50)

media = df[var_continua].mean()
mediana = df[var_continua].median()
moda = df[var_continua].mode()[0] if not df[var_continua].mode().empty else np.nan
v_max = df[var_continua].max()
v_min = df[var_continua].min()
amplitude = v_max - v_min
variancia = df[var_continua].var()
desvio_padrao = df[var_continua].std()
coef_variacao = (desvio_padrao / media) * 100 if media != 0 else 0
q1 = df[var_continua].quantile(0.25)
q3 = df[var_continua].quantile(0.75)

print(f"-> Média Aritmética: {media:.2f}")
print(f"-> Mediana (Q2):     {mediana:.2f}")
print(f"-> Moda:             {moda:.2f}")
print(f"-> Mínimo / Máximo:  {v_min:.2f} / {v_max:.2f}")
print(f"-> Amplitude Total:  {amplitude:.2f}")
print(f"-> Variância:        {variancia:.2f}")
print(f"-> Desvio Padrão:    {desvio_padrao:.2f}")
print(f"-> Coef. Variação:   {coef_variacao:.2f}%")
print(f"-> Quartis Q1 / Q3:  {q1:.2f} / {q3:.2f}")
print("=" * 50)