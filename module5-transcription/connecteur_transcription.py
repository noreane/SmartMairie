""" Connecteur Transcription - Module 5 (Smart Mairie)
Transcrit un fichier audio (ex: extrait d'intervention en conseil municipal, message vocal citoyen) via Whisper, puis produit :
  1. un CSV standardise dans module2-connecteurs/data/staging/, pret a
     etre declare dans le CONFIGS de module1-nettoyage/classement.py
     (c'est ce fichier qui alimente le pipeline automatise)
  2. un PDF lisible par un humain dans module5-transcription/data/pdf/,
     pour archive/consultation directe (ne rentre PAS dans le pipeline
     Module 1, c'est un sous-produit parallele pour un usage humain) """

import os
from datetime import date
import whisper
import pandas as pd
import ollama
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

DOSSIER_SOURCE = os.path.join("module5-transcription", "data", "sources")
DOSSIER_STAGING = os.path.join("module2-connecteurs", "data", "staging")
DOSSIER_PDF = os.path.join("module5-transcription", "data", "pdf")
DELIMITER = ";"

TAILLE_MODELE = "base" 
MODELE_SYNTHESE = "llama3.2:3B"


def synthetiser(texte: str) -> str:
    """Resume le texte transcrit via un LLM local (Ollama)."""
    prompt = f"""Voici la transcription d'un enregistrement audio (reunion ou
message vocal recu par une mairie) :

{texte}

Redige une synthese en 3 a 5 phrases maximum, en francais, qui reprend
les points cles et decisions evoquees. Reste factuel, ne rajoute rien
qui ne soit pas dans le texte."""

    try:
        reponse = ollama.generate(model=MODELE_SYNTHESE, prompt=prompt)
        return reponse["response"].strip()
    except Exception as erreur:
        print(f"[ATTENTION] Synthese impossible : {erreur}")
        return ""


def transcrire_audio(chemin_audio: str, modele) -> str:
    """Transcrit un fichier audio en francais via Whisper."""
    resultat = modele.transcribe(chemin_audio, language="fr")
    return resultat["text"].strip()


def generer_pdf(nom_fichier_audio: str, texte: str, synthese: str, chemin_pdf: str):
    """Genere un PDF lisible (archive humaine, hors pipeline Module 1)."""
    os.makedirs(os.path.dirname(chemin_pdf), exist_ok=True)
    doc = SimpleDocTemplate(chemin_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Transcription automatique", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Fichier source : {nom_fichier_audio}", styles["Normal"]))
    story.append(Paragraph(f"Date de traitement : {date.today().isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 20))

    if synthese:
        story.append(Paragraph("Synthese", styles["Heading2"]))
        story.append(Paragraph(synthese, styles["Normal"]))
        story.append(Spacer(1, 20))

    story.append(Paragraph("Transcription complete", styles["Heading2"]))
    story.append(Spacer(1, 8))

    for paragraphe in texte.split(". "):
        if paragraphe.strip():
            story.append(Paragraph(paragraphe.strip() + ".", styles["Normal"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    print(f"[OK] PDF genere : {chemin_pdf}")


def run():
    if not os.path.exists(DOSSIER_SOURCE):
        print(f"[ERREUR] Dossier introuvable : {DOSSIER_SOURCE}")
        return

    fichiers = [f for f in os.listdir(DOSSIER_SOURCE) if f.lower().endswith((".wav", ".mp3", ".m4a"))]

    if not fichiers:
        print(f"[INFO] Aucun fichier audio trouve dans {DOSSIER_SOURCE}")
        return

    print(f"[INFO] Chargement du modele Whisper ({TAILLE_MODELE})...")
    modele = whisper.load_model(TAILLE_MODELE)

    resultats = []
    for i, nom_fichier in enumerate(fichiers, start=1):
        chemin = os.path.join(DOSSIER_SOURCE, nom_fichier)
        print(f"[INFO] Transcription : {chemin}")

        try:
            texte = transcrire_audio(chemin, modele)
        except Exception as e:
            print(f"[ERREUR] Echec transcription sur {nom_fichier} : {e} - fichier ignore")
            continue

        print(f"[INFO] Synthese automatique de {nom_fichier}...")
        synthese = synthetiser(texte)

        resultats.append({
            "id_projet": f"TRANS-{date.today().strftime('%Y%m%d')}-{i:03d}",
            "date_transcription": date.today().isoformat(),
            "fichier_source": nom_fichier,
            "objet": "Intervention conseil municipal" if "conseil" in nom_fichier.lower() else "Message vocal citoyen",
            "synthese": synthese,
            "texte_transcrit": texte,
        })

        nom_pdf = os.path.splitext(nom_fichier)[0] + ".pdf"
        generer_pdf(nom_fichier, texte, synthese, os.path.join(DOSSIER_PDF, nom_pdf))

    if not resultats:
        print("[INFO] Aucun fichier traite avec succes")
        return

    df = pd.DataFrame(resultats)

    os.makedirs(DOSSIER_STAGING, exist_ok=True)
    chemin_sortie = os.path.join(DOSSIER_STAGING, "transcriptions.csv")
    df.to_csv(chemin_sortie, index=False, sep=DELIMITER, encoding="utf-8-sig")
    print(f"[OK] Export ecrit : {chemin_sortie} ({len(df)} ligne(s))")


if __name__ == "__main__":
    run()