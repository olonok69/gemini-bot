from langchain.prompts import ChatPromptTemplate, PromptTemplate

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
