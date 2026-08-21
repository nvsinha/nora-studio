# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

import os

from google import genai


def test_gemini_api_key():
    """
    Method to test the Gemini API key.
    Reads the Gemini API key from an environment variable,
    Creates a client, and submits a simple query ("What's the capital of France?").
    The response should include the word "Paris".
    Any exceptions (Invalid API Key, Gemini access being blocked, etc.) are reported.
    :return: Nothing
    """

    # Set your Gemini details
    api_key = os.getenv("GOOGLE_API_KEY")  # or use a string directly
    model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-3-flash-preview")  # e.g., "gemini-3-flash-preview"

    try:
        # Create a Gemini model client with a Gemini API key and send a simple prompt
        client = genai.Client(api_key=api_key)  # Or just use: "your-key-here"
        response = client.models.generate_content(model=model_name, contents="What's the capital of France?")

        print("Successful call to Gemini")
        print(response.text)

    except Exception as e:
        print("Failed call to Gemini. Exception:")
        print(e)


if __name__ == "__main__":
    test_gemini_api_key()
