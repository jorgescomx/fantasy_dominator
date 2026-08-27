// NFL Fantasy Dominator - Frontend Client Controller

const API_BASE = '/api/v1';
const USER_TEAM_STORAGE_KEY = 'fantasy_dominator_user_team_id';

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function encodedPlayerId(playerId) {
    return encodeURIComponent(String(playerId ?? ''));
}

let currentPosFilter = 'ALL';
let currentTeamFilter = 'ALL';
let currentSearchQuery = '';
let currentOptimizationMode = 'balanced';
let cachedPlayers = [];
let allRosterPlayers = [];
let cachedDraftBoard = [];
let leagueTeams = [];

// --- User Team Preference Helpers ---
function getSelectedTeamId() {
    const saved = localStorage.getItem(USER_TEAM_STORAGE_KEY);
    if (saved) {
        const parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed > 0) {
            return parsed;
        }
    }
    return null;
}

function getActiveTeamObject() {
    const activeId = getSelectedTeamId();
    if (leagueTeams && leagueTeams.length > 0) {
        if (activeId !== null) {
            const found = leagueTeams.find(t => t.id === activeId);
            if (found) return found;
        }
        return leagueTeams[0];
    }
    return null;
}

async function setSelectedTeamId(teamId, refreshData = true) {
    const idNum = parseInt(teamId, 10);
    if (isNaN(idNum) || idNum <= 0) return;
    
    localStorage.setItem(USER_TEAM_STORAGE_KEY, idNum.toString());
    updateTeamUI(idNum);

    // Sync draft engine pick with selected team
    try {
        await fetch(`${API_BASE}/draft/reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_pick: idNum })
        });
    } catch (err) {
        console.error('Error syncing draft user pick:', err);
    }

    if (refreshData) {
        await loadDraftState();
        await loadLineupOptimization();
        await loadWaiverRadar();
        await loadLeagueOverview();
    }
}

function updateTeamUI(activeId) {
    const team = (leagueTeams || []).find(t => t.id === activeId) || { id: activeId, name: `Team ${activeId}`, owner: 'Manager' };
    const ownerStr = team.owner && team.owner !== 'Manager' ? ` (${team.owner})` : '';
    const displayLabel = `${team.name}${ownerStr}`;

    // Update Header Pill
    const headerTeamName = document.getElementById('header-user-team-name');
    if (headerTeamName) {
        headerTeamName.textContent = `My Team: ${displayLabel}`;
    }

    // Update Settings Active Badge
    const settingsBadge = document.getElementById('settings-active-team-badge');
    if (settingsBadge) {
        settingsBadge.textContent = `Active: #${team.id} ${team.name}`;
    }

    // Update Lineup & Waiver labels
    const lineupTeamName = document.getElementById('lineup-user-team-name');
    if (lineupTeamName) {
        lineupTeamName.textContent = team.name;
    }
    const waiverTeamName = document.getElementById('waiver-user-team-name');
    if (waiverTeamName) {
        waiverTeamName.textContent = team.name;
    }

    // Update Dropdown Values without triggering onchange loop
    const draftSelect = document.getElementById('user-team-select');
    if (draftSelect && parseInt(draftSelect.value) !== activeId) {
        draftSelect.value = activeId;
    }

    const settingsSelect = document.getElementById('settings-user-team-select');
    if (settingsSelect && parseInt(settingsSelect.value) !== activeId) {
        settingsSelect.value = activeId;
    }

    // Update Details Box in Settings
    renderSelectedTeamDetails(team);
}

function renderSelectedTeamDetails(team) {
    const detailsBox = document.getElementById('selected-team-details');
    if (!detailsBox) return;

    if (!team) {
        detailsBox.innerHTML = `<div style="font-size: 0.85rem; color: var(--text-muted);">No team selected yet.</div>`;
        return;
    }

    const standingText = team.standing ? `#${team.standing}` : 'N/A';
    const recordText = (team.wins !== undefined && team.losses !== undefined) ? `${team.wins}-${team.losses}` : '0-0';
    const pointsText = team.points_for ? `${team.points_for} pts` : '0.0 pts';

    detailsBox.innerHTML = `
        <div class="selected-team-info">
            <div class="selected-team-info-name">⚡ #${escapeHtml(team.id)} ${escapeHtml(team.name)}</div>
            <div class="selected-team-info-meta">Owner: <strong>${escapeHtml(team.owner || 'Manager')}</strong> • Team ID: #${escapeHtml(team.id)}</div>
        </div>
        <div class="selected-team-stats">
            <div class="selected-team-stat-item">
                <span class="selected-team-stat-val">${standingText}</span>
                <span class="selected-team-stat-lbl">Standing</span>
            </div>
            <div class="selected-team-stat-item">
                <span class="selected-team-stat-val">${recordText}</span>
                <span class="selected-team-stat-lbl">Record</span>
            </div>
            <div class="selected-team-stat-item">
                <span class="selected-team-stat-val">${pointsText}</span>
                <span class="selected-team-stat-lbl">Total Pts</span>
            </div>
        </div>
    `;
}

function populateAllTeamSelectors(teams) {
    if (!teams || teams.length === 0) return;
    leagueTeams = teams;

    let activeId = getSelectedTeamId();
    if (activeId === null || !teams.some(t => t.id === activeId)) {
        activeId = teams[0].id;
        localStorage.setItem(USER_TEAM_STORAGE_KEY, activeId.toString());
    }

    const selectElements = [
        document.getElementById('user-team-select'),
        document.getElementById('settings-user-team-select')
    ];

    selectElements.forEach(select => {
        if (!select) return;
        select.innerHTML = '';
        teams.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            const ownerText = t.owner && t.owner !== 'Manager' ? ` (${t.owner})` : '';
            opt.textContent = `#${t.id} ${t.name}${ownerText}`;
            if (t.id === activeId) {
                opt.selected = true;
            }
            select.appendChild(opt);
        });
    });

    updateTeamUI(activeId);
}

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDraftAssistant();
    initLineupOptimizer();
    initWaiverRadar();
    initESPNSync();
    initRefreshButton();

    // Initial Load
    initPlayerModal();
    refreshAllData();
});

document.addEventListener('click', (event) => {
    const draftButton = event.target.closest('[data-draft-player]');
    if (draftButton) {
        event.stopPropagation();
        draftPlayer(decodeURIComponent(draftButton.dataset.draftPlayer));
    }
});

// --- Tab Navigation ---
function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetId = tab.dataset.tab;
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// --- Refresh Button Handler ---
function initRefreshButton() {
    const refreshBtn = document.getElementById('btn-refresh-data');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', handleRefreshData);
    }
}

