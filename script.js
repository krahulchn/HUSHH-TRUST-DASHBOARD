// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    try {
        animateProgressOnLoad();
    } catch (error) {
        console.warn('Progress animation error:', error);
    }
    
    try {
        setupPermissionToggleListeners();
    } catch (error) {
        console.warn('Permission toggle error:', error);
    }
    
    try {
        setupCardHoverEffects();
    } catch (error) {
        console.warn('Card hover error:', error);
    }
    
    try {
        setupIndicatorAnimations();
    } catch (error) {
        console.warn('Indicator animation error:', error);
    }
    
    try {
        setupServiceRowClickHandling();
    } catch (error) {
        console.warn('Service row click error:', error);
    }
    
    try {
        setupNotificationCenter();
    } catch (error) {
        console.warn('Notification setup error:', error);
    }
});

// =============================
// Sidebar Navigation System
// =============================
(function setupSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const closeSidebar = document.getElementById('closeSidebar');
    const navItems = document.querySelectorAll('.nav-item');
    
    // Toggle sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar
    if (closeSidebar) {
        closeSidebar.addEventListener('click', function() {
            sidebar.classList.remove('active');
        });
    }
    
    // Close sidebar when overlay clicked
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
        });
    }
    
    // Handle navigation item clicks
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active to clicked item
            this.classList.add('active');
            
            const section = this.getAttribute('data-section');
            const label = this.querySelector('.nav-label').textContent;
            
            showToast(`Navigating to ${label}`, `Loading ${label.toLowerCase()} section...`, 'info', 2500);
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }
        });
    });
    
    // Set dashboard as active on page load
    const dashboardItem = document.querySelector('[data-section="dashboard"]');
    if (dashboardItem) {
        dashboardItem.classList.add('active');
    }
})();

// =============================
// Theme Toggle System
// =============================
(function setupThemeToggle() {
    const themeBtn = document.getElementById('themeToggle');
    const html = document.documentElement;
    const body = document.body;
    
    // Check for saved theme preference or default to dark theme
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    
    function applyTheme(theme) {
        if (theme === 'light') {
            body.classList.add('light-theme');
            themeBtn.textContent = '☀️';
            themeBtn.title = 'Switch to Dark Theme';
            localStorage.setItem('dashboard-theme', 'light');
        } else {
            body.classList.remove('light-theme');
            themeBtn.textContent = '🌙';
            themeBtn.title = 'Switch to Light Theme';
            localStorage.setItem('dashboard-theme', 'dark');
        }
    }
    
    // Apply saved theme on page load
    applyTheme(savedTheme);
    
    // Toggle theme on button click
    if (themeBtn) {
        themeBtn.addEventListener('click', function() {
            const currentTheme = body.classList.contains('light-theme') ? 'light' : 'dark';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(newTheme);
            showToast(`${newTheme.charAt(0).toUpperCase() + newTheme.slice(1)} Theme`, `Switched to ${newTheme} mode`, 'info', 2500);
        });
    }
})();

