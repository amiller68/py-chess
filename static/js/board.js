// Global state for piece selection
let selectedPiece = null;
let fromSquare = null;
let toSquare = null;
let legalMoves = {};

// Get legal moves from board data attribute
function getLegalMoves() {
    const chessboard = document.getElementById('chessboard');
    if (!chessboard) return {};
    try {
        return JSON.parse(chessboard.getAttribute('data-legal-moves') || '{}');
    } catch (e) {
        return {};
    }
}

// Check if a square has a piece that can move
function canSelectPiece(square) {
    const squareId = square.getAttribute('id');
    return legalMoves[squareId] && legalMoves[squareId].length > 0;
}

// Check if a move is legal
function isLegalMove(fromId, toId) {
    return legalMoves[fromId] && legalMoves[fromId].includes(toId);
}

// Highlight legal destination squares
function highlightLegalMoves(fromId) {
    clearHighlights();
    const destinations = legalMoves[fromId] || [];
    for (const toId of destinations) {
        const square = document.getElementById(toId);
        if (square) {
            square.classList.add('legal-move');
        }
    }
}

// Clear all highlights
function clearHighlights() {
    const squares = document.querySelectorAll('.legal-move');
    for (const sq of squares) {
        sq.classList.remove('legal-move');
    }
}

// Logic for moving a piece
function movePiece(fromSq, toSq) {
    // Get the piece class for tracking
    let fromPieceClass = null;
    for (const cls of fromSq.classList) {
        if (cls.startsWith('chess-piece-')) {
            fromPieceClass = cls;
            break;
        }
    }
    const fromPiece = fromPieceClass ? fromPieceClass.split('-')[2] : '';

    // Get positions
    const fromPosition = fromSq.getAttribute('id');
    const toPosition = toSq.getAttribute('id');
    const toRank = toPosition[1];

    // Build UCI move
    let uciMove = `${fromPosition}${toPosition}`;

    // Handle pawn promotion (auto-queen for simplicity)
    let promotionHtml = null;
    let promotionClass = null;
    if ((fromPiece === 'P' && toRank === '8') || (fromPiece === 'p' && toRank === '1')) {
        uciMove += 'q';
        if (fromPiece === 'P') {
            promotionHtml = '♕';
            promotionClass = 'chess-piece-Q';
        } else {
            promotionHtml = '♛';
            promotionClass = 'chess-piece-q';
        }
    }

    // Update the board optimistically
    const toPieceHtml = promotionHtml || fromSq.innerHTML;
    const toPieceClass = promotionClass || fromPieceClass;

    // Remove old piece class from destination
    for (const cls of Array.from(toSq.classList)) {
        if (cls.startsWith('chess-piece-')) {
            toSq.classList.remove(cls);
        }
    }

    toSq.innerHTML = toPieceHtml;
    if (toPieceClass) {
        toSq.classList.add(toPieceClass);
    }

    // Clear source square
    fromSq.innerHTML = '';
    if (fromPieceClass) {
        fromSq.classList.remove(fromPieceClass);
    }

    // Store for potential rollback
    fromSquare = fromSq;
    toSquare = toSq;

    // Send the move
    sendMove(uciMove);
}

function sendMove(uciMove) {
    console.log('Move:', uciMove);
    const moveInput = document.getElementById('uciMoveInput');
    const moveForm = document.getElementById('moveForm');

    if (moveInput && moveForm) {
        moveInput.value = uciMove;
        moveForm.style.display = 'block';
    }
}

function initBoard() {
    selectedPiece = null;
    fromSquare = null;
    toSquare = null;
    legalMoves = getLegalMoves();

    const moveForm = document.getElementById('moveForm');
    const moveInput = document.getElementById('uciMoveInput');

    if (moveForm) {
        moveForm.style.display = 'none';
    }
    if (moveInput) {
        moveInput.value = '';
    }

    clearHighlights();

    // Find the chessboard
    const chessboard = document.getElementById('chessboard');
    if (!chessboard) {
        return;
    }

    // Remove old listeners by cloning
    const newBoard = chessboard.cloneNode(true);
    chessboard.parentNode.replaceChild(newBoard, chessboard);

    // Re-read legal moves from the new board
    legalMoves = getLegalMoves();

    // Add click handler
    newBoard.addEventListener('click', function(event) {
        const clickedSquare = event.target.closest('[class*="chess-square-"]');
        if (!clickedSquare) return;

        const clickedId = clickedSquare.getAttribute('id');

        if (!selectedPiece) {
            // Try to select a piece
            if (canSelectPiece(clickedSquare)) {
                selectedPiece = clickedSquare;
                fromSquare = clickedSquare;
                clickedSquare.classList.add('selected');
                highlightLegalMoves(clickedId);
            }
        } else {
            const fromId = selectedPiece.getAttribute('id');

            if (clickedSquare === selectedPiece) {
                // Deselect
                clickedSquare.classList.remove('selected');
                clearHighlights();
                selectedPiece = null;
                return;
            }

            // Check if clicking another piece that can move
            if (canSelectPiece(clickedSquare) && !isLegalMove(fromId, clickedId)) {
                // Switch selection to new piece
                selectedPiece.classList.remove('selected');
                clearHighlights();
                selectedPiece = clickedSquare;
                fromSquare = clickedSquare;
                clickedSquare.classList.add('selected');
                highlightLegalMoves(clickedId);
                return;
            }

            // Check if legal move
            if (isLegalMove(fromId, clickedId)) {
                toSquare = clickedSquare;
                movePiece(selectedPiece, clickedSquare);
                selectedPiece.classList.remove('selected');
                clearHighlights();
                selectedPiece = null;
            }
        }
    });
}

// Handle move errors - revert the move
document.body.addEventListener('htmx:responseError', function(event) {
    if (event.target.id === 'submitMove' && fromSquare && toSquare) {
        // Swap pieces back
        const fromHtml = fromSquare.innerHTML;
        fromSquare.innerHTML = toSquare.innerHTML;
        toSquare.innerHTML = fromHtml;

        // Reset form
        const moveForm = document.getElementById('moveForm');
        if (moveForm) {
            moveForm.style.display = 'none';
        }
    }
});

// Reset state after HTMX swap
document.body.addEventListener('htmx:afterSwap', function(event) {
    selectedPiece = null;
    fromSquare = null;
    toSquare = null;
    clearHighlights();
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', initBoard);