async function handleRefreshData() {
    const refreshBtn = document.getElementById('btn-refresh-data');
    refreshBtn.classList.add('loading');
    refreshBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/refresh/teams-and-players`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const result = await response.json();
            showNotification('✓ Teams and players refreshed successfully!', 'success');
            await refreshAllData();
        } else {
            showNotification('✗ Refresh failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Refresh error:', error);
        showNotification('✗ Network error. Please try again.', 'error');
    } finally {
        refreshBtn.classList.remove('loading');
        refreshBtn.disabled = false;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 18px;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 600;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;

    if (type === 'success') {
        notification.style.background = 'rgba(16, 185, 129, 0.2)';
        notification.style.color = '#10b981';
        notification.style.border = '1px solid rgba(16, 185, 129, 0.3)';
    } else if (type === 'error') {
        notification.style.background = 'rgba(244, 63, 94, 0.2)';
        notification.style.color = '#f43f5e';
        notification.style.border = '1px solid rgba(244, 63, 94, 0.3)';
    }

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// --- Injury Badge Helper ---
function getInjuryBadgeHtml(status, inline = true) {
    if (!status || status.toUpperCase() === 'ACTIVE') return '';
    const st = status.toUpperCase();
    let badgeClass = 'injury-q';
    let text = st;
    if (['QUESTIONABLE', 'Q'].includes(st)) {
        badgeClass = 'injury-q';
        text = 'Q';
    } else if (['DOUBTFUL', 'D'].includes(st)) {
        badgeClass = 'injury-d';
        text = 'D';
    } else if (['OUT', 'O'].includes(st)) {
        badgeClass = 'injury-out';
        text = 'OUT';
    } else if (st === 'IR') {
        badgeClass = 'injury-ir';
        text = 'IR';
    } else if (st === 'PUP') {
        badgeClass = 'injury-pup';
        text = 'PUP';
    } else {
        badgeClass = 'injury-out';
        text = st;
    }
    const cls = inline ? `injury-inline-badge ${badgeClass}` : `injury-badge ${badgeClass}`;
    return `<span class="${cls}" title="Injury Status: ${st}">${text}</span>`;
}

// --- Player Rating Explanation Modal ---
let currentModalPlayerId = null;

function initPlayerModal() {
    const modal = document.getElementById('player-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const draftBtn = document.getElementById('modal-draft-btn');

    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    draftBtn.addEventListener('click', async () => {
        if (currentModalPlayerId) {
            modal.classList.add('hidden');
            await window.draftPlayer(currentModalPlayerId);
        }
    });
}

window.showPlayerExplanation = async function(playerId) {
    currentModalPlayerId = playerId;
    const modal = document.getElementById('player-modal');

    try {
        const res = await fetch(`${API_BASE}/players/${playerId}/rating-breakdown`);
        if (!res.ok) {
            alert('Failed to load rating breakdown');
            return;
        }
        const data = await res.json();
        const p = data.player;

        // Header info
        document.getElementById('modal-pos-badge').textContent = p.position;
        document.getElementById('modal-team-tag').textContent = p.team;
        
        const tierBadge = document.getElementById('modal-tier-badge');
        tierBadge.textContent = `Tier ${p.tier}`;
        tierBadge.className = `tier-badge tier-${Math.min(p.tier, 3)}`;

        // Injury status badge in modal
        const injuryBadge = document.getElementById('modal-injury-badge');
        if (injuryBadge) {
            const inj = (p.injury_status && p.injury_status.toUpperCase() !== 'ACTIVE') ? p.injury_status.toUpperCase() : '';
            if (inj) {
                injuryBadge.classList.remove('hidden', 'injury-q', 'injury-d', 'injury-out', 'injury-ir', 'injury-pup');
                let badgeClass = 'injury-q';
                let text = inj;
                if (['QUESTIONABLE', 'Q'].includes(inj)) { badgeClass = 'injury-q'; text = 'QUESTIONABLE'; }
                else if (['DOUBTFUL', 'D'].includes(inj)) { badgeClass = 'injury-d'; text = 'DOUBTFUL'; }
                else if (inj === 'IR') { badgeClass = 'injury-ir'; text = 'INJURED RESERVE (IR)'; }
                else if (inj === 'PUP') { badgeClass = 'injury-pup'; text = 'PUP LIST'; }
                else { badgeClass = 'injury-out'; text = 'OUT'; }
                injuryBadge.classList.add(badgeClass);
                injuryBadge.textContent = text;
            } else {
                injuryBadge.classList.add('hidden');
            }
        }

        document.getElementById('modal-player-name').textContent = p.name;
        document.getElementById('modal-player-archetype').textContent = p.archetype || 'Key Starter';

        // Stats grid
        document.getElementById('modal-vorp-val').textContent = `+${data.vorp_points}`;
        document.getElementById('modal-vorp-sub').textContent = `+${data.vorp_per_week} / week`;
        document.getElementById('modal-pos-rank').textContent = `#${data.position_rank} ${p.position}`;
        document.getElementById('modal-cutoff-sub').textContent = `vs #${data.baseline_threshold} Cutoff`;
        document.getElementById('modal-xfp-val').textContent = p.xfp;
        document.getElementById('modal-season-pts').textContent = p.projected_season;

        // Dedicated Injury Intelligence & Availability Card
        const injuryCard = document.getElementById('modal-injury-card');
        if (injuryCard) {
            if (data.injury_info) {
                injuryCard.classList.remove('hidden', 'injury-severe');
                const info = data.injury_info;
                const statusPill = document.getElementById('modal-injury-status-pill');
                if (statusPill) {
                    statusPill.className = 'injury-badge';
                    let stClass = 'injury-q';
                    if (['QUESTIONABLE', 'Q'].includes(info.status)) stClass = 'injury-q';
                    else if (['DOUBTFUL', 'D'].includes(info.status)) stClass = 'injury-d';
                    else if (info.status === 'IR') stClass = 'injury-ir';
                    else if (info.status === 'PUP') stClass = 'injury-pup';
                    else stClass = 'injury-out';
                    
                    statusPill.classList.add(stClass);
                    statusPill.textContent = info.status;
                }

                if (['OUT', 'IR', 'PUP', 'DOUBTFUL'].includes(info.status)) {
                    injuryCard.classList.add('injury-severe');
                }

                document.getElementById('modal-injury-type').textContent = info.type || 'Injury Maintenance';
                document.getElementById('modal-injury-timeline').textContent = info.time_away || 'Day-to-day';
                document.getElementById('modal-injury-notes').textContent = info.notes || '';
                document.getElementById('modal-injury-impact').textContent = info.impact_summary || '';
            } else {
                injuryCard.classList.add('hidden');
            }
        }

        // Scouting Takeaway
        document.getElementById('modal-scouting-text').textContent = data.scouting_takeaway;

        // Metrics list
        const metricsContainer = document.getElementById('modal-metrics-list');
        metricsContainer.innerHTML = '';

        data.metrics.forEach(m => {
            const row = document.createElement('div');
            row.className = 'metric-row';
            row.innerHTML = `
                <div class="metric-row-header">
                    <span class="metric-title">${escapeHtml(m.metric)}</span>
                    <div class="metric-badges">
                        <span class="metric-val-tag">${escapeHtml(m.value)}</span>
                        <span class="metric-rating-tag">${escapeHtml(m.rating)}</span>
                    </div>
                </div>
                <div class="metric-desc">${escapeHtml(m.explanation)}</div>
            `;
            metricsContainer.appendChild(row);
        });

        // Show Modal
        modal.classList.remove('hidden');

    } catch (e) {
        console.error('Error fetching player breakdown:', e);
    }
};

