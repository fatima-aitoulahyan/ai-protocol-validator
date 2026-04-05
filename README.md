# 🧪 AI Protocol Validator

> Plateforme intelligente de validation de protocoles industriels et cosmétiques basée sur l'intelligence artificielle multi-agents (LangGraph + Groq).

---

## 📋 Table des matières

- [Aperçu du projet](#aperçu-du-projet)
- [Fonctionnalités](#fonctionnalités)
- [Architecture technique](#architecture-technique)
- [Pipeline multi-agents](#pipeline-multi-agents)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [API Reference](#api-reference)
- [Normes supportées](#normes-supportées)
- [Exemple de protocole test](#exemple-de-protocole-test)
- [Résultats attendus](#résultats-attendus)
- [Technologies utilisées](#technologies-utilisées)
- [Auteur](#auteur)

---

## 📌 Aperçu du projet

**AI Protocol Validator** est une application web full-stack qui permet de valider automatiquement des protocoles de fabrication (cosmétique, pharmaceutique, agroalimentaire) contre des normes industrielles telles que **ISO 22716**.

L'utilisateur charge un fichier PDF contenant son protocole, sélectionne la norme applicable, et le système orchestre un pipeline de 6 agents IA spécialisés qui analysent, vérifient, évaluent le risque, et génèrent un rapport de conformité complet.

---

## ✨ Fonctionnalités

- 📄 **Import PDF** — Glisser-déposer ou sélection de fichier PDF
- 🤖 **Analyse multi-agents** — Pipeline LangGraph avec 6 agents IA spécialisés
- 📏 **Vérification ISO** — Contrôle automatique contre les règles ISO 22716
- 📊 **Score de risque** — Évaluation sur 10 avec justification
- ✅ **Décision automatique** — ACCEPTÉ ou REJETÉ selon le score
- 📑 **Rapport PDF** — Généré automatiquement en cas de non-conformité
- 🔄 **Optimisation automatique** — Le protocole est corrigé si des écarts sont détectés
- 🎯 **Interface intuitive** — Barre de progression animée par étape d'agent

---

## 🏗️ Architecture technique

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (HTML/CSS/JS)             │
│  - Upload PDF        - Barre de progression          │
│  - Extraction texte  - Affichage résultats           │
│    (pdf.js)          - Téléchargement rapport PDF    │
└────────────────────────┬────────────────────────────┘
                         │ HTTP POST /api/analyze
                         ▼
┌─────────────────────────────────────────────────────┐
│                  BACKEND (Flask + Python)            │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           LangGraph — Pipeline agents        │   │
│  │                                             │   │
│  │  [Analyzer] → [ISO Expert] → [Validator]    │   │
│  │       ↓                          ↓          │   │
│  │  [Risk Assessor] → [Optimizer] → [Scribe]   │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│               LLM : Groq (Llama 3.1 8B)            │
│               PDF : ReportLab                       │
└─────────────────────────────────────────────────────┘
```

---

## 🤖 Pipeline multi-agents

Le coeur du système est un graphe d'agents orchestré par **LangGraph**. Chaque agent a un rôle précis :

| # | Agent | Rôle | Technologie |
|---|-------|------|-------------|
| 1 | **Analyzer** | Extrait les données clés du protocole (température, pH, durée, EPI...) en JSON structuré | Groq LLM |
| 2 | **ISO Expert** | Injecte les règles ISO 22716 statiques dans le pipeline | Règles statiques |
| 3 | **Validator** | Compare les données extraites aux règles ISO et liste les violations | Groq LLM |
| 4 | **Risk Assessor** | Calcule un score de risque de 0 à 10 avec justification | Groq LLM |
| 5 | **Optimizer** | Si score ≥ 3, réécrit les étapes problématiques du protocole | Groq LLM |
| 6 | **Scribe** | Génère le rapport d'audit final structuré en 4 sections | Groq LLM |

### Logique de décision

```
Score < 3  → ACCEPTÉ  → Rapport automatique sans LLM (Scribe Direct)
Score ≥ 3  → REJETÉ   → Optimisation → Nouveau cycle → Rapport complet PDF
```

---

## ✅ Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python** 3.10 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Node.js** (optionnel, uniquement si vous souhaitez modifier le frontend)
- Un compte **Groq** avec une clé API valide → [https://console.groq.com](https://console.groq.com)
- Un navigateur moderne (Chrome, Firefox, Edge)

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/ai-protocol-validator.git
cd ai-protocol-validator
```

### 2. Créer un environnement virtuel Python

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

**Contenu de `requirements.txt` :**

```
flask
flask-cors
python-dotenv
langchain-groq
langgraph
reportlab
```

---

## ⚙️ Configuration

### Créer le fichier `.env`

À la racine du projet, créez un fichier `.env` :

```bash
touch .env
```

Ajoutez votre clé API Groq :

```env
GROQ_API_KEY=votre_cle_api_groq_ici
```

> ⚠️ **Important** : Ne partagez jamais votre clé API. Ajoutez `.env` à votre `.gitignore`.

### Fichier `.gitignore` recommandé

```
.env
venv/
__pycache__/
*.pyc
*.pdf
```

---

## ▶️ Lancement

### Démarrer le serveur backend Flask

```bash
python app.py
```

Le serveur démarre sur `http://localhost:5000`.

Vous devriez voir :

```
🚀 Serveur Flask démarré sur http://localhost:5000
```

### Ouvrir le frontend

Ouvrez le fichier `index.html` directement dans votre navigateur, ou utilisez un serveur local :

```bash
# Option 1 : Python
python -m http.server 3000

# Option 2 : Node.js (live-server)
npx live-server --port=3000
```

Accédez à : `http://localhost:3000`

---

## 🖥️ Utilisation

### Étape 1 — Charger un protocole PDF

Glissez-déposez votre fichier PDF dans la zone prévue, ou cliquez sur **"Parcourir les fichiers"** pour sélectionner votre fichier.

> Le fichier doit être un PDF avec du texte extractible (non scanné).

### Étape 2 — Saisir la norme industrielle

Dans le champ **"Norme Industrielle"**, saisissez la norme applicable, par exemple :

```
ISO 22716
```

### Étape 3 — Lancer l'analyse

Cliquez sur **"Analyser le protocole"**. La barre de progression affiche l'avancement en temps réel à travers les 5 étapes agents.

### Étape 4 — Consulter les résultats

Une fois l'analyse terminée :

- **Score de risque** — Affiché sur 10 avec code couleur (vert / orange / rouge)
- **Décision** — ACCEPTÉ ou REJETÉ
- Si **ACCEPTÉ** → Message de conformité affiché, aucun PDF généré
- Si **REJETÉ** → Bouton de téléchargement du rapport PDF disponible
- **Analyse du protocole** — Étapes, ingrédients, normes appliquées
- **Validation** — Liste des erreurs détectées ou confirmation de conformité

---

## 📁 Structure du projet

```
ai-protocol-validator/
│
├── app.py                  # Backend Flask + Pipeline LangGraph
├── index.html              # Interface utilisateur principale
├── script.js               # Logique frontend (upload, API, résultats)
├── styles.css              # Styles CSS de l'interface
├── requirements.txt        # Dépendances Python
├── .env                    # Clé API Groq (non versionné)
├── .gitignore              # Fichiers à exclure du dépôt
└── README.md               # Documentation du projet
```

---

## 📡 API Reference

### `POST /api/analyze`

Analyse un protocole et retourne les résultats complets.

**Request** — `multipart/form-data`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `protocol` | `string` | ✅ | Texte extrait du PDF |
| `norme` | `string` | ✅ | Norme industrielle (ex: ISO 22716) |

**Response** — `application/json`

```json
{
  "analysis": {
    "etapes": ["Étape 1 : ...", "Étape 2 : ..."],
    "ingredients": ["Composant A", "Composant B"],
    "normes": ["Température max : 75°C", "pH : 4.5–7.5", "..."]
  },
  "risk_score": 2,
  "decision": "ACCEPTÉ",
  "validation": {
    "erreurs": []
  },
  "pdf_url": "data:application/pdf;base64,...",
  "final_report": "RÉSUMÉ EXÉCUTIF\n..."
}
```

---

### `GET /api/health`

Vérifie que le serveur est opérationnel.

**Response**

```json
{
  "status": "ok",
  "message": "Server is running"
}
```

---

### `POST /api/download-pdf`

Télécharge le PDF généré.

**Request** — `application/json`

```json
{
  "pdf_data": "data:application/pdf;base64,..."
}
```

**Response** — Fichier PDF en téléchargement direct.

---

## 📏 Normes supportées

Le système est pré-configuré avec les règles **ISO 22716** (cosmétiques) :

| Règle | Valeur |
|-------|--------|
| Température maximale | 75 °C |
| pH produit fini | 4,5 à 7,5 |
| EPI obligatoires | Gants haute température + lunettes + tablier |
| Durée max mélange à chaud | 20 minutes |
| Dépassement thermique | Suspension du lot obligatoire |

> D'autres normes peuvent être ajoutées en modifiant la liste `ISO_RULES` dans `app.py`.

---

## 🧪 Exemple de protocole test

Pour tester rapidement l'application, utilisez ce protocole conforme :

```
PROTOCOLE DE FABRICATION — CRÈME HYDRATANTE
Lot : LOT-2024-001 | Statut : CONFORME

Étape 1 : Peser les ingrédients (eau purifiée, glycérine, cire émulsifiante, huile de jojoba)
Étape 2 : Chauffer la phase aqueuse à 65°C
Étape 3 : Chauffer la phase huileuse à 65°C
Étape 4 : Mélange à chaud des deux phases pendant 15 minutes
Étape 5 : Refroidissement progressif jusqu'à 35°C
Étape 6 : Ajout des actifs thermosensibles
Étape 7 : Contrôle pH = 5,5
EPI portés : gants haute température, lunettes de protection, tablier
Température max atteinte : 65°C | Seuil autorisé : 75°C
Dépassement détecté : NON
```

---

## 📊 Résultats attendus

| Score | Couleur | Décision | Action |
|-------|---------|----------|--------|
| 0 – 2 | 🟢 Vert | ACCEPTÉ | Message de conformité, pas de PDF |
| 3 – 6 | 🟡 Orange | REJETÉ | Optimisation + rapport PDF généré |
| 7 – 10 | 🔴 Rouge | REJETÉ | Optimisation + rapport PDF détaillé |

---

## 🛠️ Technologies utilisées

| Technologie | Usage |
|-------------|-------|
| **Python 3.10+** | Backend principal |
| **Flask** | Serveur API REST |
| **Flask-CORS** | Gestion des requêtes cross-origin |
| **LangGraph** | Orchestration du pipeline multi-agents |
| **LangChain-Groq** | Interface LLM (Llama 3.1 8B Instant) |
| **Groq API** | Inférence LLM ultra-rapide |
| **ReportLab** | Génération de rapports PDF |
| **pdf.js** | Extraction de texte côté frontend |
| **HTML / CSS / JS** | Interface utilisateur |
| **python-dotenv** | Gestion des variables d'environnement |

---

## 👤 Auteur

Développé dans le cadre d'un projet d'intelligence artificielle appliquée à la validation de protocoles industriels.

- 📧 Contact : votre.email@exemple.com
- 🐙 GitHub : [github.com/votre-username](https://github.com/votre-username)

---

> 💡 **Astuce** : Pour tester rapidement sans PDF, copiez le texte du protocole exemple dans un fichier `.txt`, renommez-le en `.pdf`, et chargez-le dans l'application. Le fallback de lecture texte prendra le relais automatiquement.
