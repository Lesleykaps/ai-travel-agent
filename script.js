/**
 * Fly Buddy - Redesigned JavaScript
 * Refactored for better performance, maintainability, and organization
 * while preserving exact functionality and visual design
 */

'use strict';

// ========================================
// CONSTANTS AND CONFIGURATION
// ========================================

const CONFIG = {
  API: {
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
      ? 'http://localhost:5001' 
      : window.location.origin,
    ENDPOINTS: {
      CHAT: '/api/chat'
    },
    TIMEOUT: 30000
  },
  UI: {
    TYPING_DELAY: 50,
    SCROLL_BEHAVIOR: 'smooth',
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 300,
    MAX_MESSAGE_LENGTH: 2000,
    AUTO_SAVE_INTERVAL: 5000
  },
  STORAGE: {
    KEYS: {
      THEME: 'travel-agent-theme',
      SETTINGS: 'travel-agent-settings',
      CONVERSATIONS: 'travel-agent-conversations',
      CURRENT_CONVERSATION: 'travel-agent-current-conversation'
    }
  },
  DEFAULTS: {
    THEME: 'light',
    SETTINGS: {
      notifications: true,
      soundEnabled: true,
      autoSave: true,
      language: 'en'
    }
  }
};

const SUGGESTED_PROMPTS = [
 
  "Find flights from New York to London on 7 November",
 
];

const QUICK_ACTIONS = [
  { icon: 'fas fa-plane', text: 'Find Flights', action: 'findFlights' },
  { icon: 'fas fa-hotel', text: 'Find Hotels', action: 'findHotels' },
  { icon: 'fas fa-map-marked-alt', text: 'Plan Itinerary', action: 'planItinerary' },
  { icon: 'fas fa-globe-americas', text: 'Explore Destinations', action: 'exploreDestinations' }
];

// ========================================
// UTILITY FUNCTIONS
// ========================================

const Utils = {
  /**
   * Debounce function to limit function calls
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Throttle function to limit function calls
   */
  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * Generate unique ID
   */
  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  },

  /**
   * Format timestamp
   */
  formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 168) {
      return `${Math.floor(diffInHours / 24)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  },

  /**
   * Sanitize HTML content
   */
  sanitizeHtml(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  },

  /**
   * Copy text to clipboard
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textArea);
      return success;
    }
  },

  /**
   * Play notification sound
   */
  playNotificationSound() {
    if (StorageManager.getSettings().soundEnabled) {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTuR2O/Eeyw');
      audio.volume = 0.1;
      audio.play().catch(() => {}); // Ignore errors
    }
  }
};

// ========================================
// STORAGE MANAGER
// ========================================

const StorageManager = {
  /**
   * Get theme from localStorage
   */
  getTheme() {
    return localStorage.getItem(CONFIG.STORAGE.KEYS.THEME) || CONFIG.DEFAULTS.THEME;
  },

  /**
   * Set theme in localStorage
   */
  setTheme(theme) {
    localStorage.setItem(CONFIG.STORAGE.KEYS.THEME, theme);
  },

  /**
   * Get settings from localStorage
   */
  getSettings() {
    try {
      const settings = localStorage.getItem(CONFIG.STORAGE.KEYS.SETTINGS);
      return settings ? { ...CONFIG.DEFAULTS.SETTINGS, ...JSON.parse(settings) } : CONFIG.DEFAULTS.SETTINGS;
    } catch (error) {
      console.warn('Failed to parse settings from localStorage:', error);
      return CONFIG.DEFAULTS.SETTINGS;
    }
  },

  /**
   * Set settings in localStorage
   */
  setSettings(settings) {
    try {
      localStorage.setItem(CONFIG.STORAGE.KEYS.SETTINGS, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save settings to localStorage:', error);
    }
  },

  /**
   * Get conversations from localStorage
   */
  getConversations() {
    try {
      const conversations = localStorage.getItem(CONFIG.STORAGE.KEYS.CONVERSATIONS);
      return conversations ? JSON.parse(conversations) : [];
    } catch (error) {
      console.warn('Failed to parse conversations from localStorage:', error);
      return [];
    }
  },

  /**
   * Set conversations in localStorage
   */
  setConversations(conversations) {
    try {
      localStorage.setItem(CONFIG.STORAGE.KEYS.CONVERSATIONS, JSON.stringify(conversations));
    } catch (error) {
      console.error('Failed to save conversations to localStorage:', error);
    }
  },

  /**
   * Get current conversation from localStorage
   */
  getCurrentConversation() {
    try {
      const conversation = localStorage.getItem(CONFIG.STORAGE.KEYS.CURRENT_CONVERSATION);
      return conversation ? JSON.parse(conversation) : null;
    } catch (error) {
      console.warn('Failed to parse current conversation from localStorage:', error);
      return null;
    }
  },

  /**
   * Set current conversation in localStorage
   */
  setCurrentConversation(conversation) {
    try {
      localStorage.setItem(CONFIG.STORAGE.KEYS.CURRENT_CONVERSATION, JSON.stringify(conversation));
    } catch (error) {
      console.error('Failed to save current conversation to localStorage:', error);
    }
  }
};

// ========================================
// EVENT EMITTER
// ========================================

class EventEmitter {
  constructor() {
    this.events = {};
  }

  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }

  off(event, callback) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(cb => cb !== callback);
  }

  emit(event, data) {
    if (!this.events[event]) return;
    this.events[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for ${event}:`, error);
      }
    });
  }
}

