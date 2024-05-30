
from puzzledraw.puzzledraw import puzzledraw
from puzzlesolver.Puzzle.Puzzle import Puzzle


if __name__ == "__main__":
    path = "./data/Solved/400kSubscribers_by_PjotrV.json"
    puzzle = Puzzle.fromJSON(path)

    puzzledraw(puzzle)