// --- Refresh Core Data ---
async function refreshAllData() {
    await loadLeagueOverview();
    await loadDraftState();
    await loadLineupOptimization();
    await loadWaiverRadar();
}

// --- TAB 1: LIVE DRAFT ASSISTANT ---
let currentSortColumn = null;
let currentSortDirection = 'asc';

function initDraftAssistant() {
    // Positional Filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPosFilter = btn.dataset.pos;
            renderVORPBoard(cachedDraftBoard);
        });
    });

    // Team Filter Dropdown
    const teamFilter = document.getElementById('draft-team-filter');
    if (teamFilter) {
        teamFilter.addEventListener('change', (e) => {
            currentTeamFilter = e.target.value;
            if (currentTeamFilter !== 'ALL') {
                teamFilter.classList.add('active-filter');
            } else {
                teamFilter.classList.remove('active-filter');
            }
            renderVORPBoard(cachedDraftBoard);
        });
    }

    // Search Input
    const searchInput = document.getElementById('draft-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchQuery = e.target.value.toLowerCase().trim();
            renderVORPBoard(cachedDraftBoard);
        });
    }

    // Column Header Sorting
    const sortableHeaders = document.querySelectorAll('.vorp-table th.sortable');
    sortableHeaders.forEach(th => {
        th.addEventListener('click', () => {
            const col = th.dataset.sort;
            if (currentSortColumn === col) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = col;
                // Default high-to-low for stats like VORP, xFP, Proj; low-to-high for Tier & Name
                if (['vorp', 'xfp', 'projected_season', 'need'].includes(col)) {
                    currentSortDirection = 'desc';
                } else {
                    currentSortDirection = 'asc';
                }
            }

            // Update UI sort indicators
            sortableHeaders.forEach(h => {
                h.classList.remove('sorted-asc', 'sorted-desc');
            });
            th.classList.add(currentSortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');

            renderVORPBoard(cachedDraftBoard);
        });
    });

    // Undo Pick
    document.getElementById('btn-undo-pick').addEventListener('click', async () => {
        try {
            const res = await fetch(`${API_BASE}/draft/undo`, { method: 'POST' });
            if (res.ok) {
                await loadDraftState();
            } else {
                const err = await res.json();
                alert(err.detail || 'Failed to undo pick');
            }
        } catch (e) {
            console.error(e);
        }
    });

    // Draft Team Dropdown Listener
    const teamSelect = document.getElementById('user-team-select');
    if (teamSelect) {
        teamSelect.addEventListener('change', async (e) => {
            const newPickSlot = parseInt(e.target.value, 10);
            await setSelectedTeamId(newPickSlot, true);
            const team = getActiveTeamObject();
            showNotification(`✓ Active team set to: ${team ? team.name : 'Team ' + newPickSlot}`, 'success');
        });
    }

    // Live ESPN Draft Sync Button
    const syncEspnBtn = document.getElementById('btn-sync-espn-draft');
    if (syncEspnBtn) {
        syncEspnBtn.addEventListener('click', async () => {
            syncEspnBtn.disabled = true;
            syncEspnBtn.textContent = '⏳ Syncing...';
            try {
                const res = await fetch(`${API_BASE}/draft/sync-espn`, { method: 'POST' });
                const data = await res.json();
                if (data.sync_stats && data.sync_stats.new_picks_count > 0) {
                    showNotification(`⚡ Synced ${data.sync_stats.new_picks_count} new pick(s) from ESPN!`, 'success');
                } else {
                    showNotification('✓ Up to date with ESPN draft room', 'info');
                }
                await loadDraftState();
            } catch (e) {
                console.error(e);
            } finally {
                syncEspnBtn.disabled = false;
                syncEspnBtn.textContent = '⚡ Sync ESPN';
            }
        });
    }

    // Auto-Sync Toggle (Every 3 seconds)
    let autoSyncInterval = null;
    const autoSyncBtn = document.getElementById('btn-toggle-auto-sync');
    let isAutoSyncEnabled = false;

    function startAutoSync() {
        if (autoSyncInterval) clearInterval(autoSyncInterval);
        autoSyncInterval = setInterval(async () => {
            const draftTab = document.getElementById('draft-tab');
            if (draftTab && draftTab.classList.contains('active') && isAutoSyncEnabled) {
                try {
                    const res = await fetch(`${API_BASE}/draft/sync-espn`, { method: 'POST' });
                    const data = await res.json();
                    if (data.sync_stats && data.sync_stats.new_picks_count > 0) {
                        showNotification(`⚡ ${data.sync_stats.new_picks_count} new pick(s) synced from ESPN!`, 'success');
                        await loadDraftState();
                    }
                } catch (err) {
                    // silently pass
                }
            }
        }, 3000);
    }

    if (autoSyncBtn) {
        // Off by default to allow clean mock drafting/testing
        autoSyncBtn.textContent = '⚪ Auto-Sync: OFF';
        autoSyncBtn.style.background = 'rgba(255, 255, 255, 0.05)';
        autoSyncBtn.style.color = 'var(--text-muted)';

        autoSyncBtn.addEventListener('click', () => {
            isAutoSyncEnabled = !isAutoSyncEnabled;
            if (isAutoSyncEnabled) {
                autoSyncBtn.textContent = '🟢 Auto-Sync: ON (3s)';
                autoSyncBtn.style.background = 'rgba(16, 185, 129, 0.2)';
                autoSyncBtn.style.color = 'var(--accent-emerald)';
                startAutoSync();
                showNotification('🟢 Live ESPN Draft Auto-Sync is ACTIVE (every 3s)', 'success');
            } else {
                autoSyncBtn.textContent = '⚪ Auto-Sync: OFF';
                autoSyncBtn.style.background = 'rgba(255, 255, 255, 0.05)';
                autoSyncBtn.style.color = 'var(--text-muted)';
                if (autoSyncInterval) clearInterval(autoSyncInterval);
                showNotification('Auto-sync paused.', 'info');
            }
        });
    }

    // Reset Draft
    const resetBtn = document.getElementById('btn-reset-draft');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            try {
                // Temporarily pause auto-sync so ESPN doesn't instantly refill
                if (isAutoSyncEnabled && autoSyncBtn) {
                    isAutoSyncEnabled = false;
                    autoSyncBtn.textContent = '⚪ Auto-Sync: OFF';
                    autoSyncBtn.style.background = 'rgba(255, 255, 255, 0.05)';
                    autoSyncBtn.style.color = 'var(--text-muted)';
                    if (autoSyncInterval) clearInterval(autoSyncInterval);
                }

                const userPick = getSelectedTeamId() || 1;

                const res = await fetch(`${API_BASE}/draft/reset`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_pick: userPick })
                });

                if (res.ok) {
                    showNotification('✓ Draft board successfully reset to Pick 1.01!', 'success');
                    await loadDraftState();
                } else {
                    showNotification('Failed to reset draft', 'error');
                }
            } catch (e) {
                console.error(e);
                showNotification('Network error while resetting draft', 'error');
            }
        });
    }
}

