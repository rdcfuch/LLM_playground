from openai import OpenAI
import json
import inspect
from duckduckgo_search import DDGS
import requests


def search_internet(search_query: str) -> list:
    results = DDGS().text(str(search_query), max_results=5)
    return results


def get_exchange_rate(base_currency: str, target_currency: str, date: str = "latest") -> float:
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency.lower()}.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get(base_currency.lower(), {}).get(target_currency.lower(), None)
    else:
        raise Exception(f"Failed to fetch exchange rate: {response.status_code}")


first_tools = [
        # Tool 1 - Get Exchange Rate
        {
            "type": "function",
            "function": {
                "name": "get_exchange_rate",
                "description": "Get the current exchange rate of a base currency and target currency",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base_currency": {
                            "type": "string",
                            "description": "The base currency for exchange rate calculations, i.e. USD, EUR, RUB",
                        },
                        "target_currency": {
                            "type": "string",
                            "description": "The target currency for exchange rate calculations, i.e. USD, EUR, RUB"
                        },
                        "date": {
                            "type": "string",
                            "description": "A specific day to reference, in YYYY-MM-DD format."
                        },
                    },
                    "required": ["base_currency", "target_currency"],
                },
            },
        },
        # Tool 2 - Search Internet
        {
            "type": "function",
            "function": {
                "name": "search_internet",
                "description": "Get internet search results for real time information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "The query to search the web for",
                        }
                    },
                    "required": ["search_query"],
                },
            },
        }
    ]


# Main conversation function
def run_conversation(prompt, tools, input_tool_choice="auto"):
    messages = [{"role": "user", "content": prompt}]

    print("\nInitial Message: ", messages)

    client = OpenAI(
        api_key='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'
    )
    # Send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice=input_tool_choice,
    )
    response_message = response.choices[0].message
    print("\nResponse Message: ", response_message)

    tool_calls = response_message.tool_calls
    print("\nTool Calls: ", tool_calls)

    # Check if the model wanted to call a function
    if tool_calls:

        # Call the functions
        available_functions = {
            "get_exchange_rate": get_exchange_rate,
            "search_internet": search_internet,
        }
        # extend conversation with assistant's reply
        messages.append(response_message)

        # Call the function and add the response
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            # Get the function signature and call the function with given arguments
            sig = inspect.signature(function_to_call)
            call_args = {
                k: function_args.get(k, v.default)
                for k, v in sig.parameters.items()
                if k in function_args or v.default is not inspect.Parameter.empty
            }
            print(f"\nCalling {function_to_call} with arguments {call_args}")

            function_response = str(function_to_call(**call_args))

            print("\nFunction Response: ", function_response)

            # Put output into a tool message
            tool_message = {
                "tool_call_id": tool_call.id,  # Needed for Parallel Tool Calling
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
            print("\nAppending Message: ", tool_message)

            # Extend conversation with function response
            messages.append(tool_message)

            # Get a new response from the model where it can see the entire conversation including the function call outputs
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        print("\nLLM Response: ", second_response)

        print("\n---Formatted LLM Response---")
        print("\n", second_response.choices[0].message.content)

        return


prompt = "How much is a dollar worth in Japan? How about poland? Whats the current news in Argentina?"

run_conversation(prompt, first_tools)
