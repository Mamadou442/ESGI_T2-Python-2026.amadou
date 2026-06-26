import os



FTP_ROOT = "FTP_ROOT"

print("Initialisation de l'arborescence FTP...\n")

sites = ["paris", "grenoble", "marseille", "rennes"]
dossiers = ["data", "backups/daily", "backups/weekly", "archives"]

for site in sites:
    for dossier in dossiers:
        chemin = os.path.join("FTP_ROOT", site, dossier)
        os.makedirs(chemin, exist_ok=True)
        print(f"Créé : {chemin}")


