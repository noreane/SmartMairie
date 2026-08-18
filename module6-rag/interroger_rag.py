"""Interrogation RAG - Module 6 (Smart Mairie) : Pose une question en langage naturel, recherche les documents les
plus pertinents dans la base vectorielle ChromaDB (créée par indexer_rag.py), puis genere une reponse via un LLM local (Ollama)
en s'appuyant sur ces documents. """

import os
import ollama
import chromadb

DOSSIER_CHROMA = os.path.join("module6-rag", "chroma_db")
MODELE_EMBEDDING = "nomic-embed-text"
MODELE_LLM = "llama3.2:3B"
NOM_COLLECTION = "documents_mairie"
NB_DOCUMENTS_RECUPERES = 4


def rechercher_documents(question: str, collection) -> list[str]:
    """Trouve les documents les plus proches de la question."""
    reponse = ollama.embeddings(model=MODELE_EMBEDDING, prompt=question)
    vecteur_question = reponse["embedding"]

    resultats = collection.query(
        query_embeddings=[vecteur_question],
        n_results=NB_DOCUMENTS_RECUPERES,
    )

    return resultats["documents"][0] if resultats["documents"] else []


def generer_reponse(question: str, documents_contexte: list[str]) -> str:
    """Genere une reponse via le LLM local, en s'appuyant sur le contexte."""
    contexte = "\n\n---\n\n".join(documents_contexte)

    prompt = f"""Tu es un assistant qui aide les agents d'une mairie a retrouver
des informations dans leurs documents administratifs.

Voici des extraits de documents pertinents :

{contexte}

Question : {question}

Reponds uniquement a partir des informations ci-dessus. Si tu ne trouves
pas la reponse dans ces extraits, dis-le clairement plutot que d'inventer."""

    reponse = ollama.generate(model=MODELE_LLM, prompt=prompt)
    return reponse["response"]


def poser_question(question: str):
    if not os.path.exists(DOSSIER_CHROMA):
        print("[ERREUR] Base vectorielle introuvable. Lance d'abord indexer_rag.py")
        return

    client = chromadb.PersistentClient(path=DOSSIER_CHROMA)
    collection = client.get_collection(NOM_COLLECTION)

    print(f"[INFO] Recherche des documents pertinents pour : {question}")
    documents_pertinents = rechercher_documents(question, collection)

    if not documents_pertinents:
        print("[INFO] Aucun document pertinent trouve.")
        return

    print(f"[INFO] {len(documents_pertinents)} document(s) trouve(s), generation de la reponse...")
    reponse = generer_reponse(question, documents_pertinents)

    print("\n" + "=" * 60)
    print("REPONSE :")
    print("=" * 60)
    print(reponse)


if __name__ == "__main__":
    print("Assistant RAG - Smart Mairie (tape 'quit' pour sortir)\n")
    while True:
        question = input("Ta question : ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if question:
            poser_question(question)
            print()