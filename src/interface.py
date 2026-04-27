import gradio as gr
from orchestrador import orchestrate

def send_message(message, history):
    """
    Process new incoming user message (Main conversation Route).

    Parameters:
    - message: str -> user input from textbox
    - history: list -> conversation history stored in gr.State

    Returns:
    - empty string to clear textbox
    - updated history for Chatbot UI
    - updated history for State (source of truth)
    """
    
    # User sends empty message = do nothing
    if not message:
        return "", history
    
    # Build event for orchestrator and call AI orchestration layer that calls sales task and agent
    event = {"mensagem": message}
    ai_response = str(orchestrate("nova_mensagem", event))
    
    # Handoff handling by intercepting a specific tag that transfer to a human
    if "[HANDOFF]" in ai_response:
        ai_response = "🚨 Atendimento humano acionado. Aguarde por favor"

    # DO NOT mutate the existing list. Create a new one (User message, bot answer)
    updated_history = history + [
    {"role": "user", "content": message},
    {"role": "assistant", "content": ai_response}]
    
    # Return an empty string (to clear the user's Textbox), updated chatbot UI visor and updated state
    return "", updated_history, updated_history


def activate_followup(history):
    """
    Simulates a CRM-triggered warning when the lead becomes inactive (Follow-up Route).

    Parameters:
    - history: list -> current conversation history

    Returns:
    - updated history for Chatbot UI
    - updated history for State
    """
    
    # Define the context/payload for the orchestrator
    event = {"ultimo_assunto": "Banho para Poodle / Ração"}
    resposta_ia = str(orchestrate("lead_inativo", event))
    
    # Bot initiates the message (no user role)
    updated_history = history + [
    {"role": "assistant", "content": f"⏳ *Follow-up automático*\n\n{resposta_ia}"}]    
    
    # Return updated chatbot UI visor and updated state (no need to clean Textbox)
    return updated_history, updated_history



# INTERFACE CONSTRUCTION (Gradio Blocks)

def build_interface():
    """
    Builds and returns the Gradio interface.
    """

    #theme Soft provides a modern, user-friendly UI instead of the default terminal look
    with gr.Blocks(theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("## 📱🐶 Assistente Comercial de Pet Shop para Apps de Mensagem")

        # This is the TRUE source of conversation state. It persists across user interactions
        state = gr.State([])
        
        # Chat display component (UI only, not source of truth)
        chatbot = gr.Chatbot(height=450, label="Atendimento", type="messages")
        
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


        # Buttons actions (event bindings)

        # user presses Enter inside the textbox
        message_box.submit(
            send_message, 
            inputs=[message_box, state], 
            outputs=[message_box, chatbot, state]
        )
        
        # user presses the Send button
        send_button.click(
            send_message, 
            inputs=[message_box, state], 
            outputs=[message_box, chatbot, state]
        )
        
        # user presses the Follou-up button
        inactive_button.click(
            activate_followup, 
            inputs=[state], 
            outputs=[chatbot, state]
        )

    return interface