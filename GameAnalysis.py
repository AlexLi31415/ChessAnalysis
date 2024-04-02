import pandas as pd
from math import exp
import numpy as np
import scipy.stats as sps
import matplotlib.pyplot as plt
import chess
import chess.pgn
import chess.engine

def win_prob_lichess(centipawns):
    return 0.5 + 0.5 * (2 / (1 + exp(-0.00368208 * centipawns)) - 1)