// =============================
// Toast Notifications System
// =============================
function showToast(title, message='', type='info', duration=4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-content">
            <p class="toast-title">${title}</p>
            ${message ? `<p class="toast-message">${message}</p>` : ''}
        </div>
        <button class="toast-close">✕</button>
        <div class="toast-progress"></div>
    `;
    
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    });
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// =============================
// Animate the main circular progress on page load
// =============================
function animateProgressOnLoad() {
    const progressCircle = document.querySelector('.progress-circle-fill');
    const targetScore = 78;
    const maxDashOffset = 339.29;
    const dashOffset = maxDashOffset - (targetScore / 100) * maxDashOffset;
    
    // Start with full circle
    progressCircle.style.strokeDashoffset = maxDashOffset;
    
    // Animate to target
    setTimeout(() => {
        progressCircle.style.transition = 'stroke-dashoffset 1.5s ease-out';
        progressCircle.style.strokeDashoffset = dashOffset;
    }, 300);
}

// Update trust score when permissions are toggled
function setupPermissionToggleListeners() {
    const toggles = document.querySelectorAll('.switch input[type="checkbox"]');
    const scoreNumber = document.querySelector('.score-number');
    const scoreBar = document.querySelector('.progress-circle-fill');
    
    const permissionNames = {
        0: 'Profile Data',
        1: 'Analytics',
        2: 'Location',
        3: 'Notifications'
    };
    
    toggles.forEach((toggle, index) => {
        toggle.addEventListener('change', function() {
            const permName = permissionNames[index] || 'Permission';
            const status = this.checked ? 'enabled' : 'disabled';
            showToast(`${permName} ${status}`, `Trust Score updated`, this.checked ? 'success' : 'warning');
            updateTrustScore();
            checkboxAnimation(this);
        });
    });
    
    function updateTrustScore() {
        const totalToggles = toggles.length;
        const enabledToggles = Array.from(toggles).filter(t => t.checked).length;
        const newScore = Math.round((enabledToggles / totalToggles) * 78) + 45;
        
        // Animate score change
        animateValue(parseInt(scoreNumber.textContent), newScore, 300, (val) => {
            scoreNumber.textContent = val;
        });
        
        // Update progress bar
        const maxDashOffset = 339.29;
        const dashOffset = maxDashOffset - (newScore / 100) * maxDashOffset;
        scoreBar.style.transition = 'stroke-dashoffset 0.6s ease-out';
        scoreBar.style.strokeDashoffset = dashOffset;
    }
}

// Animate checkbox toggle
function checkboxAnimation(checkbox) {
    const label = checkbox.closest('.switch');
    label.style.transform = 'scale(1.1)';
    setTimeout(() => {
        label.style.transform = 'scale(1)';
    }, 150);
}

// Smooth number animation
function animateValue(start, end, duration, callback) {
    const startTime = Date.now();
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const value = Math.round(start + (end - start) * progress);
        callback(value);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    update();
}

// Add hover effects to cards
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card.glass-effect');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = '0 8px 32px rgba(56, 189, 248, 0.2)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
}

// Animate indicators on scroll
function setupIndicatorAnimations() {
    const indicators = document.querySelectorAll('.indicator-fill');
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target;
                const width = fill.style.width;
                fill.style.width = '0%';
                fill.style.transition = 'width 1s ease-out';
                
                setTimeout(() => {
                    fill.style.width = width;
                }, 100);
                
                observer.unobserve(fill);
            }
        });
    }, observerOptions);
    
    indicators.forEach(indicator => {
        observer.observe(indicator);
    });
}

// Add click interactions to service rows
document.addEventListener('DOMContentLoaded', function() {
    const serviceRows = document.querySelectorAll('.service-row');
    
    serviceRows.forEach(row => {
        row.style.cursor = 'pointer';
        
        row.addEventListener('click', function(e) {
            if (!e.target.closest('input')) {
                this.classList.toggle('service-active');
                const serviceName = this.querySelector('strong')?.textContent || 'Service';
                const isActive = this.classList.contains('service-active');
                showToast(`${serviceName} ${isActive ? 'Connected' : 'Disconnected'}`, isActive ? 'Service activated' : 'Service deactivated', isActive ? 'success' : 'warning', 2500);
                createPulseEffect(this);
            }
        });
        
        row.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(56, 189, 248, 0.1)';
            this.style.transition = 'all 0.3s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            if (!this.classList.contains('service-active')) {
                this.style.background = 'rgba(255, 255, 255, 0.03)';
            }
        });
    });
});

// Create pulse effect on click
function createPulseEffect(element) {
    const pulse = document.createElement('div');
    pulse.style.position = 'absolute';
    pulse.style.borderRadius = '50%';
    pulse.style.background = 'rgba(56, 189, 248, 0.6)';
    pulse.style.width = '20px';
    pulse.style.height = '20px';
    pulse.style.pointerEvents = 'none';
    pulse.style.animation = 'pulse-animation 0.6s ease-out';
    
    const rect = element.getBoundingClientRect();
    pulse.style.left = '50%';
    pulse.style.top = '50%';
    pulse.style.transform = 'translate(-50%, -50%)';
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(pulse);
    
    setTimeout(() => pulse.remove(), 600);
}

// Add CSS animation for pulse
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse-animation {
        0% {
            width: 20px;
            height: 20px;
            opacity: 1;
        }
        100% {
            width: 100px;
            height: 100px;
            opacity: 0;
        }
    }
    
    .service-active {
        background: rgba(56, 189, 248, 0.15) !important;
        border-left: 3px solid #38bdf8 !important;
    }
    
    .switch {
        transition: transform 0.15s ease;
    }
`;
document.head.appendChild(style);

// =============================
// Notification System Logic
// =============================
let currentNotificationFilter = 'all';
let notificationsData = [];

function setupNotificationCenter() {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationModal = document.getElementById('notificationModal');
    const notificationOverlay = document.getElementById('notificationOverlay');
    const closeNotificationBtn = document.getElementById('closeNotification');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    if (!notificationBtn || !notificationModal) return;
    
    // Open notification modal
    notificationBtn.addEventListener('click', function() {
        notificationModal.classList.add('active');
        if (notificationOverlay) notificationOverlay.classList.add('active');
        loadNotifications();
        const unreadCount = notificationsData.filter(n => !n.read).length;
        showToast('💬 Notifications', `You have ${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`, 'info', 2500);
    });
    
    // Close notification modal
    closeNotificationBtn.addEventListener('click', closeNotificationModal);
    if (notificationOverlay) {
        notificationOverlay.addEventListener('click', closeNotificationModal);
    }
    
    function closeNotificationModal() {
        notificationModal.classList.remove('active');
        if (notificationOverlay) notificationOverlay.classList.remove('active');
    }
    
    // Mark all as read
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllNotificationsAsRead);
    }
    
    // Clear all notifications
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllNotifications);
    }
    
    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentNotificationFilter = this.getAttribute('data-filter');
            displayNotifications(notificationsData);
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && notificationModal.classList.contains('active')) {
            closeNotificationModal();
        }
    });
}

