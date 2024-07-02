from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.tools.semanticscholar.tool import SemanticScholarQueryRun
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_core.runnables import RunnableParallel


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
