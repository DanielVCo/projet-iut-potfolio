import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from upstash_vector import Index

load_dotenv()

st.set_page_config(page_title="ChatBoy - Daniel", page_icon="🤖")

# Connexions
@st.cache_resource
def get_clients():
    try:
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        upstash_index = Index(
            url=os.getenv("UPSTASH_VECTOR_REST_URL"),
            token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        )
        return openai_client, upstash_index
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None, None

client, index = get_clients()

# Fonction de recherche (RAG)
def search_vector_db(query):
    if not index: return ""
    res = index.query(data=query, top_k=3, include_metadata=True, include_data=True)
    context = ""
    for r in res:
        if r.data:
            context += f"\n---\nSource: {r.metadata.get('source', 'Inconnu')}\nContenu: {r.data}\n"
    return context

# Interface Utilisateur
st.title("🤖 ChatBoy Daniel")
st.markdown("Posez-moi des questions sur mon parcours, mes stages ou mes projets !")

# historique
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Votre question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Je recherche dans le portfolio..."):
            #Recherche dans Upstash
            contexte = search_vector_db(prompt)
            
            # Préparation du prompt pour GPT
            system_prompt = """
            Tu es l'assistant virtuel de Daniel. Tu réponds aux recruteurs.
            Utilise le contexte fourni pour répondre. Si tu ne sais pas, dis-le.
            Sois professionnel et concis.
            """
            
            messages_gpt = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexte:\n{contexte}\n\nQuestion: {prompt}"}
            ]

            # Appel à OpenAI 
            try:
                stream = client.chat.completions.create(
                    model="gpt-4.1-nano", 
                    messages=messages_gpt,
                    stream=True
                )
                response = st.write_stream(stream)
            except Exception as e:
                response = "Désolé, une erreur est survenue."
                st.error(e)

    # On sauvegarde la réponse
    st.session_state.messages.append({"role": "assistant", "content": response})