async function loadDraftState() {
    try {
        const res = await fetch(`${API_BASE}/draft/state`);
        const state = await res.json();

        // Populate and synchronize Team Selectors with Real League Teams
        if (state.league_teams && state.league_teams.length > 0) {
            populateAllTeamSelectors(state.league_teams);
        }

        // Update Telemetry
        document.getElementById('current-round-text').textContent = `Round ${state.round}`;
        document.getElementById('current-pick-text').textContent = `Pick ${state.round}.${state.pick_in_round < 10 ? '0' + state.pick_in_round : state.pick_in_round} (Overall #${state.current_pick_number})`;
        
        const onClockName = state.current_team_name || `Team ${state.current_team_id}`;
        document.getElementById('on-clock-team').textContent = state.is_user_turn 
            ? `${onClockName} (You)` 
            : onClockName;

        const turnElem = document.getElementById('picks-until-turn');
        if (state.is_user_turn) {
            turnElem.textContent = 'ON THE CLOCK NOW!';
            turnElem.className = 'val-turn highlight-turn';
        } else {
            turnElem.textContent = `${state.picks_until_user} pick(s) away`;
            turnElem.className = 'val-turn';
        }

        // Update Top Balanced Recommendation Banner
        const topRec = state.top_balanced_recommendation;
        const banner = document.getElementById('balanced-pick-banner');
        if (topRec) {
            banner.style.display = 'flex';
            document.getElementById('rec-player-title').textContent = `${topRec.name} (${topRec.position} - ${topRec.team})`;
            document.getElementById('rec-player-rationale').textContent = `${topRec.need_badge}: ${topRec.need_rationale}`;
            
            const quickBtn = document.getElementById('btn-quick-draft-rec');
            quickBtn.onclick = () => window.draftPlayer(topRec.id);
        } else {
            banner.style.display = 'none';
        }

        // Cache Draft Board & Render
        cachedDraftBoard = state.recommended_board || [];
        populateDraftTeamFilter(cachedDraftBoard);
        renderVORPBoard(cachedDraftBoard);

        // Render Opponent Threats
        renderOpponentThreats(state.opponent_threats);

        // Render User Roster
        renderUserRoster(state.user_roster);

        // Render Target Position & Best Available Plan
        renderTargetPositionsPlan(state.user_roster, cachedDraftBoard, state);

    } catch (e) {
        console.error('Error loading draft state:', e);
    }
}

function populateDraftTeamFilter(board) {
    const teamFilter = document.getElementById('draft-team-filter');
    if (!teamFilter) return;

    const currentVal = teamFilter.value || currentTeamFilter || 'ALL';
    
    // Extract unique sorted NFL teams from the board and known NFL teams
    const allNflTeams = [
        "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
        "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
        "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG",
        "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"
    ];
    
    const boardTeams = Array.from(new Set((board || []).map(p => p.team).filter(Boolean)));
    const uniqueTeams = Array.from(new Set([...boardTeams, ...allNflTeams])).sort();

    // Preserve options
    teamFilter.innerHTML = '<option value="ALL">🏈 All Teams</option>';
    uniqueTeams.forEach(team => {
        const opt = document.createElement('option');
        opt.value = team;
        opt.textContent = team;
        if (team === currentVal) {
            opt.selected = true;
        }
        teamFilter.appendChild(opt);
    });

    if (currentVal !== 'ALL' && uniqueTeams.includes(currentVal)) {
        teamFilter.value = currentVal;
        teamFilter.classList.add('active-filter');
    } else {
        teamFilter.value = 'ALL';
        currentTeamFilter = 'ALL';
        teamFilter.classList.remove('active-filter');
    }
}

