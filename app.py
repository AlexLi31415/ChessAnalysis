import streamlit as st
import os
from pgn_analysis import analyse_pgn_file
import pandas as pd

# Cache analysis to speed up repeated runs
@st.cache(show_spinner=False)
def load_and_analyse(pgn_bytes, engine_path='stockfish', depth=18):
    # Write uploaded bytes to a temporary file
    tmp_path = 'upload.pgn'
    with open(tmp_path, 'wb') as f:
        f.write(pgn_bytes)
    # Analyse PGN and return DataFrame
    df = analyse_pgn_file(tmp_path, engine_path=engine_path, depth=depth)
    # Clean up
    try:
        os.remove(tmp_path)
    except OSError:
        pass
    return df


def main():
    st.set_page_config(page_title="Chess Analysis Dashboard", layout="wide")
    st.title("📊 Chess Analysis Dashboard")

    st.sidebar.header("Settings")
    engine = st.sidebar.text_input("Path to engine", value="stockfish")
    depth = st.sidebar.slider("Engine depth", 8, 24, 18, step=2)

    uploaded_file = st.file_uploader("Upload a PGN file", type=['pgn'])
    if not uploaded_file:
        st.info("Upload a .pgn file to start analysis.")
        return

    # Perform analysis
    bytes_data = uploaded_file.getvalue()
    df = load_and_analyse(bytes_data, engine_path=engine, depth=depth)

    if df.empty:
        st.error("No games found in the PGN.")
        return

    # Select game
    game_ids = df['game_id'].unique().tolist()
    game_id = st.selectbox("Select Game", game_ids)
    game_df = df[df['game_id'] == game_id]

    # Show DataFrame
    st.subheader(f"Move-by-Move Analysis: {game_id}")
    st.dataframe(game_df[['move_number', 'san', 'centipawn', 'win_prob']])

    # Plot win probability
    st.subheader("Win Probability Over Game")
    chart_data = game_df.set_index('move_number')['win_prob']
    st.line_chart(chart_data)

    # Centipawn losses
    st.subheader("Centipawn Evaluation Over Game")
    st.line_chart(game_df.set_index('move_number')['centipawn'])

    # Download results
    csv = game_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name=f"analysis_{game_id}.csv", mime='text/csv')


if __name__ == '__main__':
    main()
