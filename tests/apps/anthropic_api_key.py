# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import os

import anthropic


def test_anthropic_api_key():
    """
    Method to test the Anthropic API key.
    Reads the Anthropic API key from an environment variable,
    Creates a client, and submits a simple query ("What's the capital of France?").
    The response should include the word "Paris".
    Any exceptions (Invalid API Key, Anthropic access being blocked, etc.) are reported.
    :return: Nothing
    """

    # Set your Anthropic details
    api_key = os.getenv("ANTHROPIC_API_KEY")  # or use a string directly

    # Set `model` to the model you want to use, e.g., "claude-opus-4-20250514"
    model = "claude-opus-4-20250514"

    # Create an Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Set up the client with your API key
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": [{"type": "text", "text": "What's the capital of France?"}]}],
        )

        # Print the assistant's reply
        print("Successful call to Anthropic")
        print(f"response: {message.content[0].text}")

    except Exception as e:
        print("Failed call to Anthropic. Exception:")
        print(e)


if __name__ == "__main__":
    test_anthropic_api_key()
