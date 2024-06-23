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
