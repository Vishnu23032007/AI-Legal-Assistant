import os
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct",  # you can change model if needed
        messages=[
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        max_tokens=50
    )

    print("✅ API is working!")
    print("Response:", response.choices[0].message.content)

except Exception as e:
    print("❌ API is NOT working")
    print("Error:", str(e))