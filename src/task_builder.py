from crewai import Task
from settings import configs_tasks, catalogo_str, salesperson, followup


def task_sales(event_data):
    return Task(
        description=configs_tasks['task_sales']['description'].format(
        catalogo=catalogo_str,
        history=event_data.get("history", "Nenhuma conversa anterior, este é o primeiro contato"),
        message=event_data["mensagem"]),
        expected_output=configs_tasks['task_sales']['expected_output'],
        agent=salesperson
    )


def task_followup(event_data):
    return Task(
        description=configs_tasks['task_follow_up']['description'].format(
        catalogo=catalogo_str,
        history=event_data.get("history", "O cliente não mandou nenhuma mensagem clara antes de sumir")),
        expected_output=configs_tasks['task_follow_up']['expected_output'],
        agent=followup
    )