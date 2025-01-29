import random
from datetime import datetime
from fc_pydantic_agent import DynamicAgent

def main():
    system_prompt = (
        "You're a dice game assistant. Roll a six-sided die and compare "
        "the result to the user's guess. If they match, declare the user a winner."
    )
    
    agent = DynamicAgent("ollama", system_prompt)
    
    # Game tools
    def roll_die() -> str:
        return str(random.randint(1, 6))
    
    def get_player_name(ctx) -> str:
        return ctx.deps.get("player_name", "Player")
    
    # Register tools
    agent.add_tool(roll_die, "tool_plain")
    agent.add_tool(get_player_name, "tool")
    
    # Game loop
    while True:
        try:
            user_input = input("Enter a number between 1-6 (or 'exit'): ")
            if user_input.lower() == 'exit':
                break
                
            response = agent.interact_with_model(
                user_input,
                deps={"player_name": "FC Player"}
            )
            print(f"\nGame Result: {response}\n")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()