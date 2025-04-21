import chess
import chess.pgn
import chess.engine
import pandas as pd
import matplotlib.pyplot as plt
from game_analysis import win_prob_white_position


def parse_pgn(file_path):
    """
    Generator that yields games from a PGN file.

    Parameters:
        file_path (str): Path to the PGN file.

    Yields:
        chess.pgn.Game: Parsed game object.
    """
    with open(file_path, 'r', encoding='utf-8') as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            yield game


def analyse_game(game, engine_path='stockfish', depth=18):
    """
    Analyzes a single game with a chess engine, returning move-by-move evaluations.

    Parameters:
        game (chess.pgn.Game): Game to analyze.
        engine_path (str): Path to the UCI engine executable.
        depth (int): Engine analysis depth.

    Returns:
        pandas.DataFrame: DataFrame with columns ['move_number', 'san', 'centipawn', 'win_prob'].
    """
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    board = game.board()
    records = []

    for ply, move in enumerate(game.mainline_moves(), start=1):
        board.push(move)
        cp = engine.analyse(board, limit=chess.engine.Limit(depth=depth))['score'].white().score()
        wp = win_prob_white_position(board, engine, depth)
        records.append({
            'move_number': ply,
            'san': board.san(move),
            'centipawn': cp,
            'win_prob': wp
        })

    engine.quit()
    return pd.DataFrame(records)


def analyse_pgn_file(file_path, engine_path='stockfish', depth=18):
    """
    Analyzes all games in a PGN file.

    Parameters:
        file_path (str): Path to the PGN file.
        engine_path (str): Path to the UCI engine.
        depth (int): Depth for engine analysis.

    Returns:
        pandas.DataFrame: Concatenated DataFrame across all games, with an extra 'game_id' column.
    """
    dfs = []
    for game in parse_pgn(file_path):
        df = analyse_game(game, engine_path, depth)
        game_id = game.headers.get('Event', '') or game.headers.get('Site', '')
        df['game_id'] = game_id
        dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def plot_win_prob(df, game_id=None):
    """
    Plots the win probability over moves for a single DataFrame (single game).

    Parameters:
        df (pandas.DataFrame): DataFrame from analyse_game.
        game_id (str): Optional identifier for plot title.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df['move_number'], df['win_prob'], marker='o')
    plt.xlabel('Ply')
    plt.ylabel('Win Probability for White')
    title = f"Win Probability over Game: {game_id}" if game_id else "Win Probability over Game"
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Analyze a PGN file and plot win probabilities.')
    parser.add_argument('pgn_file', help='Path to the PGN file')
    parser.add_argument('--engine', default='stockfish', help='Path to the UCI engine executable')
    parser.add_argument('--depth', type=int, default=18, help='Engine analysis depth')
    args = parser.parse_args()

    df_all = analyse_pgn_file(args.pgn_file, args.engine, args.depth)
    # Plot only first game as example
    if not df_all.empty:
        first_game_id = df_all.loc[0, 'game_id']
        first_game_df = df_all[df_all['game_id'] == first_game_id]
        plot_win_prob(first_game_df, first_game_id)
