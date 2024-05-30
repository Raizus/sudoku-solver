
from puzzlesolver.SolvePuzzle import SolverOptions, solve_puzzle

if __name__ == '__main__':
    filepath = "./data/Solved/CrossAboutDominoes_by_FullDeckandMissingAFewCards.json"
    filepath = "./data/Solved/Ludoku_by_questionable_compensation.json"
    filepath = "./data/Solved/JustSumAmbiguity_by_SSG.json"

    filepath = "./data/NotImplemented/BorderSquareDiagonals_by_Phistomefel.json"
    # filepath = "./data/Solved/BalancedChaos_by_fritzdis.json"

    options = SolverOptions(log_solutions=True, max_time=3600)
    solve_puzzle(filepath, options)
