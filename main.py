import argparse
import os
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI


def main():
    # Get API key
    _ = load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Please configure the right api_key")

    # Initiate a client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    # Parse user argument
    parser = argparse.ArgumentParser(description="AI Code Assistance")
    _ = parser.add_argument("user_prompt", type=str, help="Prompt to send to the LLM")
    args = parser.parse_args()
    prompt = cast(str, args.user_prompt) # args.user_prompt is Any

    # Get a reponse
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    # Acess the communication token usage
    if not response.usage:
        raise RuntimeError("The API response appears to be malformed")
    print(f"User prompt: {prompt}")
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Response tokens: {response.usage.completion_tokens}")

    # Acess the response message content
    print(f"Response:{response.choices[0].message.content}")



if __name__ == "__main__":
    main()
