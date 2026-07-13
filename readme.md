# NoVisageLock

NoVisageLock est une application Python pour Windows qui verrouille automatiquement la session lorsqu'aucun visage autorisé n'est détecté devant la webcam.

La reconnaissance faciale repose sur **InsightFace** et un modèle biométrique du propriétaire enregistré lors de la première utilisation.

---

# Fonctionnalités

* Détection automatique du propriétaire.
* Verrouillage de la session Windows après une durée d'absence configurable.
* Enrôlement automatique du propriétaire lors du premier lancement.
* Possibilité de déclarer un nouveau propriétaire depuis l'icône de la barre des tâches.
* Prévisualisation de la caméra (activable/désactivable).
* Mise en pause de la surveillance.
* Journalisation des événements.

---

# Configuration minimale

* Windows 10 ou Windows 11
* Webcam fonctionnelle
* Python 3.12 recommandé
* Environ 2 Go d'espace disque

---

# Version de Python recommandée

Le projet a été développé avec **Python 3.12 (64 bits)**.

Il est déconseillé d'utiliser Python 3.14 pour le moment car certaines bibliothèques (notamment InsightFace et ses dépendances) peuvent ne pas être totalement compatibles.

Pour vérifier votre version :

```bash
python --version
```

Le résultat attendu est par exemple :

```text
Python 3.12.x
```

---

# Installation de Python

Télécharger Python depuis le site officiel :

https://www.python.org/downloads/windows/

Pendant l'installation, cocher impérativement :

* Add Python to PATH

Puis choisir :

* Install Now

Vérifier ensuite :

```bash
python --version
```

---

# Cloner ou copier le projet

Le projet doit avoir une structure similaire à :

```text
NoVisageLock
│
├── main.py
├── tray.py
├── enroll_camera.py
├── config.json
├── requirements.txt
│
├── models
│   └── buffalo_l
│
├── embeddings
│
└── venv
```

---

# Création de l'environnement virtuel

Depuis le dossier du projet :

```bash
python -m venv venv
```

Activation :

PowerShell :

```powershell
venv\Scripts\Activate.ps1
```

Invite de commandes :

```cmd
venv\Scripts\activate.bat
```

---

# Installation des dépendances

Mettre pip à jour :

```bash
python -m pip install --upgrade pip
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

# Exemple de requirements.txt

```text
opencv-python
numpy
insightface
onnxruntime
pystray
Pillow
filelock
```

---

# Premier lancement

Lancer :

```bash
python main.py
```

Si aucun propriétaire n'est enregistré :

* la caméra s'ouvre ;
* plusieurs images sont capturées ;
* le fichier `embeddings/owner.npy` est créé automatiquement.

Les lancements suivants utiliseront directement ce profil.

---

# Utilisation

Une fois lancé :

* l'application fonctionne en arrière-plan ;
* une icône apparaît dans la zone de notification Windows.

Le menu permet de :

* Afficher la caméra.
* Masquer la caméra.
* Mettre la surveillance en pause.
* Reprendre la surveillance.
* Déclarer un nouveau propriétaire.
* Quitter l'application.

---

# Modifier le propriétaire

Depuis le menu de l'icône :

**Changer propriétaire**

L'ancien profil est supprimé puis une nouvelle phase d'enrôlement démarre.

---

# Configuration

Le fichier `config.json` permet de modifier le comportement de l'application.

Exemple :

```json
{
    "camera": 0,
    "frame_skip": 5,
    "absence_timeout": 60,
    "owner_threshold": 0.45
}
```

Description des paramètres :

* `camera` : numéro de la webcam.
* `frame_skip` : nombre d'images ignorées entre deux analyses.
* `absence_timeout` : délai (en secondes) avant le verrouillage.
* `owner_threshold` : seuil de reconnaissance du propriétaire.

---

# Dossier models

Le dossier `models` doit contenir le modèle InsightFace (`buffalo_l`) téléchargé automatiquement lors du premier lancement ou copié depuis une installation existante.

---

# Dossier embeddings

Le dossier `embeddings` contient :

```text
owner.npy
```

Ce fichier représente l'empreinte biométrique du propriétaire.

Il ne contient pas de photographie.

---

# Lancer automatiquement au démarrage

Le projet peut être lancé automatiquement avec un script `.bat` ou une tâche planifiée Windows.

Exemple de fichier `launch.bat` :

```bat
@echo off
cd /d "C:\Chemin\Vers\NoVisageLock"
start "" venv\Scripts\pythonw.exe main.py
```

L'utilisation de `pythonw.exe` permet de ne pas afficher de fenêtre PowerShell.

---

# Résolution des problèmes

## Webcam inaccessible

Vérifier que :

* aucune autre application n'utilise la webcam ;
* les autorisations Windows sont accordées.

---

## owner.npy absent

Supprimer le contenu du dossier `embeddings` puis relancer :

```bash
python main.py
```

Une nouvelle phase d'enrôlement sera lancée.

---

## Modèle InsightFace introuvable

Vérifier que le dossier `models` existe.

Au premier lancement, InsightFace peut télécharger automatiquement les modèles nécessaires.

---

## Erreur d'installation

Mettre pip à jour :

```bash
python -m pip install --upgrade pip
```

Puis réinstaller les dépendances :

```bash
pip install -r requirements.txt
```

---

# Journal

Les événements sont enregistrés dans :

```text
novisagelock.log
```

Ce fichier permet de diagnostiquer les erreurs et de suivre le fonctionnement de l'application.

---

# Licence

Projet développé à des fins pédagogiques et personnelles.

Les bibliothèques utilisées conservent leurs licences respectives.
