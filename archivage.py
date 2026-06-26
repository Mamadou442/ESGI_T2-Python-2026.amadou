import os
from datetime import datetime

# ────────────────────────────────────────────────
# Module d'archivage des versions de fichiers
# ────────────────────────────────────────────────

# Dossier racine FTP simulé
FTP_ROOT = "FTP_ROOT"


### Etape 1 : Extraire le numéro de version depuis un nom de fichier archivé
def extraire_numero_version(nom_fichier: str) -> int:
    """Extrait le numéro de version d'un fichier archivé de la forme 'NOM_V12.ext'.
    Retourne 0 si aucun numéro de version trouvé.
    
    Méthode : on cherche '_V' dans le nom, puis on lit les chiffres qui suivent.
    Exemple : 'rapport_V12.txt' → on trouve '_V' à l'index 7, on lit '12' → retourne 12"""

    # On cherche la position de '_V' dans le nom du fichier 
    nom_sans_ext = nom_fichier.split(".")[0]        # 'rapport_V12'
    position = nom_sans_ext.find("_V")              # cherche '_V' dans la chaîne

    if position == -1:
        return 0    # pas de '_V' trouvé → pas de numéro de version

    # On récupère tout ce qui est après '_V' : ex. '12'
    apres_v = nom_sans_ext[position + 2:]           # +2 pour sauter '_V'

    # On lit les chiffres tant qu'ils sont numériques
    chiffres = ""
    for caractere in apres_v:
        if caractere.isdigit():
            chiffres += caractere
        else:
            break   # on s'arrête dès qu'on rencontre autre chose qu'un chiffre

    if chiffres == "":
        return 0    # rien de numérique après '_V'

    return int(chiffres)


### Etape 2 : Obtenir la prochaine version disponible pour un fichier
def prochain_numero_version(dossier_archives: str, nom_base: str) -> int:
    """Parcourt le dossier archives et retourne le prochain numéro de version.
    Exemple : si FICH_V12 existe déjà, retourne 13."""

    if not os.path.exists(dossier_archives):
        return 1

    versions_existantes = []

    for fichier in os.listdir(dossier_archives):
        # On vérifie que le fichier correspond bien au même nom de base
        if fichier.startswith(nom_base):
            num = extraire_numero_version(fichier)
            if num > 0:
                versions_existantes.append(num)

    if not versions_existantes:
        return 1

    return max(versions_existantes) + 1


### Etape 3 : Copier un fichier manuellement 
def copier_fichier(source: str, destination: str) -> None:
    """Copie un fichier octet par octet avec open() en mode binaire.
    Même principe que dans cryptage.py : on lit 'rb' et on écrit 'wb'."""

    with open(source, "rb") as f_entree:
        donnees = f_entree.read()

    with open(destination, "wb") as f_sortie:
        f_sortie.write(donnees)


### Etape 4 : Archiver un fichier (copier l'ancienne version dans archives/)
def archiver_fichier(chemin_fichier: str, dossier_archives: str) -> str | None:
    """Copie un fichier existant vers le dossier archives/ avec un numéro de version.
    Exemple : 'rapport.txt' → 'rapport_V1.txt'
    Retourne le chemin d'archive ou None si le fichier source n'existe pas."""

    if not os.path.exists(chemin_fichier):
        print(f"Fichier source introuvable : {chemin_fichier}")
        return None

    ## Décomposition du nom de fichier
    nom_fichier  = os.path.basename(chemin_fichier)
    nom_sans_ext = nom_fichier.split(".")[0]        # 'rapport'
    extension    = "." + nom_fichier.split(".")[-1] if "." in nom_fichier else ""  # '.txt'

    ## Calcul du numéro de version suivant
    os.makedirs(dossier_archives, exist_ok=True)
    num_version  = prochain_numero_version(dossier_archives, nom_sans_ext)

    ## Nom du fichier archivé
    nom_archive    = nom_sans_ext + "_V" + str(num_version) + extension
    chemin_archive = os.path.join(dossier_archives, nom_archive)

    ## Copie vers archives/ avec notre propre fonction
    copier_fichier(chemin_fichier, chemin_archive)
    print(f"Archivé : {chemin_fichier} → {chemin_archive}")

    return chemin_archive


