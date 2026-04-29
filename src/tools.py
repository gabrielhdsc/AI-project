import json
from crewai.tools import tool

@tool("Consultar Estoque e Precos")
def consult_catalog(search_term: str) -> str:
    """
    Use esta ferramenta SEMPRE que o cliente perguntar sobre produtos, serviços, preços ou o que o petshop vende.
    Passe um termo de pesquisa curto (ex: 'ração', 'banho', 'gold').
    A ferramenta retorna os detalhes, preços e se o item está em estoque.
    """
    print(f"\n[SISTEMA] A IA está pesquisando no catálogo por: '{search_term}'...")
    
    # Consult catalog in real-time
    try:
        with open('src/catalogo.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        return "Erro: Sistema de catálogo fora do ar."
  
    resultados = []
    
    # Search the term in catalog. Ignore upper case
    for item in dados['itens']:
        if search_term.lower() in item['nome'].lower() or search_term.lower() in item['categoria']:
            status = "SIM" if item['em_estoque'] else "ESGOTADO"
            
            info = (
                f"Nome: {item['nome']}\n"
                f"Preço: {item['preco']}\n"
                f"Em Estoque: {status}\n"
                f"Detalhes: {item['detalhes']}\n"
                f"Dica de Venda: {item['objecoes']}\n"
            )
            resultados.append(info)

    # Return the result 
    if resultados:
        return "\n---\n".join(resultados)
    else:
        return f"Não encontramos nenhum item correspondente a '{search_term}' no catálogo. Diga ao cliente que não temos."