// Main JavaScript for KakaoTalk Chat Analyzer

// Global variables
let currentPage = 'dashboard';
let searchTimeout = null;

// Utility functions
const Utils = {
    // Format number with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Show notification
    showNotification: function(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const icon = this.getNotificationIcon(type);
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${icon} ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        // Add to page
        $('main').prepend(notification);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            notification.alert('close');
        }, 5000);
    },

    // Get notification icon
    getNotificationIcon: function(type) {
        const icons = {
            success: '<i class="bi bi-check-circle"></i>',
            error: '<i class="bi bi-exclamation-triangle"></i>',
            warning: '<i class="bi bi-exclamation-triangle"></i>',
            info: '<i class="bi bi-info-circle"></i>'
        };
        return icons[type] || icons.info;
    },

    // Debounce function
    debounce: function(func, wait) {
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(searchTimeout);
                func(...args);
            };
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('클립보드에 복사되었습니다!', 'success');
        }).catch(() => {
            this.showNotification('클립보드 복사에 실패했습니다.', 'error');
        });
    },

    // Download JSON
    downloadJSON: function(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

// Search functionality
const Search = {
    // Initialize search
    init: function() {
        this.bindEvents();
        this.loadSearchHistory();
    },

    // Bind search events
    bindEvents: function() {
        const searchInput = $('#searchInput');
        if (searchInput.length) {
            searchInput.on('input', Utils.debounce(() => {
                this.performSearch();
            }, 300));
        }

        // Search form submit
        $('#searchForm').on('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
    },

    // Perform search
    performSearch: function() {
        const keyword = $('#searchInput').val().trim();
        const nickname = $('#nicknameInput').val().trim();
        const limit = $('#limitInput').val() || 100;

        if (!keyword && !nickname) {
            $('#searchResults').html('<p class="text-muted text-center">검색어를 입력해주세요.</p>');
            return;
        }

        // Show loading
        $('#searchResults').html('<div class="text-center"><i class="bi bi-arrow-clockwise spin"></i> 검색 중...</div>');

        // API call
        $.get('/api/search', { keyword, nickname, limit })
            .done((response) => {
                this.displayResults(response.results);
                this.saveSearchHistory(keyword, nickname);
            })
            .fail(() => {
                $('#searchResults').html('<p class="text-danger text-center">검색 중 오류가 발생했습니다.</p>');
            });
    },

    // Display search results
    displayResults: function(results) {
        const container = $('#searchResults');
        
        if (results.length === 0) {
            container.html('<p class="text-muted text-center">검색 결과가 없습니다.</p>');
            return;
        }

        let html = `<div class="mb-3"><strong>${results.length}개의 결과를 찾았습니다.</strong></div>`;
        
        results.forEach((result, index) => {
            html += `
                <div class="search-result">
                    <div class="message-meta">
                        <span class="badge bg-primary">${result.nickname}</span>
                        <span class="text-muted">${result.time_str}</span>
                        <span class="badge bg-secondary">${result.message_type}</span>
                    </div>
                    <div class="message-content">
                        ${this.highlightText(result.message_text || result.raw_line)}
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="Utils.copyToClipboard('${result.raw_line.replace(/'/g, "\\'")}')">
                            <i class="bi bi-clipboard"></i> 복사
                        </button>
                    </div>
                </div>
            `;
        });

        container.html(html);
    },

    // Highlight search terms
    highlightText: function(text) {
        const keyword = $('#searchInput').val().trim();
        if (!keyword) return text;
        
        const regex = new RegExp(`(${keyword})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    },

    // Save search history
    saveSearchHistory: function(keyword, nickname) {
        const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        const search = { keyword, nickname, timestamp: new Date().toISOString() };
        
        // Remove duplicates
        const filtered = history.filter(item => 
            item.keyword !== keyword || item.nickname !== nickname
        );
        
        // Add to beginning
        filtered.unshift(search);
        
        // Keep only last 10 searches
        if (filtered.length > 10) {
            filtered.splice(10);
        }
        
        localStorage.setItem('searchHistory', JSON.stringify(filtered));
    },

    // Load search history
    loadSearchHistory: function() {
        const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        const container = $('#searchHistory');
        
        if (history.length === 0) {
            container.html('<p class="text-muted">검색 기록이 없습니다.</p>');
            return;
        }

        let html = '<h6>최근 검색</h6>';
        history.forEach(item => {
            const displayText = item.keyword || item.nickname || '전체 검색';
            html += `
                <div class="mb-2">
                    <button class="btn btn-sm btn-outline-secondary" onclick="Search.loadFromHistory('${item.keyword || ''}', '${item.nickname || ''}')">
                        ${displayText}
                    </button>
                </div>
            `;
        });

        container.html(html);
    },

    // Load from history
    loadFromHistory: function(keyword, nickname) {
        $('#searchInput').val(keyword);
        $('#nicknameInput').val(nickname);
        this.performSearch();
    }
};

// Statistics functionality
const Statistics = {
    // Initialize statistics
    init: function() {
        this.loadStatistics();
        this.initCharts();
    },

    // Load statistics
    loadStatistics: function() {
        $.get('/api/statistics')
            .done((data) => {
                this.displayStatistics(data);
            })
            .fail(() => {
                Utils.showNotification('통계를 불러오는 중 오류가 발생했습니다.', 'error');
            });
    },

    // Display statistics
    displayStatistics: function(data) {
        // Update user statistics
        if (data.user_statistics) {
            this.displayUserStats(data.user_statistics);
        }

        // Update keyword statistics
        if (data.keyword_frequency) {
            this.displayKeywordStats(data.keyword_frequency);
        }
    },

    // Display user statistics
    displayUserStats: function(users) {
        const container = $('#userStats');
        if (!container.length) return;

        let html = '';
        users.slice(0, 10).forEach((user, index) => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <span class="badge bg-primary me-2">${index + 1}</span>
                        <span class="text-truncate">${user.nickname}</span>
                    </div>
                    <div>
                        <span class="badge bg-success">${Utils.formatNumber(user.total_messages)}</span>
                    </div>
                </div>
            `;
        });

        container.html(html);
    },

    // Display keyword statistics
    displayKeywordStats: function(keywords) {
        const container = $('#keywordStats');
        if (!container.length) return;

        let html = '';
        keywords.slice(0, 10).forEach((keyword, index) => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="text-truncate">${keyword.keyword}</span>
                    <span class="badge bg-info">${Utils.formatNumber(keyword.frequency)}</span>
                </div>
            `;
        });

        container.html(html);
    },

    // Initialize charts (placeholder for future chart implementation)
    initCharts: function() {
        // Future implementation for Chart.js integration
        console.log('Charts initialization placeholder');
    }
};

// Page-specific functionality
const PageManager = {
    // Initialize page
    init: function() {
        this.detectPage();
        this.initPageSpecific();
    },

    // Detect current page
    detectPage: function() {
        const path = window.location.pathname;
        if (path === '/') currentPage = 'dashboard';
        else if (path === '/upload') currentPage = 'upload';
        else if (path === '/search') currentPage = 'search';
        else if (path === '/statistics') currentPage = 'statistics';
    },

    // Initialize page-specific functionality
    initPageSpecific: function() {
        switch (currentPage) {
            case 'dashboard':
                // Dashboard specific initialization
                break;
            case 'search':
                Search.init();
                break;
            case 'statistics':
                Statistics.init();
                break;
            case 'upload':
                // Upload specific initialization is handled in upload.html
                break;
        }
    }
};

// Initialize when document is ready
$(document).ready(function() {
    // Initialize page manager
    PageManager.init();

    // Global event handlers
    $(document).on('click', '[data-copy]', function() {
        const text = $(this).data('copy');
        Utils.copyToClipboard(text);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        $('.alert').alert('close');
    }, 5000);

    // Add loading states to buttons
    $(document).on('click', '.btn', function() {
        const $btn = $(this);
        if (!$btn.hasClass('btn-loading')) {
            $btn.addClass('btn-loading').prop('disabled', true);
            setTimeout(() => {
                $btn.removeClass('btn-loading').prop('disabled', false);
            }, 2000);
        }
    });
});

// Export for global access
window.Utils = Utils;
window.Search = Search;
window.Statistics = Statistics; 