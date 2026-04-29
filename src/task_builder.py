# Python functions that inject dynamic data into YAML tasks
# It instantiates the Tasks by formatting the strings from the YAML file with dynamic data

from crewai import Task
from settings import configs_tasks, salesperson, classifier, support, post_sales, info_store


def task_classifier(event_data):
    """
    Takes event_data (a dictionary containing the chat history and new message)
    and maps it to the {history} and {message} variables in the tasks.YAML.
    """
    return Task(
        description=configs_tasks['task_classifier']['description'].format(
            # .get() to prevent crashes if the key doesn't exist.
            # If "history" is empty or missing, it defaults to the string after the comma.
            history=event_data.get("history", "Nenhuma conversa anterior, este é o primeiro contato"),
            message=event_data.get("message", "")
        ),
        expected_output=configs_tasks['task_classifier']['expected_output'],
        agent=classifier
    )

def task_sales(event_data):
    return Task(
        description=configs_tasks['task_sales']['description'].format(
            history=event_data.get("history", "Nenhuma conversa anterior, este é o primeiro contato"),
            message=event_data.get("message", "")
        ),
        expected_output=configs_tasks['task_sales']['expected_output'],
        agent=salesperson
    )


def task_followup(event_data):
    return Task(
        description=configs_tasks['task_follow_up']['description'].format(
            history=event_data.get("history", "O cliente não mandou nenhuma message clara antes de sumir")
            # No message variable, trigger is a timeout
        ),
        expected_output=configs_tasks['task_follow_up']['expected_output'],
        agent=salesperson
    )


def task_support(event_data):
    return Task(
        description=configs_tasks['task_support']['description'].format(
            info_store = info_store, # Injects the store infos
            history=event_data.get("history", "Nenhuma conversa anterior, este é o primeiro contato"),
            message=event_data.get("message", "")
        ),
        expected_output=configs_tasks['task_support']['expected_output'],
        agent=support
    )

def task_post_sales(event_data):
    return Task(
        description=configs_tasks['task_post_sales']['description'].format(
          history=event_data.get("history", "Nenhuma conversa anterior, este é o primeiro contato"),
           # No message variable, trigger is time
        ),
        expected_output=configs_tasks['task_post_sales']['expected_output'],
        agent=post_sales
    )