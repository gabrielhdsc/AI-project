# Define the interface
# Triggers events in the orchestrador based on the users messages

import gradio as gr
from orchestrador import orchestrate

def send_message(message, history):
    """
    Process new incoming user message (Main conversation Route).
    Triggered when the user send a message
    """
    
    # User sends empty message, do nothing
    if not message:
        return "", history
    
    # Slice the history array to get only the last 10 interactions. Define a "context window" of the 10 last messages (5 user + 5 assistant)
    # This keeps the AI context relevant for chats of message apps
    context_window = history[-6:]

    text_history = ""
    for msg in context_window:
        if msg["role"] == "user":
            text_history += f"Cliente: {msg['content']}\n"

        elif msg["role"] == "assistant":
            # Ignore system logs so it does not confuse the Sales Agent
            if "⏳ [SISTEMA" not in msg["content"]:
                text_history += f"Vendedor: {msg['content']}\n"


    # Build event and send to the orchestrator. Call AI orchestration defining an event of type "new_message"
    event = {"message": message, "history":text_history}
    ai_response = str(orchestrate("new_message", event))
    
    
    # UI checks if the AI decided to call a human
    # if the tag is present it is intercepted that transfer to a human. visual system alert
    if "[HANDOFF]" in ai_response:
        ai_response = "🚨 Atendimento humano acionado. Aguarde por favor"

    # Append the new user message and the AI response to the UI history
    # DO NOT mutate the existing list. Create a new one (User message, assistant answer)
    updated_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": ai_response}
    ]
    
    # Return an empty string (to clear the user's Textbox) and the updated chatbot UI.
    return "", updated_history


def activate_followup(history):
    """
    Simulates a CRM-triggered warning when the lead becomes inactive (Follow-up Route).
    Triggered by the testing panel button.
    """

    context_window = history[-6:]

    text_history = ""
    for msg in context_window:
        if msg["role"] == "user":
            text_history += f"Cliente: {msg['content']}\n"
        elif msg["role"] == "assistant":
            if "⏳ [SISTEMA" not in msg["content"]:
                text_history += f"Vendedor: {msg['content']}\n"

    
    # Define the context for the orchestrator and call it with the specific event
    event = {"history": text_history} # No message in the event. The user didn't need to type anything
    ai_response = str(orchestrate("inactive_lead", event))
    
    # Bot initiates the message (no user role). Added visual tag to show it was a system trigger
    updated_history = history + [{"role": "assistant", "content": f"⏳ [SISTEMA: Disparo de Follow-up]\n\n{ai_response}"}]
    
    # Return updated chatbot UI visor
    return updated_history


def activate_post_sales(history):
    """
    Simulates a CRM trigger after a service is concluded to check client satisfaction.
    """

    context_window = history[-6:]

    text_history = ""
    for msg in context_window: 
        if msg["role"] == "user":
            text_history += f"Cliente: {msg['content']}\n"
        elif msg["role"] == "assistant" and "⏳ [SISTEMA" not in msg["content"]:
            text_history += f"Vendedor: {msg['content']}\n"

    event = {"history": text_history}
    ai_response = str(orchestrate("post_sales", event))
    
    updated_history = history + [{"role": "assistant", "content": f"⏳ [SISTEMA: Disparo de Pós-Venda]\n\n{ai_response}"}]
    return updated_history


# INTERFACE CONSTRUCTION (Gradio Blocks)

def build_interface():
    """
    Builds the visual layout and binds the events (clicks/submits) to the Python functions.
    """

    #theme Soft provides a modern, user-friendly UI instead of the default terminal look
    with gr.Blocks(theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("## 📱🐶 Assistente Comercial de Pet Shop para Apps de Mensagem")
        
        # Chat display component (UI only, not source of truth)
        chatbot = gr.Chatbot(height=450, label="Atendimento")
        
        # User input area
        with gr.Row():
            message_box = gr.Textbox(
                show_label=False, 
                placeholder="Digite sua mensagem...", 
                scale=4
            )
            send_button = gr.Button("Enviar ↗️", scale=1, variant="primary")
            
        gr.Markdown("---")
        

        # Testing panel (simulating CRM behavior)
        gr.Markdown("### ⚙️ Painel de Testes do Sistema")
        inactive_button = gr.Button("Simular: Cliente inativo há 24h (Disparar Follow-up)")
        post_sales_button = gr.Button("Simular: Serviço Concluído (Pós-Venda) ")


        # Event bindings - UI interactions to the functions (Buttons actions)
        # "inputs" are variables passed to the function, "outputs" are the UI components that get updated. 

        # user presses Enter inside the textbox
        message_box.submit(
            send_message, 
            inputs=[message_box, chatbot], 
            outputs=[message_box, chatbot]
        )
        
        # user presses the Send button
        send_button.click(
            send_message, 
            inputs=[message_box, chatbot], 
            outputs=[message_box, chatbot]
        )
        
        # user presses the Follou-up button
        inactive_button.click(
            activate_followup, 
            inputs=[chatbot], 
            outputs=[chatbot]
        )

        post_sales_button.click(
            activate_post_sales, 
            inputs=[chatbot], 
            outputs=[chatbot]
        )
    return interface