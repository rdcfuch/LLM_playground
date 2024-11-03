import openai
from openai import OpenAI


MODEL = "llama3.1:70b"
MODEL_BASE_URL = 'http://127.0.0.1:11436/v1'  # use my server
API_KEY_SET = 'ollama'
SYS_PROMT={"role": "system",
         "content": """
         ## role
         you are a prompt expert who can help to add tags to a prompt

        ## skill
        you will review the input prompt and add key tags to it based on it's contents

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
         """}


def prompt_rewrite(input_msg):
    user_model = MODEL
    user_messages = [
        SYS_PROMT,
        # {"role": "user", "content": "Who won the world series in 2020?"},
        # {"role": "assistant", "content": "The LA Dodgers won in 2020."},
        {"role": "user", "content": input_msg}
    ]
    client = client = OpenAI(
        base_url=MODEL_BASE_URL,  # <<<<< you need to do the port mapping kuberate desktop in VScode
        api_key=API_KEY_SET,  # required, but unused
    )
    response = client.chat.completions.create(
        model=user_model,
        messages=user_messages,

        # tools=tools,
        # tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message.content
    # print(response_message)
    return response_message

if __name__ == '__main__':
    summary = prompt_rewrite(f"generate new prompt for 'A mystical forest with ancient trees twisted into intricate shapes, glowing mushrooms illuminating the path, and mythical creatures roaming freely.'")
    print(summary)
