import ollama
from chainlit import Chainlit

MODEL = "llama3.2"
SYS_PROMPT = {
    "role": "system",
    "content": """
        ## role
        you are a prompt expert who can help to add tags to a prompt

        ## skill
        you will review the input prompt and add key tags to it based on its contents

        ## constraints
        - you will output the prompt according to the example format
        - you only output the prompt, don't output any other information

        ## example
        input prompt: "This video depicts a cat with brown hairs and a white apron washing dishes with its paws, 
                        we can see the head of the cat, the water is flowing rapidly, the dish is white and made of china, 
                        the background is a kitchen, the cat looks very happy"
        output prompt: caption: [
  {
    "description": "This video depicts a cat with brown hairs and a white apron washing dishes with its paws, we can see the head of the cat, the water is flowing rapidly, the dish is white and made of china, the background is a kitchen, the cat looks very happy",
    "tags": [
      "cat",
      "dishwashing",
      "faucet",
      "kitchen"
    ]
  }
]
    """
}

def prompt_rewrite(input_msg):
    chain = Chainlit(models=["lmstudio-community/c4ai-command-r-08-2024-GGUF"])
    user_messages = [
        SYS_PROMPT,
        {"role": "user", "content": input_msg}
    ]
    response = chain.predict(user_messages)
    return response
    
if __name__ == '__main__':
    summary = prompt_rewrite(
        "generate new prompt for 'A mystical forest with ancient trees twisted into intricate shapes, glowing mushrooms illuminating the path, and mythical creatures roaming freely.'"
    )
    print("\nFull response received:")
    print(summary)
