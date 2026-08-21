# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import os

from openai import OpenAI


def test_open_ai_api_key():
    """
    Method to test the OpenAI API key.
    Reads the OpenAI API key from an environment variable,
    Creates a client, and submits a simple query ("What's the capital of France?").
    The response should include the word "Paris".
    Any exceptions (Invalid API Key, OpenAI access being blocked, etc.) are reported.
    :return: Nothing
    """

    # Set up the client with your API key
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        # Make a chat completion request
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the capital of France?"},
            ],
        )

        # Print the assistant's reply
        print("Successful call to OpenAI")
        print(f"response: {response.choices[0].message.content}")

    except Exception as e:
        print("Failed call to OpenAI. Exception:")
        print(e)


if __name__ == "__main__":
    test_open_ai_api_key()
