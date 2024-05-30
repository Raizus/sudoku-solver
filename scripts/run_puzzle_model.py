
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.puzzle2model import puzzle2model


if __name__ == "__main__":
    path = "./data/Solved/2DWaveParticles_by_zetamath.json"
    puzzle = Puzzle.fromJSON(path)

    puzzle_model = puzzle2model(puzzle)
