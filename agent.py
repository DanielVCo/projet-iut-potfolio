import os
from dotenv import load_dotenv
from openai import OpenAI
from upstash_vector import Index

load_dotenv()

# Initialiser les connexions
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)
# Création de l'outil
def rechercher_dans_portfolio(question_utilisateur):
    print(f"   🕵️  [Agent] Je cherche l'info sur : '{question_utilisateur}'...")
    resultats = index.query(
        data=question_utilisateur, 
        top_k=3, 
        include_metadata=True,
        include_data=True
    )
    
    contexte_trouve = ""
    for res in resultats:
        if res.data:
            contexte_trouve += f"\n---\nSource : {res.metadata['source']}\nContenu : {res.data}\n"
    
    return contexte_trouve

# Création de l'agent
def discuter_avec_agent():
    print("🤖 L'Agent est prêt ! (Tape 'quit' pour arrêter)")
    
    # Instruction principale donnée à l'IA
    system_prompt = """
    Tu es l'assistant IA de Daniel Vaz Correia. Ton rôle est de répondre aux recruteurs.
    IMPORTANT : Tu dois répondre UNIQUEMENT en utilisant les informations du Contexte fourni.
    Si l'information n'est pas dans le contexte, dis poliment que tu ne sais pas.
    Sois professionnel, concis et agréable.
    """

    while True:
        # L'utilisateur pose une question
        user_input = input("\nRecruteur : ")
        
        if user_input.lower() in ["quit", "exit", "non"]:
            print("Au revoir !")
            break
            
        # L'Agent utilise son TOOL pour récupérer les infos
        contexte = rechercher_dans_portfolio(user_input)
        
        # On envoie le tout à GPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXTE ISSU DE LA BASE DE DONNÉES :\n{contexte}\n\nQUESTION DU RECRUTEUR : {user_input}"}
        ]
        try:
            reponse = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=messages
            )
            
            print(f"🤖 ChatBoy : {reponse.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    discuter_avec_agent()