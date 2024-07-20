from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from operator import itemgetter
from typing import List, Dict
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.tools.semanticscholar.tool import SemanticScholarQueryRun
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_core.runnables import RunnableParallel
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


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


def create_semantic_retrieval_chain(llm, api_wrapper, prompt_query):
    """
    create chain type LLMChain using LCEL
    args:
    llm: LLM model
    api_wrapper: api wrapper
    prompt_query: query prompt

    """
    retrieval_chain = (
        {
            "context": SemanticScholarQueryRun(api_wrapper=api_wrapper),
            "query": RunnablePassthrough(),
        }
        | prompt_query
        | llm
        | StrOutputParser()
    )
    return retrieval_chain


def create_retrieval_qa_source_chain(llm, web_research_retriever):
    """
    create chain type LLMChain using LCEL
    Args:
        llm: LLM model
        web_research_retriever: retriever
    """

    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm, retriever=web_research_retriever
    )
    return qa_chain


def create_Runnable_Parallel_chain(retrieval_chain, qa_chain):
    """
    Create Runnable Parallel to execute chains in Parallel
    Args:
        retrieval_chain: retrieval chain. Semantic serach chain
        qa_chain: qa chain. Google Search chain
    """
    map_chain = RunnableParallel(scholar=retrieval_chain, google=qa_chain)
    return map_chain


def create_combine_parallel_outputs_chain(prompt_last, llm):
    """
    Create chain to combine parallel outputs. From semantic search in Google scholar and Google Search
    Args:
        prompt_last: prompt to combine outputs. Templates.py combine_research_prompt
        llm: LLM model
    """
    second_chain = prompt_last | llm
    return second_chain


def create_complete_chain(map_chain, second_chain):
    """
    Create complete chain. Firch Chain Run in parallel search in Google Scholar and in Google Search Engine, second combine outputs of parallel run
    Args:
        map_chain: Runnable Parallel chain
        second_chain: combine parallel outputs chain

    """
    complete_chain = {
        "question": itemgetter("question"),
        "query": itemgetter("query"),
        "context": map_chain,
    } | RunnablePassthrough.assign(d=second_chain)
    return complete_chain


def function_create_history_aware_retriever(llm, retriever, prompt):
    """
    Create history aware retriever
    Args:
        llm: LLM model
        retriever: retriever
        prompt: contextualize query prompt
    """
    history_aware_retriever = create_history_aware_retriever(llm, retriever, prompt)
    return history_aware_retriever


def function_create_stuff_documents_chain(llm, prompt):
    """
    Create stuff documents chain
    Args:
        llm: LLM model
        prompt: contextualize query prompt
    """
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return stuff_documents_chain


def function_create_retrieval_chain(chain, retriever):
    """
    Create retrieval chain
    Args:
        chain: question_answer_chain
        retriever: retriever
    """
    retrieval_chain = create_retrieval_chain(retriever, chain)
    return retrieval_chain


def create_runnablewithmessagehistory(chain, store: Dict):
    """
    Create Runnable with message history
    Args:
        chain: chain
        store: store
    """

    def get_session_history(session_id: str) -> BaseChatMessageHistory:

        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    conversational_rag_chain = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_rag_chain


def create_conversational_rag_chain(llm, retriever, contex_q_prompt, qaprompt, store):
    """
    Compose all chains in a single function
    Args:
        llm: LLM model
        retriever: retriever
        contextualize_q_prompt: contextualize query prompt
        qa_prompt: qa prompt
        store: store
    """
    # create history aware retriever
    history_aware_retriever = function_create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=contex_q_prompt,
    )

    # create question_answer_chain
    question_answer_chain = function_create_stuff_documents_chain(
        llm=llm, prompt=qaprompt
    )

    # create retrieval chain
    rag_chain = function_create_retrieval_chain(
        chain=question_answer_chain,
        retriever=history_aware_retriever,
    )
    # create runnable with message history
    conversational_rag_chain = create_runnablewithmessagehistory(
        store=store, chain=rag_chain
    )
    return conversational_rag_chain