function renderVORPBoard(board) {
    const tbody = document.getElementById('vorp-board-tbody');
    tbody.innerHTML = '';

    let filtered = [...(board || [])];
    if (currentPosFilter !== 'ALL') {
        filtered = filtered.filter(p => p.position === currentPosFilter);
    }

    if (currentTeamFilter && currentTeamFilter !== 'ALL') {
        filtered = filtered.filter(p => p.team && p.team.toUpperCase() === currentTeamFilter.toUpperCase());
    }

    if (currentSearchQuery) {
        filtered = filtered.filter(p => 
            p.name.toLowerCase().includes(currentSearchQuery) ||
            p.team.toLowerCase().includes(currentSearchQuery) ||
            (p.archetype && p.archetype.toLowerCase().includes(currentSearchQuery))
        );
    }

    // Apply Column Sorting
    if (currentSortColumn) {
        filtered.sort((a, b) => {
            let valA = a[currentSortColumn];
            let valB = b[currentSortColumn];

            if (currentSortColumn === 'name') {
                valA = a.name.toLowerCase();
                valB = b.name.toLowerCase();
            } else if (currentSortColumn === 'need') {
                valA = a.need_multiplier || 1.0;
                valB = b.need_multiplier || 1.0;
            } else if (currentSortColumn === 'cliff') {
                valA = a.tier_cliff_warning ? 1 : 0;
                valB = b.tier_cliff_warning ? 1 : 0;
            } else if (currentSortColumn === 'bye_week') {
                valA = a.bye_week || 99;
                valB = b.bye_week || 99;
            } else if (currentSortColumn === 'rank') {
                valA = a.need_adjusted_score || a.vorp;
                valB = b.need_adjusted_score || b.vorp;
            }

            if (valA < valB) return currentSortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return currentSortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 2rem;">No players found matching your filter/search.</td></tr>`;
        return;
    }

    filtered.forEach((p, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'clickable-row';
        tr.onclick = () => window.showPlayerExplanation(p.id);
        
        const tierClass = `tier-${Math.min(p.tier, 3)}`;
        const cliffHtml = p.tier_cliff_warning 
            ? `<span class="cliff-badge">${escapeHtml(p.tier_cliff_warning)}</span>`
            : `<span style="color: var(--text-muted); font-size: 0.75rem;">Stable</span>`;

        const needClass = p.need_badge_class || 'need-med';
        const needBadgeHtml = `<span class="need-badge ${needClass}">${escapeHtml(p.need_badge || 'ACTIVE FIT')}</span>`;
        const injuryBadgeHtml = getInjuryBadgeHtml(p.injury_status);

        const byeText = p.bye_week ? `Wk ${p.bye_week}` : '—';
        let byeBadgeClass = 'bye-badge';
        if (p.bye_conflict_type === 'CLASH') {
            byeBadgeClass += ' bye-clash-highlight';
        } else if (p.bye_conflict_type === 'CLUSTER') {
            byeBadgeClass += ' bye-cluster-highlight';
        }

        tr.innerHTML = `
            <td>#${idx + 1}</td>
            <td>
                <div class="player-name-cell">
                    <div class="player-name-row">
                        <strong class="player-name-text">${escapeHtml(p.name)}</strong>
                        ${injuryBadgeHtml}
                    </div>
                    <div class="player-sub-row">
                        <span>${escapeHtml(p.archetype || '')}</span>
                        <span class="click-hint">🔍 Breakdown</span>
                    </div>
                </div>
            </td>
            <td><span class="badge" style="background: rgba(255,255,255,0.06);">${escapeHtml(p.position)}</span> <span style="color: var(--text-muted);">${escapeHtml(p.team)}</span></td>
            <td><span class="${byeBadgeClass}">${byeText}</span></td>
            <td><span class="tier-badge ${tierClass}">Tier ${escapeHtml(p.tier)}</span></td>
            <td>${needBadgeHtml}</td>
            <td class="vorp-val">+${escapeHtml(p.vorp)} <small style="font-size:0.7rem; color:var(--text-muted);">(+${escapeHtml(p.vorp_per_week)}/wk)</small></td>
            <td>${escapeHtml(p.xfp)}</td>
            <td>${escapeHtml(p.projected_season)}</td>
            <td>${cliffHtml}</td>
            <td>
                <button class="btn btn-pick" data-draft-player="${escapeHtml(encodedPlayerId(p.id))}">Draft</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

window.draftPlayer = async function(playerId) {
    try {
        const res = await fetch(`${API_BASE}/draft/pick`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId })
        });
        if (res.ok) {
            await loadDraftState();
            await loadLineupOptimization();
        } else {
            const err = await res.json();
            alert(err.detail || 'Pick failed');
        }
    } catch (e) {
        console.error(e);
    }
};

function renderOpponentThreats(threats) {
    const container = document.getElementById('opponent-threats-list');
    container.innerHTML = '';

    if (!threats || threats.length === 0) {
        container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 0.5rem;">No opponents drafting before your next turn.</div>`;
        return;
    }

    threats.forEach(t => {
        const div = document.createElement('div');
        div.className = 'threat-item';
        div.innerHTML = `
            <div class="threat-team-info">
                <strong>#${escapeHtml(t.team_id)} ${escapeHtml(t.team_name)}</strong>
                <span class="threat-meta">Pick #${escapeHtml(t.pick_number)} (Round ${escapeHtml(t.round)})</span>
            </div>
            <div class="threat-need">${escapeHtml(t.urgent_need)}</div>
        `;
        container.appendChild(div);
    });
}

function renderUserRoster(roster) {
    const container = document.getElementById('drafted-user-roster');
    const countBadge = document.getElementById('user-roster-count');
    container.innerHTML = '';
    
    countBadge.textContent = `${roster.length} / 15`;

    if (roster.length === 0) {
        container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 0.5rem;">No players drafted yet.</div>`;
        return;
    }

    roster.forEach(p => {
        const div = document.createElement('div');
        div.className = 'roster-item';
        const byeBadgeHtml = p.bye_week ? ` <span class="bye-badge-sm">Wk ${p.bye_week}</span>` : '';
        div.innerHTML = `
            <span><strong>${escapeHtml(p.position)}</strong> ${escapeHtml(p.name)} <small style="color:var(--text-muted);">(${escapeHtml(p.team)})</small>${byeBadgeHtml}</span>
            <span style="color: var(--accent-cyan); font-weight: 600;">${escapeHtml(p.projected_season)} pts</span>
        `;
        container.appendChild(div);
    });
}

function renderTargetPositionsPlan(userRoster, draftBoard, state) {
    const container = document.getElementById('target-positions-plan-list');
    const countBadge = document.getElementById('target-plan-count-badge');
    if (!container) return;

    container.innerHTML = '';

    const currentPickNumber = (state && state.current_pick_number) ? state.current_pick_number : 1;
    const currentRound = (state && state.round) ? state.round : 1;
    const numTeams = (state && state.league_teams && state.league_teams.length > 0) ? state.league_teams.length : 10;

    // Define standard 15 roster position slots
    const rosterSlots = [
        { slotId: 'QB', label: 'Quarterback (QB1)', key: 'QB', allowedPos: ['QB'] },
        { slotId: 'RB1', label: 'RB1 Starter', key: 'RB1', allowedPos: ['RB'] },
        { slotId: 'RB2', label: 'RB2 Starter', key: 'RB2', allowedPos: ['RB'] },
        { slotId: 'WR1', label: 'WR1 Starter', key: 'WR1', allowedPos: ['WR'] },
        { slotId: 'WR2', label: 'WR2 Starter', key: 'WR2', allowedPos: ['WR'] },
        { slotId: 'TE', label: 'Tight End (TE1)', key: 'TE', allowedPos: ['TE'] },
        { slotId: 'FLEX', label: 'FLEX Starter (RB/WR/TE)', key: 'FLEX', allowedPos: ['RB', 'WR', 'TE'] },
        { slotId: 'DEF', label: 'Defense / ST', key: 'DEF', allowedPos: ['DEF', 'D/ST'] },
        { slotId: 'K', label: 'Kicker', key: 'K', allowedPos: ['K'] },
        { slotId: 'BN1', label: 'Bench RB Depth', key: 'BN1', allowedPos: ['RB', 'WR'] },
        { slotId: 'BN2', label: 'Bench WR Depth', key: 'BN2', allowedPos: ['WR', 'RB'] },
        { slotId: 'BN3', label: 'Bench Flex Depth', key: 'BN3', allowedPos: ['RB', 'WR', 'TE'] },
        { slotId: 'BN4', label: 'Bench QB/TE Backup', key: 'BN4', allowedPos: ['QB', 'TE', 'WR', 'RB'] },
        { slotId: 'BN5', label: 'Bench Upside Flex', key: 'BN5', allowedPos: ['WR', 'RB', 'TE'] },
        { slotId: 'BN6', label: 'Bench Upside Value', key: 'BN6', allowedPos: ['RB', 'WR', 'TE', 'QB', 'DEF', 'K'] }
    ];

    const poolRoster = [...(userRoster || [])];
    const filledSlots = {};

    function extractFirstMatching(positions) {
        const idx = poolRoster.findIndex(p => positions.includes(p.position));
        if (idx !== -1) {
            return poolRoster.splice(idx, 1)[0];
        }
        return null;
    }

    // 1. Fill Starters first
    filledSlots['QB'] = extractFirstMatching(['QB']);
    filledSlots['RB1'] = extractFirstMatching(['RB']);
    filledSlots['RB2'] = extractFirstMatching(['RB']);
    filledSlots['WR1'] = extractFirstMatching(['WR']);
    filledSlots['WR2'] = extractFirstMatching(['WR']);
    filledSlots['TE'] = extractFirstMatching(['TE']);
    filledSlots['FLEX'] = extractFirstMatching(['RB', 'WR', 'TE']);
    filledSlots['DEF'] = extractFirstMatching(['DEF', 'D/ST']);
    filledSlots['K'] = extractFirstMatching(['K']);

    // 2. Fill Bench slots
    filledSlots['BN1'] = extractFirstMatching(['RB', 'WR']);
    filledSlots['BN2'] = extractFirstMatching(['WR', 'RB']);
    filledSlots['BN3'] = extractFirstMatching(['RB', 'WR', 'TE']);
    filledSlots['BN4'] = extractFirstMatching(['QB', 'TE', 'WR', 'RB']);
    filledSlots['BN5'] = poolRoster.length > 0 ? poolRoster.shift() : null;
    filledSlots['BN6'] = poolRoster.length > 0 ? poolRoster.shift() : null;

    let filledCount = 0;
    Object.keys(filledSlots).forEach(k => {
        if (filledSlots[k]) filledCount++;
    });

    if (countBadge) {
        countBadge.textContent = `${filledCount} / 15 Filled`;
    }

    const allocatedTargetIds = new Set();
    const availablePlayers = [...(draftBoard || [])];

    rosterSlots.forEach((slot) => {
        const draftedPlayer = filledSlots[slot.slotId];
        const slotItem = document.createElement('div');

        if (draftedPlayer) {
            slotItem.className = 'target-slot-item slot-filled';
            const byeText = draftedPlayer.bye_week ? ` • Wk ${draftedPlayer.bye_week}` : '';
            
            slotItem.innerHTML = `
                <div class="target-slot-header">
                    <div class="target-slot-title">
                        <span class="target-pos-tag">${slot.key}</span>
                        <span>${escapeHtml(slot.label)}</span>
                    </div>
                    <span class="target-slot-badge badge-status-filled">✓ FILLED</span>
                </div>
                <div class="target-slot-body">
                    <div class="target-player-info">
                        <span class="target-player-name">${escapeHtml(draftedPlayer.name)} <small style="color:var(--text-muted);">(${escapeHtml(draftedPlayer.team)}${escapeHtml(byeText)})</small></span>
                        <span class="target-player-sub" style="color:var(--accent-emerald);">Drafted • ${escapeHtml(draftedPlayer.projected_season || '')} pts</span>
                    </div>
                </div>
            `;
        } else {
            let targetPlayer = null;
            for (const p of availablePlayers) {
                if (slot.allowedPos.includes(p.position) && !allocatedTargetIds.has(p.id)) {
                    targetPlayer = p;
                    allocatedTargetIds.add(p.id);
                    break;
                }
            }

            if (targetPlayer) {
                const adpVal = targetPlayer.adp || (availablePlayers.indexOf(targetPlayer) + 1);
                const estOverallPick = Math.max(1, Math.round(adpVal));
                const recRound = Math.max(1, Math.ceil(estOverallPick / numTeams));
                const pickInRound = ((estOverallPick - 1) % numTeams) + 1;
                const formattedPickStr = `${recRound}.${pickInRound < 10 ? '0' + pickInRound : pickInRound}`;

                const isCurrentTurnOrUrgent = estOverallPick <= currentPickNumber || recRound <= currentRound;

                const roundBadgeText = isCurrentTurnOrUrgent
                    ? `🚨 Pick NOW in Round ${currentRound}`
                    : `Target: Round ${recRound} (Pick ${formattedPickStr} / #${estOverallPick})`;

                const itemClass = isCurrentTurnOrUrgent ? 'target-slot-item slot-open slot-urgent' : 'target-slot-item slot-open';
                const statusBadgeClass = isCurrentTurnOrUrgent ? 'target-slot-badge badge-status-now' : 'target-slot-badge badge-status-target';
                const statusBadgeLabel = isCurrentTurnOrUrgent ? '🔥 DRAFT NOW' : '🎯 TARGET';

                slotItem.className = itemClass;
                slotItem.innerHTML = `
                    <div class="target-slot-header">
                        <div class="target-slot-title">
                            <span class="target-pos-tag">${slot.key}</span>
                            <span>${escapeHtml(slot.label)}</span>
                        </div>
                        <span class="${statusBadgeClass}">${statusBadgeLabel}</span>
                    </div>
                    <div class="target-slot-body">
                        <div class="target-player-info">
                            <span class="target-player-name">${escapeHtml(targetPlayer.name)} <small style="color:var(--accent-cyan);">(${escapeHtml(targetPlayer.position)} - ${escapeHtml(targetPlayer.team)})</small></span>
                            <span class="target-round-tag ${isCurrentTurnOrUrgent ? 'now-highlight' : ''}">${roundBadgeText}</span>
                        </div>
                        <button class="btn-target-draft" data-draft-player="${escapeHtml(encodedPlayerId(targetPlayer.id))}">Draft</button>
                    </div>
                `;
            } else {
                slotItem.className = 'target-slot-item slot-open';
                slotItem.innerHTML = `
                    <div class="target-slot-header">
                        <div class="target-slot-title">
                            <span class="target-pos-tag">${slot.key}</span>
                            <span>${slot.label}</span>
                        </div>
                        <span class="target-slot-badge badge-status-target">OPEN</span>
                    </div>
                    <div class="target-slot-body">
                        <div class="target-player-info">
                            <span class="target-player-name" style="color:var(--text-muted);">No player remaining</span>
                        </div>
                    </div>
                `;
            }
        }

        container.appendChild(slotItem);
    });
}

// --- TAB 2: WEEKLY LINEUP OPTIMIZER ---
function initLineupOptimizer() {
    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentOptimizationMode = btn.dataset.mode;
            loadLineupOptimization();
        });
    });

    document.getElementById('btn-run-compare').addEventListener('click', async () => {
        const pA = document.getElementById('compare-player-a').value;
        const pB = document.getElementById('compare-player-b').value;
        if (!pA || !pB || pA === pB) {
            alert('Please select two distinct players to compare');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/lineup/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id_a: pA, player_id_b: pB })
            });
            const data = await res.json();
            renderComparisonResult(data);
        } catch (e) {
            console.error(e);
        }
    });
}

