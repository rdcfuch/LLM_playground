from openai import OpenAI
import gradio as gr

client = OpenAI(
    # base_url = 'http://192.168.1.199:11434/v1',
    base_url = 'http://127.0.0.1:11435/v1', # <<<<< you need to do the port mapping kuberate desktop in VScode
    api_key='ollama', # required, but unused
)

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})




def chat(message):
    user_model="llama3:70b"
    user_messages = [
        {"role": "system", "content": 'You are a helpful assistant. who can use function call to get the weather information if needed, if you can not find the information, just answer "I don not know"'},
        # {"role": "user", "content": "Who won the world series in 2020?"},
        # {"role": "assistant", "content": "The LA Dodgers won in 2020."},
        {"role": "user", "content": message}
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=user_model,
        messages=user_messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message=response.choices[0].message
    print(response_message.tool_calls)
    # Step 2: check if the model wanted to call a function
    if response_message.tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        user_messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            user_messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=user_model,
            messages=user_messages,
        )  # get a new response from the model where it can see the function response
        print("2nd response")
        return second_response.choices[0].message
    return response_message.content


# Create a Gradio interface
interface = gr.Interface(
  fn=chat,
  inputs="text",
  outputs="text",
  title="Basic Chatbot",
  description="Enter a message and chat with the basic bot!"
)

# Launch the Gradio interface
# interface.launch()
print(chat("get Tokyo weather for 2024.Jun.27"))
