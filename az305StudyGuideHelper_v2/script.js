// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Show corresponding content
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            // Save current tab to localStorage
            localStorage.setItem('currentTab', tabId);
        });
    });
    
    // Restore last active tab from localStorage
    const savedTab = localStorage.getItem('currentTab');
    if (savedTab) {
        const savedButton = document.querySelector(`[data-tab="${savedTab}"]`);
        if (savedButton) {
            savedButton.click();
        }
    }
    
    // Checkbox progress tracking
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    // Load saved checkbox states
    checkboxes.forEach((checkbox, index) => {
        const savedState = localStorage.getItem(`checkbox-${index}`);
        if (savedState === 'true') {
            checkbox.checked = true;
        }
        
        // Add event listener to save state
        checkbox.addEventListener('change', function() {
            localStorage.setItem(`checkbox-${index}`, this.checked);
            updateProgress();
        });
    });
    
    // Progress bar update function
    function updateProgress() {
        const totalCheckboxes = checkboxes.length;
        const checkedCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked').length;
        const percentage = Math.round((checkedCheckboxes / totalCheckboxes) * 100);
        
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressFill.style.width = percentage + '%';
        progressText.textContent = percentage + '% Complete';
        
        // Save progress to localStorage
        localStorage.setItem('overallProgress', percentage);
    }
    
    // Initialize progress bar
    updateProgress();
    
    // Reset button functionality (optional - you can add a reset button to HTML if needed)
    window.resetProgress = function() {
        if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
            localStorage.clear();
            checkboxes.forEach(checkbox => checkbox.checked = false);
            updateProgress();
            // Reset to overview tab
            document.querySelector('[data-tab="overview"]').click();
        }
    };
    
    // Export progress as JSON (optional feature)
    window.exportProgress = function() {
        const progress = {
            date: new Date().toISOString(),
            percentage: localStorage.getItem('overallProgress') || '0',
            checkboxStates: {}
        };
        
        checkboxes.forEach((checkbox, index) => {
            progress.checkboxStates[`checkbox-${index}`] = checkbox.checked;
        });
        
        const dataStr = JSON.stringify(progress, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'az305-progress.json';
        link.click();
    };
    
    // Print study guide
    window.printStudyGuide = function() {
        window.print();
    };
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + 1-5 for quick tab switching
    if (e.altKey && e.key >= '1' && e.key <= '5') {
        e.preventDefault();
        const tabs = ['overview', 'identity', 'storage', 'compute', 'infrastructure'];
        const tabIndex = parseInt(e.key) - 1;
        if (tabs[tabIndex]) {
            document.querySelector(`[data-tab="${tabs[tabIndex]}"]`).click();
        }
    }
});

// Add study statistics
function getStudyStats() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const stats = {
        identity: { total: 0, completed: 0 },
        storage: { total: 0, completed: 0 },
        compute: { total: 0, completed: 0 },
        infrastructure: { total: 0, completed: 0 }
    };
    
    checkboxes.forEach(checkbox => {
        const topic = checkbox.getAttribute('data-topic');
        if (stats[topic]) {
            stats[topic].total++;
            if (checkbox.checked) {
                stats[topic].completed++;
            }
        }
    });
    
    return stats;
}

// Console helper for users
console.log('%cAZ-305 Study Guide Helper', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('Available commands:');
console.log('  resetProgress() - Reset all progress');
console.log('  exportProgress() - Export progress as JSON');
console.log('  printStudyGuide() - Print the study guide');
console.log('  getStudyStats() - View progress by topic');
console.log('Keyboard shortcuts:');
console.log('  Alt + 1-5: Quick tab switching');
