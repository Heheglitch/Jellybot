import chess
import chess.polyglot  # Required for the reliable hashing fix
import math
import time

# --- Evaluation Constants ---
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-Square Tables (Strategy Heatmaps)
PAWN_PST = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]

KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_PST = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

KING_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]

TABLES = {chess.PAWN: PAWN_PST, chess.KNIGHT: KNIGHT_PST, chess.BISHOP: BISHOP_PST, chess.KING: KING_PST}


class ChessBot:
    def __init__(self, depth=3):
        self.depth = depth
        self.transposition_table = {}

    def evaluate_board(self, board):
        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = PIECE_VALUES[piece.piece_type]
                if piece.piece_type in TABLES:
                    idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
                    val += TABLES[piece.piece_type][idx]

                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
        return score

    def quiescence_search(self, board, alpha, beta, q_depth=0):
        static_eval = self.evaluate_board(board)
        if q_depth > 3: return static_eval

        if board.turn == chess.WHITE:
            if static_eval >= beta: return beta
            alpha = max(alpha, static_eval)
        else:
            if static_eval <= alpha: return alpha
            beta = min(beta, static_eval)

        capture_moves = [m for m in board.legal_moves if board.is_capture(m)]
        for move in sorted(capture_moves, key=lambda m: board.is_capture(m), reverse=True):
            board.push(move)
            score = self.quiescence_search(board, alpha, beta, q_depth + 1)
            board.pop()
            if board.turn == chess.WHITE:
                if score >= beta: return beta
                alpha = max(alpha, score)
            else:
                if score <= alpha: return alpha
                beta = min(beta, score)
        return alpha if board.turn == chess.WHITE else beta

    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        # FIX: Use polyglot for guaranteed hashability
        board_hash = chess.polyglot.zobrist_hash(board)

        if board_hash in self.transposition_table:
            entry_depth, entry_eval = self.transposition_table[board_hash]
            if entry_depth >= depth:
                return entry_eval

        if depth == 0 or board.is_game_over():
            return self.quiescence_search(board, alpha, beta)

        moves = sorted(board.legal_moves, key=lambda m: board.is_capture(m), reverse=True)

        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                eval = self.alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            self.transposition_table[board_hash] = (depth, max_eval)
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                eval = self.alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            self.transposition_table[board_hash] = (depth, min_eval)
            return min_eval

    def get_best_move(self, board):
        best_move = None
        alpha, beta = -math.inf, math.inf
        is_white = (board.turn == chess.WHITE)
        best_val = -math.inf if is_white else math.inf

        moves = sorted(board.legal_moves, key=lambda m: board.is_capture(m), reverse=True)
        for move in moves:
            board.push(move)
            val = self.alpha_beta(board, self.depth - 1, alpha, beta, not is_white)
            board.pop()
            if is_white:
                if val > best_val:
                    best_val, best_move = val, move
                alpha = max(alpha, val)
            else:
                if val < best_val:
                    best_val, best_move = val, move
                beta = min(beta, val)
        return best_move


def main():
    board = chess.Board()
    bot = ChessBot(depth=3)
    while not board.is_game_over():
        print("\n", board)
        if board.turn == chess.WHITE:
            user_input = input("\nYour move: ").strip().lower()
            try:
                move = chess.Move.from_uci(user_input)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print("Illegal move!")
            except:
                print("Invalid format! Use e2e4.")
        else:
            print("Bot is thinking...")
            start = time.time()
            move = bot.get_best_move(board)
            if move:
                print(f"Bot moved {move} ({time.time() - start:.2f}s)")
                board.push(move)
    print("\nGame Over! Result:", board.result())


if __name__ == "__main__":
    main()