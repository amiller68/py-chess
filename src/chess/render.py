"""Chess board HTML rendering"""

import chess

# Unicode chess piece symbols
PIECE_SYMBOLS = {
    "P": "♙",  # White pawn
    "N": "♘",  # White knight
    "B": "♗",  # White bishop
    "R": "♖",  # White rook
    "Q": "♕",  # White queen
    "K": "♔",  # White king
    "p": "♟",  # Black pawn
    "n": "♞",  # Black knight
    "b": "♝",  # Black bishop
    "r": "♜",  # Black rook
    "q": "♛",  # Black queen
    "k": "♚",  # Black king
}


def render_board_html(fen: str, perspective: str = "white") -> str:
    """
    Render a chess board as an HTML table.

    Each cell has:
    - id: square name (e.g., "e4")
    - class: chess-square-{light|dark} [chess-piece-{symbol}]
    - content: Unicode chess piece symbol

    Args:
        fen: FEN string representing the board position
        perspective: "white" or "black" - which side is at the bottom

    Returns:
        HTML string of the chess board table
    """
    board = chess.Board(fen)

    html = '<table id="chessboard" class="chess-board">'

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
