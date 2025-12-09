"""Chess board HTML rendering"""

import json

import chess

# Unicode chess piece symbols (same as krondor-chess)
# White pieces use outline glyphs, black pieces use filled glyphs
PIECE_SYMBOLS = {
    "P": "♙",  # White pawn (outline)
    "N": "♘",  # White knight (outline)
    "B": "♗",  # White bishop (outline)
    "R": "♖",  # White rook (outline)
    "Q": "♕",  # White queen (outline)
    "K": "♔",  # White king (outline)
    "p": "♟︎",  # Black pawn (filled)
    "n": "♞",  # Black knight (filled)
    "b": "♝",  # Black bishop (filled)
    "r": "♜",  # Black rook (filled)
    "q": "♛",  # Black queen (filled)
    "k": "♚",  # Black king (filled)
}


def render_board_html(fen: str, perspective: str = "white") -> str:
    """
    Render a chess board as an HTML table.

    Each cell has:
    - id: square name (e.g., "e4")
    - class: chess-square-{light|dark} [chess-piece-{symbol}]
    - content: Unicode chess piece symbol

    The table includes data-legal-moves with a JSON map of from_square -> [to_squares]

    Args:
        fen: FEN string representing the board position
        perspective: "white" or "black" - which side is at the bottom

    Returns:
        HTML string of the chess board table
    """
    board = chess.Board(fen)

    # Build legal moves map: {from_square: [to_squares]}
    legal_moves_map: dict[str, list[str]] = {}
    for move in board.legal_moves:
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)
        if from_sq not in legal_moves_map:
            legal_moves_map[from_sq] = []
        legal_moves_map[from_sq].append(to_sq)

    legal_moves_json = json.dumps(legal_moves_map)

    html = f'<table id="chessboard" class="chess-board" data-legal-moves=\'{legal_moves_json}\'>'

    # Determine iteration order based on perspective
    if perspective == "white":
        ranks = range(7, -1, -1)  # 8 down to 1
        files = range(8)  # a to h
    else:
        ranks = range(8)  # 1 up to 8
        files = range(7, -1, -1)  # h to a

    for rank in ranks:
        html += "<tr>"
        for file in files:
            square = chess.square(file, rank)
            square_name = chess.square_name(square)

            # Determine square color
            is_light = (file + rank) % 2 == 1
            color_class = "light" if is_light else "dark"

            piece = board.piece_at(square)
            if piece:
                piece_char = piece.symbol()
                piece_html = PIECE_SYMBOLS.get(piece_char, "")
                piece_class = f" chess-piece-{piece_char}"
                html += (
                    f'<td id="{square_name}" '
                    f'class="chess-square-{color_class}{piece_class}">'
                    f"{piece_html}</td>"
                )
            else:
                html += f'<td id="{square_name}" class="chess-square-{color_class}"></td>'

        html += "</tr>"

    html += "</table>"
    return html
