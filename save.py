import os
from datetime import datetime
from cryptage import chiffrer_fichier

# ────────────────────────────────────────────────
# Module de sauvegarde incrémentale
# ────────────────────────────────────────────────

# Fichier qui stocke l'empreinte de chaque fichier sauvegardé
FICHIER_INDEX = "index.txt"


### Etape 1 : Calculer une empreinte simple d'un fichier
def calculer_empreinte(chemin_fichier: str) -> str:
    """Calcule une empreinte d'un fichier à partir de sa taille et sa date de modification.
    On concatène les deux valeurs en une seule chaîne de caractères.
    Exemple : '2048_1718100000.0'
    
    Si le contenu change → la taille ou la date change → l'empreinte change aussi."""

    taille        = os.path.getsize(chemin_fichier)          # taille en octets
    date_modif    = os.path.getmtime(chemin_fichier)         # timestamp de dernière modification

    empreinte     = str(taille) + "_" + str(date_modif)     # ex : '2048_1718100000.0'
    return empreinte


### Etape 2 : Charger l'index des empreintes
def charger_index() -> dict:
    """Lit le fichier index.txt ligne par ligne et retourne un dictionnaire.
    Chaque ligne a le format :  chemin_fichier|empreinte
    Si le fichier n'existe pas encore, retourne un dictionnaire vide."""

    index = {}

    if not os.path.exists(FICHIER_INDEX):
        return index    # aucune sauvegarde précédente : on repart de zéro

    with open(FICHIER_INDEX, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()           # supprime les \n en fin de ligne

            if ligne == "":
                continue                    # on ignore les lignes vides

            # On découpe la ligne sur le séparateur '|'
            # Exemple : 'data/fich.txt|2048_1718100000.0'
            parties = ligne.split("|")

            if len(parties) == 2:
                chemin    = parties[0]      # 'data/fich.txt'
                empreinte = parties[1]      # '2048_1718100000.0'
                index[chemin] = empreinte

    return index


### Etape 3 : Sauvegarder l'index des empreintes 
def sauvegarder_index(index: dict) -> None:
    """Ecrit le dictionnaire index dans le fichier index.txt.
    Chaque entrée est écrite sur une ligne au format : chemin_fichier|empreinte"""

    with open(FICHIER_INDEX, "w", encoding="utf-8") as f:
        for chemin, empreinte in index.items():
            ligne = chemin + "|" + empreinte + "\n"
            f.write(ligne)

    print("Index mis à jour → index.txt")


### Etape 4 : Détecter les fichiers modifiés ou nouveaux
def detecter_changements(dossier_data: str, index: dict) -> tuple:
    """Parcourt le dossier data/ et compare chaque fichier à l'index.
    Retourne la liste des fichiers modifiés ou nouveaux."""

    fichiers_modifies = []

    print("Scan du dossier :", dossier_data)
    print(os.listdir(dossier_data))     # affiche les fichiers détectés

    for nom_fichier in os.listdir(dossier_data):
        chemin = os.path.join(dossier_data, nom_fichier)

        # On ignore les sous-dossiers, on ne traite que les fichiers
        if not os.path.isfile(chemin):
            continue

        empreinte_actuelle = calculer_empreinte(chemin)

        # Cas 1 : fichier nouveau (pas encore dans l'index)
        # Cas 2 : fichier modifié (empreinte différente de la dernière sauvegarde)
        if chemin not in index or index[chemin] != empreinte_actuelle:
            fichiers_modifies.append(chemin)
            index[chemin] = empreinte_actuelle  # on met l'index à jour

    print(f"{len(fichiers_modifies)} fichier(s) modifié(s) détecté(s)")
    return fichiers_modifies, index


### Etape 5 : Sauvegarde quotidienne (chaque jour)
def sauvegarde_quotidienne(dossier_data: str, dossier_sauvegardes: str, cle: bytes) -> None:
    """Détecte les fichiers modifiés et les chiffre dans backups/daily/
    Cette fonction est appelée tous les jours."""

    print("\n── Sauvegarde quotidienne ──")

    ## Etape 5.1 : charger l'index existant
    index = charger_index()

    ## Etape 5.2 : détecter les changements
    fichiers_modifies, index_maj = detecter_changements(dossier_data, index)

    if not fichiers_modifies:
        print("Aucun changement détecté. Sauvegarde inutile.")
        return

    ## Etape 5.3 : créer le dossier de destination avec la date du jour
    horodatage         = datetime.now().strftime("%Y-%m-%d_%H%M")
    dossier_destination = os.path.join(dossier_sauvegardes, "daily", horodatage)
    os.makedirs(dossier_destination, exist_ok=True)

    print("Dossier de sauvegarde créé :", dossier_destination)

    ## Etape 5.4 : chiffrer et copier chaque fichier modifié
    for chemin in fichiers_modifies:
        nom_fichier     = os.path.basename(chemin)
        fichier_chiffre = os.path.join(dossier_destination, nom_fichier + ".enc")

        chiffrer_fichier(chemin, fichier_chiffre, cle)

    print(os.listdir(dossier_destination))     # vérifier les fichiers créés

    ## Etape 5.5 : sauvegarder l'index mis à jour
    sauvegarder_index(index_maj)

    print(f"Sauvegarde quotidienne terminée : {len(fichiers_modifies)} fichier(s)")


### Etape 6 : Sauvegarde hebdomadaire (vendredi à 20h)
def est_vendredi_20h() -> bool:
    """Vérifie si on est vendredi à 20h.
    weekday() retourne 4 pour vendredi (0=lundi, 6=dimanche)."""

    maintenant = datetime.now()
    return maintenant.weekday() == 4 and maintenant.hour == 20


def sauvegarde_hebdomadaire(dossier_data: str, dossier_sauvegardes: str, cle: bytes) -> None:
    """Même logique que la sauvegarde quotidienne,
    mais déposée dans backups/weekly/ et uniquement le vendredi à 20h."""

    print("\n── Vérification sauvegarde hebdomadaire ──")

    ## Vérification du créneau : vendredi 20h uniquement
    if not est_vendredi_20h():
        print("Ce n'est pas vendredi 20h. Sauvegarde hebdomadaire ignorée.")
        return

    print("Vendredi 20h confirmé → lancement de la sauvegarde hebdomadaire")

    ## Etape 6.1 : charger l'index
    index = charger_index()

    ## Etape 6.2 : détecter les changements
    fichiers_modifies, index_maj = detecter_changements(dossier_data, index)

    if not fichiers_modifies:
        print("Aucun changement détecté.")
        return

    ## Etape 6.3 : créer le dossier weekly avec horodatage
    horodatage          = datetime.now().strftime("%Y-%m-%d_%H%M")
    dossier_destination = os.path.join(dossier_sauvegardes, "weekly", horodatage)
    os.makedirs(dossier_destination, exist_ok=True)

    print("Dossier weekly créé :", dossier_destination)

    ## Etape 6.4 : chiffrer et copier chaque fichier modifié
    for chemin in fichiers_modifies:
        nom_fichier     = os.path.basename(chemin)
        fichier_chiffre = os.path.join(dossier_destination, nom_fichier + ".enc")

        chiffrer_fichier(chemin, fichier_chiffre, cle)

    print(os.listdir(dossier_destination))     # vérifier les fichiers créés

    ## Etape 6.5 : sauvegarder l'index mis à jour
    sauvegarder_index(index_maj)

    print(f"Sauvegarde hebdomadaire terminée : {len(fichiers_modifies)} fichier(s)")