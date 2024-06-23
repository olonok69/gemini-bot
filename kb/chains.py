from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


def create_self_query_retriever(llm, vectorstore, query_prompt):
    """
    create chain type SelfQueryRetriever using LCEL
    args:
    llm: LLM model
    vectorstore: vectorstore
    query_prompt: query prompt
    """
    metadata_field_info = [
        AttributeInfo(
            name="filename",
            description="Name of the file to search",
            type="string",
        )
    ]
    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        "Extract information from document ",
        metadata_field_info,
    )
    chain = query_prompt | retriever
    return chain


def create_second_chain(llm, prompt):
    """
    create chain type LLMChain using LCEL
    args:
    llm: LLM model
    prompt: prompt
    """
    chain = prompt | llm
    return chain


def get_complete_chain(llm, vectorstore, query_prompt, prompt):
    """
    complete chain with history and filename
    args:
    llm: LLM model
    vectorstore: vectorstore
    query_prompt: query prompt
    prompt: prompt
    """
    first_chain = create_self_query_retriever(llm, vectorstore, query_prompt)
    second_chain = create_second_chain(llm, prompt)
    complete_chain = {
        "filename": itemgetter("filename"),
        "input": itemgetter("input"),
        "context": first_chain,
    } | RunnablePassthrough.assign(output=second_chain)
    return complete_chain


def get_retrieval_chain(llm, second_prompt, retriever):
    """
    create retrieval chain. Search in the whole docs and combine the result with the second prompt
    Args:
        llm: LLM model
        second_prompt: second prompt
        retriever: retriever
    """
    combine_docs_chain = create_stuff_documents_chain(llm, second_prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    return retrieval_chain
