"""
Interface graphique - Module 6 (Smart Mairie)
Interface web locale (Streamlit) pour poser des questions au systeme
RAG sans passer par la ligne de commande.

Lancement : streamlit run module6-rag/interface_rag.py
"""

import os
import streamlit as st
import ollama
import chromadb

DOSSIER_CHROMA = os.path.join("module6-rag", "chroma_db")
MODELE_EMBEDDING = "nomic-embed-text"
MODELE_LLM = "llama3.2:3B"
NOM_COLLECTION = "documents_mairie"
NB_DOCUMENTS_RECUPERES = 4


@st.cache_resource
def charger_collection():
    """Charge la base vectorielle une seule fois (mise en cache par Streamlit)."""
    client = chromadb.PersistentClient(path=DOSSIER_CHROMA)
    return client.get_collection(NOM_COLLECTION)


def rechercher_documents(question: str, collection) -> tuple[list[str], list[str]]:
    """Trouve les documents les plus proches de la question. Retourne (textes, sources)."""
    reponse = ollama.embeddings(model=MODELE_EMBEDDING, prompt=question)
    vecteur_question = reponse["embedding"]

    resultats = collection.query(
        query_embeddings=[vecteur_question],
        n_results=NB_DOCUMENTS_RECUPERES,
    )

    textes = resultats["documents"][0] if resultats["documents"] else []
    sources = [m["source"] for m in resultats["metadatas"][0]] if resultats["metadatas"] else []
    return textes, sources


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


# --- Interface ---

st.set_page_config(page_title="Assistant Smart Mairie", page_icon="🏛️")
st.title("🏛️ Assistant Smart Mairie")
st.caption("Posez une question sur les documents de la mairie (délibérations, urbanisme, subventions, écoles, courriers, transcriptions...)")

if not os.path.exists(DOSSIER_CHROMA):
    st.error("Base vectorielle introuvable. Lance d'abord `python module6-rag/indexer_rag.py` dans un terminal.")
    st.stop()

collection = charger_collection()

question = st.text_input("Votre question :", placeholder="Ex : Quelles subventions ont été accordées ?")

if st.button("Rechercher", type="primary") and question:
    with st.spinner("Recherche des documents pertinents..."):
        documents_pertinents, sources = rechercher_documents(question, collection)

    if not documents_pertinents:
        st.warning("Aucun document pertinent trouvé.")
    else:
        with st.spinner("Génération de la réponse..."):
            reponse = generer_reponse(question, documents_pertinents)

        st.subheader("Réponse")
        st.write(reponse)

        with st.expander(f"📄 Voir les {len(documents_pertinents)} document(s) source(s) utilisés"):
            for texte, source in zip(documents_pertinents, sources):
                st.markdown(f"**{source}**")
                st.text(texte)
                st.divider()