function loadNotifications() {
    // Sample notifications data
    notificationsData = [
        {
            id: 1,
            icon: '✅',
            title: 'Permission Granted',
            message: 'Profile Data permission enabled for Analytics Service',
            category: 'success',
            time: '2 minutes ago',
            read: false
        },
        {
            id: 2,
            icon: '⚠️',
            title: 'Trust Score Changed',
            message: 'Your trust score increased from 75 to 78 points',
            category: 'warning',
            time: '15 minutes ago',
            read: false
        },
        {
            id: 3,
            icon: 'ℹ️',
            title: 'Service Update',
            message: 'Google Analytics is now available for integration',
            category: 'info',
            time: '1 hour ago',
            read: true
        },
        {
            id: 4,
            icon: '🔴',
            title: 'Security Alert',
            message: 'Unusual login attempt detected. Please review account activity',
            category: 'error',
            time: '3 hours ago',
            read: true
        },
        {
            id: 5,
            icon: '✅',
            title: 'Sync Complete',
            message: 'All services synchronized successfully',
            category: 'success',
            time: '1 day ago',
            read: true
        }
    ];
    
    displayNotifications(notificationsData);
    updateNotificationBadge();
}

function displayNotifications(notifications) {
    const notificationList = document.getElementById('notificationList');
    
    let filteredNotifications = notifications;
    if (currentNotificationFilter !== 'all') {
        filteredNotifications = notifications.filter(n => n.category === currentNotificationFilter);
    }
    
    if (filteredNotifications.length === 0) {
        notificationList.innerHTML = '<p class="empty-state">No notifications</p>';
        return;
    }
    
    notificationList.innerHTML = filteredNotifications.map(notification => `
        <div class="notification-item ${notification.read ? '' : 'unread'}">
            <div class="notification-item-icon">${notification.icon}</div>
            <div class="notification-item-content">
                <p class="notification-item-title">${notification.title}</p>
                <p class="notification-item-message">${notification.message}</p>
                <span class="notification-item-category ${notification.category}">${notification.category}</span>
                <p class="notification-item-time">${notification.time}</p>
            </div>
            <div class="notification-item-actions">
                ${!notification.read ? `<button class="notification-item-btn" onclick="markNotificationRead(${notification.id})">Mark Read</button>` : ''}
                <button class="notification-item-btn" onclick="deleteNotification(${notification.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function markNotificationRead(notificationId) {
    const notification = notificationsData.find(n => n.id === notificationId);
    if (notification) {
        notification.read = true;
        showToast('Marked as Read', notification.title, 'success', 2500);
        displayNotifications(notificationsData);
        updateNotificationBadge();
    }
}

function deleteNotification(notificationId) {
    const notification = notificationsData.find(n => n.id === notificationId);
    notificationsData = notificationsData.filter(n => n.id !== notificationId);
    showToast('Notification Deleted', notification ? notification.title : '', 'info', 2500);
    displayNotifications(notificationsData);
    updateNotificationBadge();
}

function markAllNotificationsAsRead() {
    notificationsData.forEach(n => n.read = true);
    showToast('All Marked as Read', `${notificationsData.length} notifications`, 'success', 2500);
    displayNotifications(notificationsData);
    updateNotificationBadge();
}

function clearAllNotifications() {
    if (confirm('Are you sure you want to clear all notifications?')) {
        const count = notificationsData.length;
        notificationsData = [];
        showToast('All Cleared', `${count} notifications removed`, 'info', 2500);
        displayNotifications(notificationsData);
        updateNotificationBadge();
    }
}

function updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    const unreadCount = notificationsData.filter(n => !n.read).length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

// =============================
// Interactive User Guide Logic
// =============================
(function setupUserGuide() {
    const guideBtn = document.getElementById('guideBtn');
    const guideModal = document.getElementById('guideModal');
    const closeGuide = document.getElementById('closeGuide');
    const prevBtn = document.getElementById('prevStep');
    const nextBtn = document.getElementById('nextStep');
    const stepDots = Array.from(document.querySelectorAll('.dot'));
    const currentStepLabel = document.getElementById('currentStep');
    const overlay = document.querySelector('.guide-overlay');
    
    if (!guideBtn || !guideModal || !prevBtn || !nextBtn) return;
    
    const steps = Array.from(document.querySelectorAll('.guide-step'));
    let currentStep = 0;

    function showStep(idx, animate=true) {
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === idx);
            if (animate && i === idx) {
                step.style.animation = 'fadeInUp 0.5s';
            } else {
                step.style.animation = '';
            }
        });
        stepDots.forEach((dot, i) => dot.classList.toggle('active', i === idx));
        prevBtn.disabled = idx === 0;
        nextBtn.disabled = idx === steps.length - 1;
        if (currentStepLabel) currentStepLabel.textContent = (idx + 1).toString();
    }

    function openGuide() {
        guideModal.classList.add('active');
        showStep(currentStep, false);
        showToast('Welcome to the Guide!', 'Step 1 of 5 - Dashboard Overview', 'info', 3000);
    }
    
    function closeGuideModal() {
        guideModal.classList.remove('active');
        currentStep = 0;
    }
    
    function nextStep() {
        if (currentStep < steps.length - 1) {
            currentStep++;
            showStep(currentStep);
        }
    }
    
    function prevStep() {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    }
    
    // Event listeners
    if (guideBtn) guideBtn.addEventListener('click', openGuide);
    if (closeGuide) closeGuide.addEventListener('click', closeGuideModal);
    if (prevBtn) prevBtn.addEventListener('click', prevStep);
    if (nextBtn) nextBtn.addEventListener('click', nextStep);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (!guideModal.classList.contains('active')) return;
        
        if (e.key === 'ArrowRight') nextStep();
        if (e.key === 'ArrowLeft') prevStep();
        if (e.key === 'Escape') closeGuideModal();
    });
    
    // Close on overlay click
    if (overlay) {
        overlay.addEventListener('click', closeGuideModal);
    }
})();

// =============================
// Section Navigation System
// =============================
(function setupSectionNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = {
        'dashboard': document.getElementById('dashboard-section'),
        'analytics': document.getElementById('analytics-section'),
        'audit-logs': document.getElementById('audit-logs-section')
    };
    
    function showSection(sectionId) {
        // Hide all sections with fade out
        Object.values(sections).forEach(section => {
            if (section) {
                section.classList.add('hidden');
            }
        });
        
        // Show selected section with fade in
        if (sections[sectionId]) {
            sections[sectionId].classList.remove('hidden');
        }
    }
    
    // Update sidebar click handlers to switch sections
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const sectionId = this.getAttribute('data-section');
            
            // Only handle dashboard, analytics, and audit-logs
            if (sectionId === 'dashboard' || sectionId === 'analytics' || sectionId === 'audit-logs') {
                e.preventDefault();
                showSection(sectionId);
            }
        });
    });
    
    // Show dashboard by default
    showSection('dashboard');
})();