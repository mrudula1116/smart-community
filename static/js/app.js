/**
 * CommunityPulse AI — Frontend Application
 * SPA Navigation, API Service, Charts, and Interactions
 */

// ═══════════════════════════════════════════════════
// Configuration & State
// ═══════════════════════════════════════════════════

const API_BASE = '';
const state = {
    currentPage: 'dashboard',
    dashboardData: null,
    complaints: [],
    alerts: [],
    chatSessionId: crypto.randomUUID ? crypto.randomUUID() : 'session-' + Date.now(),
    chatMessages: [],
    charts: {},
    isLoading: false,
};

// ═══════════════════════════════════════════════════
// API Service
// ═══════════════════════════════════════════════════

const api = {
    async get(url) {
        try {
            const res = await fetch(`${API_BASE}${url}`);
            return await res.json();
        } catch (err) {
            console.error('API GET error:', err);
            return { success: false, error: err.message };
        }
    },
    
    async post(url, data) {
        try {
            const res = await fetch(`${API_BASE}${url}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            return await res.json();
        } catch (err) {
            console.error('API POST error:', err);
            return { success: false, error: err.message };
        }
    },
    
    async put(url, data) {
        try {
            const res = await fetch(`${API_BASE}${url}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            return await res.json();
        } catch (err) {
            console.error('API PUT error:', err);
            return { success: false, error: err.message };
        }
    },
};

// ═══════════════════════════════════════════════════
// Toast Notifications
// ═══════════════════════════════════════════════════

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const icons = { success: '✓', error: '✗', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${icons[type] || 'ℹ'}</span>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.classList.add('removing'); setTimeout(() => this.parentElement.remove(), 300)">×</button>
    `;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ═══════════════════════════════════════════════════
// Navigation
// ═══════════════════════════════════════════════════

function navigateTo(page) {
    state.currentPage = page;
    
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    
    // Update page sections
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.toggle('active', section.id === `page-${page}`);
    });
    
    // Update header
    const titles = {
        dashboard: { icon: '📊', title: 'Command Dashboard', subtitle: 'Real-time community intelligence overview' },
        complaints: { icon: '📋', title: 'AI Complaint Analyzer', subtitle: 'Intelligent complaint processing & routing' },
        emergency: { icon: '🚨', title: 'Emergency Preparedness', subtitle: 'Active alerts & safety guidance' },
        insights: { icon: '🔍', title: 'Community Insights', subtitle: 'AI-powered analytics & predictions' },
        chat: { icon: '🤖', title: 'AI Assistant', subtitle: 'Natural language community intelligence' },
        reports: { icon: '📈', title: 'Reports & Impact', subtitle: 'Social impact tracking & AI reports' },
    };
    
    const pageInfo = titles[page] || titles.dashboard;
    const headerSection = document.querySelector('.page-title-section');
    if (headerSection) {
        headerSection.innerHTML = `
            <span class="page-icon">${pageInfo.icon}</span>
            <div>
                <h2>${pageInfo.title}</h2>
                <div class="page-subtitle">${pageInfo.subtitle}</div>
            </div>
        `;
    }
    
    // Load page data
    loadPageData(page);
    
    // Close mobile sidebar
    document.querySelector('.sidebar')?.classList.remove('open');
}

async function loadPageData(page) {
    switch (page) {
        case 'dashboard': await loadDashboard(); break;
        case 'complaints': await loadComplaints(); break;
        case 'emergency': await loadAlerts(); break;
        case 'insights': await loadInsights(); break;
        case 'chat': initChat(); break;
        case 'reports': await loadReports(); break;
    }
}

// ═══════════════════════════════════════════════════
// Dashboard
// ═══════════════════════════════════════════════════

async function loadDashboard() {
    const result = await api.get('/api/dashboard');
    if (!result.success) return showToast('Failed to load dashboard', 'error');
    
    state.dashboardData = result.data;
    renderDashboard(result.data);
    
    // Load trends for charts
    const trends = await api.get('/api/dashboard/trends');
    if (trends.success) {
        renderDashboardCharts(trends.data, result.data);
    }
}

function renderDashboard(data) {
    // Update stat cards with counting animation
    animateCounter('stat-total', data.total_complaints);
    animateCounter('stat-open', data.open_complaints);
    animateCounter('stat-active-alerts', data.active_alerts);
    animateCounter('stat-resolved', data.resolved);
    animateCounter('stat-resolution-rate', data.resolution_rate, true);
    
    // Update wellbeing score
    const wellbeingEl = document.getElementById('wellbeing-value');
    if (wellbeingEl) {
        animateCounter('wellbeing-value', data.wellbeing_score, true);
    }
    
    // Render recent complaints activity feed
    const feedEl = document.getElementById('activity-feed');
    if (feedEl && data.recent_complaints) {
        feedEl.innerHTML = data.recent_complaints.map(c => `
            <li class="activity-item">
                <div class="activity-icon" style="background: ${getSeverityBgColor(c.severity)}">
                    ${getCategoryIcon(c.category)}
                </div>
                <div class="activity-content">
                    <div class="activity-title">${escapeHtml(c.title)}</div>
                    <div class="activity-time">
                        <span class="badge ${c.status.toLowerCase().replace(' ', '-')}">${c.status}</span>
                        · ${timeAgo(c.created_at)}
                    </div>
                </div>
            </li>
        `).join('');
    }
    
    // Update emergency ticker
    renderTicker(data.active_alerts);
}

function renderDashboardCharts(trendsData, dashData) {
    // Category Distribution Doughnut
    if (dashData.category_distribution?.length > 0) {
        const catCtx = document.getElementById('chart-categories');
        if (catCtx) {
            if (state.charts.categories) state.charts.categories.destroy();
            
            const colors = ['#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4', '#f43f5e'];
            state.charts.categories = new Chart(catCtx, {
                type: 'doughnut',
                data: {
                    labels: dashData.category_distribution.map(c => c.category),
                    datasets: [{
                        data: dashData.category_distribution.map(c => c.count),
                        backgroundColor: colors.slice(0, dashData.category_distribution.length),
                        borderColor: '#0c1229',
                        borderWidth: 3,
                        hoverBorderWidth: 0,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '68%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#94a3b8',
                                font: { family: 'Inter', size: 11, weight: 500 },
                                padding: 16,
                                usePointStyle: true,
                                pointStyleWidth: 8,
                            },
                        },
                    },
                },
            });
        }
    }
    
    // Status Distribution Bar
    if (dashData.status_distribution?.length > 0) {
        const statusCtx = document.getElementById('chart-status');
        if (statusCtx) {
            if (state.charts.status) state.charts.status.destroy();
            
            const statusColors = {
                'Open': '#3b82f6',
                'In Progress': '#f59e0b',
                'Resolved': '#10b981',
                'Closed': '#64748b',
            };
            
            state.charts.status = new Chart(statusCtx, {
                type: 'bar',
                data: {
                    labels: dashData.status_distribution.map(s => s.status),
                    datasets: [{
                        data: dashData.status_distribution.map(s => s.count),
                        backgroundColor: dashData.status_distribution.map(s => statusColors[s.status] || '#6366f1'),
                        borderRadius: 8,
                        borderSkipped: false,
                        barThickness: 40,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } },
                            border: { display: false },
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 11 }, stepSize: 1 },
                            border: { display: false },
                            beginAtZero: true,
                        },
                    },
                },
            });
        }
    }
    
    // Complaint Trend Line Chart
    if (trendsData.metrics?.complaints_received?.length > 0) {
        const trendCtx = document.getElementById('chart-trend');
        if (trendCtx) {
            if (state.charts.trend) state.charts.trend.destroy();
            
            const received = trendsData.metrics.complaints_received;
            const resolved = trendsData.metrics.complaints_resolved || [];
            
            state.charts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: received.map(d => formatDate(d.date)),
                    datasets: [
                        {
                            label: 'Received',
                            data: received.map(d => d.value),
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99,102,241,0.1)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 5,
                        },
                        {
                            label: 'Resolved',
                            data: resolved.map(d => d.value),
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16,185,129,0.05)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 5,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            align: 'end',
                            labels: {
                                color: '#94a3b8',
                                font: { family: 'Inter', size: 11 },
                                usePointStyle: true,
                                pointStyleWidth: 8,
                                boxHeight: 6,
                            },
                        },
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 8 },
                            border: { display: false },
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.04)' },
                            ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } },
                            border: { display: false },
                            beginAtZero: true,
                        },
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index',
                    },
                },
            });
        }
    }
    
    // Department Performance
    if (dashData.department_distribution?.length > 0) {
        const deptCtx = document.getElementById('chart-departments');
        if (deptCtx) {
            if (state.charts.departments) state.charts.departments.destroy();
            
            const deptColors = ['#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#a855f7', '#ef4444', '#f43f5e'];
            
            state.charts.departments = new Chart(deptCtx, {
                type: 'bar',
                data: {
                    labels: dashData.department_distribution.map(d => d.department),
                    datasets: [{
                        data: dashData.department_distribution.map(d => d.count),
                        backgroundColor: deptColors.slice(0, dashData.department_distribution.length),
                        borderRadius: 6,
                        borderSkipped: false,
                    }],
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255,255,255,0.04)' },
                            ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 }, stepSize: 1 },
                            border: { display: false },
                            beginAtZero: true,
                        },
                        y: {
                            grid: { display: false },
                            ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } },
                            border: { display: false },
                        },
                    },
                },
            });
        }
    }
}

function renderTicker(alertCount) {
    const ticker = document.getElementById('emergency-ticker');
    if (!ticker) return;
    
    if (alertCount > 0) {
        ticker.classList.remove('ticker-hidden');
    } else {
        ticker.classList.add('ticker-hidden');
    }
}

// ═══════════════════════════════════════════════════
// Complaints
// ═══════════════════════════════════════════════════

async function loadComplaints() {
    const status = document.getElementById('filter-status')?.value || 'All';
    const category = document.getElementById('filter-category')?.value || 'All';
    const priority = document.getElementById('filter-priority')?.value || 'All';
    
    const result = await api.get(`/api/complaints?status=${status}&category=${category}&priority=${priority}`);
    if (!result.success) return showToast('Failed to load complaints', 'error');
    
    state.complaints = result.data;
    renderComplaints(result.data);
}

function renderComplaints(complaints) {
    const tbody = document.getElementById('complaints-table-body');
    if (!tbody) return;
    
    if (complaints.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center" style="padding: 48px; color: var(--text-muted);">
                    No complaints found matching filters.
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = complaints.map(c => `
        <tr onclick="viewComplaint('${c.tracking_id}')" style="cursor: pointer;">
            <td>
                <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent-secondary);">
                    ${c.tracking_id}
                </span>
            </td>
            <td>
                <div class="truncate" style="max-width: 280px;" title="${escapeHtml(c.title)}">
                    ${escapeHtml(c.title)}
                </div>
            </td>
            <td>${getCategoryIcon(c.category)} ${c.category}</td>
            <td><span class="badge ${c.severity?.toLowerCase()}">${c.severity || 'N/A'}</span></td>
            <td><span class="badge ${c.status?.toLowerCase().replace(' ', '-')}">${c.status}</span></td>
            <td>${c.department || '—'}</td>
            <td style="font-size: 0.78rem; color: var(--text-muted);">${timeAgo(c.created_at)}</td>
        </tr>
    `).join('');
}

async function submitComplaint(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> Submitting...';
    
    const data = {
        title: form.querySelector('#complaint-title').value,
        description: form.querySelector('#complaint-description').value,
        category: form.querySelector('#complaint-category').value,
        location: form.querySelector('#complaint-location').value,
        citizen_name: form.querySelector('#complaint-name').value || 'Anonymous',
        citizen_contact: form.querySelector('#complaint-contact').value || '',
    };
    
    // Create complaint
    const result = await api.post('/api/complaints', data);
    
    if (result.success) {
        showToast(`Complaint registered! Tracking ID: ${result.data.tracking_id}`, 'success');
        
        // Now analyze it with AI
        showToast('🤖 Running AI analysis...', 'info');
        const analysis = await api.post('/api/complaints/analyze', {
            ...data,
            complaint_id: result.data.tracking_id,
        });
        
        if (analysis.success) {
            showToast('AI analysis complete!', 'success');
            renderAnalysisPanel(analysis.analysis);
        }
        
        form.reset();
        await loadComplaints();
    } else {
        showToast('Failed to submit complaint: ' + (result.error || 'Unknown error'), 'error');
    }
    
    submitBtn.disabled = false;
    submitBtn.innerHTML = '🚀 Submit & Analyze';
}

async function viewComplaint(trackingId) {
    const result = await api.get(`/api/complaints/${trackingId}`);
    if (!result.success) return showToast('Failed to load complaint', 'error');
    
    const c = result.data;
    const modal = document.getElementById('complaintModal');
    const modalBody = document.getElementById('complaintModalBody');
    
    let aiAnalysis = {};
    let recommendations = [];
    try { aiAnalysis = JSON.parse(c.ai_analysis || '{}'); } catch(e) {}
    try { recommendations = JSON.parse(c.ai_recommendations || '[]'); } catch(e) {}
    
    modalBody.innerHTML = `
        <div class="detail-header">
            <div>
                <div class="detail-title">${escapeHtml(c.title)}</div>
                <div class="detail-id">${c.tracking_id} · ${c.citizen_name || 'Anonymous'}</div>
            </div>
            <span class="badge ${c.status?.toLowerCase().replace(' ', '-')}" style="font-size: 0.78rem;">${c.status}</span>
        </div>
        
        <div class="detail-info-grid">
            <div class="detail-info-item">
                <div class="detail-info-label">Category</div>
                <div class="detail-info-value">${getCategoryIcon(c.category)} ${c.category}</div>
            </div>
            <div class="detail-info-item">
                <div class="detail-info-label">Severity</div>
                <div class="detail-info-value"><span class="badge ${c.severity?.toLowerCase()}">${c.severity}</span></div>
            </div>
            <div class="detail-info-item">
                <div class="detail-info-label">Priority</div>
                <div class="detail-info-value"><span class="badge ${c.priority?.toLowerCase()}">${c.priority}</span></div>
            </div>
            <div class="detail-info-item">
                <div class="detail-info-label">Department</div>
                <div class="detail-info-value">${c.department || 'Unassigned'}</div>
            </div>
            <div class="detail-info-item">
                <div class="detail-info-label">Location</div>
                <div class="detail-info-value">${c.location || 'Not specified'}</div>
            </div>
            <div class="detail-info-item">
                <div class="detail-info-label">Sentiment</div>
                <div class="detail-info-value"><span class="badge ${c.sentiment?.toLowerCase()}">${c.sentiment || 'N/A'}</span></div>
            </div>
        </div>
        
        <div style="padding: var(--space-md); background: var(--bg-glass); border-radius: var(--radius-md); margin-bottom: var(--space-lg);">
            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">Description</div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.7;">${escapeHtml(c.description)}</p>
        </div>
        
        ${aiAnalysis.impact_assessment ? `
        <div style="padding: var(--space-md); background: rgba(99,102,241,0.08); border-radius: var(--radius-md); border: 1px solid rgba(99,102,241,0.15); margin-bottom: var(--space-lg);">
            <div style="font-size: 0.75rem; color: var(--accent-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">🤖 AI Impact Assessment</div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">${aiAnalysis.impact_assessment}</p>
        </div>
        ` : ''}
        
        ${recommendations.length > 0 ? `
        <div>
            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">AI Recommendations</div>
            <ul class="recommendations-list">
                ${recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
    `;
    
    openModal('complaintModal');
}

async function analyzeExistingComplaint(trackingId) {
    const complaint = state.complaints.find(c => c.tracking_id === trackingId);
    if (!complaint) return;
    
    showToast('🤖 Running AI analysis...', 'info');
    
    const result = await api.post('/api/complaints/analyze', {
        title: complaint.title,
        description: complaint.description,
        category: complaint.category,
        location: complaint.location,
        complaint_id: trackingId,
    });
    
    if (result.success) {
        showToast('AI analysis complete!', 'success');
        renderAnalysisPanel(result.analysis);
        await loadComplaints();
    } else {
        showToast('Analysis failed', 'error');
    }
}

function renderAnalysisPanel(analysis) {
    const panel = document.getElementById('analysis-panel');
    if (!panel) return;
    
    panel.classList.remove('hidden');
    panel.innerHTML = `
        <div class="analysis-header">
            <span class="ai-badge">🤖 AI Powered</span>
            <h3>Complaint Analysis Report</h3>
            <span style="margin-left: auto; font-size: 0.75rem; color: var(--text-muted);">Source: ${analysis.source || 'AI Engine'}</span>
        </div>
        
        <div class="analysis-metrics">
            <div class="analysis-metric">
                <div class="metric-label">Severity</div>
                <div class="metric-value" style="color: ${getSeverityColor(analysis.severity)}">${analysis.severity}</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">Score: ${analysis.severity_score}/10</div>
            </div>
            <div class="analysis-metric">
                <div class="metric-label">Sentiment</div>
                <div class="metric-value" style="color: ${getSentimentColor(analysis.sentiment)}">${analysis.sentiment}</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">Score: ${analysis.sentiment_score}</div>
            </div>
            <div class="analysis-metric">
                <div class="metric-label">Priority</div>
                <div class="metric-value" style="color: ${getSeverityColor(analysis.priority)}">${analysis.priority}</div>
            </div>
            <div class="analysis-metric">
                <div class="metric-label">Department</div>
                <div class="metric-value" style="font-size: 1rem;">${analysis.department}</div>
            </div>
            <div class="analysis-metric">
                <div class="metric-label">Urgency</div>
                <div class="metric-value" style="font-size: 0.95rem;">${analysis.urgency}</div>
            </div>
            <div class="analysis-metric">
                <div class="metric-label">Est. Resolution</div>
                <div class="metric-value" style="font-size: 0.95rem;">${analysis.estimated_resolution_time || 'N/A'}</div>
            </div>
        </div>
        
        ${analysis.impact_assessment ? `
        <div style="padding: var(--space-md); background: var(--bg-glass); border-radius: var(--radius-md); margin-bottom: var(--space-lg); border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.75rem; color: var(--accent-secondary); margin-bottom: 6px; font-weight: 600;">IMPACT ASSESSMENT</div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">${analysis.impact_assessment}</p>
            ${analysis.affected_population_estimate ? `<div style="margin-top: 6px; font-size: 0.78rem; color: var(--text-muted);">Estimated affected population: <strong style="color: var(--accent-amber);">${analysis.affected_population_estimate}</strong></div>` : ''}
        </div>
        ` : ''}
        
        <div style="margin-bottom: var(--space-md);">
            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: var(--space-sm); font-weight: 600;">AI Recommendations</div>
            <ul class="recommendations-list">
                ${(analysis.recommendations || []).map(r => `<li>${escapeHtml(r)}</li>`).join('')}
            </ul>
        </div>
        
        ${analysis.similar_patterns ? `
        <div style="padding: var(--space-md); background: rgba(245,158,11,0.08); border-radius: var(--radius-md); border: 1px solid rgba(245,158,11,0.15);">
            <div style="font-size: 0.75rem; color: var(--accent-amber); margin-bottom: 4px; font-weight: 600;">⚠️ PATTERN DETECTED</div>
            <p style="font-size: 0.82rem; color: var(--text-secondary);">${analysis.similar_patterns}</p>
        </div>
        ` : ''}
    `;
    
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ═══════════════════════════════════════════════════
// Emergency Alerts
// ═══════════════════════════════════════════════════

async function loadAlerts() {
    const result = await api.get('/api/alerts');
    if (!result.success) return showToast('Failed to load alerts', 'error');
    
    state.alerts = result.data;
    renderAlerts(result.data);
}

function renderAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    if (!container) return;
    
    const activeAlerts = alerts.filter(a => a.is_active);
    const inactiveAlerts = alerts.filter(a => !a.is_active);
    
    if (alerts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🛡️</div>
                <h4>No Active Alerts</h4>
                <p>All clear! No emergency alerts at this time.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        ${activeAlerts.length > 0 ? `
            <div class="section-header">
                <h3>🔴 Active Alerts (${activeAlerts.length})</h3>
            </div>
            ${activeAlerts.map(a => renderAlertCard(a)).join('')}
        ` : ''}
        
        ${inactiveAlerts.length > 0 ? `
            <div class="section-header mt-lg">
                <h3 style="color: var(--text-muted);">📋 Past Alerts (${inactiveAlerts.length})</h3>
            </div>
            ${inactiveAlerts.map(a => renderAlertCard(a)).join('')}
        ` : ''}
    `;
}

function renderAlertCard(alert) {
    let dosAndDonts = {};
    let contacts = [];
    try { dosAndDonts = JSON.parse(alert.dos_and_donts || '{}'); } catch(e) {}
    try { contacts = JSON.parse(alert.emergency_contacts || '[]'); } catch(e) {}
    
    return `
        <div class="alert-card ${alert.severity?.toLowerCase()}" style="${!alert.is_active ? 'opacity: 0.6;' : ''}">
            <div class="alert-card-header">
                <h4>${alert.title}</h4>
                <div class="flex gap-sm">
                    <span class="badge ${alert.severity?.toLowerCase()}">${alert.severity}</span>
                    ${alert.is_active ? '<span class="badge critical" style="animation: pulse 2s infinite;">ACTIVE</span>' : '<span class="badge" style="background: rgba(100,116,139,0.15); color: var(--text-muted);">EXPIRED</span>'}
                </div>
            </div>
            
            <div class="alert-card-body">${escapeHtml(alert.description)}</div>
            
            <div class="alert-meta">
                <span>📍 ${alert.affected_zones || 'All Zones'}</span>
                <span>🏢 ${alert.issued_by || 'System'}</span>
                <span>🕐 ${timeAgo(alert.created_at)}</span>
                ${alert.expires_at ? `<span>⏰ Expires: ${formatDateTime(alert.expires_at)}</span>` : ''}
            </div>
            
            ${dosAndDonts.dos || dosAndDonts.donts ? `
            <div class="guidance-grid">
                ${dosAndDonts.dos ? `
                <div class="guidance-card dos">
                    <h5>✅ Do's</h5>
                    <ul>${dosAndDonts.dos.map(d => `<li>${escapeHtml(d)}</li>`).join('')}</ul>
                </div>
                ` : ''}
                ${dosAndDonts.donts ? `
                <div class="guidance-card donts">
                    <h5>❌ Don'ts</h5>
                    <ul>${dosAndDonts.donts.map(d => `<li>${escapeHtml(d)}</li>`).join('')}</ul>
                </div>
                ` : ''}
            </div>
            ` : ''}
            
            ${contacts.length > 0 ? `
            <div class="contacts-grid">
                ${contacts.map(c => `
                    <div class="contact-card">
                        <div class="contact-icon">📞</div>
                        <div>
                            <div class="contact-name">${c.name}</div>
                            <div class="contact-number">${c.number}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
            ` : ''}
        </div>
    `;
}

async function submitAlert(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> Creating...';
    
    const data = {
        title: form.querySelector('#alert-title').value,
        description: form.querySelector('#alert-description').value,
        alert_type: form.querySelector('#alert-type').value,
        severity: form.querySelector('#alert-severity').value,
        affected_zones: form.querySelector('#alert-zones').value,
        issued_by: form.querySelector('#alert-issuer').value || 'System',
    };
    
    const result = await api.post('/api/alerts', data);
    
    if (result.success) {
        showToast('Emergency alert created with AI-generated safety guidance!', 'success');
        form.reset();
        await loadAlerts();
        // Refresh ticker
        const dashboard = await api.get('/api/dashboard');
        if (dashboard.success) renderTicker(dashboard.data.active_alerts);
    } else {
        showToast('Failed to create alert', 'error');
    }
    
    submitBtn.disabled = false;
    submitBtn.innerHTML = '🚨 Issue Alert';
}

// ═══════════════════════════════════════════════════
// Community Insights
// ═══════════════════════════════════════════════════

async function loadInsights() {
    // Insights content is mostly driven by the AI chat in the query bar
    // But we can load predictions
    await loadPredictions();
}

async function loadPredictions() {
    const container = document.getElementById('predictions-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading-overlay"><div class="spinner spinner-lg"></div><p>Generating AI predictions...</p></div>';
    
    const result = await api.post('/api/predict', {});
    
    if (result.success) {
        const p = result.predictions;
        container.innerHTML = `
            <div class="prediction-grid">
                <div class="prediction-card">
                    <h4>📊 7-Day Complaint Forecast</h4>
                    <div class="prediction-value text-primary">${p.complaint_forecast_7d}</div>
                    <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: var(--space-sm);">Expected complaints in next 7 days</p>
                </div>
                <div class="prediction-card">
                    <h4>📈 30-Day Complaint Forecast</h4>
                    <div class="prediction-value text-amber">${p.complaint_forecast_30d}</div>
                    <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: var(--space-sm);">Expected complaints in next 30 days</p>
                </div>
                <div class="prediction-card">
                    <h4>🏘️ Wellbeing Forecast</h4>
                    <div class="prediction-value text-emerald">${p.wellbeing_forecast}/100</div>
                    <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: var(--space-sm);">Projected community wellbeing score</p>
                </div>
            </div>
            
            <div class="glass-card mt-lg">
                <div class="card-header">
                    <h3>🔥 Trending Categories</h3>
                </div>
                <div class="card-body">
                    <div class="flex gap-sm" style="flex-wrap: wrap;">
                        ${p.trending_categories.map(c => `<span class="badge medium">${c}</span>`).join('')}
                    </div>
                </div>
            </div>
            
            <div class="glass-card mt-lg">
                <div class="card-header">
                    <h3>⚠️ Risk Areas</h3>
                </div>
                <div class="card-body">
                    <ul class="recommendations-list">
                        ${p.risk_areas.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="glass-card mt-lg">
                <div class="card-header">
                    <h3>💡 Key Insights</h3>
                </div>
                <div class="card-body">
                    <ul class="recommendations-list">
                        ${p.key_insights.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="glass-card mt-lg">
                <div class="card-header">
                    <h3>🎯 Recommended Actions</h3>
                </div>
                <div class="card-body">
                    <ul class="recommendations-list">
                        ${p.recommended_actions.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">📊</div><h4>Could not load predictions</h4></div>`;
    }
}

async function queryInsights(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById('insights-query');
    if (!input || !input.value.trim()) return;
    
    const query = input.value.trim();
    const resultContainer = document.getElementById('insights-result');
    
    resultContainer.innerHTML = '<div class="loading-overlay"><div class="spinner"></div><p>Analyzing...</p></div>';
    resultContainer.classList.remove('hidden');
    
    const result = await api.post('/api/chat', { message: query, session_id: 'insights-' + Date.now() });
    
    if (result.success) {
        resultContainer.innerHTML = `
            <div class="report-content">
                ${markdownToHtml(result.response)}
            </div>
        `;
    } else {
        resultContainer.innerHTML = '<p style="color: var(--accent-rose);">Failed to process query</p>';
    }
}

// ═══════════════════════════════════════════════════
// AI Chat
// ═══════════════════════════════════════════════════

function initChat() {
    const messagesEl = document.getElementById('chat-messages');
    if (!messagesEl) return;
    
    if (state.chatMessages.length === 0) {
        // Welcome message
        state.chatMessages.push({
            role: 'assistant',
            message: `👋 Hello! I'm **CommunityPulse AI**, your intelligent assistant for community decision-making.

I can help you with:
- 📊 **Community data analysis** — "What are the top issues?"
- 📈 **Predictions & forecasting** — "Predict next week's complaints"
- ⏱️ **Performance metrics** — "How fast are complaints resolved?"
- 🚨 **Emergency information** — "Any active emergencies?"
- 🏘️ **Wellbeing assessment** — "Community wellbeing score"
- 🌍 **Impact tracking** — "Social impact report"

Ask me anything about your community!`,
        });
        renderChatMessages();
    }
}

function renderChatMessages() {
    const messagesEl = document.getElementById('chat-messages');
    if (!messagesEl) return;
    
    messagesEl.innerHTML = state.chatMessages.map(msg => `
        <div class="chat-message ${msg.role}">
            <div class="chat-avatar">${msg.role === 'assistant' ? '🤖' : '👤'}</div>
            <div class="chat-bubble">${markdownToHtml(msg.message)}</div>
        </div>
    `).join('');
    
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendChatMessage(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById('chat-input');
    if (!input || !input.value.trim()) return;
    
    const message = input.value.trim();
    input.value = '';
    
    // Add user message
    state.chatMessages.push({ role: 'user', message });
    renderChatMessages();
    
    // Add typing indicator
    state.chatMessages.push({ role: 'assistant', message: '⏳ *Thinking...*' });
    renderChatMessages();
    
    // Get response
    const result = await api.post('/api/chat', {
        message,
        session_id: state.chatSessionId,
    });
    
    // Remove typing indicator
    state.chatMessages.pop();
    
    if (result.success) {
        state.chatMessages.push({ role: 'assistant', message: result.response });
    } else {
        state.chatMessages.push({ role: 'assistant', message: '❌ Sorry, I encountered an error processing your request. Please try again.' });
    }
    
    renderChatMessages();
}

function useChatSuggestion(text) {
    const input = document.getElementById('chat-input');
    if (input) {
        input.value = text;
        input.focus();
    }
}

// ═══════════════════════════════════════════════════
// Reports & Impact
// ═══════════════════════════════════════════════════

async function loadReports() {
    await loadImpactMetrics();
}

async function loadImpactMetrics() {
    const result = await api.get('/api/impact');
    if (!result.success) return;
    
    const container = document.getElementById('impact-container');
    if (!container) return;
    
    container.innerHTML = result.data.map(init => {
        const utilization = Math.round((init.budget_utilized / Math.max(init.budget_allocated, 1)) * 100);
        return `
            <div class="impact-card">
                <div class="impact-card-header">
                    <div>
                        <h4>${init.initiative_name}</h4>
                        <span class="badge ${init.status === 'Active' ? 'open' : 'resolved'}" style="margin-top: 4px;">${init.status}</span>
                    </div>
                    <div class="impact-score">${init.impact_score}</div>
                </div>
                <div class="impact-description">${init.description}</div>
                <div class="impact-stats">
                    <div class="impact-stat">
                        <div class="impact-stat-label">Beneficiaries</div>
                        <div class="impact-stat-value">${formatNumber(init.beneficiaries)}</div>
                    </div>
                    <div class="impact-stat">
                        <div class="impact-stat-label">Category</div>
                        <div class="impact-stat-value" style="font-size: 0.82rem;">${init.category}</div>
                    </div>
                    <div class="impact-stat">
                        <div class="impact-stat-label">Budget Allocated</div>
                        <div class="impact-stat-value">₹${formatNumber(init.budget_allocated)}</div>
                    </div>
                    <div class="impact-stat">
                        <div class="impact-stat-label">Utilized</div>
                        <div class="impact-stat-value">${utilization}%</div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: ${utilization}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

async function generateReport() {
    const container = document.getElementById('report-output');
    const btn = document.getElementById('btn-generate-report');
    
    if (!container || !btn) return;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> Generating...';
    
    container.innerHTML = '<div class="loading-overlay"><div class="spinner spinner-lg"></div><p>AI is generating your community report...</p></div>';
    container.classList.remove('hidden');
    
    const reportType = document.getElementById('report-type')?.value || 'Weekly Community Report';
    const result = await api.post('/api/reports/generate', { report_type: reportType });
    
    if (result.success) {
        container.innerHTML = `<div class="report-content">${markdownToHtml(result.report)}</div>`;
        showToast('Report generated successfully!', 'success');
    } else {
        container.innerHTML = '<p style="color: var(--accent-rose); padding: 24px;">Failed to generate report</p>';
    }
    
    btn.disabled = false;
    btn.innerHTML = '📊 Generate Report';
}

// ═══════════════════════════════════════════════════
// Modals
// ═══════════════════════════════════════════════════

function openModal(modalId) {
    document.getElementById(modalId)?.classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId)?.classList.remove('active');
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

// ═══════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════

function animateCounter(elementId, target, hasDecimal = false) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    const start = 0;
    const duration = 1200;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = start + (target - start) * eased;
        
        el.textContent = hasDecimal ? current.toFixed(1) : Math.round(current);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function timeAgo(dateStr) {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatNumber(num) {
    if (num >= 10000000) return (num / 10000000).toFixed(1) + ' Cr';
    if (num >= 100000) return (num / 100000).toFixed(1) + ' L';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
}

function getSeverityColor(severity) {
    const colors = {
        'Critical': '#ef4444', 'High': '#f59e0b',
        'Medium': '#6366f1', 'Low': '#10b981',
    };
    return colors[severity] || '#94a3b8';
}

function getSentimentColor(sentiment) {
    const colors = {
        'Negative': '#ef4444', 'Frustrated': '#ef4444',
        'Concerned': '#f59e0b', 'Neutral': '#94a3b8',
        'Positive': '#10b981', 'Urgent': '#ef4444',
    };
    return colors[sentiment] || '#94a3b8';
}

function getSeverityBgColor(severity) {
    const colors = {
        'Critical': 'rgba(239,68,68,0.15)', 'High': 'rgba(245,158,11,0.15)',
        'Medium': 'rgba(99,102,241,0.15)', 'Low': 'rgba(16,185,129,0.15)',
    };
    return colors[severity] || 'rgba(100,116,139,0.15)';
}

function getCategoryIcon(category) {
    const icons = {
        'Infrastructure': '🏗️', 'Public Health': '🏥', 'Healthcare': '⚕️',
        'Sanitation': '🧹', 'Transportation': '🚦', 'Environment': '🌿',
        'Public Spaces': '🏞️', 'Safety': '🛡️', 'Education': '📚',
        'General': '📌',
    };
    return icons[category] || '📌';
}

function markdownToHtml(text) {
    if (!text) return '';
    
    return text
        // Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // Bold and italic
        .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Code
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Tables
        .replace(/^\|(.+)\|$/gm, function(match) {
            const cells = match.split('|').filter(c => c.trim());
            if (cells.every(c => /^[\s-:]+$/.test(c))) return ''; // separator row
            const tag = 'td';
            return '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
        })
        .replace(/(<tr>.*<\/tr>\n?)+/g, '<table>$&</table>')
        // Horizontal rules
        .replace(/^---$/gm, '<hr>')
        // Line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        // Wrap in paragraph
        .replace(/^(?!<[htp1-6rua])(.+)/gm, '<p>$1</p>')
        // Clean up empty paragraphs
        .replace(/<p><\/p>/g, '')
        .replace(/<p><br><\/p>/g, '');
}

// ═══════════════════════════════════════════════════
// Initialize App
// ═══════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // Set up navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => navigateTo(item.dataset.page));
    });
    
    // Mobile menu toggle
    const menuToggle = document.getElementById('mobile-menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            document.querySelector('.sidebar')?.classList.toggle('open');
        });
    }
    
    // Chat input — submit on Enter
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    // Insights query — submit on Enter
    const insightsInput = document.getElementById('insights-query');
    if (insightsInput) {
        insightsInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                queryInsights();
            }
        });
    }
    
    // Load initial page
    navigateTo('dashboard');
    
    console.log('%c🏛️ CommunityPulse AI v1.0.0', 'color: #6366f1; font-size: 16px; font-weight: bold;');
    console.log('%cAI-Powered Decision Intelligence Platform', 'color: #94a3b8; font-size: 12px;');
});
