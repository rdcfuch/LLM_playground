import openai
from typing import Optional, Dict, Any
from openai import OpenAI


def generate_open_ai_llm_response(
        user_message: str,
        api_key: Optional[
            str] = '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',
        input_model: str = "gpt-3.5-turbo",
        input_temperature: float = 0.7,
        input_max_tokens: int = 500,
        additional_params: Optional[Dict[str, Any]] = None,
        input_base_url: str = '',
) -> str:
    """
    Generate a response from an OpenAI Large Language Model.

    Parameters:
    - user_message (str): The input message to send to the LLM
    - api_key (str, optional): OpenAI API key. If not provided, uses environment variable.
    - model (str, optional): The OpenAI model to use. Defaults to "gpt-3.5-turbo".
    - temperature (float, optional): Controls randomness of output. Defaults to 0.7.
    - max_tokens (int, optional): Maximum number of tokens in the response. Defaults to 500.
    - additional_params (dict, optional): Additional parameters to pass to the API call

    Returns:
    - str: The generated response from the LLM
    """
    # Set the API key

    # Prepare the default parameters

    try:
        if input_base_url:
            client = OpenAI(
                api_key="ollama",
                base_url=input_base_url,
            )
        else:
            client = OpenAI(
                api_key=api_key,
            )
        # Make the API call
        response = client.chat.completions.create(
            model=input_model,
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=input_temperature,
            max_tokens=input_max_tokens,
        )

        # Extract and return the model's response
        return response.choices[0].message.content

    except Exception as e:
        # Handle potential errors
        return f"An error occurred: {str(e)}"


# Example usage
if __name__ == "__main__":
    try:
        response = generate_open_ai_llm_response("who are you",input_model="llama3.2",input_base_url="http://localhost:11434/v1")
        print(response)


    except Exception as e:
        print(f"Failed to generate response: {e}")