// ========================================
// TOAST NOTIFICATION SYSTEM
// ========================================

class ToastManager {
  constructor() {
    this.container = this.createContainer();
    this.toasts = new Map();
  }

  createContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'false');
      document.body.appendChild(container);
    }
    return container;
  }

  show(message, type = 'info', duration = 5000) {
    const id = Utils.generateId();
    const toast = this.createToast(id, message, type);
    
    this.container.appendChild(toast);
    this.toasts.set(id, toast);

    // Trigger animation
    requestAnimationFrame(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateX(0)';
    });

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => this.remove(id), duration);
    }

    return id;
  }

  createToast(id, message, type) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease-out';

    const iconMap = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle',
      info: 'fas fa-info-circle'
    };

    toast.innerHTML = `
      <div class="toast-icon">
        <i class="${iconMap[type] || iconMap.info}"></i>
      </div>
      <div class="toast-message">${Utils.sanitizeHtml(message)}</div>
      <button class="toast-close" aria-label="Close notification">
        <i class="fas fa-times"></i>
      </button>
    `;

    // Add close event listener
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => this.remove(id));

    return toast;
  }

  remove(id) {
    const toast = this.toasts.get(id);
    if (!toast) return;

    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';

    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
      this.toasts.delete(id);
    }, 300);
  }

  clear() {
    this.toasts.forEach((_, id) => this.remove(id));
  }
}

// ========================================
// MODAL MANAGER
// ========================================

