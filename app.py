# app.py
from flask import Flask, request, jsonify
from datetime import date
import os
import textwrap
import warnings

# --- Configurações iniciais ---
warnings.filterwarnings("ignore")

# Configurar sua API KEY do Google Gemini
os.environ["GOOGLE_API_KEY"] = "SUA_CHAVE_AQUI"

# SDK Gemini
from google import genai
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Agentes ADK
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

# Função para chamada do agente
def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text + "\n"
    return final_response

# Agente Gemini
def agente_buscador(topico, data_de_hoje):
    buscador = Agent(
        name="agente_buscador",
        model="gemini-2.0-flash",
        instruction="""
Objetivo:
Ajudar o usuário a resolver problemas comuns ou entender melhor um tema técnico, com explicações simples e acessíveis. Você pode usar o google.search.

Regras:
- Forneça respostas claras, passo a passo, como se estivesse explicando para alguém leigo.
- Nunca solicite que o usuário instale programas, execute comandos avançados ou acesse áreas que exigem permissões de administrador.
- Priorize soluções simples, como:
  - Reiniciar o computador
  - Verificar conexões de cabos
  - Ajustar configurações básicas (brilho da tela, volume)
  - Acessar páginas web seguras
- Você está em uma empresa com rede robusta — não sugira reiniciar modem ou roteador doméstico.
- Explique como se fosse para uma criança de 10 anos.
- Corrija erros de digitação e ortografia mantendo o sentido original.
- Dê no máximo 4 soluções e finalize com um link de abertura de chamado e texto sugerido.
- Link: https://centraldeservicos.tce.ap.gov.br/
""",
        description="Agente de suporte técnico",
        tools=[google_search]
    )

    entrada = f"Tópico: {topico}\nData: {data_de_hoje}"
    return call_agent(buscador, entrada)

# --- FLASK APP ---
app = Flask(__name__)

@app.route('/suporte', methods=['POST'])
def suporte():
    data = request.get_json()
    topico = data.get('topico', '').strip()

    if not topico:
        return jsonify({"erro": "Tópico não informado."}), 400

    data_de_hoje = date.today().strftime("%d/%m/%Y")
    resposta = agente_buscador(topico, data_de_hoje)
    return jsonify({"resposta": resposta.strip()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
