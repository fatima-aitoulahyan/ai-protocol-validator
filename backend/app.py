import json
import time
import os
import re
import base64
from io import BytesIO
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import operator
from typing import List, TypedDict, Annotated, Optional
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from dotenv import load_dotenv

# ==================== CONFIGURATION FLASK ====================
app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION LLM ====================

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise EnvironmentError(" GROQ_API_KEY manquante. Ajoutez-la dans votre fichier .env")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=1024,
    api_key=groq_api_key
)

def safe_invoke(prompt: str):
    """Retry exponentiel sur quota 429."""
    for attempt in range(3):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if "429" not in str(e):
                raise
            wait = 30 * (attempt + 1)
            print(f"⚠️ Quota ({attempt+1}/3) — pause {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Quota épuisé après 3 tentatives.")

# ==================== ÉTAT LANGGRAPH ====================
class AgentState(TypedDict):
    protocol_raw: str
    structured_data: Optional[str]
    # ✅ FIX 2 : on garde operator.add pour les deux champs accumulateurs,
    #            mais on réinitialise explicitement dans optimizer_node
    iso_rules: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    risk_score: int
    risk_justification: str
    iterations: int
    final_report: str

# ==================== RÈGLES ISO STATIQUES ====================
ISO_RULES = [
    "Température max absolue : 75 °C (ISO 22716) — tout pic au-dessus est une violation.",
    "pH produit fini : 4,5–7,5 (ISO 22716).",
    "EPI obligatoires : gants haute température + lunettes + tablier en phase chaude.",
    "Durée max mélange à chaud : 20 min (ISO 22716).",
    "Tout lot avec dépassement thermique doit être suspendu jusqu'au contrôle qualité.",
]

# ==================== AGENTS LANGGRAPH ====================

def analyzer_node(state: AgentState) -> dict:
    print("─── AGENT 1 : ANALYSE ───")
    res = safe_invoke(
        "Tu analyses un rapport de surveillance IoT d'un protocole cosmétique.\n"
        "Le texte peut contenir des tableaux mal formatés (valeurs séparées par espaces).\n"
        "Extrais UNIQUEMENT ce JSON (champs absents = null) :\n"
        "{\n"
        '  "produit": "nom du produit en cours",\n'
        '  "temp_max_atteinte_C": valeur numérique du pic de température détecté,\n'
        '  "temp_seuil_C": seuil max autorisé par le protocole,\n'
        '  "temps_min": durée de mélange à chaud en minutes,\n'
        '  "epi_mentionnes": true/false selon si des EPI sont mentionnés,\n'
        '  "pH_controle": valeur numérique du pH attendu ou mesuré,\n'
        '  "statut_lot": statut du lot (ex: SUSPENDU, CONFORME...),\n'
        '  "depassement_detecte": true/false\n'
        "}\n"
        "Réponds UNIQUEMENT avec le JSON brut, sans commentaire.\n\n"
        f"Rapport :\n{state['protocol_raw']}"
    )
    return {
        "structured_data": res.content,
        "iterations": state.get("iterations", 0) + 1,
    }

def iso_expert_node(state: AgentState) -> dict:
    """Agent 2 : Vérification ISO."""
    print("─── AGENT 2 : ISO (statique) ───")
    return {"iso_rules": ISO_RULES}

def validator_node(state: AgentState) -> dict:
    print("─── AGENT 3 : VALIDATION ───")
    unique_rules = list(dict.fromkeys(state["iso_rules"]))
    rules_str = "\n".join(f"- {r}" for r in unique_rules)
    res = safe_invoke(
        "Tu valides un protocole cosmétique IoT contre les règles ISO.\n"
        f"Données extraites (JSON) :\n{state['structured_data']}\n\n"
        f"Règles ISO à vérifier :\n{rules_str}\n\n"
        "IMPORTANT : compare temp_max_atteinte_C avec la règle température max.\n"
        "Liste les violations constatées (1 ligne par violation, sois précis avec les valeurs).\n"
        "Si tout est conforme, réponds exactement 'OK'."
    )
    return {"errors": [res.content] if res.content.strip() != "OK" else []}

def risk_assessor_node(state: AgentState) -> dict:
    """Agent 4 : Évaluation du risque."""
    print("─── AGENT 4 : RISQUE ───")
    # On déduplique les erreurs avant de les envoyer au LLM
    unique_errors = list(dict.fromkeys(state["errors"]))
    errors_str = "\n".join(unique_errors) if unique_errors else "Aucune violation"
    res = safe_invoke(
        f"Violations : {errors_str}\n"
        "Réponds UNIQUEMENT en JSON : "
        '{"score":0-10,"justification":"<20 mots max"}'
    )
    try:
        m = re.search(r"\{.*?\}", res.content, re.DOTALL)
        d = json.loads(m.group())
        return {"risk_score": int(d["score"]), "risk_justification": d["justification"]}
    except Exception:
        return {"risk_score": 5, "risk_justification": "Parsing échoué."}

