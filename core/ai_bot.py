import os

from config import GROQ_API_KEY

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from tools.calendar_tools import marcar_consulta_wrapper, ver_horarios_disponiveis
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools.base import ToolException

from prompts.prompts_texts import classification, simple_prompt, complex_prompt
from redis_tools.redis_client_history import add_to_history, get_history

os.environ['GROQ_API_KEY'] = GROQ_API_KEY

str_parser = StrOutputParser()

tools = [marcar_consulta_wrapper, ver_horarios_disponiveis]

model_classification = ChatGroq(
    model='llama-3.1-8b-instant',
    temperature=0.1
)

model_complex = ChatGroq(
    model= 'llama-3.3-70b-versatile',
    temperature=0.1
)

classification_chain = (
    PromptTemplate.from_template(classification)
    | model_classification
    | str_parser
)

simple_chain = (
    PromptTemplate.from_template(simple_prompt)
    | model_classification
    | str_parser
)

agent_prompt = PromptTemplate(
    template=complex_prompt,
    input_variables=["tools", "tool_names", "pergunta", "agent_scratchpad"]
)

agent = create_react_agent(
    llm=model_complex,
    tools=tools,
    prompt=agent_prompt
)

complex_agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    early_stopping_method="generate" 
)

def route(message, classificacao, chat_id=None):
    print(f"\n--- DEBUG: Função route ---")
    print(f"Pergunta recebida na rota: '{message}'")
    print(f"Classificação recebida na rota: '{classificacao}'")

    if "complexa" in classificacao.lower():
        history = "\n".join(get_history(chat_id)) if chat_id else ""
        pergunta_contextualizada = f"{history}\nUsuário: {message}"

        try:
            resposta_dict = complex_agent_executor.invoke({
                "pergunta": pergunta_contextualizada,
                })
            return resposta_dict.get("output", str(resposta_dict))

        except ToolException as e:
            print(f"DEBUG: Capturou ToolException: {e}")
            return str(e)

        except Exception as e:
            print(f"DEBUG: Capturou outra exceção: {e}")
            return "Desculpe, ocorreu um erro inesperado."

    
    elif "simples" in classificacao.lower():
        print("DEBUG: Entrou na lógica 'simples'. Chamando simple_chain.")
        return simple_chain.invoke({'pergunta': message})
    
    else:
        print(f"DEBUG: Classificação não reconhecida: '{classificacao}'. Retornando mensagem padrão.")
        return "Desculpe, não consegui entender a sua pergunta."


class AIBot:
    
    @staticmethod
    def contem_palavras_chave(resposta: str) -> bool:
        palavras_chave = [["consulta"], ["marcada", "agendada"]]
        return all(any(p.lower() in resposta.lower() for p in grupo) for grupo in palavras_chave)


    def classify_question(self, message, chat_id):
        print(f"\n--- DEBUG: classify_question ---")
        print(f"Classificando pergunta: '{message}'")
        print(f"DEBUG: chat_id recebido no webhook: {chat_id}")

        classificacao = classification_chain.invoke({'pergunta': message})
        print(f"Pergunta classificada como: '{classificacao}'")
        return classificacao
        
    def invoke(self, message, chat_id=None):  # adicione chat_id
        print(f"\n--- DEBUG: AIBot.invoke ---")
        print(f"Invocando AIBot com pergunta: '{message}'")

        if chat_id:
            add_to_history(chat_id, f"Usuário: {message}")

        classificacao = self.classify_question(message, chat_id)
        classificacao_str = str(classificacao).strip().lower()

        resposta = route(message, classificacao_str, chat_id=chat_id)

        final_response = str(resposta)
        print(f"DEBUG: Resposta final do AIBot: '{final_response}'")

        if chat_id:
            add_to_history(chat_id, f"Bot: {final_response}")

        print(f"--- FIM AIBot.invoke ---")
        return final_response