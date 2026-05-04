# Define the interface
# Triggers events in the orchestrador based on the users messages

import gradio as gr
from orchestrador import orchestrate

WHATSAPP_CSS = """
body, .gradio-container {
    background: #e5ddd5;
    color: #111;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
}
.gradio-container > .container {
    max-width: 1200px;
    margin: auto;
    padding: 0;
}
.gradio-blocks {
    padding: 0;
}
.wa-app-shell {
    background: #e5ddd5;
    min-height: 100vh;
}
.wa-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #075E54;
    color: white;
    padding: 18px 20px;
    border-radius: 0 0 24px 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.14);
}
.wa-header h1 {
    margin: 0;
    font-size: 1.2rem;
}
.wa-header .wa-subtitle {
    color: #d8eae3;
    margin-top: 4px;
    font-size: 0.95rem;
}
.wa-chat-panel {
    background: #f0f0f0;
    border-radius: 32px;
    padding: 18px;
    min-height: 560px;
    box-shadow: inset 0 2px 0 rgba(255,255,255,0.8);
}
.wa-sidebar {
    background: rgba(255,255,255,0.92);
    border-radius: 28px;
    padding: 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
.wa-input-row {
    gap: 12px;
}
.wa-input-box textarea {
    border-radius: 999px !important;
    padding: 18px 20px !important;
    min-height: 64px !important;
    background: #ffffff !important;
    border: 1px solid #dcdcdc !important;
}
.wa-input-row .gr-button {
    border-radius: 999px;
    background: #25D366;
    color: white;
    border: none;
    min-width: 120px;
}
.gr-chatbot {
    background: transparent !important;
}
.gr-chatbot .message,
.chatbot .message {
    border-radius: 20px;
    padding: 12px 16px;
    margin-bottom: 10px;
    max-width: 72%;
}
.gr-chatbot .message.user,
.chatbot .message.user {
    background: #DCF8C6 !important;
    align-self: flex-end !important;
}
.gr-chatbot .message.assistant,
.chatbot .message.assistant {
    background: white !important;
    align-self: flex-start !important;
}
.gr-chatbot .message .content,
.chatbot .message .content {
    white-space: pre-wrap;
}
.gr-chatbot .message .metadata,
.chatbot .message .metadata {
    display: none;
}
"""

def send_message(message, history, actual_agent):
    """
    Process new incoming user message (Main conversation Route).
    Triggered when the user send a message
    """
    
    # User sends empty message, do nothing
    if not message:
        return "", history, actual_agent
    
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
    event = {"message": message, "history":text_history, "current_agent": actual_agent}
    ai_response, new_agent = orchestrate("new_message", event)
    
    
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
    return "", updated_history, new_agent


def activate_followup(history, actual_agent):
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
    event = {"history": text_history, "current_agent": actual_agent} # No message in the event. The user didn't need to type anything
    ai_response, new_agent = orchestrate("inactive_lead", event)
    
    # Bot initiates the message (no user role). Added visual tag to show it was a system trigger
    updated_history = history + [{"role": "assistant", "content": f"⏳ [SISTEMA: Disparo de Follow-up]\n\n{ai_response}"}]
    
    # Return updated chatbot UI visor
    return updated_history, new_agent


def activate_post_sales(history, actual_agent):
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

    event = {"history": text_history, "current_agent": actual_agent}
    ai_response, new_agent = orchestrate("post_sales", event)
    
    updated_history = history + [{"role": "assistant", "content": f"⏳ [SISTEMA: Disparo de Pós-Venda]\n\n{ai_response}"}]
    return updated_history, new_agent


# INTERFACE CONSTRUCTION (Gradio Blocks)

def build_interface():
    """
    Builds the visual layout and binds the events (clicks/submits) to the Python functions.
    """

    with gr.Blocks(css=WHATSAPP_CSS, theme=gr.themes.Soft(primary_hue="green")) as interface:

        actual_agent = gr.State("classifier")

        with gr.Column(elem_classes="wa-app-shell"):
            gr.HTML(
                "<div class='wa-header'><div><h1>Assistente Pet Shop 🐶</h1><div class='wa-subtitle'>Atendimento estilo WhatsApp</div></div></div>"
            )

            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Column(elem_classes="wa-chat-panel"):
                        chatbot = gr.Chatbot(elem_classes="gr-chatbot", height=560, label="Atendimento")

                    with gr.Row(elem_classes="wa-input-row"):
                        message_box = gr.Textbox(
                            show_label=False,
                            placeholder="Digite sua mensagem...",
                            lines=2,
                            elem_classes="wa-input-box",
                            scale=4
                        )
                        send_button = gr.Button("Enviar ➤", scale=1, variant="primary")

                with gr.Column(scale=1):
                    with gr.Column(elem_classes="wa-sidebar"):
                        gr.Markdown("### ⚙️ Painel de Testes")
                        gr.Markdown("Simule eventos do CRM para testar respostas do assistente em contexto real.")
                        inactive_button = gr.Button("Cliente inativo: Disparar Follow-up")
                        post_sales_button = gr.Button("Serviço concluído: Pós-Venda")


        # Event bindings - UI interactions to the functions (Buttons actions)
        # "inputs" are variables passed to the function, "outputs" are the UI components that get updated. 

        # user presses Enter inside the textbox
        message_box.submit(
            send_message, 
            inputs=[message_box, chatbot, actual_agent], 
            outputs=[message_box, chatbot, actual_agent]
        )
        
        # user presses the Send button
        send_button.click(
            send_message, 
            inputs=[message_box, chatbot, actual_agent], 
            outputs=[message_box, chatbot, actual_agent]
        )
        
        # user presses the Follou-up button
        inactive_button.click(
            activate_followup, 
            inputs=[chatbot, actual_agent], 
            outputs=[chatbot, actual_agent]
        )

        post_sales_button.click(
            activate_post_sales, 
            inputs=[chatbot, actual_agent], 
            outputs=[chatbot, actual_agent]
        )
    return interface