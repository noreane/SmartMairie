""" Connecteur OCR - Module 4 (Smart Mairie)
Lit un document scanné (image ou PDF) depuse par un agent de la mairie (ex: courrier de demande de subvention recu par voie postale), extrait 
le texte via Tesseract OCR, puis parse les champs cles (date, objet, reference) pour produire un CSV standardise dans
module2-connecteurs/data/staging/, pret a etre declare dans le CONFIGS de module1-nettoyage/classement.py. """

import os
import re
from datetime import date, datetime
import pytesseract
from PIL import Image
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DOSSIER_SOURCE = os.path.join("module4-ocr", "data", "sources")
DOSSIER_STAGING = os.path.join("module2-connecteurs", "data", "staging")
DELIMITER = ";"

os.environ["TESSDATA_PREFIX"] = os.path.join(os.getcwd(), "module4-ocr", "tessdata")


def extraire_texte(chemin_image: str) -> str:
    """Fait tourner Tesseract sur l'image, retourne le texte brut."""
    image = Image.open(chemin_image)
    return pytesseract.image_to_string(image, lang="fra")


def parser_champs(texte: str, id_fallback: str) -> dict:
    """Extrait les champs clés d'une image (date, objet, reference) pour produire un dictionnaire prêt à être converti en CSV."""
    def chercher(motif, texte, defaut=None):
        resultat = re.search(motif, texte, re.IGNORECASE)
        return resultat.group(1).strip() if resultat else defaut

    reference = chercher(r"R[ée]f[ée]rence dossier\s*:\s*(\S+)", texte)
    date_brute = chercher(r"Fait le\s*([\d/]+)", texte)
    objet = chercher(r"Objet\s*:\s*(.+)", texte)
    association = chercher(r"Nom\s*-\s*D[ée]nomination\s*:\s*(.+)", texte)
    montant = chercher(r"Montant sollicit[ée]\s*:\s*(.+)", texte)

    if date_brute:
        try:
            date_courrier = datetime.strptime(date_brute, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            date_courrier = date.today().isoformat()
    else:
        date_courrier = date.today().isoformat()

    return {
        "id_projet": reference or id_fallback,
        "date_courrier": date_courrier,
        "objet": objet or "Non identifie",
        "association": association,
        "montant_demande": montant,
        "texte_brut": texte.strip().replace("\n", " | "),
    }


def run():
    resultats = []

    if not os.path.exists(DOSSIER_SOURCE):
        print(f"[ERREUR] Dossier introuvable : {DOSSIER_SOURCE}")
        return

    fichiers = [f for f in os.listdir(DOSSIER_SOURCE) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    if not fichiers:
        print(f"[INFO] Aucun document trouve dans {DOSSIER_SOURCE}")
        return

    for i, nom_fichier in enumerate(fichiers, start=1):
        chemin = os.path.join(DOSSIER_SOURCE, nom_fichier)
        print(f"[INFO] Traitement OCR : {chemin}")
        try:
            texte = extraire_texte(chemin)
        except Exception as e:
            print(f"[ERREUR] Echec OCR sur {nom_fichier} : {e} - fichier ignore")
            continue

        # Fallback unique par fichier (numero de sequence), pas par date seule,
        # pour eviter que deux courriers sans reference le meme jour ecrasent le meme id_projet.
        id_fallback = f"OCR-{date.today().strftime('%Y%m%d')}-{str(i).zfill(3)}"
        champs = parser_champs(texte, id_fallback)
        resultats.append(champs)

    if not resultats:
        print("[INFO] Aucun document traite avec succes")
        return

    df = pd.DataFrame(resultats)

    os.makedirs(DOSSIER_STAGING, exist_ok=True)
    chemin_sortie = os.path.join(DOSSIER_STAGING, "courriers_ocr.csv")
    df.to_csv(chemin_sortie, index=False, sep=DELIMITER, encoding="utf-8-sig")
    print(f"[OK] Export ecrit : {chemin_sortie} ({len(df)} ligne(s))")


if __name__ == "__main__":
    run()