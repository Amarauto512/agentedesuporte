import subprocess
subprocess.run(["pip", "install", "--upgrade", "google-generativeai==0.3.2"], check=True)

from flask import Flask, request, jsonify
from datetime import date
import os
import warnings

warnings.filterwarnings("ignore")

# Configurar chave da API do Gemini (vem da variável de ambiente)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
import subprocess
subprocess.run(["pip", "install", "--upgrade", "google-generativeai==0.3.2"])

from google.generativeai import configure
configure(api_key=os.environ["GOOGLE_API_KEY"])

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

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

def agente_buscador(topico, data_de_hoje):
    buscador = Agent(
        name="agente_buscador",
        model="gemini-2.0-flash",
        instruction="""Ajudar o usuário a resolver problemas comuns com soluções simples. 
Não use termos técnicos complicados. Dê no máximo 4 sugestões e finalize com o link: 
https://centraldeservicos.tce.ap.gov.br/""",
        description="Agente de suporte técnico",
        tools=[google_search]
    )
    entrada = f"Tópico: {topico}\nData: {data_de_hoje}"
    return call_agent(buscador, entrada)

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
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

