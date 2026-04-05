# AI Protocol Validator

Plateforme intelligente de validation de protocoles industriels et cosmetiques basee sur l'intelligence artificielle multi-agents (LangGraph + Groq).

---

## Table des matieres

- [Apercu du projet](#apercu-du-projet)
- [Fonctionnalites](#fonctionnalites)
- [Architecture technique](#architecture-technique)
- [Pipeline multi-agents](#pipeline-multi-agents)
- [Prerequis](#prerequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [API Reference](#api-reference)
- [Normes supportees](#normes-supportees)
- [Exemple de protocole test](#exemple-de-protocole-test)
- [Resultats attendus](#resultats-attendus)
- [Technologies utilisees](#technologies-utilisees)
- [Auteur](#auteur)

---

## Apercu du projet

AI Protocol Validator est une application web full-stack qui permet de valider automatiquement des protocoles de fabrication (cosmetique, pharmaceutique, agroalimentaire) contre des normes industrielles telles que ISO 22716.

L'utilisateur charge un fichier PDF contenant son protocole, selectionne la norme applicable, et le systeme orchestre un pipeline de 6 agents IA specialises qui analysent, verifient, evaluent le risque, et generent un rapport de conformite complet.

---

## Fonctionnalites

- Import PDF par glisser-deposer ou selection de fichier
- Analyse multi-agents via pipeline LangGraph avec 6 agents IA specialises
- Verification automatique contre les regles ISO 22716
- Score de risque sur 10 avec justification
- Decision automatique ACCEPTE ou REJETE selon le score
- Generation de rapport PDF uniquement en cas de non-conformite
- Optimisation automatique du protocole si des ecarts sont detectes
- Interface avec barre de progression animee par etape d'agent

---

## Architecture technique

```
+-----------------------------------------------------+
|               FRONTEND (HTML / CSS / JS)            |
|  - Upload PDF          - Barre de progression       |
|  - Extraction texte    - Affichage des resultats    |
|    via pdf.js          - Telechargement rapport PDF |
+------------------------+----------------------------+
                         |
                         | HTTP POST /api/analyze
                         |
                         v
+-----------------------------------------------------+
|               BACKEND (Flask + Python)              |
|                                                     |
|  +-----------------------------------------------+ |
|  |         LangGraph -- Pipeline agents           | |
|  |                                               | |
|  |  [Analyzer] -> [ISO Expert] -> [Validator]    | |
|  |       |                            |          | |
|  |  [Risk Assessor] -> [Optimizer] -> [Scribe]   | |
|  +-----------------------------------------------+ |
|                         |                          |
|              LLM : Groq (Llama 3.1 8B)            |
|              PDF : ReportLab                       |
+-----------------------------------------------------+
```

---

## Pipeline multi-agents

Le coeur du systeme est un graphe d'agents orchestre par LangGraph. Chaque agent a un role precis :

| Numero | Agent | Role | Technologie |
|--------|-------|------|-------------|
| 1 | Analyzer | Extrait les donnees cles du protocole (temperature, pH, duree, EPI) en JSON structure | Groq LLM |
| 2 | ISO Expert | Injecte les regles ISO 22716 statiques dans le pipeline | Regles statiques |
| 3 | Validator | Compare les donnees extraites aux regles ISO et liste les violations | Groq LLM |
| 4 | Risk Assessor | Calcule un score de risque de 0 a 10 avec justification | Groq LLM |
| 5 | Optimizer | Si score superieur ou egal a 3, recrit les etapes problematiques du protocole | Groq LLM |
| 6 | Scribe | Genere le rapport d'audit final structure en 4 sections | Groq LLM |

### Logique de decision

```
Score < 3   -->  ACCEPTE  -->  Message de conformite, pas de PDF genere
Score >= 3  -->  REJETE   -->  Optimisation --> Nouveau cycle --> Rapport PDF complet
```

---

## Prerequis

Avant de commencer, assurez-vous d'avoir installe :

- Python 3.10 ou superieur
- pip (gestionnaire de paquets Python)
- Node.js (optionnel, uniquement si vous souhaitez modifier le frontend)
- Un compte Groq avec une cle API valide : https://console.groq.com
- Un navigateur moderne (Chrome, Firefox, Edge)

---

## Installation

### 1. Cloner le depot

```bash
git clone https://github.com/votre-username/ai-protocol-validator.git
cd ai-protocol-validator
```

### 2. Creer un environnement virtuel Python

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS et Linux
source venv/bin/activate
```

### 3. Installer les dependances Python

```bash
pip install -r requirements.txt
```

Contenu du fichier `requirements.txt` :

```
flask
flask-cors
python-dotenv
langchain-groq
langgraph
reportlab
```

---

## Configuration

### Creer le fichier .env

A la racine du projet, creez un fichier `.env` :

```bash
touch .env
```

Ajoutez votre cle API Groq :

```
GROQ_API_KEY=votre_cle_api_groq_ici
```

Important : ne partagez jamais votre cle API. Ajoutez `.env` a votre `.gitignore`.

### Fichier .gitignore recommande

```
.env
venv/
__pycache__/
*.pyc
*.pdf
```

---

## Lancement

### Demarrer le serveur backend Flask

```bash
python app.py
```

Le serveur demarre sur `http://localhost:5000`. Vous devriez voir dans le terminal :

```
Serveur Flask demarre sur http://localhost:5000
```

### Ouvrir le frontend

Ouvrez le fichier `index.html` directement dans votre navigateur, ou utilisez un serveur local :

```bash
# Option 1 : Python
python -m http.server 3000

# Option 2 : Node.js avec live-server
npx live-server --port=3000
```

Puis accedez a : `http://localhost:3000`

---

## Utilisation

### Etape 1 — Charger un protocole PDF

Glissez-deposez votre fichier PDF dans la zone prevue, ou cliquez sur "Parcourir les fichiers" pour selectionner votre fichier. Le fichier doit etre un PDF avec du texte extractible (non scanne).

### Etape 2 — Saisir la norme industrielle

Dans le champ "Norme Industrielle", saisissez la norme applicable. Exemple :

```
ISO 22716
```

### Etape 3 — Lancer l'analyse

Cliquez sur "Analyser le protocole". La barre de progression affiche l'avancement en temps reel a travers les 5 etapes agents.

### Etape 4 — Consulter les resultats

Une fois l'analyse terminee :

- Le score de risque est affiche sur 10 avec code couleur (vert, orange, rouge)
- La decision ACCEPTE ou REJETE est affichee
- Si ACCEPTE : un message de conformite s'affiche, aucun PDF n'est genere
- Si REJETE : le bouton de telechargement du rapport PDF apparait
- Le detail de l'analyse affiche les etapes, ingredients et normes appliquees
- La section Validation liste les erreurs detectees ou confirme la conformite

---

## Structure du projet

```
ai-protocol-validator/
|
+-- app.py                  Backend Flask et pipeline LangGraph
+-- index.html              Interface utilisateur principale
+-- script.js               Logique frontend (upload, API, resultats)
+-- styles.css              Styles CSS de l'interface
+-- requirements.txt        Dependances Python
+-- .env                    Cle API Groq (non versionnee)
+-- .gitignore              Fichiers a exclure du depot
+-- README.md               Documentation du projet
```

---

## API Reference

### POST /api/analyze

Analyse un protocole et retourne les resultats complets.

**Requete** — multipart/form-data

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| protocol | string | Oui | Texte extrait du PDF |
| norme | string | Oui | Norme industrielle (ex : ISO 22716) |

**Reponse** — application/json

```json
{
  "analysis": {
    "etapes": ["Etape 1 : ...", "Etape 2 : ..."],
    "ingredients": ["Composant A", "Composant B"],
    "normes": ["Temperature max : 75 C", "pH : 4.5 a 7.5"]
  },
  "risk_score": 2,
  "decision": "ACCEPTE",
  "validation": {
    "erreurs": []
  },
  "pdf_url": "data:application/pdf;base64,...",
  "final_report": "RESUME EXECUTIF\n..."
}
```

---

### GET /api/health

Verifie que le serveur est operationnel.

**Reponse**

```json
{
  "status": "ok",
  "message": "Server is running"
}
```

---

### POST /api/download-pdf

Telecharge le PDF genere.

**Requete** — application/json

```json
{
  "pdf_data": "data:application/pdf;base64,..."
}
```

**Reponse** : fichier PDF en telechargement direct.

---

## Normes supportees

Le systeme est pre-configure avec les regles ISO 22716 (cosmetiques) :

| Regle | Valeur |
|-------|--------|
| Temperature maximale | 75 degres C |
| pH produit fini | 4,5 a 7,5 |
| EPI obligatoires | Gants haute temperature, lunettes, tablier |
| Duree max melange a chaud | 20 minutes |
| Depassement thermique | Suspension du lot obligatoire |

D'autres normes peuvent etre ajoutees en modifiant la liste `ISO_RULES` dans `app.py`.

---

## Exemple de protocole test

Pour tester rapidement l'application, utilisez ce protocole conforme :

```
PROTOCOLE DE FABRICATION — CREME HYDRATANTE
Lot : LOT-2024-001 | Statut : CONFORME

Etape 1 : Peser les ingredients (eau purifiee, glycerine, cire emulsifiante, huile de jojoba)
Etape 2 : Chauffer la phase aqueuse a 65 degres C
Etape 3 : Chauffer la phase huileuse a 65 degres C
Etape 4 : Melange a chaud des deux phases pendant 15 minutes
Etape 5 : Refroidissement progressif jusqu'a 35 degres C
Etape 6 : Ajout des actifs thermosensibles
Etape 7 : Controle pH = 5,5
EPI portes : gants haute temperature, lunettes de protection, tablier
Temperature max atteinte : 65 degres C | Seuil autorise : 75 degres C
Depassement detecte : NON
```

---

## Resultats attendus

| Score | Couleur affichee | Decision | Action |
|-------|-----------------|----------|--------|
| 0 a 2 | Vert | ACCEPTE | Message de conformite, pas de PDF genere |
| 3 a 6 | Orange | REJETE | Optimisation automatique et rapport PDF genere |
| 7 a 10 | Rouge | REJETE | Optimisation automatique et rapport PDF detaille |

---

## Technologies utilisees

| Technologie | Usage |
|-------------|-------|
| Python 3.10+ | Backend principal |
| Flask | Serveur API REST |
| Flask-CORS | Gestion des requetes cross-origin |
| LangGraph | Orchestration du pipeline multi-agents |
| LangChain-Groq | Interface avec le LLM Llama 3.1 8B |
| Groq API | Inference LLM ultra-rapide |
| ReportLab | Generation de rapports PDF |
| pdf.js | Extraction de texte PDF cote frontend |
| HTML / CSS / JS | Interface utilisateur |
| python-dotenv | Gestion des variables d'environnement |

---

## Auteur

Developpe dans le cadre d'un projet d'intelligence artificielle appliquee a la validation de protocoles industriels.

- Contact : votre.email@exemple.com
- GitHub : https://github.com/votre-username

---

Note : Pour tester rapidement sans PDF, copiez le texte du protocole exemple dans un fichier `.txt`, renommez-le en `.pdf`, et chargez-le dans l'application. Le systeme lira le texte brut automatiquement via le fallback de lecture.
