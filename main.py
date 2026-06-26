import os
from ftplib import FTP
from cryptage import generer_cle, chiffrer_fichier, dechiffrer_fichier
from save     import sauvegarde_quotidienne, sauvegarde_hebdomadaire
from archivage import (
    archiver_avant_mise_a_jour,
    lister_versions,
    restaurer_version,
    nettoyer_archives,
)

# ────────────────────────────────────────────────
# Configuration FTP (FileZilla sur XAMPP)
# ────────────────────────────────────────────────
FTP_HOST = "127.0.0.1"
FTP_PORT = 21           # port par défaut FileZilla Server
FTP_ROOT = "FTP_ROOT"

# Utilisateurs FileZilla configurés (login : contraction prénom+nom)
UTILISATEURS_FTP = {
    "paris":     {"user": "Diengstein", "pwd": "root"},
    "grenoble":  {"user": "agrenoble",  "pwd": "root"},
    "marseille": {"user": "amarseille", "pwd": "root"},
    "rennes":    {"user": "arennes",    "pwd": "root"},
}

SITES = list(UTILISATEURS_FTP.keys())

# Clé de chiffrement active (générée ou chargée au démarrage)
CLE_ACTIVE: bytes = None


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────

def separateur():
    print("\n" + "─" * 55)


def choisir_site():
    """Affiche la liste des sites et retourne le choix de l'utilisateur."""
    print("\nSites disponibles :")
    for i, s in enumerate(SITES, 1):
        print(f"  {i}. {s.capitalize()}")
    choix = input("Choisissez un site (numéro) : ").strip()
    try:
        return SITES[int(choix) - 1]
    except (ValueError, IndexError):
        print("Choix invalide.")
        return None


def connecter_ftp(site: str):
    """Ouvre une connexion FTP vers FileZilla avec les identifiants du site."""
    creds = UTILISATEURS_FTP.get(site)
    if not creds:
        print(f"Aucun identifiant trouvé pour le site '{site}'.")
        return None
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(creds["user"], creds["pwd"])
        print(f"Connecté au serveur FTP en tant que '{creds['user']}' (site {site})")
        return ftp
    except Exception as e:
        print(f"Erreur de connexion FTP : {e}")
        return None


# ────────────────────────────────────────────────
# Option 1 : Gestion de la clé de chiffrement
# ────────────────────────────────────────────────

def menu_cle():
    separateur()
    print("  GESTION DE LA CLÉ DE CHIFFREMENT")
    separateur()
    print("  1. Générer une nouvelle clé")
    print("  2. Charger une clé depuis un fichier")
    print("  3. Sauvegarder la clé active dans un fichier")
    print("  0. Retour")
    separateur()
    choix = input("Votre choix : ").strip()

    global CLE_ACTIVE

    if choix == "1":
        CLE_ACTIVE = generer_cle()
        print("Clé générée et activée.")

    elif choix == "2":
        chemin = input("Chemin du fichier clé : ").strip()
        if not os.path.exists(chemin):
            print("Fichier introuvable.")
            return
        with open(chemin, "rb") as f:
            CLE_ACTIVE = f.read().strip()
        print("Clé chargée.")

    elif choix == "3":
        if CLE_ACTIVE is None:
            print("Aucune clé active. Générez-en une d'abord.")
            return
        chemin = input("Nom du fichier de sauvegarde (ex: ma_cle.key) : ").strip()
        with open(chemin, "wb") as f:
            f.write(CLE_ACTIVE)
        print(f"Clé sauvegardée → {chemin}")


# ────────────────────────────────────────────────
# Option 2 : Chiffrement d'un fichier
# ────────────────────────────────────────────────

def menu_chiffrement():
    separateur()
    print("  CHIFFREMENT DE FICHIER")
    separateur()

    if CLE_ACTIVE is None:
        print("Aucune clé active. Allez dans 'Gestion de la clé' d'abord.")
        return

    chemin_entree = input("Fichier à chiffrer : ").strip()
    if not os.path.exists(chemin_entree):
        print("Fichier introuvable.")
        return

    chemin_sortie = input(f"Fichier de sortie [{chemin_entree}.enc] : ").strip()
    if chemin_sortie == "":
        chemin_sortie = chemin_entree + ".enc"

    chiffrer_fichier(chemin_entree, chemin_sortie, CLE_ACTIVE)


# ────────────────────────────────────────────────
# Option 3 : Déchiffrement d'un fichier
# ────────────────────────────────────────────────

