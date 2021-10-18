import model as Game
import time

def time_took(f):
    def r(*args,**kwargs):
        start_time = time.time()
        solved_g = f(*args,**kwargs)
        print(f"Solving took: {time.time() - start_time:.2f}s...\n")
        return solved_g
    return r

@time_took
def solve(game):
    # LS
    game.heuristic()
    # INIT
    GAME_HISTORY = set()

    # SOLVE LOOP
    while (len(game) != 0) and not game.is_solved():
        current_game = game
        while (len(current_game)!=0) and  not game.is_solved() and str(current_game) not in GAME_HISTORY:
            current_game = Game.constructor_from_grid(*game.extract_conf())
            current_game.random_tent()
            GAME_HISTORY.add(str(current_game))
            current_game.heuristic()

        if str(current_game) in GAME_HISTORY:
            print('Skipped... back to start')
        if not current_game.is_solved():
            print('Reached invalid state, restarting...')
        if (len(current_game) == 0) and (current_game.is_solved()):
            print('Solved !')
            game = current_game
        # ELSE THROW AWAY AND RETRY
    return game
