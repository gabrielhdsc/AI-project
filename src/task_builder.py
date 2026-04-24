from crewai import Task
from settings import configs_tasks, catalogo_str, salesperson, followup


def task_sales(event_data):
    return Task(
        description=configs_tasks['task_sales']['description'].format(
        catalogo=catalogo_str,
        mensagem=event_data["mensagem"]),
        expected_output=configs_tasks['task_sales']['expected_output'],
        agent=salesperson
    )


def task_followup(event_data):
    return Task(
        description=configs_tasks['task_follow_up']['description'].format(
        catalogo=catalogo_str,
        last_topic=event_data["ultimo_assunto"]),
        expected_output=configs_tasks['task_follow_up']['expected_output'],
        agent=followup
    )