/**
 * Script principal de l'application Punk Eco
 * Fonctionnalités du tableau de bord
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Punk Eco - Tableau de bord chargé');
    
    // Initialisation des composants
    initMobileMenu();
    initAlerts();
    initTooltips();
    initThemeToggle();
    initSmoothScroll();
    initScrollProgress();
    initScrollToTop();
    initMatrixEffect();
});

/**
 * Initialise le menu mobile
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('#mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true' || false;
            this.setAttribute('aria-expanded', !isExpanded);
            
            if (mainNav) {
                mainNav.setAttribute('data-visible', !isExpanded);
                document.body.style.overflow = !isExpanded ? 'hidden' : '';
            }
            
            // Empêcher le défilement du fond lorsque le menu est ouvert
            if (!isExpanded) {
                document.body.classList.add('menu-open');
            } else {
                document.body.classList.remove('menu-open');
            }
        });
    }
    
    // Fermer le menu lors du clic sur un lien
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 992) {
                menuToggle.setAttribute('aria-expanded', 'false');
                if (mainNav) {
                    mainNav.setAttribute('data-visible', 'false');
                }
                document.body.classList.remove('menu-open');
                document.body.style.overflow = '';
            }
        });
    });
    
    // Fermer le menu lors du redimensionnement de la fenêtre
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 992) {
                if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
                if (mainNav) mainNav.setAttribute('data-visible', 'false');
                document.body.classList.remove('menu-open');
                document.body.style.overflow = '';
            }
        }, 250);
    });
}

/**
 * Initialise les alertes avec bouton de fermeture
 */
function initAlerts() {
    // Fermer les alertes
    document.addEventListener('click', function(e) {
        if (e.target.closest('.alert-close')) {
            const alert = e.target.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 300);
            }
        }
    });
    
    // Supprimer automatiquement les alertes après 5 secondes
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
}

/**
 * Initialise les infobulles
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', showTooltip);
        tooltip.addEventListener('mouseleave', hideTooltip);
    });
    
    function showTooltip(e) {
        const tooltipText = this.getAttribute('data-tooltip');
        const tooltipElement = document.createElement('div');
        tooltipElement.className = 'tooltip';
        tooltipElement.textContent = tooltipText;
        
        document.body.appendChild(tooltipElement);
        
        const rect = this.getBoundingClientRect();
        tooltipElement.style.top = `${rect.top - tooltipElement.offsetHeight - 10}px`;
        tooltipElement.style.left = `${rect.left + (this.offsetWidth / 2) - (tooltipElement.offsetWidth / 2)}px`;
        
        this.tooltipElement = tooltipElement;
    }
    
    function hideTooltip() {
        if (this.tooltipElement) {
            this.tooltipElement.remove();
            this.tooltipElement = null;
        }
    }
}

/**
 * Initialise le basculement de thème (clair/sombre)
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Vérifier le thème sauvegardé ou utiliser les préférences du système
    const currentTheme = localStorage.getItem('theme') || (prefersDarkScheme.matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    if (themeToggle) {
        // Mettre à jour l'icône du bouton
        updateThemeIcon(currentTheme);
        
        // Basculer le thème au clic
        themeToggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-theme');
            const newTheme = theme === 'dark' ? 'light' : 'dark';
            
            // Mettre à jour le thème
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Mettre à jour l'icône
            updateThemeIcon(newTheme);
            
            // Déclencher un événement personnalisé pour les autres composants
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
        });
    }
    
    // Mettre à jour le thème si les préférences système changent
    const handleColorSchemeChange = (e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            updateThemeIcon(newTheme);
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
        }
    };
    
    // Ajouter le listener pour les changements de préférence système
    if (prefersDarkScheme.addEventListener) {
        prefersDarkScheme.addEventListener('change', handleColorSchemeChange);
    } else {
        // Pour la compatibilité avec les anciens navigateurs
        prefersDarkScheme.addListener(handleColorSchemeChange);
    }
    
    // Fonction pour mettre à jour l'icône du thème
    function updateThemeIcon(theme) {
        const sunIcon = themeToggle.querySelector('.sun-icon');
        const moonIcon = themeToggle.querySelector('.moon-icon');
        
        if (theme === 'dark') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
            themeToggle.setAttribute('aria-label', 'Passer en mode clair');
            themeToggle.setAttribute('title', 'Mode sombre');
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
            themeToggle.setAttribute('aria-label', 'Passer en mode sombre');
            themeToggle.setAttribute('title', 'Mode clair');
        }
    }
    
    // Initialiser la barre de progression de défilement
    initScrollProgress();
}

/**
 * Initialise la barre de progression de défilement
 */
function initScrollProgress() {
    const scrollProgress = document.querySelector('.scroll-progress');
    const progressBar = document.querySelector('.scroll-progress-bar');
    
    if (!scrollProgress || !progressBar) return;
    
    let isScrolling;
    
    window.addEventListener('scroll', () => {
        // Annuler le setTimeout en cours
        window.clearTimeout(isScrolling);
        
        // Masquer la barre de progression après un délai d'inactivité
        scrollProgress.style.opacity = '1';
        
        // Calculer la progression du défilement
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = window.scrollY;
        const progress = (scrolled / documentHeight) * 100;
        
        // Mettre à jour la largeur de la barre de progression
        progressBar.style.width = `${progress}%`;
        scrollProgress.setAttribute('aria-valuenow', Math.round(progress));
        
        // Masquer la barre après l'arrêt du défilement
        isScrolling = setTimeout(() => {
            scrollProgress.style.opacity = '0';
        }, 1000);
    }, { passive: true });
}

/**
 * Initialise le défilement fluide pour les ancres
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Compenser la hauteur du header
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Effet de fond matriciel (comme dans Matrix)
 */
function initMatrixEffect() {
    const canvas = document.createElement('canvas');
    const container = document.getElementById('matrix');
    if (!container) return;
    
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.15';
    canvas.style.pointerEvents = 'none';
    
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
    const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const nums = '0123456789';
    const alphabet = katakana + latin + nums;
    
    const fontSize = 16;
    const columns = canvas.width / fontSize;
    
    const rainDrops = Array(Math.floor(columns)).fill(1);
    
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#0f0';
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < rainDrops.length; i++) {
            const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
            
            if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                rainDrops[i] = 0;
            }
            rainDrops[i]++;
        }
    }
    
    // Redimensionner le canvas lorsque la fenêtre est redimensionnée
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    
    // Démarrer l'animation
    setInterval(draw, 30);
}

/**
 * Effectue une requête AJAX
 * @param {string} url - URL de l'API
 * @param {string} method - Méthode HTTP (GET, POST, etc.)
 * @param {Object} data - Données à envoyer (optionnel)
 * @returns {Promise} - Promesse avec la réponse JSON
 */
function fetchData(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP! statut: ${response.status}`);
            }
            return response.json();
        });
}

/**
 * Initialise le bouton de retour en haut de page
 */
function initScrollToTop() {
    const scrollToTopBtn = document.querySelector('.scroll-to-top');
    
    if (!scrollToTopBtn) return;
    
    // Gérer le clic sur le bouton
    scrollToTopBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Afficher/masquer le bouton lors du défilement
    function handleScroll() {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.classList.add('show');
        } else {
            scrollToTopBtn.classList.remove('show');
        }
    }
    
    // Écouter l'événement de défilement
    window.addEventListener('scroll', handleScroll);
    
    // Vérifier la position initiale
    handleScroll();
}

// Exposer les fonctions globales si nécessaire
window.PunkEco = {
    fetchData
};
