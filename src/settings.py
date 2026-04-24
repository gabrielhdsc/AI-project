import os
import json
import yaml
from dotenv import load_dotenv
from crewai import Agent, LLM

#Load the API key from .env file and the llm model
load_dotenv()
llm = LLM(model="azure/gpt-4o",
            api_key=os.getenv("AZURE_API_KEY"),
            api_base=os.getenv("AZURE_API_BASE"))


#reading catalog, agents and tasks files
with open('src/catalogo.json', 'r', encoding='utf-8') as f:
    catalogo_str = json.dumps(json.load(f), ensure_ascii=False)

with open('src/config/agents.yaml', 'r', encoding='utf-8') as f:
    configs_agents = yaml.safe_load(f)

with open('src/config/tasks.yaml', 'r', encoding='utf-8') as f:
    configs_tasks = yaml.safe_load(f)


salesperson = Agent(config=configs_agents['sales'], llm=llm)
followup = Agent(config=configs_agents['follow-up'], llm=llm)