def optimizer_node(state: AgentState) -> dict:
    """Agent 5 : Optimisation."""
    print("─── AGENT 5 : OPTIMISATION ───")
    # ✅ FIX 2 : on réinitialise errors et iso_rules pour éviter l'accumulation
    #            lors du prochain cycle analyze → iso → validate
    unique_errors = list(dict.fromkeys(state["errors"]))
    violations = "\n".join(unique_errors)
    res = safe_invoke(
        f"Protocole à corriger :\n{state['protocol_raw']}\n"
        f"Violations :\n{violations}\n"
        "Réécris UNIQUEMENT les étapes problématiques corrigées, en bullet points."
    )
    return {
        "protocol_raw": res.content,
        "structured_data": None,
        # ✅ FIX 2 : listes remises à zéro — operator.add repartira de []
        "errors": [],
        "iso_rules": [],
    }

def scribe_node(state: AgentState) -> dict:
    """Agent 6 : Génération du rapport."""
    print("─── AGENT 6 : RAPPORT ───")
    verdict = "CONFORME" if state["risk_score"] < 3 else "NON CONFORME"
    unique_errors = list(dict.fromkeys(state["errors"]))
    violations = "\n".join(unique_errors) or "Aucune"
    # APRÈS
    res = safe_invoke(
        "Tu es un expert en audit de protocoles de fabrication cosmétique. "
        "Rédige un rapport d'audit professionnel en français UNIQUEMENT sur le protocole fourni. "
        "Ne parle jamais de code informatique, de fichiers JSON ou de programmation. "
        "Sections exactes : RÉSUMÉ EXÉCUTIF | ÉCARTS ISO | PROTOCOLE CORRIGÉ | RECOMMANDATIONS. "
        "Sois concis (max 300 mots).\n"
        f"Verdict : {verdict} | Score : {state['risk_score']}/10\n"
        f"Justification : {state['risk_justification']}\n"
        f"Violations : {violations}\n"
        f"Protocole final : {state['protocol_raw']}"
    )
    return {"final_report": res.content}

def should_continue(state: AgentState) -> str:
    score = state["risk_score"]
    iterations = state.get("iterations", 0)

    if score >= 3 and iterations <= 1:
        print(f"→ Score {score}/10 : optimisation requise (itération {iterations})")
        return "optimize"
    elif score < 3 and iterations <= 1:
        # ✅ Conforme dès le 1er passage → rapport simple, pas de LLM
        print(f"→ Score {score}/10 : conforme dès le départ → rapport direct")
        return "scribe_direct"
    else:
        # Après optimisation → rapport complet via LLM
        print(f"→ Score {score}/10 : rédaction du rapport final post-optimisation")
        return "scribe"

def scribe_direct_node(state: AgentState) -> dict:
    """Agent 6b : Rapport automatique sans LLM si protocole déjà conforme."""
    print("─── AGENT 6b : RAPPORT DIRECT (conforme) ───")
    score = state["risk_score"]
    justification = state["risk_justification"]

    report = (
        "RÉSUMÉ EXÉCUTIF\n"
        f"Le protocole analysé est conforme aux normes ISO applicables. "
        f"Score de risque : {score}/10.\n\n"
        "ÉCARTS ISO\n"
        "Aucun écart détecté. Toutes les exigences sont respectées.\n\n"
        "PROTOCOLE CORRIGÉ\n"
        "Aucune correction nécessaire. Le protocole original est validé tel quel.\n\n"
        "RECOMMANDATIONS\n"
        f"- Maintenir les pratiques actuelles.\n"
        f"- Justification du score : {justification}\n"
        "- Conserver les enregistrements de conformité pour audit futur."
    )
    return {"final_report": report}
def create_graph():
    workflow = StateGraph(AgentState)

    for name, fn in [
        ("analyze", analyzer_node),
        ("iso", iso_expert_node),
        ("validate", validator_node),
        ("assess", risk_assessor_node),
        ("optimize", optimizer_node),
        ("scribe", scribe_node),
        ("scribe_direct", scribe_direct_node),
    ]:
        workflow.add_node(name, fn)

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "iso")
    workflow.add_edge("iso", "validate")
    workflow.add_edge("validate", "assess")
    workflow.add_conditional_edges(
        "assess",
        should_continue,
        {
            "optimize": "optimize",
            "scribe": "scribe",
            "scribe_direct": "scribe_direct",
        }
    )
    workflow.add_edge("optimize", "analyze")
    workflow.add_edge("scribe", END)
    workflow.add_edge("scribe_direct", END)

    return workflow.compile()

