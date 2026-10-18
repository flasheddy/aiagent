import os

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

    # Get a reponse
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum.",
            }
        ]
    )

    # Acess the response message content
    print(response.choices[0].message.content)



if __name__ == "__main__":
    main()
