from crewai import Crew
from settings import salesperson, followup
from task_builder import task_sales, task_followup


def run_crew(agent, task):
    return Crew(agents=[agent], tasks=[task]).kickoff()


def orchestrate(event_type, event_data):
    if event_type == "nova_mensagem":
        task = task_sales(event_data)
        return run_crew(salesperson, task)

    elif event_type == "lead_inativo":
        task = task_followup(event_data)
        return run_crew(followup, task)

    return "Erro: Tipo de evento desconhecido."