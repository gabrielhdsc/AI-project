# Assistente Comercial de Pet Shop

Aplicação demonstrativa de atendimento para pet shop. Ela usa agentes de IA para receber mensagens, identificar a intenção do cliente e gerar respostas adequadas para vendas, suporte e relacionamento pós-venda. A interface é uma conversa web em Gradio, com ações extras que simulam gatilhos de um CRM.

## O que a aplicação cria

Ao iniciar, o projeto disponibiliza uma interface de chat com:

- respostas a mensagens de clientes, roteadas por intenção;
- recomendações de produtos e serviços do catálogo local, incluindo preço e disponibilidade;
- atendimento de dúvidas operacionais, como horário, endereço e trocas;
- uma mensagem de follow-up para contatos inativos há 24 horas;
- uma mensagem de pós-venda para coletar feedback;
- sinalização de encaminhamento para atendimento humano quando necessário.

É um protótipo: não envia mensagens pelo WhatsApp, não grava conversas em banco de dados e os botões de CRM são simulações locais.

## Arquitetura e fluxo

O núcleo da aplicação é o **CrewAI**. Cada atendimento é executado como uma `Crew` com um único agente e uma tarefa construída a partir do contexto atual. O módulo `orchestrador.py` decide qual agente executar e aplica as regras de transferência.

```text
Mensagem do cliente
        |
        v
Classificador
  |       |        |
vendas  suporte  humano
  |
consulta opcional ao catálogo
```

### Agentes

| Agente | Responsabilidade |
| --- | --- |
| `classifier` | Recebe a mensagem, dá boas-vindas quando necessário e classifica a intenção. Não vende. |
| `sales` | Recomenda produtos e serviços, contorna objeções e conduz ao fechamento ou agendamento. |
| `support` | Responde questões operacionais e acolhe reclamações, sem fazer venda. |
| `post_sales` | Solicita feedback após uma compra ou serviço e promove relacionamento. |

As personas estão em `src/config/agents.yaml`, e as instruções e formatos de saída em `src/config/tasks.yaml`.

### Eventos do orquestrador

| Evento | Origem | Efeito |
| --- | --- | --- |
| `new_message` | Campo de mensagem do chat | O classificador escolhe o destino; o agente especializado responde quando há encaminhamento. |
| `inactive_lead` | Botão de teste do CRM | Executa o follow-up pelo agente de vendas. |
| `post_sales` | Botão de teste do CRM | Aciona o agente de pós-venda. |

### Catálogo e contexto

O agente `sales` recebe a ferramenta `Consultar Estoque e Precos`. Quando a conversa envolve produtos, serviços, preço ou disponibilidade, ele pode pesquisar automaticamente `src/catalogo.json` antes de responder. A busca usa uma ou duas palavras-chave e retorna nome, preço, estoque, detalhes e argumentos de venda.

Para manter o prompt compacto, a interface envia apenas as **últimas seis interações do chat** como histórico contextual (3 mensagens do usuário + 3 interações do agente). Registros visuais dos gatilhos de sistema não são enviados ao modelo. Não há persistência em banco de dados: ao recarregar a página, o histórico é perdido.

### Confiabilidade e limites

- Os agentes especializados são instruídos a responder JSON. `parse_json` extrai o bloco entre chaves com regex e o valida com `json.loads`, tolerando respostas que venham envoltas em Markdown.
- Se esse JSON vier vazio ou inválido, o orquestrador tenta uma nova decisão pelo classificador. Caso ele também falhe, devolve uma mensagem de erro genérica.
- O sistema aceita somente `sales`, `support` e `post_sales` como destinos internos; decisões desconhecidas são rejeitadas. `human` produz um handoff terminal.
- Há um limite de `MAX_HANDOFFS = 4` transferências entre agentes para evitar ciclos. Ao excedê-lo, o fluxo é encerrado com encaminhamento humano.
- O handoff é apenas sinalizado na interface por enquanto; a integração com uma fila ou atendente humano real ainda não existe.

## Requisitos

- Python 3.10 ou superior
- Uma implantação Azure OpenAI compatível com o modelo configurado em `src/settings.py`
- CrewAI (framework de orquestração de agentes)
- Gradio (interface web)

## Instalação

No PowerShell, a partir da raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto com as credenciais da sua Azure OpenAI:

```env
AZURE_API_KEY=sua_chave
AZURE_API_BASE=https://seu-recurso.openai.azure.com/
```

Se a sua implantação tiver outro nome, ajuste `model="azure/gpt-4o"` em `src/settings.py`.

## Executar

```powershell
python src/main.py
```

Abra no navegador o endereço local exibido pelo Gradio. Use o campo de texto para conversar e os botões do painel de testes para simular follow-up e pós-venda.

## Como testar

| Objetivo | Mensagem ou ação | Resultado esperado |
| --- | --- | --- |
| Saudação | `Oi` | O classificador cumprimenta e pergunta como pode ajudar. |
| Venda | `Quanto custa o banho para cachorro?` | Roteamento para `sales`, consulta ao catálogo e resposta comercial. |
| Produto esgotado | `Tem ração Gold para gatos?` | `sales` consulta catálogo e informa a indisponibilidade. |
| Suporte | `Qual é o horário de funcionamento?` | Roteamento para `support` e resposta com os dados da loja. |
| Reclamação grave | `Meu pet passou mal depois do serviço e quero falar com alguém.` | Encaminhamento humano. |
| Proteção de loop | Enviar 5+ mensagens que geram transferências contínuas | Após 4 transferências, encaminhamento automático para humano. |
| Follow-up | Clique em **Simular: Cliente inativo há 24h** | Mensagem curta de reengajamento gerada pelo agente de vendas. |
| Pós-venda | Clique em **Simular: Serviço Concluído** | Mensagem de satisfação gerada por `post_sales`. |

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `src/main.py` | Inicializa a interface. |
| `src/interface.py` | Monta o chat Gradio e transforma ações da tela em eventos. |
| `src/orchestrador.py` | Classifica, roteia e controla transferências entre agentes. |
| `src/task_builder.py` | Monta as tarefas do CrewAI com o contexto da conversa. |
| `src/settings.py` | Carrega credenciais, configura o modelo e instancia os agentes. |
| `src/tools.py` | Disponibiliza a busca no catálogo para vendas. |
| `src/catalogo.json` | Dados locais de produtos e serviços. |

## Próximos passos recomendados

- Persistir sessões e histórico em banco de dados ou CRM.
- Substituir o catálogo JSON por uma fonte de estoque e preços em tempo real.
- Adicionar testes para roteamento, parsing de JSON e busca no catálogo.
