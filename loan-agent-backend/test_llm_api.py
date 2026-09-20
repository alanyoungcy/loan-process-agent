"""Test the LLM API endpoint directly"""
import asyncio
import os
from openai import AsyncOpenAI

async def test_api():
    client = AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )

    try:
        print("Testing OpenAI API endpoint...")
        print(f"Base URL: {client.base_url}")
        print(f"API Key: {client.api_key[:20]}...")
        print()

        response = await client.chat.completions.create(
            model="gpt-5.6-terra",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            temperature=0.7,
            max_tokens=50
        )

        print(f"Response type: {type(response)}")
        print(f"Response: {response}")

        if hasattr(response, 'choices'):
            print(f"\nContent: {response.choices[0].message.content}")
        else:
            print(f"\nRaw response: {str(response)[:500]}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_api())
