import openai

openai.api_key = "your-api-key"

def generate_lyrics(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Example usage
genre = "R&B"
prompt = f"Write a {genre} song verse about heartbreak."
lyrics = generate_lyrics(prompt)
print(lyrics)
