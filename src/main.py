from orchestrador import orchestrate

# Inicia um chat contínuo no terminal
while True:
    # 1. Aguarda a entrada de dados (simulando o cliente digitando no WhatsApp)
    entrada_usuario = input("\nCliente: ")

    # Condição de parada do teste
    if entrada_usuario.lower() == 'tchau':
        print("Encerrando o sistema...")
        break
        
    # Simulando o CRM avisando que o lead sumiu
    elif entrada_usuario.lower() == 'inativo':
        event = {"ultimo_assunto": "Banho para Poodle"}
        resposta_ia = orchestrate("lead_inativo", event)
        
    # Fluxo normal: Nova mensagem do cliente
    else:
        event = {"mensagem": entrada_usuario}
        resposta_ia = orchestrate("nova_mensagem", event)


    texto_final = str(resposta_ia)

    if "[HANDOFF]" in texto_final:
        # Se a IA inseriu a tag, o sistema bloqueia e chama o humano
        print("\n" + "🚨 "*10)
        print("ALERTA DE HANDOFF: O cliente quer um humano ou saiu do escopo!")
        print("A IA tentou responder isto (mas foi bloqueada):")
        print(f">>> {texto_final}")
        print("🚨 "*10)
        
        # Aqui no mundo real você enviaria uma notificação pro celular do dono
        print("\n[Sistema] Transferindo para atendimento humano. Encerrando automação para este lead.")
        break 
        
    else:
        # Se não houver handoff, envia a mensagem normalmente
        print(f"\n🤖 Assistente: {texto_final}")