### Etape 5 : Archiver avant mise à jour 
def archiver_avant_mise_a_jour(chemin_fichier: str, site: str) -> bool:
    """Archive l'ancienne version d'un fichier avant qu'il soit remplacé.
    Le dossier archives/ est celui du site concerné dans FTP_ROOT.
    Retourne True si l'archivage a réussi."""

    ## Construction du chemin vers le dossier archives du site
    dossier_archives = os.path.join(FTP_ROOT, site, "archives")

    if not os.path.exists(chemin_fichier):
        print(f"Aucun fichier existant à archiver : {chemin_fichier}")
        return False

    resultat = archiver_fichier(chemin_fichier, dossier_archives)
    return resultat is not None


### Etape 6 : Lister les versions archivées d'un fichier
def lister_versions(nom_base: str, site: str) -> list:
    """Liste toutes les versions archivées d'un fichier pour un site donné.
    Retourne la liste triée par numéro de version."""

    dossier_archives = os.path.join(FTP_ROOT, site, "archives")

    if not os.path.exists(dossier_archives):
        print(f"Dossier archives introuvable pour le site '{site}'.")
        return []

    versions = []

    for fichier in os.listdir(dossier_archives):
        if fichier.startswith(nom_base):
            num = extraire_numero_version(fichier)
            if num > 0:
                chemin = os.path.join(dossier_archives, fichier)
                versions.append({
                    "version": num,
                    "nom":     fichier,
                    "chemin":  chemin,
                    "taille":  os.path.getsize(chemin),
                    "modifie": datetime.fromtimestamp(os.path.getmtime(chemin)).strftime("%Y-%m-%d %H:%M")
                })

    versions.sort(key=lambda x: x["version"])

    if not versions:
        print(f"Aucune version archivée pour '{nom_base}' sur le site '{site}'.")
        return []

    print(f"\n Versions archivées de '{nom_base}' sur le site '{site}' :")
    print(f"{'VERSION':<10} {'FICHIER':<30} {'TAILLE':<12} {'MODIFIÉ'}")
    print("-" * 65)

    for v in versions:
        print(f"V{v['version']:<9} {v['nom']:<30} {v['taille']:<12} {v['modifie']}")

    return versions


### Etape 7 : Restaurer une version archivée
def restaurer_version(nom_base: str, site: str, numero_version: int, destination: str) -> bool:
    """Copie une version archivée vers un emplacement de destination.
    Retourne True si la restauration a réussi."""

    dossier_archives = os.path.join(FTP_ROOT, site, "archives")

    ## Recherche du fichier archivé correspondant
    fichier_trouve = None
    for fichier in os.listdir(dossier_archives):
        if fichier.startswith(nom_base) and extraire_numero_version(fichier) == numero_version:
            fichier_trouve = os.path.join(dossier_archives, fichier)
            break

    if not fichier_trouve:
        print(f"Version V{numero_version} introuvable pour '{nom_base}' sur le site '{site}'.")
        return False

    ## Copie vers la destination avec notre propre fonction 
    dossier_destination = os.path.dirname(destination)
    if dossier_destination != "":
        os.makedirs(dossier_destination, exist_ok=True)

    copier_fichier(fichier_trouve, destination)
    print(f"Version V{numero_version} restaurée → {destination}")

    return True


### Etape 8 : Nettoyage des archives (conserver uniquement les N dernières versions)
def nettoyer_archives(nom_base: str, site: str, nb_versions_a_garder: int = 5) -> None:
    """Supprime les versions archivées les plus anciennes pour ne garder
    que les 'nb_versions_a_garder' plus récentes."""

    versions = lister_versions(nom_base, site)

    if len(versions) <= nb_versions_a_garder:
        print(f"Aucun nettoyage nécessaire ({len(versions)} version(s) archivée(s)).")
        return

    ## Les versions à supprimer sont les plus anciennes (début de la liste triée)
    versions_a_supprimer = versions[: len(versions) - nb_versions_a_garder]

    for v in versions_a_supprimer:
        os.remove(v["chemin"])
        print(f"Supprimé : {v['nom']}")

    print(f"{len(versions_a_supprimer)} ancienne(s) version(s) supprimée(s). {nb_versions_a_garder} version(s) conservée(s).")


