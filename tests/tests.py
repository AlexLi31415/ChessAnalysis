from ..game_analysis import win_prob_white_position
import chess
STARTING_BOARD = chess.Board('rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1')

def test_win_prob_white_position():
    engine = chess.engine.SimpleEngine.popen_uci('/opt/homebrew/bin/stockfish', timeout=None)
    board = chess.Board()
    move = chess.Move.from_uci("d2d4")
    board.push(move)
    try:
        assert 0.4 <= win_prob_white_position(board, engine) <= 0.6
    except:
        raise AssertionError
    finally:
        engine.quit()
