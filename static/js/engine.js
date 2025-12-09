/**
 * Engine overlay module for chess analysis display.
 *
 * Provides:
 * - Toggle button to enable/disable engine analysis
 * - Evaluation bar showing position score (-1 to +1)
 * - Best move arrow overlay on the board
 *
 * TODO: For real engine integration:
 * - Consider WebSocket for real-time updates during long analysis
 * - Add support for principal variation (PV) display
 * - Cache analysis results client-side for repeated positions
 */

// Engine state
let engineEnabled = false;
let analysisController = null;
let currentFen = null;

/**
 * Initialize engine overlay functionality.
 * Call this after board.js initBoard().
 */
function initEngineOverlay() {
    // Restore saved preference
    engineEnabled = localStorage.getItem('engineEnabled') === 'true';
    updateToggleState();

    // Get initial FEN
    currentFen = getCurrentFen();

    if (engineEnabled && currentFen) {
        requestAnalysis();
    }
}

/**
 * Get current FEN from the chessboard table data attribute.
 * The chessboard table is inside board-container and gets replaced on SSE updates,
 * so reading from the table ensures we always have the current FEN.
 */
function getCurrentFen() {
    const chessboard = document.getElementById('chessboard');
    return chessboard ? chessboard.getAttribute('data-fen') : null;
}

/**
 * Toggle engine overlay on/off.
 */
function toggleEngine() {
    engineEnabled = !engineEnabled;
    localStorage.setItem('engineEnabled', engineEnabled);
    updateToggleState();

    if (engineEnabled) {
        currentFen = getCurrentFen();
        if (currentFen) {
            requestAnalysis();
        }
    } else {
        hideOverlay();
        cancelPendingAnalysis();
        clearArrow();
    }
}

/**
 * Update toggle button and overlay visibility.
 */
function updateToggleState() {
    const toggle = document.getElementById('engineToggle');
    if (toggle) {
        toggle.classList.toggle('engine-toggle-active', engineEnabled);
        const text = toggle.querySelector('.engine-toggle-text');
        if (text) {
            text.textContent = engineEnabled ? 'Engine ON' : 'Engine';
        }
    }

    const overlay = document.getElementById('engineOverlay');
    if (overlay) {
        overlay.style.display = engineEnabled ? 'flex' : 'none';
    }
}

/**
 * Request analysis from the engine API.
 */
async function requestAnalysis() {
    if (!engineEnabled) return;

    const fen = getCurrentFen();
    if (!fen) return;

    // Cancel any pending request
    cancelPendingAnalysis();

    // Show loading state
    setLoadingState(true);

    // Create abort controller for this request
    analysisController = new AbortController();

    try {
        const response = await fetch(
            `/api/v0/engine/analyze?fen=${encodeURIComponent(fen)}&depth=10`,
            { signal: analysisController.signal }
        );

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Analysis failed: ${response.statusText}`);
        }

        const data = await response.json();
        displayAnalysis(data);
    } catch (error) {
        if (error.name !== 'AbortError') {
            console.error('Engine analysis error:', error);
            showAnalysisError(error.message);
        }
    } finally {
        setLoadingState(false);
        analysisController = null;
    }
}

/**
 * Cancel any pending analysis request.
 */
function cancelPendingAnalysis() {
    if (analysisController) {
        analysisController.abort();
        analysisController = null;
    }
}

/**
 * Display analysis results in the overlay.
 */
function displayAnalysis(analysis) {
    // Update evaluation bar
    const evalBar = document.getElementById('evalBar');
    if (evalBar) {
        // Score -1 to 1 maps to 0% to 100% width (white advantage)
        const barPercent = ((analysis.score + 1) / 2) * 100;
        evalBar.style.width = `${barPercent}%`;
    }

    // Update score display
    const scoreDisplay = document.getElementById('evalScore');
    if (scoreDisplay) {
        const sign = analysis.score >= 0 ? '+' : '';
        scoreDisplay.textContent = `${sign}${analysis.score.toFixed(2)}`;

        // Color based on who's winning
        scoreDisplay.classList.remove('score-white', 'score-black', 'score-equal');
        if (analysis.score > 0.1) {
            scoreDisplay.classList.add('score-white');
        } else if (analysis.score < -0.1) {
            scoreDisplay.classList.add('score-black');
        } else {
            scoreDisplay.classList.add('score-equal');
        }
    }

    // Update best move text
    const bestMoveEl = document.getElementById('bestMove');
    if (bestMoveEl) {
        bestMoveEl.textContent = analysis.best_move || '—';
    }

    // Draw arrow for best move
    if (analysis.best_move) {
        drawBestMoveArrow(analysis.best_move);
    } else {
        clearArrow();
    }
}

/**
 * Draw an arrow on the board showing the best move.
 */
function drawBestMoveArrow(uciMove) {
    clearArrow();

    if (!uciMove || uciMove.length < 4) return;

    const fromSquare = uciMove.substring(0, 2);
    const toSquare = uciMove.substring(2, 4);

    const fromEl = document.getElementById(fromSquare);
    const toEl = document.getElementById(toSquare);
    const svg = document.getElementById('arrowOverlay');
    const boardWrapper = document.querySelector('.board-wrapper');

    if (!fromEl || !toEl || !svg || !boardWrapper) return;

    // Get board wrapper position for relative positioning
    const wrapperRect = boardWrapper.getBoundingClientRect();

    // Get square centers relative to wrapper
    const fromRect = fromEl.getBoundingClientRect();
    const toRect = toEl.getBoundingClientRect();

    const fromX = fromRect.left - wrapperRect.left + fromRect.width / 2;
    const fromY = fromRect.top - wrapperRect.top + fromRect.height / 2;
    const toX = toRect.left - wrapperRect.left + toRect.width / 2;
    const toY = toRect.top - wrapperRect.top + toRect.height / 2;

    // Calculate arrow with shortened length (don't go all the way to center)
    const dx = toX - fromX;
    const dy = toY - fromY;
    const length = Math.sqrt(dx * dx + dy * dy);
    const shortenBy = 15; // Pixels to shorten from each end

    const unitX = dx / length;
    const unitY = dy / length;

    const startX = fromX + unitX * shortenBy;
    const startY = fromY + unitY * shortenBy;
    const endX = toX - unitX * shortenBy;
    const endY = toY - unitY * shortenBy;

    // Update SVG size to match wrapper
    svg.setAttribute('width', wrapperRect.width);
    svg.setAttribute('height', wrapperRect.height);

    // Create arrow marker if it doesn't exist
    let defs = svg.querySelector('defs');
    if (!defs) {
        defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <marker id="arrowhead" markerWidth="4" markerHeight="3"
                    refX="3.5" refY="1.5" orient="auto">
                <polygon points="0 0, 4 1.5, 0 3" fill="rgba(34, 197, 94, 0.8)" />
            </marker>
        `;
        svg.appendChild(defs);
    }

    // Create line element
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', startX);
    line.setAttribute('y1', startY);
    line.setAttribute('x2', endX);
    line.setAttribute('y2', endY);
    line.setAttribute('class', 'best-move-arrow');
    line.setAttribute('marker-end', 'url(#arrowhead)');

    svg.appendChild(line);
}

