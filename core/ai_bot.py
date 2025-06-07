import os

from config import GROQ_API_KEY

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from tools.calendar_tools import marcar_consulta_wrapper, ver_horarios_disponiveis
from langchain.agents import create_react_agent, AgentExecutor
from prompts.prompts_texts import classification, simple_prompt, complex_prompt

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
    handle_parsing_errors=True
)

def route(message, classificacao):
    print(f"\n--- DEBUG: Função route ---")
    print(f"Pergunta recebida na rota: '{message}'")
    print(f"Classificação recebida na rota: '{classificacao}'")

    if "complexa" in classificacao.lower():
        print("DEBUG: Entrou na lógica 'complexa'. Chamando complex_chain.")
        resposta_dict = complex_agent_executor.invoke({"pergunta": message})
        return resposta_dict.get("output", str(resposta_dict))

    
    elif "simples" in classificacao.lower():
        print("DEBUG: Entrou na lógica 'simples'. Chamando simple_chain.")
        return simple_chain.invoke({'pergunta': message})
    
    else:
        print(f"DEBUG: Classificação não reconhecida: '{classificacao}'. Retornando mensagem padrão.")
        return "Desculpe, não consegui entender a sua pergunta."


class AIBot:

    def __init__(self):
        self.__chat = model_classification 

    def classify_question(self, message):
        print(f"\n--- DEBUG: classify_question ---")
        print(f"Classificando pergunta: '{message}'")
        classificacao = classification_chain.invoke({'pergunta': message})
        print(f"Pergunta classificada como: '{classificacao}'")
        return classificacao
        
    def invoke(self, message):
        print(f"\n--- DEBUG: AIBot.invoke ---")
        print(f"Invocando AIBot com pergunta: '{message}'")
        classificacao = self.classify_question(message)
        
        # Isso é importante para evitar problemas de tipo na função route.
        classificacao_str = str(classificacao).strip().lower() 
        print(f"Classificação após tratamento: '{classificacao_str}' (Tipo: {type(classificacao_str)})")
        
        resposta = route(message, classificacao_str)
    
        final_response = str(resposta) 
        print(f"DEBUG: Resposta final do AIBot: '{final_response}'")
        print(f"--- FIM AIBot.invoke ---")
        return final_response