def menu_dechiffrement():
    separateur()
    print("  DÉCHIFFREMENT DE FICHIER")
    separateur()

    if CLE_ACTIVE is None:
        print("Aucune clé active. Allez dans 'Gestion de la clé' d'abord.")
        return

    chemin_chiffre = input("Fichier chiffré (.enc) : ").strip()
    if not os.path.exists(chemin_chiffre):
        print("Fichier introuvable.")
        return

    # Propose un nom de sortie en retirant l'extension .enc si présente
    nom_defaut = chemin_chiffre.replace(".enc", "_dechiffre")
    chemin_sortie = input(f"Fichier de sortie [{nom_defaut}] : ").strip()
    if chemin_sortie == "":
        chemin_sortie = nom_defaut

    dechiffrer_fichier(chemin_chiffre, chemin_sortie, CLE_ACTIVE)


# ────────────────────────────────────────────────
# Option 4 : Sauvegarde (quotidienne / hebdomadaire)
# ────────────────────────────────────────────────

def menu_sauvegarde():
    separateur()
    print("  SAUVEGARDE")
    separateur()

    if CLE_ACTIVE is None:
        print("Aucune clé active. Allez dans 'Gestion de la clé' d'abord.")
        return

    site = choisir_site()
    if not site:
        return

    dossier_data        = os.path.join(FTP_ROOT, site, "data")
    dossier_sauvegardes = os.path.join(FTP_ROOT, site, "backups")

    if not os.path.exists(dossier_data):
        print(f"Dossier data introuvable pour le site '{site}' : {dossier_data}")
        return

    print("\n  1. Sauvegarde quotidienne")
    print("  2. Sauvegarde hebdomadaire (vendredi 20h)")
    choix = input("Votre choix : ").strip()

    if choix == "1":
        sauvegarde_quotidienne(dossier_data, dossier_sauvegardes, CLE_ACTIVE)
    elif choix == "2":
        sauvegarde_hebdomadaire(dossier_data, dossier_sauvegardes, CLE_ACTIVE)
    else:
        print("Choix invalide.")


# ────────────────────────────────────────────────
# Option 5 : Archivage
# ────────────────────────────────────────────────

def menu_archivage():
    separateur()
    print("  ARCHIVAGE DES VERSIONS")
    separateur()
    print("  1. Archiver un fichier avant mise à jour")
    print("  2. Lister les versions archivées")
    print("  3. Restaurer une version archivée")
    print("  4. Nettoyer les anciennes archives")
    print("  0. Retour")
    separateur()
    choix = input("Votre choix : ").strip()

    site = choisir_site()
    if not site:
        return

    if choix == "1":
        chemin = input("Chemin du fichier à archiver : ").strip()
        ok = archiver_avant_mise_a_jour(chemin, site)
        if ok:
            print("Archivage réussi.")

    elif choix == "2":
        nom_base = input("Nom de base du fichier (ex: rapport) : ").strip()
        lister_versions(nom_base, site)

    elif choix == "3":
        nom_base = input("Nom de base du fichier (ex: rapport) : ").strip()
        lister_versions(nom_base, site)
        num = input("Numéro de version à restaurer : ").strip()
        destination = input("Chemin de destination : ").strip()
        try:
            restaurer_version(nom_base, site, int(num), destination)
        except ValueError:
            print("Numéro de version invalide.")

    elif choix == "4":
        nom_base = input("Nom de base du fichier (ex: rapport) : ").strip()
        nb = input("Nombre de versions à conserver [5] : ").strip()
        nb = int(nb) if nb.isdigit() else 5
        nettoyer_archives(nom_base, site, nb)


# ────────────────────────────────────────────────
# Option 6 : Upload / Download FTP
# ────────────────────────────────────────────────

def menu_transfert_ftp():
    separateur()
    print("  TRANSFERT FTP (FileZilla / XAMPP)")
    separateur()
    print("  1. Upload d'un fichier vers le serveur FTP")
    print("  2. Download d'un fichier depuis le serveur FTP")
    print("  3. Lister les fichiers distants")
    print("  0. Retour")
    separateur()
    choix = input("Votre choix : ").strip()

    site = choisir_site()
    if not site:
        return

    ftp = connecter_ftp(site)
    if not ftp:
        return

    try:
        if choix == "1":
            _upload_ftp(ftp, site)

        elif choix == "2":
            _download_ftp(ftp, site)

        elif choix == "3":
            dossier_distant = input("Dossier distant à lister [/] : ").strip() or "/"
            try:
                ftp.cwd(dossier_distant)
                print(f"\nContenu de '{dossier_distant}' :")
                ftp.retrlines("LIST")
            except Exception as e:
                print(f"Erreur lors du listing : {e}")
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


