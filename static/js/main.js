// Initialize end year with current year
window.addEventListener('DOMContentLoaded', function() {
    const currentYear = new Date().getFullYear();
    const anneeFinInput = document.getElementById('annee_fin');
    anneeFinInput.value = currentYear;
    anneeFinInput.max = currentYear;
    document.getElementById('annee_debut').max = currentYear;
});

// Handle "Select all/Deselect all" button for Twitter
document.getElementById('twitter-toggle-all').addEventListener('click', function(e) {
    e.preventDefault();
    const checkboxes = document.querySelectorAll('.twitter-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
    
    this.textContent = allChecked ? 'Tout sélectionner' : 'Tout désélectionner';
});

// Handle Twitter form submission
document.getElementById('twitter-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('twitter-file');
    const checkboxes = document.querySelectorAll('input[name="features"]:checked');
    const alertDiv = document.getElementById('twitter-alert');
    const loadingDiv = document.getElementById('twitter-loading');
    
    // Check that at least one feature is selected
    if (checkboxes.length === 0) {
        showAlert(alertDiv, 'Veuillez sélectionner au moins une feature', 'error');
        return;
    }
    
    // Check that a file is selected
    if (!fileInput.files.length) {
        showAlert(alertDiv, 'Veuillez sélectionner un fichier', 'error');
        return;
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    // Add selected features
    checkboxes.forEach(checkbox => {
        formData.append('features', checkbox.value);
    });
    
    // Add output format
    const format = document.querySelector('#twitter-form input[name="output_format"]:checked').value;
    formData.append('output_format', format);
    
    // Show loading
    loadingDiv.style.display = 'block';
    alertDiv.classList.remove('show');
    
    try {
        const response = await fetch('/extract-twitter', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, `tweets_extracted.${format}`);
            showAlert(alertDiv, 'Fichier téléchargé avec succès!', 'success');
        } else {
            const error = await response.json();
            showAlert(alertDiv, error.error || 'Une erreur est survenue', 'error');
        }
    } catch (error) {
        showAlert(alertDiv, 'Erreur de connexion: ' + error.message, 'error');
    } finally {
        loadingDiv.style.display = 'none';
    }
});

// Handle SM Caen form submission
document.getElementById('caen-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const debut = parseInt(document.getElementById('annee_debut').value);
    const fin = parseInt(document.getElementById('annee_fin').value);
    const alertDiv = document.getElementById('caen-alert');
    const loadingDiv = document.getElementById('caen-loading');
    
    // Validate years
    if (debut >= fin) {
        showAlert(alertDiv, 'L\'année de fin doit être strictement supérieure à l\'année de début', 'error');
        return;
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('annee_debut', debut);
    formData.append('annee_fin', fin);
    
    // Add output format
    const format = document.querySelector('#caen-form input[name="output_format"]:checked').value;
    formData.append('output_format', format);
    
    // Show loading
    loadingDiv.style.display = 'block';
    alertDiv.classList.remove('show');
    
    try {
        const response = await fetch('/extract-caen', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, `caen_data_${debut}_${fin}.${format}`);
            showAlert(alertDiv, 'Fichier téléchargé avec succès!', 'success');
        } else {
            const error = await response.json();
            showAlert(alertDiv, error.error || 'Une erreur est survenue', 'error');
        }
    } catch (error) {
        showAlert(alertDiv, 'Erreur de connexion: ' + error.message, 'error');
    } finally {
        loadingDiv.style.display = 'none';
    }
});

// Utility functions
function showAlert(alertDiv, message, type) {
    alertDiv.textContent = message;
    alertDiv.className = `alert show ${type}`;
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
