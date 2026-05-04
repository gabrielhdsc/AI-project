import json
from crewai.tools import tool

@tool("Consultar Estoque e Precos")
def consult_catalog(search_term: str) -> str:
    """
    Use esta ferramenta SEMPRE para pesquisar sobre produtos, serviços, preços no catálogo ou o que o petshop vende.
    REGRA DE OURO: Pesquise usando apenas UMA ou DUAS palavras-chave simples por vez (ex: 'racao', 'cachorro', 'gato', 'consulta', 'banho'). 
    Nunca pesquise frases inteiras como 'produto cachorro'.
    """
    print(f"\n[SISTEMA] A IA está pesquisando no catálogo por: '{search_term}'...")
    
    # Consult catalog in real-time
    try:
        with open('src/catalogo.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Erro: Sistema de catálogo fora do ar."
  
    results = []
    
    # Split words used in AI search ("produto cachorro" turns into ["produto", "cachorro"])
    search_words = search_term.lower().split()


    # Search the term in catalog. Ignore upper case
    for item in data['itens']:
        # Put all item information togheter
        item_text = f"{item['nome']} {item['categoria']} {item['detalhes']} {item['id']}".lower()

        # Verifies if at least one search_words matches with the words from item_text
        if any(text in item_text for text in search_words):
            status = "SIM" if item['em_estoque'] else "ESGOTADO"
            
            info = (
                f"Nome: {item['nome']}\n"
                f"Preço: {item['preco']}\n"
                f"Em Estoque: {status}\n"
                f"Detalhes: {item['detalhes']}\n"
                f"Dica de Venda: {item['objecoes']}\n"
            )
            results.append(info)

    # Return the result 
    if results:
        return "\n---\n".join(results)
    else:
        return f"Não encontramos nenhum item correspondente a '{search_term}' no catálogo. Diga ao cliente que não temos."