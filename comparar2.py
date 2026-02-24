import pandas as pd
import matplotlib.pyplot as plt

nome_entrada = 'produtos.csv'
dados_processados = []

with open(nome_entrada, 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()
    for i, linha in enumerate(linhas[1:]):
        partes = [p.strip() for p in linha.strip().split(',')]
        if len(partes) >= 4:
            marca = partes[0]
            produto_original = partes[1]
            preco_str = partes[-1]
            composicao_bruta = ",".join(partes[2:-1]).replace('"', '')
            
            lista_ingredientes = [ing.strip().lower() for ing in composicao_bruta.split(',') if ing.strip()]
            
            try:
                preco_limpo = preco_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
                preco = float(preco_limpo)
            except:
                preco = 0.0
            
            dados_processados.append({
                'Marca': marca,
                'Produto': produto_original,
                'ID': f"{marca} ({produto_original})",
                'lista_ing': lista_ingredientes,
                'Preco': preco
            })

df = pd.DataFrame(dados_processados)

def calcular_similaridade_posicional(l1, l2):

    if not l1 or not l2: return 0
    
    set1, set2 = set(l1), set(l2)
    comuns = set1.intersection(set2)
    
    if not comuns: return 0
    
    score_total = 0
    tamanho_max = max(len(l1), len(l2))
    
    for ingrediente in comuns:
        pos1 = l1.index(ingrediente)
        pos2 = l2.index(ingrediente)
        
        # Peso baseado na importância (quem está no topo vale mais)
        peso_posicao = (tamanho_max - pos1) + (tamanho_max - pos2)
        
        distancia = abs(pos1 - pos2)
        
        score_ingrediente = peso_posicao / (1 + distancia)
        score_total += score_ingrediente


    max_score = sum([( (tamanho_max - i) + (tamanho_max - i) ) for i in range(len(l1))])
    
    final_score = (score_total / (max_score / 1)) * 100
    return round(final_score, 1)

print("\n" + "="*40)
print("     BUSCADOR DE SIMILARES (ORDENADO)")
print("="*40)
termo_busca = input("Digite o nome (ou parte do nome) do produto: ").strip()

alvo_matches = df[df['Produto'].str.contains(termo_busca, case=False, na=False, regex=False)]

if alvo_matches.empty:
    print(f"\n[!] Erro: Não encontrei '{termo_busca}'.")
else:
    prod_alvo = alvo_matches.iloc[0]
    print(f"\n>>> SELECIONADO: {prod_alvo['Marca']} - {prod_alvo['Produto']}")
    print(f">>> PREÇO: R$ {prod_alvo['Preco']:.2f}")
    
    resultados = []
    for i, linha in df.iterrows():
        if linha['Marca'].lower() != prod_alvo['Marca'].lower():
            score_porcentagem = calcular_similaridade_posicional(prod_alvo['lista_ing'], linha['lista_ing'])
            
            if score_porcentagem > 5.0: # Filtro de similaridade mínima
                diff = linha['Preco'] - prod_alvo['Preco']
                resultados.append({
                    'Concorrente': linha['ID'],
                    'Similaridade %': score_porcentagem, 
                    'Preco': linha['Preco'],
                    'Economia': round(-diff, 2)
                })

    if not resultados:
        print("\nNenhum similar de outra marca encontrado com essa lógica de ordem.")
    else:
        df_res = pd.DataFrame(resultados).sort_values(by='Similaridade %', ascending=False)
        print("\n--- TOP SIMILARES ENCONTRADOS (POR ORDEM DE COMPOSIÇÃO) ---")
        print(df_res[['Concorrente', 'Similaridade %', 'Preco', 'Economia']].head(10).to_string(index=False))

        plt.figure(figsize=(12, 6))
        top_plot = df_res.head(10)
        cores = ['#2ecc71' if x >= 0 else '#e74c3c' for x in top_plot['Economia']]
        
        bars = plt.barh(top_plot['Concorrente'], top_plot['Similaridade %'], color=cores)
        
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                     f'{width}%', va='center', fontweight='bold')

        plt.xlabel('Similaridade Ponderada por Ordem (%)')
        plt.xlim(0, 110)
        plt.title(f'Similaridade Real: {prod_alvo["Produto"]}\n(Leva em conta a concentração dos ingredientes)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()