from cryptography.fernet import Fernet
from ftplib import FTP
import os


def generer_cle() -> bytes:
    """Génère une nouvelle clé et l'affiche (à sauvegarder !)"""
    cle = Fernet.generate_key()
    print(" Attention : SAUVEGARDEZ CETTE CLÉ dans un lieu SÛR !")
    print(cle.decode())
    return cle

### méthodes de chiffrement et déchiffrement

def chiffrer_fichier(fichier_entree: str, fichier_sortie: str, cle: bytes) -> None:
    fernet = Fernet(cle)
    
    with open(fichier_entree, "rb") as f:
        donnees = f.read()
    
    donnees_chiffrees = fernet.encrypt(donnees)
    
    with open(fichier_sortie, "wb") as f:
        f.write(donnees_chiffrees)
    
    print(f"Fichier chiffré → {fichier_sortie}")

### 
def dechiffrer_fichier(fichier_chiffre: str, fichier_sortie: str, cle: bytes) -> None:
    fernet = Fernet(cle)
    
    with open(fichier_chiffre, "rb") as f:
        donnees_chiffrees = f.read()
    
    try:
        donnees = fernet.decrypt(donnees_chiffrees)
    except Exception as e:
        print("Erreur : mauvaise clé ou fichier corrompu", e)
        return
    
    with open(fichier_sortie, "wb") as f:
        f.write(donnees)
    
    print(f"Fichier déchiffré → {fichier_sortie}")


def envoyer_fichier_securise(chemin_local, cle, ftp_host, ftp_user, ftp_pass, dossier_distant):
    """Chiffre un fichier puis l'envoie sur le FTP (simule un transfert VPN)"""
    
    # 1. Chiffrement local AVANT tout envoi réseau
    fichier_chiffre = chemin_local + ".enc"
    chiffrer_fichier(chemin_local, fichier_chiffre, cle)
    print(f"Fichier chiffré localement : {fichier_chiffre}")
    
    # 2. Connexion FTP et upload du fichier déjà chiffré
    ftp = FTP(ftp_host)
    ftp.login(ftp_user, ftp_pass)
    ftp.cwd(dossier_distant)
    
    with open(fichier_chiffre, "rb") as f:
        ftp.storbinary(f"STOR {os.path.basename(fichier_chiffre)}", f)
    print("Transfert terminé (réseau = données chiffrées uniquement)")
    
    ftp.quit()
    


