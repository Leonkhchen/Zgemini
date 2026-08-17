/**
 * AuraFocus Theme Controller Module
 */
export function initTheme() {
  const themeBtn = document.getElementById('theme-btn');
  const themeDropdown = document.getElementById('theme-dropdown');
  const themeOptions = document.querySelectorAll('.theme-option');
  
  // Toggle theme dropdown
  themeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    themeDropdown.classList.toggle('hidden');
  });

  // Close dropdown on click outside
  document.addEventListener('click', (e) => {
    if (!themeSelectorContains(e.target)) {
      themeDropdown.classList.add('hidden');
    }
  });

  function themeSelectorContains(target) {
    const container = document.querySelector('.theme-selector-container');
    return container && container.contains(target);
  }

  // Handle theme option selection
  themeOptions.forEach(option => {
    option.addEventListener('click', () => {
      const selectedTheme = option.getAttribute('data-theme');
      setTheme(selectedTheme);
      
      // Update UI active state in options
      themeOptions.forEach(opt => opt.classList.remove('active'));
      option.classList.add('active');
      
      // Hide dropdown
      themeDropdown.classList.add('hidden');
    });
  });

  // Set the theme class on body and save to localStorage
  function setTheme(themeName) {
    // Remove all theme classes first
    document.body.className = '';
    
    // Add selected theme class
    const themeClass = `theme-${themeName}`;
    document.body.classList.add(themeClass);
    
    // Save to localStorage
    localStorage.setItem('aurafocus-theme', themeName);
  }

  // Load initial theme from localStorage or default to 'forest'
  const savedTheme = localStorage.getItem('aurafocus-theme') || 'forest';
  setTheme(savedTheme);

  // Sync active class in dropdown list
  themeOptions.forEach(option => {
    if (option.getAttribute('data-theme') === savedTheme) {
      option.classList.add('active');
    } else {
      option.classList.remove('active');
    }
  });
}
