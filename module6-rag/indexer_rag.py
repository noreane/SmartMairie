""" Indexation RAG - Module 6 (Smart Mairie)
Parcourt tous les documents classes par le Module 1 (module1-nettoyage/data/classe/...), les decoupe en morceaux,
calcule leurs embeddings via Ollama, et les stocke dans une bas vectorielle locale ChromaDB. Cette base sert ensuite au script
interroger_rag.py pour repondre aux questions. """

import os
import csv
import ollama
import chromadb

DOSSIER_CLASSE = os.path.join("module1-nettoyage", "data", "classe")
DOSSIER_CHROMA = os.path.join("module6-rag", "chroma_db")
MODELE_EMBEDDING = "nomic-embed-text"
NOM_COLLECTION = "documents_mairie"


def lire_contenu_csv(chemin_fichier: str) -> str:
    """Lit un fichier CSV classe et le convertit en texte lisible."""
    lignes_texte = []
    try:
        with open(chemin_fichier, mode="r", encoding="utf-8-sig") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                paires = [f"{cle}: {valeur}" for cle, valeur in ligne.items() if valeur]
                lignes_texte.append(" | ".join(paires))
    except Exception as erreur:
        print(f"[ATTENTION] Impossible de lire {chemin_fichier} : {erreur}")
        return ""
    return "\n".join(lignes_texte)


def collecter_documents() -> list[dict]:
    """Parcourt l'arborescence classee et collecte tous les documents CSV."""
    documents = []

    if not os.path.exists(DOSSIER_CLASSE):
        print(f"[ERREUR] Dossier introuvable : {DOSSIER_CLASSE}")
        return documents

    for racine, _, fichiers in os.walk(DOSSIER_CLASSE):
        for nom_fichier in fichiers:
            if nom_fichier.lower().endswith(".csv"):
                chemin = os.path.join(racine, nom_fichier)
                contenu = lire_contenu_csv(chemin)
                if contenu.strip():
                    documents.append({
                        "id": chemin,
                        "texte": contenu,
                        "source": nom_fichier,
                    })

    return documents


def indexer():
    print("[INFO] Collecte des documents classes...")
    documents = collecter_documents()
    print(f"[INFO] {len(documents)} document(s) trouve(s)")

    if not documents:
        print("[INFO] Rien a indexer. Lance d'abord le Module 1 et 2/4/5.")
        return

    os.makedirs(DOSSIER_CHROMA, exist_ok=True)
    client = chromadb.PersistentClient(path=DOSSIER_CHROMA)

    # Repart de zero a chaque indexation pour eviter les doublons
    try:
        client.delete_collection(NOM_COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(NOM_COLLECTION)

    # Traitement par lots (batch) : un seul appel Ollama pour plusieurs
    # documents a la fois, au lieu d'un appel reseau par document.
    # Reduit fortement le temps total quand il y a des milliers de fichiers.
    TAILLE_LOT = 32

    for debut in range(0, len(documents), TAILLE_LOT):
        lot = documents[debut:debut + TAILLE_LOT]
        textes_lot = [doc["texte"] for doc in lot]

        reponse = ollama.embed(model=MODELE_EMBEDDING, input=textes_lot)
        vecteurs_lot = reponse["embeddings"]

        collection.add(
            ids=[doc["id"] for doc in lot],
            embeddings=vecteurs_lot,
            documents=textes_lot,
            metadatas=[{"source": doc["source"]} for doc in lot],
        )

        print(f"[INFO] Embedding {min(debut + TAILLE_LOT, len(documents))}/{len(documents)}")

    print(f"[OK] Indexation terminee : {len(documents)} document(s) dans {DOSSIER_CHROMA}")


if __name__ == "__main__":
    indexer()