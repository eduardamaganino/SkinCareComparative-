import pandas as pd
import matplotlib.pyplot as plt

nome_entrada = 'produtos.csv'

comedogenicos_db = {
    'isopropyl isostearate': 5, 'isopropyl myristate': 5, 'myristyl myristate': 5,
    'algae extract': 5, 'sodium chloride': 5, 'wheat germ oil': 5,
    'coconut oil': 4, 'cocoa butter': 4, 'acetylated lanolin': 4, 'lauric acid': 4,
    'palm oil': 4, 'coconut butter': 4, 'polyglyceryl-3 diisostearate': 4,
    'glyceryl stearate se': 3, 'soybean oil': 3, 'sulfated castor oil': 3, 'myristic acid': 3,
    'stearic acid': 2, 'cetearyl alcohol': 2, 'lanolin': 2, 'decyl oleate': 2,
    'talc': 1, 'mineral oil': 0, 'glycerin': 0, 'water': 0
}

dados_analisados = []
categorias_contagem = {'Seguro': 0, 'Atenção': 0, 'Moderado': 0, 'Crítico': 0}

with open(nome_entrada, 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()
    for linha in linhas[1:]:
        partes = [p.strip() for p in linha.strip().split(',')]
        if len(partes) >= 3:
            marca, produto = partes[0], partes[1]
            composicao = ",".join(partes[2:-1]).replace('"', '').lower()
            ingredientes = [i.strip() for i in composicao.split(',') if i.strip()]
            
            grau_max = 0
            vilao = "Nenhum"
            for ing in ingredientes:
                grau = comedogenicos_db.get(ing, 0)
                if grau > grau_max:
                    grau_max = grau
                    vilao = ing
            
            # Define a fatia
            if grau_max >= 4: cat = 'Crítico'
            elif grau_max == 3: cat = 'Moderado'
            elif grau_max == 2: cat = 'Atenção'
            else: cat = 'Seguro'
            
            categorias_contagem[cat] += 1
            dados_analisados.append({
                'Marca': marca,
                'Produto': produto,
                'ID': f"{marca} - {produto}",
                'Grau': grau_max,
                'Categoria': cat,
                'Ingrediente_Chave': vilao
            })

df = pd.DataFrame(dados_analisados)

def exibir_pizza_geral():
    labels = list(categorias_contagem.keys())
    valores = list(categorias_contagem.values())
    cores = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    
    plt.figure(figsize=(8, 6))
    plt.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, colors=cores, shadow=True)
    plt.title('Distribuição de Comedogenicidade do Catálogo')
    plt.show()

exibir_pizza_geral()

print("\n" + "="*50)
print("       LOCALIZADOR DE PRODUTO NA PIZZA")
print("="*50)
busca = input("Digite o nome do produto para localizar: ").strip().lower()

resultado = df[df['ID'].str.lower().str.contains(busca, regex=False)]

if not resultado.empty:
    res = resultado.iloc[0]
    cor_alerta = {
        'Seguro': '🟢 (VERDE)',
        'Atenção': '🟡 (AMARELO)',
        'Moderado': '🟠 (LARANJA)',
        'Crítico': '🔴 (VERMELHO)'
    }
    
    print(f"\n✅ PRODUTO ENCONTRADO: {res['ID']}")
    print(f"📍 POSIÇÃO NA PIZZA: Este produto está na fatia {cor_alerta[res['Categoria']]}")
    print(f"📊 GRAU DE RISCO: {res['Grau']}/5")
    
    if res['Grau'] > 0:
        print(f"🔍 MOTIVO: Contém o ingrediente '{res['Ingrediente_Chave']}'")
    else:
        print(f"✨ MOTIVO: Não contém ingredientes comedogênicos conhecidos.")
else:
    print("\n[!] Produto não localizado no catálogo.")