async function loadLineupOptimization() {
    try {
        const userTeamId = getSelectedTeamId() || 1;
        const res = await fetch(`${API_BASE}/lineup/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team_id: userTeamId, mode: currentOptimizationMode })
        });
        const data = await res.json();

        document.getElementById('optimal-total-points').textContent = data.total_projected;

        // Render Starters
        const startersGrid = document.getElementById('starters-list');
        startersGrid.innerHTML = '';

        data.starters.forEach(p => {
            const div = document.createElement('div');
            div.className = 'starter-card';
            
            const weatherWind = p.wind_mph >= 15 
                ? `<span style="color: var(--accent-rose);">💨 ${p.wind_mph}mph</span>` 
                : `${p.is_dome ? '🏟️ Dome' : `🌤️ ${p.wind_mph}mph`}`;
            const injuryBadgeHtml = getInjuryBadgeHtml(p.injury_status);

            div.innerHTML = `
                <div class="slot-tag">${escapeHtml(p.assigned_slot)}</div>
                <div>
                    <div class="player-info-title">${escapeHtml(p.name)} ${injuryBadgeHtml}</div>
                    <div class="player-info-sub">${escapeHtml(p.position)} • ${escapeHtml(p.team)} vs ${escapeHtml(p.opponent || 'TBD')}</div>
                </div>
                <div class="context-tag">
                    <div>Vegas: <strong>${escapeHtml(p.implied_team_pts || 22.0)} pts</strong> (${escapeHtml(p.spread || 0)})</div>
                    <div>Weather: ${weatherWind}</div>
                </div>
                <div class="context-tag">
                    <div>xFP: <strong>${escapeHtml(p.xfp)}</strong></div>
                    <div>Matchup: <strong>#${escapeHtml(p.opp_rank_vs_pos || 16)} def</strong></div>
                </div>
                <div class="proj-pts-badge">${escapeHtml(p.score)}</div>
            `;
            startersGrid.appendChild(div);
        });

        // Render Bench
        const benchGrid = document.getElementById('bench-list');
        benchGrid.innerHTML = '';
        data.bench.forEach(p => {
            const div = document.createElement('div');
            div.className = 'bench-card';
            const injuryBadgeHtml = getInjuryBadgeHtml(p.injury_status);
            div.innerHTML = `
                <span><strong>${escapeHtml(p.position)}</strong> ${escapeHtml(p.name)} ${injuryBadgeHtml} <small style="color:var(--text-muted);">(${escapeHtml(p.team)})</small></span>
                <span style="color: var(--text-secondary);">${escapeHtml(p.score)} pts</span>
            `;
            benchGrid.appendChild(div);
        });

        // Populate Sit/Start Dropdowns
        allRosterPlayers = [...data.starters, ...data.bench];
        populateCompareSelectors(allRosterPlayers);

    } catch (e) {
        console.error('Error loading lineup optimization:', e);
    }
}

function populateCompareSelectors(roster) {
    const selA = document.getElementById('compare-player-a');
    const selB = document.getElementById('compare-player-b');
    
    selA.innerHTML = '';
    selB.innerHTML = '';

    roster.forEach((p, idx) => {
        const optA = document.createElement('option');
        optA.value = p.id;
        optA.textContent = `${p.position} - ${p.name} (${p.team})`;
        selA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = p.id;
        optB.textContent = `${p.position} - ${p.name} (${p.team})`;
        if (idx === 1) optB.selected = true;
        selB.appendChild(optB);
    });
}

function renderComparisonResult(data) {
    const box = document.getElementById('compare-result-box');
    box.classList.remove('hidden');

    document.getElementById('compare-winner-title').textContent = data.recommendation;
    
    const list = document.getElementById('compare-advantages-list');
    list.innerHTML = '';
    data.key_advantages.forEach(adv => {
        const li = document.createElement('li');
        li.textContent = adv;
        list.appendChild(li);
    });
}

// --- TAB 3: WAIVER ARBITRAGE RADAR ---
function initWaiverRadar() {}

async function loadWaiverRadar() {
    try {
        // Breakout targets
        const resRadar = await fetch(`${API_BASE}/waiver/radar`);
        const dataRadar = await resRadar.json();
        renderBreakoutFeed(dataRadar.breakout_targets);

        // Drop candidates for active user team
        const userTeamId = getSelectedTeamId() || 1;
        const resDrop = await fetch(`${API_BASE}/waiver/drop-candidates?team_id=${userTeamId}`);
        const dataDrop = await resDrop.json();
        renderDropCandidates(dataDrop.drop_candidates);

    } catch (e) {
        console.error('Error loading waiver radar:', e);
    }
}

function renderBreakoutFeed(targets) {
    const container = document.getElementById('breakout-cards-container');
    container.innerHTML = '';

    if (!targets || targets.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); padding: 1rem;">No immediate breakout anomalies detected.</div>`;
        return;
    }

    targets.forEach(p => {
        const div = document.createElement('div');
        div.className = 'breakout-card';

        const signalsHtml = p.breakout_signals.map(s => `<div class="signal-bullet">⚡ ${escapeHtml(s)}</div>`).join('');
        const deltaSign = p.arbitrage_delta >= 0 ? `+${p.arbitrage_delta}` : `${p.arbitrage_delta}`;
        const injuryBadgeHtml = getInjuryBadgeHtml(p.injury_status);

        div.innerHTML = `
            <div class="breakout-top">
                <div>
                    <h4 style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700;">${escapeHtml(p.name)} ${injuryBadgeHtml}</h4>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(p.position)} • ${escapeHtml(p.team)} | ${escapeHtml(p.espn_ownership)}% Roster %</span>
                </div>
                <div class="signal-score-badge">
                    <span class="score-num">${escapeHtml(p.breakout_score)}</span>
                    <span class="score-lbl">BREAKOUT INDEX</span>
                </div>
            </div>

            <div class="breakout-signals-list">
                ${signalsHtml}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                <span class="delta-badge">${deltaSign} pts vs ESPN Proj</span>
                <span style="font-size: 0.75rem; color: var(--accent-cyan); font-weight: 600;">Model: ${escapeHtml(p.contextual_proj)} pts</span>
            </div>
        `;
        container.appendChild(div);
    });
}

function renderDropCandidates(candidates) {
    const container = document.getElementById('drop-candidates-list');
    container.innerHTML = '';

    if (!candidates || candidates.length === 0) {
        container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 0.5rem;">Your bench roster is fully optimized. No urgent drop candidates.</div>`;
        return;
    }

    candidates.forEach(c => {
        const div = document.createElement('div');
        div.className = 'drop-item';
        div.innerHTML = `
            <div class="drop-name">${escapeHtml(c.name)} (${escapeHtml(c.position)} - ${escapeHtml(c.team)})</div>
            <div class="drop-sub">${escapeHtml(c.drop_reasons.join(' • '))}</div>
        `;
        container.appendChild(div);
    });
}

// --- TAB 4: ESPN LEAGUE SYNC & SETTINGS ---
function initESPNSync() {
    // Header Active Team Pill Click -> Go to Settings
    const teamPill = document.getElementById('active-user-team-pill');
    if (teamPill) {
        teamPill.addEventListener('click', () => {
            const espnTabBtn = document.querySelector('.nav-tab[data-tab="espn-tab"]');
            if (espnTabBtn) espnTabBtn.click();
            const settingsSelect = document.getElementById('settings-user-team-select');
            if (settingsSelect) {
                settingsSelect.focus();
                settingsSelect.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

    // Settings Team Picker Preview on Change
    const settingsSelect = document.getElementById('settings-user-team-select');
    if (settingsSelect) {
        settingsSelect.addEventListener('change', (e) => {
            const previewId = parseInt(e.target.value, 10);
            const previewTeam = (leagueTeams || []).find(t => t.id === previewId);
            renderSelectedTeamDetails(previewTeam);
        });
    }

    // Save as My Team Button
    const saveTeamBtn = document.getElementById('btn-save-user-team');
    if (saveTeamBtn) {
        saveTeamBtn.addEventListener('click', async () => {
            const sel = document.getElementById('settings-user-team-select');
            if (sel) {
                const newId = parseInt(sel.value, 10);
                saveTeamBtn.disabled = true;
                saveTeamBtn.textContent = '⏳ Saving...';
                try {
                    await setSelectedTeamId(newId, true);
                    const team = getActiveTeamObject();
                    showNotification(`✓ Saved "${team ? team.name : 'Team ' + newId}" as your active team!`, 'success');
                } finally {
                    saveTeamBtn.disabled = false;
                    saveTeamBtn.innerHTML = '<span class="icon">💾</span> Set as My Team';
                }
            }
        });
    }

    // ESPN Connect Form
    const form = document.getElementById('espn-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const leagueId = document.getElementById('espn-league-id').value;
        const year = parseInt(document.getElementById('espn-year').value, 10) || 2024;
        const swid = document.getElementById('espn-swid').value;
        const espnS2 = document.getElementById('espn-s2').value;

        try {
            const res = await fetch(`${API_BASE}/league/connect`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    league_id: leagueId,
                    year: year,
                    swid: swid,
                    espn_s2: espnS2
                })
            });
            const data = await res.json();
            await loadLeagueOverview();
            await refreshAllData();
            if (data.status === "connected") {
                // Smooth non-blocking UI confirmation
                const statusBadge = document.getElementById('connection-status-pill');
                if (statusBadge) {
                    statusBadge.textContent = `Connected: ${data.league_name || 'ESPN'}`;
                }
                showNotification(`✓ Connected to ESPN League: ${data.league_name || 'ESPN'}`, 'success');
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error(err);
            alert('Failed to connect to ESPN League: ' + err.message);
        }
    });

    document.getElementById('btn-use-demo').addEventListener('click', async () => {
        document.getElementById('espn-league-id').value = '';
        document.getElementById('espn-swid').value = '';
        document.getElementById('espn-s2').value = '';
        await fetch(`${API_BASE}/league/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ league_id: '', year: 2024 })
        });
        await loadLeagueOverview();
        await refreshAllData();
        showNotification('Switched to 10-Team Demo Mode', 'info');
    });
}

async function loadLeagueOverview() {
    try {
        const res = await fetch(`${API_BASE}/league/overview`);
        const data = await res.json();

        // Populate league teams in selector
        if (data.teams && data.teams.length > 0) {
            populateAllTeamSelectors(data.teams);
        }

        const syncPill = document.getElementById('league-sync-pill');
        const syncText = document.getElementById('sync-status-text');
        const statusBadge = document.getElementById('connection-status-pill');

        if (data.is_live_espn) {
            syncPill.className = 'sync-pill sync-live';
            const leagueLabel = data.league_name || `League #${data.league_id}`;
            syncText.textContent = `ESPN Live: ${leagueLabel}`;
            statusBadge.className = 'badge badge-status';
            statusBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            statusBadge.style.color = 'var(--accent-emerald)';
            statusBadge.textContent = `Live: ${leagueLabel}`;
        } else {
            syncPill.className = 'sync-pill sync-demo';
            syncText.textContent = 'Demo 10-Team League';
            statusBadge.className = 'badge badge-status';
            statusBadge.style.background = 'rgba(245, 158, 11, 0.2)';
            statusBadge.style.color = 'var(--accent-amber)';
            statusBadge.textContent = '10-Team Demo Mode';
        }

        // Render Standings Table
        const standingsContainer = document.getElementById('league-standings-table');
        standingsContainer.innerHTML = '';

        const userTeamId = getSelectedTeamId() || 1;

        data.teams.forEach(t => {
            const isUser = t.id === userTeamId;
            const div = document.createElement('div');
            div.className = isUser ? 'team-row user-highlight-row' : 'team-row';
            if (isUser) {
                div.style.background = 'rgba(0, 242, 254, 0.12)';
                div.style.border = '1px solid rgba(0, 242, 254, 0.4)';
                div.style.borderRadius = '8px';
                div.style.padding = '8px 12px';
            }

            div.innerHTML = `
                <div>
                    <strong style="${isUser ? 'color: var(--accent-cyan); font-weight: 800;' : ''}">#${escapeHtml(t.standing)} ${escapeHtml(t.name)}${isUser ? ' (You)' : ''}</strong>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">(${escapeHtml(t.owner)})</span>
                </div>
                <div>
                    <span style="font-weight: 700; color: var(--accent-cyan);">${escapeHtml(t.wins)}-${escapeHtml(t.losses)}</span>
                </div>
            `;
            standingsContainer.appendChild(div);
        });

    } catch (e) {
        console.error('Error loading league overview:', e);
    }
}

