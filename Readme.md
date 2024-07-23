# What is Gemini Fornsic Tool .
Gemini Forensic Tool is an application developed in Python that helps forensic doctors perform their work from start to finish. Forensic doctors are health professionals who work on all types of criminal cases and medical or legal investigations. They are responsible for creating medical expert reports for the courts of justice and providing medicolegal advice for health administration or the resolution of litigation.


# Techonolgy.

The main techonlogies use in this application are:
- Python 3.11
- GCP Compute Engine / Vertex Ai
- Docker
- Gemini Studio / GCP Vertex Ai SDK,s and Models. Primarily gemini-1.5-pro-001 and models/text-embedding-004
- Langchain
- Pinecone, Chroma and Faiss
- Streamlit

File requirements.txt [here](requirements.txt)



# Description
Home 
![alt text](docs/images/home.png)

Main Sections
- Maintenance: We can add , modify and delete entries in the tables Propmts, Forensic report and Gemini Annwers.
- Chat Gemini: Here we Interact with the model:
    - 1 Doc+ Prompt: Here you can use a Document (PDF) and a Fix Prompt to extract and Format the extraction. We use this option to extract the factual information we got frpm patients in form or medical reports , prescriptions etc. You Interacts with the llm in a Multimodal Chabot Conversation and refine the answer provided by the model. When you are satisfaced with the answer you can save the conversation answer or abamdone
    - 1 + Documents:  Here you can use multiple documents related to a case or any other topic like medical research or law and dialog with the LLM to extract relevant information. You can decide if later apply the answer/ extraction to a case or no. Also you can decide if save the conversation or no
    - Combine periciales: Here you can combine the Gemini Answers you got from in the previous two options which apply to cases with previous forensic reports where we keep in a pinecone vectore store colection. You can find in the vector Store using Natural Language which previous report suit better the current case you are working on. When you made a search you receive top 5 most similar reports and you can look at their content to decide if that can be use as example. Each report have 5 sections
        - Background Documents: Facts extracted from Documents.
        - Backgroud Doctor: Analisys Provided by Forensic Doctor after analysis of Background Documents.
        - Current Status: Forensic Doctor Observation of the patient for this report.
        - Medico-Legal Considerations: Medical Regulations and Law Framework that apply to the case.
        - Conclusions: Final conclusion for this case. Usually 3 to 4 bulletpoints as summary for the court.
    - Combine KB: Here you can combine Gemini Answers which are not extracted from case documents (like extracted from medical Research, legislation or other) with Previous Forensic Reports. Same than previous but here we combine the sections with External Information we get either from our Knowledge Base or from Extraction in a conversation with Gemini. ALso posible to add information we get from Pubmed or Google Scholar (This need a refinement).
- Periciales: Here we can query our Forensic vector store Database and visualize reports
- Knowledge Base:
    - Search in KB: Here we have created a Knowledge Base from documents. We Initially have upload all legislation and Law that apply to Forensic Medicine into a category, but we can upload documents to other sections. Here you Interact with the model in a conversation and you can decide at the end if to save the whole conversation (only Gemini anwers) or only part to later use it in combine with your current case.
    - Google Scholar: Here we look for relevant Documents, Research and Information related to Medical Conditions , rare topics, law or anything that the Doctor need to support the case. 
    - Pubmed : Here we do the same than with Google Scholar. This section is temporarily hide due to redesing.
    - Add Doc to Kb. Add a new document to a category to the Knowledge Base

# Logging
We use logging capabilties of GCP to keep track of what happens whith the application.
### docs
https://cloud.google.com/logging/docs
### library
https://pypi.org/project/google-cloud-logging/

# Pendings
    - Authentication and Security
    - Setup workflows