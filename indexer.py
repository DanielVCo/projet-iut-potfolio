import os
from dotenv import load_dotenv
from upstash_vector import Index
from langchain_text_splitters import MarkdownHeaderTextSplitter

load_dotenv()

def index_files():
    print("Indexation en cours")

    # Connexion Upstash
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"), 
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )

    # Configuration des dossiers
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    
    # Chunking
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "Category"),
        ("##", "Section"),
    ])

    vectors_to_send = []
    files_a_traiter = ["Bilan2.md", "AProposDeMoi.md", "Bilan1.md", "Stage.md", "CV.md"]

    # Boucle sur les fichiers
    for filename in os.listdir(data_folder):
        if filename in files_a_traiter:
            file_path = os.path.join(data_folder, filename)
            
            try:
                # Lecture
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Découpage
                chunks = splitter.split_text(content)

                # Préparation des données
                for i, chunk in enumerate(chunks):
                    vector_id = f"{filename}_{i}"
                    
                    vectors_to_send.append({
                        "id": vector_id,
                        "data": chunk.page_content,
                        "metadata": {
                            "source": filename,
                            **chunk.metadata
                        }
                    })
                print(f"Fichier préparé : {filename} ({len(chunks)} morceaux)")
            
            except Exception as e:
                print(f"Erreur avec {filename}: {e}")

    # Envoi Upstash
    if vectors_to_send:
        print(f"Envoi de {len(vectors_to_send)} vecteurs")
        
        try:
            index.reset() 
        except:
            pass

        index.upsert(vectors=vectors_to_send)
        print("SUCCÈS ! Tout est sauvegardé dans la base de données.")
    else:
        print("Rien à envoyer.")

if __name__ == "__main__":
    index_files()