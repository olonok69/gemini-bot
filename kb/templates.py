from langchain.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder

first_prompt = ChatPromptTemplate.from_template(
    "Dame la Tabla de perjuicios particulares de las {filename}"
)  # Tablas_indemnizatorias_Baremo_2024.pdf

query_prompt = ChatPromptTemplate.from_template("extrae {input} de  {filename}")

template = """
                You are a helpful AI assistant. Answer based on the context provided. 
                In your response, include the context and document reference. 
                context: {context}
                input: {input}
                answer:
                """
second_prompt = PromptTemplate.from_template(template)


template_semantic = """ Question: {query} 
                {context}
                    with the context build a response with the following requirements:
                    - Show me a list of papers and techniques. 
                    - Based on your findings write a description, main symptoms and how to treat them
                    - Create 3 different sections: List of papers, Description/ symptoms and treatment. 
                  
"""

semantic_query = ChatPromptTemplate.from_template(template_semantic)


template_last = """
you are a researcher wich take diferent inputs and combine the to provide an anwers
instruction to build the final answer to the question{question}
from {context}
- extract 2 dictionaries with keys scholar and google 
- content of scholar is the input 1
- from dictionary google extract the key answer and this is the input 2
- with the input 1 and input2  build a final answer in human languange 
"""
combine_research_prompt = ChatPromptTemplate.from_template(template_last)


### Contextualize question ###
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

### Answer question ###
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "if the language use it is not english, dont translate to english your answer"
    "\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