/**
 * Clear the best move arrow.
 */
function clearArrow() {
    const svg = document.getElementById('arrowOverlay');
    if (svg) {
        // Remove all lines but keep defs
        const lines = svg.querySelectorAll('line');
        lines.forEach(line => line.remove());
    }
}

/**
 * Show loading state in overlay.
 */
function setLoadingState(loading) {
    const overlay = document.getElementById('engineOverlay');
    if (overlay) {
        overlay.classList.toggle('engine-loading', loading);
    }

    const scoreDisplay = document.getElementById('evalScore');
    if (scoreDisplay && loading) {
        scoreDisplay.textContent = '...';
        scoreDisplay.classList.remove('score-white', 'score-black', 'score-equal');
    }

    const bestMoveEl = document.getElementById('bestMove');
    if (bestMoveEl && loading) {
        bestMoveEl.textContent = '...';
    }

    // Clear arrow during loading
    if (loading) {
        clearArrow();
    }
}

/**
 * Hide the overlay completely.
 */
function hideOverlay() {
    const overlay = document.getElementById('engineOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Show error state in overlay.
 */
function showAnalysisError(message) {
    const scoreDisplay = document.getElementById('evalScore');
    if (scoreDisplay) {
        scoreDisplay.textContent = '—';
        scoreDisplay.classList.remove('score-white', 'score-black', 'score-equal');
    }

    const bestMoveEl = document.getElementById('bestMove');
    if (bestMoveEl) {
        bestMoveEl.textContent = 'Error';
        bestMoveEl.title = message || 'Analysis failed';
    }

    clearArrow();
}

/**
 * Handle board updates - re-run analysis if enabled.
 */
function onBoardUpdate() {
    if (engineEnabled) {
        // Small delay to ensure board data is updated
        setTimeout(() => {
            const newFen = getCurrentFen();
            if (newFen && newFen !== currentFen) {
                currentFen = newFen;
                // Clear old arrow immediately when position changes
                clearArrow();
                requestAnalysis();
            }
        }, 100);
    }
}

// Listen for SSE board updates
document.body.addEventListener('htmx:sseMessage', onBoardUpdate);

// Listen for HTMX swaps (backup in case SSE doesn't trigger)
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.target.id === 'board-container') {
        onBoardUpdate();
    }
});

// Export for use in templates
window.toggleEngine = toggleEngine;
window.initEngineOverlay = initEngineOverlay;
