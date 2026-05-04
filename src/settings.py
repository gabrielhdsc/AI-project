import os
import json
import yaml
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import consult_catalog

#Load the API key from .env file and the llm model
load_dotenv()
llm = LLM(model="azure/gpt-4o",
            api_key=os.getenv("AZURE_API_KEY"),
            api_base=os.getenv("AZURE_API_BASE"))


#reading agents and tasks files
with open('src/config/agents.yaml', 'r', encoding='utf-8') as f:
    configs_agents = yaml.safe_load(f)

with open('src/config/tasks.yaml', 'r', encoding='utf-8') as f:
    configs_tasks = yaml.safe_load(f)

# Declare agents defined in agents.yaml
classifier = Agent(config=configs_agents['classifier'], llm=llm)
support = Agent(config=configs_agents['support'], llm=llm)
salesperson = Agent(config=configs_agents['sales'], tools=[consult_catalog], llm=llm)
post_sales = Agent(config=configs_agents['post_sales'], llm=llm)


# Pet shop infos
info_store = "Horário de funcionamento: Seg-Sex 08h às 18h. Endereço: Rua dos Pets, 123. Trocas de produtos apenas em até 7 dias."