app.graph = create_graph()
PROMPT_PDF = """
Tu es un expert en audit ISO.

Génère un rapport structuré et professionnel prêt à être transformé en PDF.

Structure :

# INTRODUCTION
# RÉSUMÉ GLOBAL
# SCORE DE RISQUE
# ANALYSE DÉTAILLÉE
# NON-CONFORMITÉS
# RECOMMANDATIONS
# CONCLUSION

Règles :
- Utilise des titres clairs
- Utilise des listes à puces
- Utilise un langage professionnel
- Chaque section doit être bien détaillée mais concise

Données :
{input_data}
"""
# ==================== GÉNÉRATION PDF ====================
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import re

def clean_text(text: str) -> str:
    """Supprime les caractères Markdown comme ** et *."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # enlève **gras**
    text = text.replace("*", "")  # enlève les autres *
    return text
def generate_pdf_bytes(output: dict) -> bytes:
    """Génère un PDF structuré et professionnel en mémoire."""

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

    styles = getSampleStyleSheet()

    # Styles personnalisés
    styles.add(ParagraphStyle(
        name="CustomTitle",
        fontSize=16,
        leading=20,
        spaceAfter=12,
        fontName="Helvetica-Bold"
    ))

    styles.add(ParagraphStyle(
        name="CustomHeading",
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    ))

    styles.add(ParagraphStyle(
        name="CustomNormal",
        fontSize=10,
        leading=14
    ))

    story = []

    # ===== TITRE =====
    story.append(Paragraph("RAPPORT DE CONFORMITÉ ISO - AI VALIDATOR", styles["CustomTitle"]))
    story.append(Spacer(1, 16))

    # ===== SCORE DE RISQUE =====
    score = output.get("risk_score", 0)

    if score < 3:
        bg = colors.HexColor("#3B6D11")
    elif score < 7:
        bg = colors.HexColor("#854F0B")
    else:
        bg = colors.HexColor("#A32D2D")

    table = Table([[f"SCORE DE RISQUE : {score}/10"]], colWidths=[250])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # ===== CONTENU DU RAPPORT =====
    for line in output.get("final_report", "").split("\n"):
        line = clean_text(line.strip())

        if not line:
            story.append(Spacer(1, 6))

        elif line.startswith("# "):
            story.append(Paragraph(line[2:], styles["CustomHeading"]))

        elif line.isupper():
            story.append(Paragraph(line, styles["CustomHeading"]))

        elif line.startswith("-"):
            story.append(Paragraph(f"• {line[1:].strip()}", styles["CustomNormal"]))

        else:
            story.append(Paragraph(line, styles["CustomNormal"]))

    # ===== CONSTRUCTION DU PDF =====
    doc.build(story)

    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# ==================== API ENDPOINTS ====================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Endpoint principal : reçoit le protocole et la norme,
    retourne l'analyse complète + PDF en base64.
    """
    try:
        protocol_text = request.form.get('protocol', '').strip()
        norme = request.form.get('norme', 'ISO 22716')

        if not protocol_text:
            return jsonify({"error": "Protocole vide"}), 400

        # ✅ FIX 3 : on refuse les placeholders envoyés par le frontend si le vrai texte n'est pas fourni
        if "Contenu du PDF" in protocol_text and len(protocol_text) < 100:
            return jsonify({"error": "Le texte du PDF n'a pas été correctement extrait côté frontend."}), 400

        print(f"\n🚀 Lancement de l'analyse pour : {norme}")
        final_output = app.graph.invoke({
            "protocol_raw": protocol_text,
            "iterations": 0,
            "errors": [],
            "iso_rules": [],
            "risk_score": 0,
            "risk_justification": "",
            "structured_data": None,
            "final_report": "",
        })

        pdf_bytes = generate_pdf_bytes(final_output)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Déduplique avant de renvoyer au frontend
        unique_errors = list(dict.fromkeys(final_output.get("errors", [])))
        unique_rules  = list(dict.fromkeys(final_output.get("iso_rules", ISO_RULES)))

        response_data = {
            "analysis": {
                "etapes": [l for l in final_output.get("protocol_raw", "").split("\n") if l.strip()][:5],
                "ingredients": ["Composant A", "Composant B"],
                "normes": unique_rules
            },
            "risk_score": final_output["risk_score"],
            "decision": "ACCEPTÉ" if final_output["risk_score"] < 7 else "REJETÉ",
            "validation": {
                "erreurs": unique_errors
            },
            "pdf_url": f"data:application/pdf;base64,{pdf_base64}",
            "final_report": final_output["final_report"]
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Endpoint pour télécharger le PDF généré."""
    try:
        pdf_data = request.json.get('pdf_data', '')
        pdf_bytes = base64.b64decode(pdf_data.split(',')[1])
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='rapport_conformite.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"}), 200


# ==================== LANCEMENT ====================
if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)