def _upload_ftp(ftp: FTP, site: str):
    """Upload un fichier (chiffré si clé active) vers le serveur FTP."""
    chemin_local = input("Fichier local à envoyer : ").strip()

    if not os.path.exists(chemin_local):
        print("Fichier local introuvable.")
        return

    # Chiffrement avant envoi si une clé est disponible (simulation VPN)
    if CLE_ACTIVE is not None:
        chemin_enc = chemin_local + ".enc"
        chiffrer_fichier(chemin_local, chemin_enc, CLE_ACTIVE)
        chemin_a_envoyer = chemin_enc
        print("Fichier chiffré localement avant transfert (simulation VPN).")
    else:
        chemin_a_envoyer = chemin_local
        print("Aucune clé active : envoi sans chiffrement.")

    # Dossier distant : répertoire du site sur le serveur FileZilla
    dossier_distant = input(f"Dossier distant [/{site}/data] : ").strip()
    if dossier_distant == "":
        dossier_distant = f"/{site}/data"

    try:
        ftp.cwd(dossier_distant)
    except Exception:
        print(f"Impossible d'accéder à '{dossier_distant}'. Vérifiez les droits FileZilla.")
        return

    nom_distant = os.path.basename(chemin_a_envoyer)
    with open(chemin_a_envoyer, "rb") as f:
        ftp.storbinary(f"STOR {nom_distant}", f)

    print(f"Upload réussi : '{nom_distant}' → {dossier_distant}")


def _download_ftp(ftp: FTP, site: str):
    """Télécharge un fichier depuis le serveur FTP et le déchiffre si nécessaire."""
    dossier_distant = input(f"Dossier distant [/{site}/data] : ").strip()
    if dossier_distant == "":
        dossier_distant = f"/{site}/data"

    try:
        ftp.cwd(dossier_distant)
        print(f"\nFichiers disponibles dans '{dossier_distant}' :")
        ftp.retrlines("LIST")
    except Exception as e:
        print(f"Erreur : {e}")
        return

    nom_fichier = input("Nom du fichier à télécharger : ").strip()
    destination = input(f"Dossier local de destination [téléchargements/] : ").strip()
    if destination == "":
        destination = "telechargements"
    os.makedirs(destination, exist_ok=True)

    chemin_local = os.path.join(destination, nom_fichier)

    with open(chemin_local, "wb") as f:
        ftp.retrbinary(f"RETR {nom_fichier}", f.write)
    print(f"Fichier téléchargé → {chemin_local}")

    # Déchiffrement automatique si le fichier est .enc et qu'une clé est active
    if nom_fichier.endswith(".enc") and CLE_ACTIVE is not None:
        rep = input("Déchiffrer automatiquement ce fichier ? (o/n) : ").strip().lower()
        if rep == "o":
            chemin_dechiffre = chemin_local.replace(".enc", "")
            dechiffrer_fichier(chemin_local, chemin_dechiffre, CLE_ACTIVE)


# ────────────────────────────────────────────────
# Menu principal
# ────────────────────────────────────────────────

def afficher_menu():
    separateur()
    print("  GESTION FTP SÉCURISÉE — American Hospital (T2)")
    separateur()
    cle_status = "✓ Clé active" if CLE_ACTIVE is not None else "✗ Aucune clé"
    print(f"  [{cle_status}]")
    separateur()
    print("  1. Gestion de la clé de chiffrement")
    print("  2. Chiffrer un fichier")
    print("  3. Déchiffrer un fichier")
    print("  4. Sauvegarde (quotidienne / hebdomadaire)")
    print("  5. Archivage des versions")
    print("  6. Transfert FTP (upload / download)")
    print("  0. Quitter")
    separateur()


def main():
    print("\n  Bienvenue dans l'outil FTP sécurisé — AH")
    print("  Projet T2 — ESGI 3JSRC 2025-2026")

    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()

        if choix == "1":
            menu_cle()
        elif choix == "2":
            menu_chiffrement()
        elif choix == "3":
            menu_dechiffrement()
        elif choix == "4":
            menu_sauvegarde()
        elif choix == "5":
            menu_archivage()
        elif choix == "6":
            menu_transfert_ftp()
        elif choix == "0":
            print("\nFermeture de l'application. À bientôt !")
            break
        else:
            print("Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    main()
