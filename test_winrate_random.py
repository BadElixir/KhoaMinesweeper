import time
from main import Game, CustomNotif
from AI import solve

def run_simulation(games_to_play=100, board_size=8, bomb_count=10):
    wins = 0
    losses = 0
    errors = 0
    
    print(f"Starting test for {games_to_play} games | Size: {board_size}x{board_size} | Bombs: {bomb_count}...")
    start_time = time.time()

    for i in range(games_to_play):
        game = Game(board_size=board_size, bomb_count=bomb_count)
        game_status = "PLAYING"
        
        while not game.game_over:
            board = game.get_board_state()
            action, r, c = solve(board, game.available_flags)
            
            if action == "none":
                # AI could not find a move (Should not happen due to random fallback)
                errors += 1
                break
                
            if action == "reveal":
                result = game.reveal(r, c)
                if result == CustomNotif.GAME_WON:
                    wins += 1
                    game_status = "WON"
                elif result == CustomNotif.FOUND_BOMB:
                    losses += 1
                    game_status = "LOST"
                    
            elif action == "flag":
                game.flag(r, c)

        # Show progress every 10 games
        if (i + 1) % 10 == 0:
            print(f"Played {i + 1}/{games_to_play} games...")

    end_time = time.time()
    total_time = end_time - start_time
    win_rate = (wins / games_to_play) * 100

    print("\n" + "="*40)
    print("📊 WINRATE TEST RESULTS")
    print("="*40)
    print(f"Games played: {games_to_play}")
    print(f"Wins:         {wins}")
    print(f"Losses:       {losses}")
    print(f"Errors/Stuck: {errors}")
    print(f"Win rate:     {win_rate:.2f}%")
    print(f"Total time:   {total_time:.2f} seconds")
    print(f"Avg speed:    {total_time/games_to_play:.3f} seconds/game")
    print("="*40)

if __name__ == "__main__":
    # You can change these parameters to test different difficulties
    run_simulation(games_to_play=100, board_size=16, bomb_count=40)