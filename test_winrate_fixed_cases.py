import time
import random
from main import Game, CustomNotif
from AI import solve

def run_intermediate_simulation(games_to_play=50, base_seed=2000):
    # Cấu hình mức Intermediate
    BOARD_SIZE = 16
    BOMB_COUNT = 40
    FIRST_CLICK = (0, 0)
    
    wins = 0
    losses = 0
    errors = 0
    
    print(f"--- INTERMEDIATE TEST (16x16, 40 Bombs) ---")
    print(f"Base Seed: {base_seed} | Games: {games_to_play}")
    
    start_time = time.time()

    for i in range(games_to_play):
        random.seed(base_seed + i) 
        game = Game(board_size=BOARD_SIZE, bomb_count=BOMB_COUNT)
        
        while not game.game_over:
            board = game.get_board_state()
            is_first_move = all(all(cell is None for cell in row) for row in board)
            
            if is_first_move:
                action, r, c = ("reveal", FIRST_CLICK[0], FIRST_CLICK[1])
            else:
                action, r, c = solve(board, game.available_flags)
            
            if action == "none":
                errors += 1
                break
                
            if action == "reveal":
                result = game.reveal(r, c)
                if result == CustomNotif.GAME_WON:
                    wins += 1
                elif result == CustomNotif.FOUND_BOMB:
                    losses += 1
            elif action == "flag":
                game.flag(r, c)

        if (i + 1) % 5 == 0:
            print(f"Progress: {i + 1}/{games_to_play} games finished...")

    end_time = time.time()
    win_rate = (wins / games_to_play) * 100

    print("\n" + "="*40)
    print(f"📊 INTERMEDIATE RESULTS")
    print("="*40)
    print(f"Wins:         {wins}")
    print(f"Losses:       {losses}")
    print(f"Win rate:     {win_rate:.2f}%")
    print(f"Total Time:   {end_time - start_time:.2f}s")
    print(f"Avg Speed:    {(end_time - start_time)/games_to_play:.2f}s/game")
    print("="*40)

if __name__ == "__main__":
    run_intermediate_simulation(games_to_play=100, base_seed=100)