class ModalManager {
  constructor() {
    this.activeModal = null;
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.activeModal) {
        this.close();
      }
    });

    // Close modal on backdrop click
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.close();
      }
    });
  }

  open(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.error(`Modal with id "${modalId}" not found`);
      return;
    }

    this.activeModal = modal;
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    // Focus management
    const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (firstFocusable) {
      firstFocusable.focus();
    }

    // Setup close button
    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.onclick = () => this.close();
    }
  }

  close() {
    if (!this.activeModal) return;

    this.activeModal.classList.remove('show');
    document.body.style.overflow = '';
    this.activeModal = null;
  }

  createModal(id, title, content, footer = '') {
    const modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h2>${Utils.sanitizeHtml(title)}</h2>
          <button class="modal-close" aria-label="Close modal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          ${content}
        </div>
        ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
      </div>
    `;

    document.body.appendChild(modal);
    return modal;
  }
}

// ========================================
// MAIN APPLICATION CLASS
// ========================================

class TravelAgentChat extends EventEmitter {
  constructor() {
    super();
    this.currentConversation = null;
    this.conversations = [];
    this.isTyping = false;
    this.autoSaveTimer = null;
    
    // Initialize managers
    this.toastManager = new ToastManager();
    this.modalManager = new ModalManager();
    
    // Cache DOM elements
    this.elements = {};
    
    // Initialize the application
    this.init();
  }

  /**
   * Initialize the application
   */
  async init() {
    try {
      this.cacheElements();
      this.loadTheme();
      this.loadSettings();
      this.loadConversations();
      this.setupEventListeners();
      this.setupAccessibility();
      this.startAutoSave();
      
      // Load current conversation or show welcome screen
      const currentConv = StorageManager.getCurrentConversation();
      if (currentConv && currentConv.messages.length > 0) {
        this.loadConversation(currentConv);
      } else {
        this.showWelcomeScreen();
      }

      this.emit('initialized');
      console.log('Travel Agent Chat initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Travel Agent Chat:', error);
      this.toastManager.show('Failed to initialize application', 'error');
    }
  }

  /**
   * Cache frequently used DOM elements
   */
  cacheElements() {
    const selectors = {
      // Sidebar elements
      sidebar: '.sidebar',
      sidebarToggle: '.sidebar-toggle',
      newChatBtn: '.new-chat-btn',
      quickActions: '.quick-actions',
      themeToggle: '.theme-toggle',
      settingsBtn: '.settings-btn',
      
      // Main content elements
      mainContent: '.main-content',
      chatContainer: '.chat-container',
      chatMessages: '.chat-messages',
      welcomeScreen: '.welcome-screen',
      typingIndicator: '.typing-indicator',
      
      // Input elements
      inputArea: '.input-area',
      messageInput: '.message-input',
      sendBtn: '.send-btn',
      charCount: '.char-count',
      
      // Header elements
      chatTitle: '.chat-title h1',
      statusIndicator: '.status-indicator',
      mobileMenuToggle: '.mobile-menu-toggle',
      
      // Other elements
      suggestedFollowups: '.suggested-followups',
      followupButtons: '.followup-buttons'
    };

    for (const [key, selector] of Object.entries(selectors)) {
      this.elements[key] = document.querySelector(selector);
      if (!this.elements[key]) {
        console.warn(`Element not found: ${selector}`);
      }
    }
  }

  /**
   * Setup all event listeners
   */
  setupEventListeners() {
    this.setupSidebarEvents();
    this.setupInputEvents();
    this.setupHeaderEvents();
    this.setupKeyboardEvents();
    this.setupWindowEvents();
  }

  /**
   * Setup sidebar event listeners
   */
  setupSidebarEvents() {
    // Sidebar toggle
    if (this.elements.sidebarToggle) {
      this.elements.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
    }

    // Mobile menu toggle
    if (this.elements.mobileMenuToggle) {
      this.elements.mobileMenuToggle.addEventListener('click', () => this.toggleMobileSidebar());
    }

    // New chat button
    if (this.elements.newChatBtn) {
      this.elements.newChatBtn.addEventListener('click', () => this.startNewChat());
    }

    // Quick actions
    if (this.elements.quickActions) {
      this.elements.quickActions.addEventListener('click', (e) => {
        const actionBtn = e.target.closest('.action-btn');
        if (actionBtn) {
          const action = actionBtn.dataset.action;
          this.handleQuickAction(action);
        }
      });
    }

    // Theme toggle
    if (this.elements.themeToggle) {
      this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    // Settings button
    if (this.elements.settingsBtn) {
      this.elements.settingsBtn.addEventListener('click', () => this.openSettings());
    }


  }

  /**
   * Setup input event listeners
   */
  setupInputEvents() {
    if (!this.elements.messageInput || !this.elements.sendBtn) return;

    // Input change handler with debouncing
    const debouncedInputChange = Utils.debounce(() => {
      this.handleInputChange();
    }, CONFIG.UI.DEBOUNCE_DELAY);

    this.elements.messageInput.addEventListener('input', debouncedInputChange);
    this.elements.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
    this.elements.sendBtn.addEventListener('click', () => this.sendMessage());

    // Auto-resize textarea
    this.elements.messageInput.addEventListener('input', () => this.autoResizeTextarea());
  }

  /**
   * Setup header event listeners
   */
  setupHeaderEvents() {
    // Export button
    const exportBtn = document.querySelector('.header-btn[data-action="export"]');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.openExportModal());
    }

    // Clear chat button
    const clearBtn = document.querySelector('.header-btn[data-action="clear"]');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearCurrentChat());
    }
  }

  /**
   * Setup keyboard event listeners
   */
  setupKeyboardEvents() {
    document.addEventListener('keydown', (e) => {
      // Sidebar toggle (Ctrl/Cmd + B)
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        this.toggleSidebar();
      }

      // New chat (Ctrl/Cmd + N)
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        this.startNewChat();
      }

      // Focus input (Ctrl/Cmd + /)
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        if (this.elements.messageInput) {
          this.elements.messageInput.focus();
        }
      }
    });
  }

  /**
   * Setup window event listeners
   */
  setupWindowEvents() {
    // Responsive sidebar handling
    const handleResize = Utils.throttle(() => {
      this.handleWindowResize();
    }, 250);

    window.addEventListener('resize', handleResize);

    // Handle beforeunload for auto-save
    window.addEventListener('beforeunload', () => {
      this.saveCurrentConversation();
    });
  }

  /**
   * Setup accessibility features
   */
  setupAccessibility() {
    // Announce sidebar state changes
    this.on('sidebarToggled', (isCollapsed) => {
      this.announceToScreenReader(
        isCollapsed ? 'Sidebar collapsed' : 'Sidebar expanded'
      );
    });

    // Setup skip link
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
      skipLink.addEventListener('click', (e) => {
        e.preventDefault();
        const mainContent = document.querySelector('#main-content');
        if (mainContent) {
          mainContent.focus();
          mainContent.scrollIntoView();
        }
      });
    }
  }

  /**
   * Handle input changes
   */
  handleInputChange() {
    if (!this.elements.messageInput) return;

    const value = this.elements.messageInput.value;
    const length = value.length;
    const maxLength = CONFIG.UI.MAX_MESSAGE_LENGTH;

    // Update character count with visual feedback
    if (this.elements.charCount) {
      this.elements.charCount.textContent = `${length}/${maxLength}`;
      
      // Remove existing classes
      this.elements.charCount.classList.remove('warning', 'error');
      
      // Add appropriate class based on character count
      if (length > maxLength) {
        this.elements.charCount.classList.add('error');
      } else if (length > maxLength * 0.8) {
        this.elements.charCount.classList.add('warning');
      }
    }

    // Update send button state
    if (this.elements.sendBtn) {
      this.elements.sendBtn.disabled = length === 0 || length > maxLength;
    }

    // Auto-save draft
    if (this.currentConversation) {
      this.currentConversation.draft = value;
      this.saveCurrentConversation();
    }
  }

  /**
   * Handle keydown events in input
   */
  handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Auto-resize textarea based on content
   */
  autoResizeTextarea() {
    if (!this.elements.messageInput) return;

    const textarea = this.elements.messageInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  }

  /**
   * Send message to the backend
   */
  async sendMessage() {
    if (!this.elements.messageInput || !this.elements.sendBtn) return;

    const message = this.elements.messageInput.value.trim();
    if (!message || this.isTyping) return;

    try {
      // Disable input and show loading state
      this.setInputState(false);
      
      // Add user message to chat
      this.addMessage('user', message);
      
      // Clear input
      this.elements.messageInput.value = '';
      this.handleInputChange();
      this.autoResizeTextarea();
      
      // Show typing indicator
      this.showTypingIndicator();
      
      // Send to backend
      const response = await this.sendToBackend(message);
      
      // Hide typing indicator
      this.hideTypingIndicator();
      
      // Add assistant response
      this.addMessage('assistant', response.message, response.data);
      
      // Show suggested follow-ups if provided
      if (response.suggestions && response.suggestions.length > 0) {
        this.showSuggestedFollowups(response.suggestions);
      }
      
      // Play notification sound
      Utils.playNotificationSound();
      
    } catch (error) {
      console.error('Error sending message:', error);
      this.hideTypingIndicator();
      
      // Show error message
      const errorMessage = this.generateFallbackResponse();
      this.addMessage('assistant', errorMessage);
      
      this.toastManager.show('Failed to send message. Please try again.', 'error');
    } finally {
      // Re-enable input
      this.setInputState(true);
    }
  }

  /**
   * Send message to backend API
   */
  async sendToBackend(message) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.API.TIMEOUT);

    try {
      const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.ENDPOINTS.CHAT}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: this.currentConversation?.id,
          timestamp: Date.now()
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  }

  /**
   * Generate fallback response when API fails
   */
  generateFallbackResponse() {
    const responses = [
      "I apologize, but I'm having trouble connecting to my travel database right now. Please try again in a moment.",
      "It seems there's a temporary issue with my travel planning service. Let me try to help you in a different way.",
      "I'm experiencing some technical difficulties at the moment. Please try your request again shortly.",
      "Sorry, I'm having trouble accessing my travel information right now. Please try again later."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  }

  /**
   * Add message to chat
   */
  addMessage(sender, content, data = null) {
    if (!this.elements.chatMessages) return;

    // Ensure we have a current conversation
    if (!this.currentConversation) {
      this.startNewChat();
    }

    const messageId = Utils.generateId();
    const timestamp = Date.now();

    const message = {
      id: messageId,
      sender,
      content,
      data,
      timestamp
    };

    // Add to conversation
    this.currentConversation.messages.push(message);
    this.currentConversation.updatedAt = timestamp;

    // Create message element
    const messageElement = this.createMessageElement(message);
    this.elements.chatMessages.appendChild(messageElement);

    // Hide welcome screen if visible
    this.hideWelcomeScreen();

    // Scroll to bottom
    this.scrollToBottom();

    // Save conversation
    this.saveCurrentConversation();

    // Update conversation title if this is the first user message
    if (sender === 'user' && this.currentConversation.messages.filter(m => m.sender === 'user').length === 1) {
      this.generateConversationTitle();
    }
  }

  /**
   * Create message element
   */
  createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.sender}`;
    messageDiv.dataset.messageId = message.id;

    const avatar = this.createMessageAvatar(message.sender);
    const content = this.createMessageContent(message);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    return messageDiv;
  }

  /**
   * Create message avatar
   */
  createMessageAvatar(sender) {
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (sender === 'user') {
      avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else {
      avatar.innerHTML = '<i class="fas fa-robot"></i>';
    }

    return avatar;
  }

  /**
   * Create message content
   */
  createMessageContent(message) {
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Add message text
    const textElement = document.createElement('div');
    textElement.className = 'message-text';
    textElement.textContent = message.content;
    bubble.appendChild(textElement);

    // Add structured data if present
    if (message.data) {
      const dataElement = this.createStructuredDataElement(message.data);
      if (dataElement) {
        bubble.appendChild(dataElement);
      }
    }

    contentDiv.appendChild(bubble);

    // Add metadata
    const metadata = this.createMessageMetadata(message);
    contentDiv.appendChild(metadata);

    // Add actions for assistant messages
    if (message.sender === 'assistant') {
      const actions = this.createMessageActions(message);
      contentDiv.appendChild(actions);
    }

    return contentDiv;
  }

  /**
   * Create structured data element (flights, hotels, etc.)
   */
  createStructuredDataElement(data) {
    if (!data || typeof data !== 'object') return null;

    const container = document.createElement('div');
    container.className = 'structured-data';

    if (data.flights && Array.isArray(data.flights)) {
      data.flights.forEach(flight => {
        const flightCard = this.createFlightCard(flight);
        container.appendChild(flightCard);
      });
    }

    if (data.hotels && Array.isArray(data.hotels)) {
      data.hotels.forEach(hotel => {
        const hotelCard = this.createHotelCard(hotel);
        container.appendChild(hotelCard);
      });
    }

    return container.children.length > 0 ? container : null;
  }

  /**
   * Create flight card element
   */
  createFlightCard(flight) {
    const card = document.createElement('div');
    card.className = 'flight-card';
    
    card.innerHTML = `
      <div class="flight-header">
        <div class="airline">
          <strong>${Utils.sanitizeHtml(flight.airline || 'Unknown Airline')}</strong>
          <span class="flight-number">${Utils.sanitizeHtml(flight.flightNumber || '')}</span>
        </div>
        <div class="price">
          <span class="amount">${Utils.sanitizeHtml(flight.price || 'N/A')}</span>
        </div>
      </div>
      <div class="flight-route">
        <div class="departure">
          <div class="airport">${Utils.sanitizeHtml(flight.departure?.airport || 'N/A')}</div>
          <div class="time">${Utils.sanitizeHtml(flight.departure?.time || 'N/A')}</div>
        </div>
        <div class="flight-duration">
          <i class="fas fa-plane"></i>
          <span>${Utils.sanitizeHtml(flight.duration || 'N/A')}</span>
        </div>
        <div class="arrival">
          <div class="airport">${Utils.sanitizeHtml(flight.arrival?.airport || 'N/A')}</div>
          <div class="time">${Utils.sanitizeHtml(flight.arrival?.time || 'N/A')}</div>
        </div>
      </div>
      ${flight.details ? `
        <div class="flight-details">
          <small>${Utils.sanitizeHtml(flight.details)}</small>
        </div>
      ` : ''}
    `;

    return card;
  }

  /**
   * Create hotel card element
   */
  createHotelCard(hotel) {
    const card = document.createElement('div');
    card.className = 'hotel-card';
    
    card.innerHTML = `
      <div class="hotel-header">
        <div class="hotel-name">
          <strong>${Utils.sanitizeHtml(hotel.name || 'Unknown Hotel')}</strong>
          ${hotel.rating ? `
            <div class="hotel-rating">
              ${'★'.repeat(Math.floor(hotel.rating))}${'☆'.repeat(5 - Math.floor(hotel.rating))}
              <span>(${hotel.rating})</span>
            </div>
          ` : ''}
        </div>
        <div class="hotel-price">
          <span class="amount">${Utils.sanitizeHtml(hotel.price || 'N/A')}</span>
          ${hotel.priceUnit ? `<span class="unit">/${hotel.priceUnit}</span>` : ''}
        </div>
      </div>
      <div class="hotel-details">
        ${hotel.location ? `<div class="location"><i class="fas fa-map-marker-alt"></i> ${Utils.sanitizeHtml(hotel.location)}</div>` : ''}
        ${hotel.amenities ? `<div class="amenities"><i class="fas fa-concierge-bell"></i> ${Utils.sanitizeHtml(hotel.amenities)}</div>` : ''}
      </div>
    `;

    return card;
  }

  /**
   * Create message metadata
   */
  createMessageMetadata(message) {
    const metadata = document.createElement('div');
    metadata.className = 'message-metadata';
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = Utils.formatTime(message.timestamp);
    
    metadata.appendChild(time);
    return metadata;
  }

  /**
   * Create message actions
   */
  createMessageActions(message) {
    const actions = document.createElement('div');
    actions.className = 'message-actions';

    // Copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'message-action-btn';
    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
    copyBtn.title = 'Copy message';
    copyBtn.addEventListener('click', () => this.copyMessage(message));

    // Like button
    const likeBtn = document.createElement('button');
    likeBtn.className = 'message-action-btn';
    likeBtn.innerHTML = '<i class="far fa-thumbs-up"></i>';
    likeBtn.title = 'Like message';
    likeBtn.addEventListener('click', () => this.likeMessage(message));

    actions.appendChild(copyBtn);
    actions.appendChild(likeBtn);

    return actions;
  }

  /**
   * Show typing indicator
   */
  showTypingIndicator() {
    if (!this.elements.typingIndicator) return;

    this.isTyping = true;
    this.elements.typingIndicator.classList.add('show');
    this.scrollToBottom();
  }

  /**
   * Hide typing indicator
   */
  hideTypingIndicator() {
    if (!this.elements.typingIndicator) return;

    this.isTyping = false;
    this.elements.typingIndicator.classList.remove('show');
  }

  /**
   * Scroll chat to bottom
   */
  scrollToBottom() {
    if (!this.elements.chatContainer) return;

    this.elements.chatContainer.scrollTo({
      top: this.elements.chatContainer.scrollHeight,
      behavior: CONFIG.UI.SCROLL_BEHAVIOR
    });
  }

  /**
   * Show welcome screen
   */
  showWelcomeScreen() {
    if (this.elements.welcomeScreen) {
      this.elements.welcomeScreen.style.display = 'flex';
    }
    
    if (this.elements.chatMessages) {
      this.elements.chatMessages.style.display = 'none';
    }

    this.setupSuggestedPrompts();
  }

  /**
   * Hide welcome screen
   */
  hideWelcomeScreen() {
    if (this.elements.welcomeScreen) {
      this.elements.welcomeScreen.style.display = 'none';
    }
    
    if (this.elements.chatMessages) {
      this.elements.chatMessages.style.display = 'flex';
    }
  }

  /**
   * Setup suggested prompts on welcome screen
   */
  setupSuggestedPrompts() {
    const promptButtons = document.querySelectorAll('.prompt-btn');
    promptButtons.forEach((btn, index) => {
      if (SUGGESTED_PROMPTS[index]) {
        btn.textContent = SUGGESTED_PROMPTS[index];
        btn.addEventListener('click', () => {
          if (this.elements.messageInput) {
            this.elements.messageInput.value = SUGGESTED_PROMPTS[index];
            this.handleInputChange();
            this.sendMessage();
          }
        });
      }
    });
  }

  /**
   * Show suggested follow-ups
   */
  showSuggestedFollowups(suggestions) {
    if (!this.elements.suggestedFollowups || !this.elements.followupButtons) return;

    // Clear existing buttons
    this.elements.followupButtons.innerHTML = '';

    // Add new buttons
    suggestions.forEach(suggestion => {
      const btn = document.createElement('button');
      btn.className = 'followup-btn';
      btn.textContent = suggestion;
      btn.addEventListener('click', () => {
        if (this.elements.messageInput) {
          this.elements.messageInput.value = suggestion;
          this.handleInputChange();
          this.sendMessage();
        }
        this.hideSuggestedFollowups();
      });
      this.elements.followupButtons.appendChild(btn);
    });

    this.elements.suggestedFollowups.classList.add('show');
  }

  /**
   * Hide suggested follow-ups
   */
  hideSuggestedFollowups() {
    if (this.elements.suggestedFollowups) {
      this.elements.suggestedFollowups.classList.remove('show');
    }
  }

  /**
   * Handle quick actions
   */
  handleQuickAction(action) {
    const actionMap = {
      findFlights: "Help me find flights",
      findHotels: "Show me hotel options",
      planItinerary: "Help me plan an itinerary",
      exploreDestinations: "Suggest travel destinations"
    };

    const message = actionMap[action];
    if (message && this.elements.messageInput) {
      this.elements.messageInput.value = message;
      this.handleInputChange();
      this.sendMessage();
    }
  }

  /**
   * Copy message content
   */
  async copyMessage(message) {
    const success = await Utils.copyToClipboard(message.content);
    if (success) {
      this.toastManager.show('Message copied to clipboard', 'success', 2000);
    } else {
      this.toastManager.show('Failed to copy message', 'error', 2000);
    }
  }

  /**
   * Like message
   */
  likeMessage(message) {
    // Update message in conversation
    const msgIndex = this.currentConversation.messages.findIndex(m => m.id === message.id);
    if (msgIndex !== -1) {
      this.currentConversation.messages[msgIndex].liked = !this.currentConversation.messages[msgIndex].liked;
      this.saveCurrentConversation();
    }

    // Update UI
    const messageElement = document.querySelector(`[data-message-id="${message.id}"]`);
    if (messageElement) {
      const likeBtn = messageElement.querySelector('.message-action-btn i.fa-thumbs-up');
      if (likeBtn) {
        likeBtn.className = message.liked ? 'fas fa-thumbs-up' : 'far fa-thumbs-up';
      }
    }

    this.toastManager.show(
      message.liked ? 'Message liked' : 'Like removed',
      'success',
      1500
    );
  }

  /**
   * Toggle sidebar
   */
  toggleSidebar() {
    if (!this.elements.sidebar) return;

    const isCollapsed = this.elements.sidebar.classList.toggle('collapsed');
    
    // Update ARIA attributes
    this.elements.sidebar.setAttribute('aria-expanded', !isCollapsed);
    
    // Save state
    localStorage.setItem('sidebar-collapsed', isCollapsed);
    
    // Emit event
    this.emit('sidebarToggled', isCollapsed);
  }

  /**
   * Toggle mobile sidebar
   */
  toggleMobileSidebar() {
    if (!this.elements.sidebar) return;

    const isOpen = this.elements.sidebar.classList.toggle('open');
    
    // Update ARIA attributes
    this.elements.sidebar.setAttribute('aria-expanded', isOpen);
    
    // Manage body scroll
    document.body.style.overflow = isOpen ? 'hidden' : '';
  }

  /**
   * Start new chat
   */
  startNewChat() {
    // Save current conversation if it exists
    if (this.currentConversation) {
      this.saveCurrentConversation();
    }

    // Create new conversation
    this.currentConversation = {
      id: Utils.generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      draft: ''
    };

    // Clear chat messages
    if (this.elements.chatMessages) {
      this.elements.chatMessages.innerHTML = '';
    }

    // Show welcome screen
    this.showWelcomeScreen();

    // Hide suggested follow-ups
    this.hideSuggestedFollowups();

    // Update title
    this.updateChatTitle('New Chat');

    // Focus input
    if (this.elements.messageInput) {
      this.elements.messageInput.focus();
    }

    // Save new conversation
    StorageManager.setCurrentConversation(this.currentConversation);

    this.toastManager.show('New chat started', 'success', 2000);
  }

  /**
   * Clear current chat
   */
  clearCurrentChat() {
    if (!this.currentConversation || this.currentConversation.messages.length === 0) {
      this.toastManager.show('No messages to clear', 'info', 2000);
      return;
    }

    if (confirm('Are you sure you want to clear this chat? This action cannot be undone.')) {
      // Clear messages
      this.currentConversation.messages = [];
      this.currentConversation.updatedAt = Date.now();

      // Clear UI
      if (this.elements.chatMessages) {
        this.elements.chatMessages.innerHTML = '';
      }

      // Show welcome screen
      this.showWelcomeScreen();

      // Hide suggested follow-ups
      this.hideSuggestedFollowups();

      // Save conversation
      this.saveCurrentConversation();

      this.toastManager.show('Chat cleared', 'success', 2000);
    }
  }

  /**
   * Load conversation by ID
   */
  loadConversationById(conversationId) {
    const conversation = this.conversations.find(c => c.id === conversationId);
    if (conversation) {
      this.loadConversation(conversation);
    }
  }

  /**
   * Load conversation
   */
  loadConversation(conversation) {
    // Save current conversation if it exists
    if (this.currentConversation) {
      this.saveCurrentConversation();
    }

    this.currentConversation = { ...conversation };

    // Clear chat messages
    if (this.elements.chatMessages) {
      this.elements.chatMessages.innerHTML = '';
    }

    // Load messages
    if (conversation.messages && conversation.messages.length > 0) {
      this.hideWelcomeScreen();
      
      conversation.messages.forEach(message => {
        const messageElement = this.createMessageElement(message);
        this.elements.chatMessages.appendChild(messageElement);
      });

      this.scrollToBottom();
    } else {
      this.showWelcomeScreen();
    }

    // Update title
    this.updateChatTitle(conversation.title);

    // Load draft if exists
    if (conversation.draft && this.elements.messageInput) {
      this.elements.messageInput.value = conversation.draft;
      this.handleInputChange();
    }



    // Save as current conversation
    StorageManager.setCurrentConversation(this.currentConversation);
  }

  /**
   * Save current conversation
   */
  saveCurrentConversation() {
    if (!this.currentConversation) return;

    // Update conversation in list
    const existingIndex = this.conversations.findIndex(c => c.id === this.currentConversation.id);
    if (existingIndex !== -1) {
      this.conversations[existingIndex] = { ...this.currentConversation };
    } else {
      this.conversations.unshift({ ...this.currentConversation });
    }

    // Save to storage
    StorageManager.setConversations(this.conversations);
    StorageManager.setCurrentConversation(this.currentConversation);
  }

  /**
   * Generate conversation title
   */
  generateConversationTitle() {
    if (!this.currentConversation || this.currentConversation.messages.length === 0) return;

    const firstUserMessage = this.currentConversation.messages.find(m => m.sender === 'user');
    if (firstUserMessage) {
      // Generate title from first user message (first 50 characters)
      let title = firstUserMessage.content.substring(0, 50);
      if (firstUserMessage.content.length > 50) {
        title += '...';
      }
      
      this.currentConversation.title = title;
      this.updateChatTitle(title);
      this.saveCurrentConversation();
    }
  }

  /**
   * Update chat title
   */
  updateChatTitle(title) {
    if (this.elements.chatTitle) {
      this.elements.chatTitle.textContent = title;
    }
  }

  /**
   * Load conversations from storage
   */
  loadConversations() {
    this.conversations = StorageManager.getConversations();
  }



  /**
   * Load theme
   */
  loadTheme() {
    const theme = StorageManager.getTheme();
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update theme toggle icon
    if (this.elements.themeToggle) {
      const icon = this.elements.themeToggle.querySelector('i');
      if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      }
    }
  }

  /**
   * Toggle theme
   */
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    StorageManager.setTheme(newTheme);
    
    // Update theme toggle icon
    if (this.elements.themeToggle) {
      const icon = this.elements.themeToggle.querySelector('i');
      if (icon) {
        icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      }
    }

    this.toastManager.show(`Switched to ${newTheme} theme`, 'success', 2000);
  }

  /**
   * Load settings
   */
  loadSettings() {
    const settings = StorageManager.getSettings();
    // Apply settings to UI if needed
    this.updateStatusIndicator();
  }

  /**
   * Open settings modal
   */
  openSettings() {
    const settings = StorageManager.getSettings();
    
    const settingsContent = `
      <form class="settings-form">
        <div class="setting-group">
          <label for="notifications">Enable Notifications</label>
          <label class="setting-checkbox">
            <input type="checkbox" id="notifications" ${settings.notifications ? 'checked' : ''}>
            <span>Show desktop notifications</span>
          </label>
        </div>
        
        <div class="setting-group">
          <label for="soundEnabled">Sound Effects</label>
          <label class="setting-checkbox">
            <input type="checkbox" id="soundEnabled" ${settings.soundEnabled ? 'checked' : ''}>
            <span>Play notification sounds</span>
          </label>
        </div>
        
        <div class="setting-group">
          <label for="autoSave">Auto-save</label>
          <label class="setting-checkbox">
            <input type="checkbox" id="autoSave" ${settings.autoSave ? 'checked' : ''}>
            <span>Automatically save conversations</span>
          </label>
        </div>
        
        <div class="setting-group">
          <label for="language">Language</label>
          <select id="language" class="setting-select">
            <option value="en" ${settings.language === 'en' ? 'selected' : ''}>English</option>
            <option value="es" ${settings.language === 'es' ? 'selected' : ''}>Español</option>
            <option value="fr" ${settings.language === 'fr' ? 'selected' : ''}>Français</option>
          </select>
        </div>
      </form>
    `;

    const footer = `
      <button type="button" class="btn-secondary" onclick="travelAgent.modalManager.close()">Cancel</button>
      <button type="button" class="btn-primary" onclick="travelAgent.saveSettings()">Save Settings</button>
    `;

    this.modalManager.createModal('settingsModal', 'Settings', settingsContent, footer);
    this.modalManager.open('settingsModal');
  }

  /**
   * Save settings
   */
  saveSettings() {
    const form = document.querySelector('.settings-form');
    if (!form) return;

    const settings = {
      notifications: form.querySelector('#notifications').checked,
      soundEnabled: form.querySelector('#soundEnabled').checked,
      autoSave: form.querySelector('#autoSave').checked,
      language: form.querySelector('#language').value
    };

    StorageManager.setSettings(settings);
    this.modalManager.close();
    this.toastManager.show('Settings saved', 'success', 2000);

    // Restart auto-save if setting changed
    if (settings.autoSave) {
      this.startAutoSave();
    } else {
      this.stopAutoSave();
    }
  }

  /**
   * Open export modal
   */
  openExportModal() {
    if (!this.currentConversation || this.currentConversation.messages.length === 0) {
      this.toastManager.show('No conversation to export', 'info', 2000);
      return;
    }

    const exportContent = `
      <div class="export-options">
        <div class="export-option" onclick="travelAgent.exportConversation('txt')">
          <i class="fas fa-file-alt"></i>
          <div>
            <h3>Text File</h3>
            <p>Export as plain text (.txt)</p>
          </div>
        </div>
        
        <div class="export-option" onclick="travelAgent.exportConversation('json')">
          <i class="fas fa-file-code"></i>
          <div>
            <h3>JSON File</h3>
            <p>Export as JSON data (.json)</p>
          </div>
        </div>
        
        <div class="export-option" onclick="travelAgent.exportConversation('pdf')">
          <i class="fas fa-file-pdf"></i>
          <div>
            <h3>PDF Document</h3>
            <p>Export as PDF (.pdf)</p>
          </div>
        </div>
      </div>
    `;

    this.modalManager.createModal('exportModal', 'Export Conversation', exportContent);
    this.modalManager.open('exportModal');
  }

  /**
   * Export conversation
   */
  exportConversation(format) {
    if (!this.currentConversation) return;

    try {
      let content, filename, mimeType;

      switch (format) {
        case 'txt':
          content = this.generateTextExport();
          filename = `${this.currentConversation.title.replace(/[^a-z0-9]/gi, '_')}.txt`;
          mimeType = 'text/plain';
          break;

        case 'json':
          content = JSON.stringify(this.currentConversation, null, 2);
          filename = `${this.currentConversation.title.replace(/[^a-z0-9]/gi, '_')}.json`;
          mimeType = 'application/json';
          break;

        case 'pdf':
          this.generatePDFExport();
          this.modalManager.close();
          return;

        default:
          throw new Error('Unsupported export format');
      }

      // Create and download file
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      this.modalManager.close();
      this.toastManager.show(`Conversation exported as ${format.toUpperCase()}`, 'success');

    } catch (error) {
      console.error('Export failed:', error);
      this.toastManager.show('Export failed', 'error');
    }
  }

  /**
   * Generate text export
   */
  generateTextExport() {
    const lines = [
      `Travel Agent Conversation: ${this.currentConversation.title}`,
      `Created: ${new Date(this.currentConversation.createdAt).toLocaleString()}`,
      `Updated: ${new Date(this.currentConversation.updatedAt).toLocaleString()}`,
      '',
      '=' .repeat(50),
      ''
    ];

    this.currentConversation.messages.forEach(message => {
      const sender = message.sender === 'user' ? 'You' : 'Travel Agent';
      const time = new Date(message.timestamp).toLocaleString();
      
      lines.push(`[${time}] ${sender}:`);
      lines.push(message.content);
      lines.push('');
    });

    return lines.join('\n');
  }

  /**
   * Generate PDF export (simplified version)
   */
  generatePDFExport() {
    // For a full implementation, you would use a library like jsPDF
    // This is a simplified version that opens a print dialog
    const printWindow = window.open('', '_blank');
    const content = this.generateTextExport().replace(/\n/g, '<br>');
    
    printWindow.document.write(`
      <html>
        <head>
          <title>${this.currentConversation.title}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .message { margin-bottom: 15px; }
            .sender { font-weight: bold; color: #666; }
          </style>
        </head>
        <body>
          <h1>${this.currentConversation.title}</h1>
          <div>${content}</div>
        </body>
      </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
  }

  /**
   * Set input state (enabled/disabled)
   */
  setInputState(enabled) {
    if (this.elements.messageInput) {
      this.elements.messageInput.disabled = !enabled;
    }
    
    if (this.elements.sendBtn) {
      this.elements.sendBtn.disabled = !enabled;
    }
  }

  /**
   * Update status indicator
   */
  updateStatusIndicator() {
    if (this.elements.statusIndicator) {
      const statusText = this.elements.statusIndicator.querySelector('span');
      if (statusText) {
        statusText.textContent = 'Ready';
      }
    }
  }

  /**
   * Handle window resize
   */
  handleWindowResize() {
    // Handle responsive behavior
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile && this.elements.sidebar && this.elements.sidebar.classList.contains('collapsed')) {
      // On mobile, don't keep sidebar collapsed
      this.elements.sidebar.classList.remove('collapsed');
    }
  }

  /**
   * Start auto-save timer
   */
  startAutoSave() {
    const settings = StorageManager.getSettings();
    if (!settings.autoSave) return;

    this.stopAutoSave(); // Clear existing timer
    
    this.autoSaveTimer = setInterval(() => {
      if (this.currentConversation) {
        this.saveCurrentConversation();
      }
    }, CONFIG.UI.AUTO_SAVE_INTERVAL);
  }

  /**
   * Stop auto-save timer
   */
  stopAutoSave() {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
      this.autoSaveTimer = null;
    }
  }

  /**
   * Announce message to screen readers
   */
  announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.stopAutoSave();
    this.toastManager.clear();
    
    // Remove event listeners
    // (In a real implementation, you'd store references to bound functions)
    
    console.log('Travel Agent Chat destroyed');
  }
}

// ========================================
// INITIALIZATION
// ========================================

// Global instance
let travelAgent;

// Initialize when DOM is ready
 if (document.readyState === 'loading') {
   document.addEventListener('DOMContentLoaded', initializeApp);
 } else {
   initializeApp();
 }

 function initializeApp() {
   try {
     travelAgent = new TravelAgentChat();
     
     // Make it globally accessible for debugging and modal callbacks
     window.travelAgent = travelAgent;
     
     console.log('Travel Agent Chat application loaded successfully');
   } catch (error) {
     console.error('Failed to initialize Travel Agent Chat:', error);
     
     // Show fallback error message
     const errorDiv = document.createElement('div');
     errorDiv.style.cssText = `
       position: fixed;
       top: 20px;
       right: 20px;
       background: #f44336;
       color: white;
       padding: 16px;
       border-radius: 8px;
       z-index: 10000;
       font-family: Arial, sans-serif;
     `;
     errorDiv.textContent = 'Failed to initialize application. Please refresh the page.';
     document.body.appendChild(errorDiv);
     
     setTimeout(() => {
       if (errorDiv.parentNode) {
         errorDiv.parentNode.removeChild(errorDiv);
       }
     }, 5000);
   }
 }

 // Export for module systems
 if (typeof module !== 'undefined' && module.exports) {
   module.exports = { TravelAgentChat, Utils, StorageManager };
 }