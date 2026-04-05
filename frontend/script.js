// ==================== CONFIGURATION ====================
const API_BASE_URL = 'http://localhost:5000/api';
let currentAnalysisResult = null;
let currentFile = null;

// ==================== DOM ELEMENTS ====================
// IDs qui correspondent EXACTEMENT à index.html
const dropZone         = document.getElementById('dropZone');
const fileInput        = document.getElementById('fileInput');
const fileNameDisplay  = document.getElementById('fileNameDisplay');
const normInput        = document.getElementById('normInput');
const analyzeBtn       = document.getElementById('analyzeBtn');
const downloadPdfBtn   = document.getElementById('downloadPdfBtn');
const loadingSection   = document.getElementById('loadingSection');
const resultsSection   = document.getElementById('resultsSection');

// ==================== DRAG & DROP ====================
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        if (files[0].type === 'application/pdf') {
            handleFileSelect(files[0]);
        } else {
            alert('Veuillez sélectionner un fichier PDF.');
        }
    }
});

// ==================== FILE INPUT ====================
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    currentFile = file;

    // ✅ Affiche le nom du fichier dans #fileNameDisplay
    fileNameDisplay.textContent = `✅ ${file.name} (${(file.size / 1024).toFixed(1)} Ko)`;
    fileNameDisplay.style.color = '#10b981';

    // ✅ Active le bouton Analyser seulement si la norme est aussi remplie
    checkFormReady();
}

// ==================== NORME INPUT ====================
normInput.addEventListener('input', checkFormReady);

function checkFormReady() {
    // Le bouton est activé uniquement si fichier + norme sont présents
    analyzeBtn.disabled = !(currentFile && normInput.value.trim().length > 0);
}

// ==================== ANALYZE BUTTON ====================
analyzeBtn.addEventListener('click', async () => {
    if (currentFile && normInput.value.trim()) {
        await analyzeProtocol();
    }
});

// ==================== ANALYZE PROTOCOL ====================
async function analyzeProtocol() {
    analyzeBtn.disabled = true;

    // ✅ Timeout 120s avec AbortController
    const controller = new AbortController();
    const timeoutId  = setTimeout(() => controller.abort(), 120_000);

    try {
        showLoading();

        // ✅ Extraction réelle du texte PDF
        const protocolText = await extractTextFromPDF(currentFile);

        if (!protocolText || protocolText.trim().length < 20) {
            throw new Error('Impossible d\'extraire le texte. Le PDF est peut-être scanné (image uniquement).');
        }

        const formData = new FormData();
        formData.append('protocol', protocolText);
        formData.append('norme', normInput.value.trim());

        console.log('📤 Envoi au serveur...');
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erreur lors de l\'analyse');
        }

        const result = await response.json();
        currentAnalysisResult = result;

        displayResults(result);
        showResults();

    } catch (error) {
        clearTimeout(timeoutId);
        hideLoading();
        analyzeBtn.disabled = false;

        if (error.name === 'AbortError') {
            alert('⏱️ La requête a expiré (> 120 s). Vérifiez que le serveur Flask est démarré sur le port 5000.');
        } else {
            alert('❌ Erreur : ' + (error.message || 'Une erreur s\'est produite'));
        }
        console.error('Erreur analyse:', error);
    }
}

// ==================== EXTRACTION PDF RÉELLE ====================
/**
 * Utilise pdf.js si disponible, sinon lecture texte brute.
 * Ajoutez dans votre index.html avant script.js :
 * <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
 */
async function extractTextFromPDF(file) {
    if (typeof pdfjsLib !== 'undefined') {
        // ✅ Extraction réelle page par page
        pdfjsLib.GlobalWorkerOptions.workerSrc =
            'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

        const arrayBuffer = await file.arrayBuffer();
        const pdf         = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        let fullText      = '';

        for (let i = 1; i <= pdf.numPages; i++) {
            const page    = await pdf.getPage(i);
            const content = await page.getTextContent();
            fullText += content.items.map(item => item.str).join(' ') + '\n';
        }
        return fullText.trim();
    }

    // Fallback : lecture texte brute (fichiers .txt renommés en .pdf)
    return new Promise((resolve, reject) => {
        const reader   = new FileReader();
        reader.onload  = (e) => resolve(e.target.result);
        reader.onerror = ()  => reject(new Error('Lecture du fichier échouée'));
        reader.readAsText(file);
    });
}

// ==================== PROGRESS ANIMATION ====================
let progressInterval = null;

function startProgress() {
    const progressBar    = document.getElementById('progressBar');
    const pipelineStep   = document.getElementById('pipelineStep');
    const pipelinePerc   = document.getElementById('pipelinePercentage');

    const stages = [
        { id: 'stage1', label: 'Agent 1 : Extraction PDF...',          max: 20  },
        { id: 'stage2', label: 'Agent 2 : Analyse sémantique...',       max: 45  },
        { id: 'stage3', label: 'Agent 3 : Vérification des normes...',  max: 65  },
        { id: 'stage4', label: 'Agent 4 : Évaluation du risque...',     max: 85  },
        { id: 'stage5', label: 'Agent 5 : Génération du rapport...',    max: 95  },
    ];

    let progress    = 0;
    let stageIndex  = 0;

    // Reset visuel
    stages.forEach(s => {
        const el = document.getElementById(s.id);
        if (el) { el.className = 'stage pending'; }
    });

    progressInterval = setInterval(() => {
        const currentStage = stages[stageIndex];
        if (!currentStage) return;

        progress += Math.random() * 4 + 1;
        if (progress > currentStage.max) progress = currentStage.max;

        // Met à jour la barre
        progressBar.style.width    = progress + '%';
        pipelinePerc.textContent   = Math.round(progress) + '%';
        pipelineStep.textContent   = currentStage.label;

        // Marque l'étape active
        const el = document.getElementById(currentStage.id);
        if (el) el.className = 'stage active';

        // Passe à l'étape suivante
        if (progress >= currentStage.max) {
            if (el) el.className = 'stage completed';
            stageIndex++;
        }

        if (progress >= 95) clearInterval(progressInterval);
    }, 150);
}

function stopProgress() {
    clearInterval(progressInterval);
    const progressBar = document.getElementById('progressBar');
    if (progressBar) progressBar.style.width = '100%';
    ['stage1','stage2','stage3','stage4','stage5'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.className = 'stage completed';
    });
}

// ==================== DISPLAY RESULTS ====================
function displayResults(result) {
    // Score de risque
    const riskScoreEl = document.getElementById('riskScoreValue');
    const riskCard    = document.getElementById('riskCard');
    riskScoreEl.textContent = result.risk_score + '/10';

    if (result.risk_score <= 3) {
        riskCard.style.borderColor  = '#10b981';
        riskScoreEl.style.color     = '#10b981';
    } else if (result.risk_score <= 6) {
        riskCard.style.borderColor  = '#f59e0b';
        riskScoreEl.style.color     = '#f59e0b';
    } else {
        riskCard.style.borderColor  = '#ef4444';
        riskScoreEl.style.color     = '#ef4444';
    }

    // Badge décision
    const badge = document.getElementById('decisionBadge');
    badge.textContent = result.decision;
    badge.className   = 'decision-badge ' + (result.decision.includes('ACCEPTÉ') ? 'accept' : 'reject');

    // Étapes
    const stepsList = document.getElementById('analysisSteps');
    stepsList.innerHTML = '';
    (result.analysis?.etapes || []).forEach(step => {
        if (step.trim()) {
            const li = document.createElement('li');
            li.textContent = step;
            stepsList.appendChild(li);
        }
    });

    // Ingrédients
    const ingContainer = document.getElementById('analysisIngredients');
    ingContainer.innerHTML = '';
    (result.analysis?.ingredients || []).forEach(ing => {
        const chip = document.createElement('span');
        chip.className   = 'chip';
        chip.textContent = ing;
        ingContainer.appendChild(chip);
    });

    // Normes
    const normsList = document.getElementById('analysisNorms');
    normsList.innerHTML = '';
    (result.analysis?.normes || []).forEach(norm => {
        const li = document.createElement('li');
        li.textContent = norm;
        normsList.appendChild(li);
    });

    // Erreurs
    const errorsList = document.getElementById('analysisErrors');
    errorsList.innerHTML = '';
    const errors = result.validation?.erreurs || [];
    if (errors.length > 0) {
        errors.forEach(err => {
            const li = document.createElement('li');
            li.innerHTML    = `🔴 ${err}`;
            li.style.color  = '#ef4444';
            errorsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.innerHTML   = '✅ Aucune erreur détectée';
        li.style.color = '#10b981';
        errorsList.appendChild(li);
    }
}

// ==================== DOWNLOAD PDF ====================
downloadPdfBtn.addEventListener('click', () => {
    if (!currentAnalysisResult?.pdf_url) {
        alert('PDF non disponible.');
        return;
    }
    const link    = document.createElement('a');
    link.href     = currentAnalysisResult.pdf_url;
    link.download = `rapport_${normInput.value}_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// ==================== UI STATE ====================
function showLoading() {
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    startProgress();
}

function hideLoading() {
    stopProgress();
    loadingSection.classList.add('hidden');
}

function showResults() {
    hideLoading();
    resultsSection.classList.remove('hidden');
    analyzeBtn.disabled = false;
}

console.log('✅ AI Protocol Validator — script chargé');