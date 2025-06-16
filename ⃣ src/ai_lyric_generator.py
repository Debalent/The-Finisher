import openai
import os

# Secure API key retrieval
openai.api_key = os.getenv("OPENAI_API_KEY")  

def generate_lyrics(prompt):
    """Generate lyrics based on the user's prompt using OpenAI's GPT model."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating lyrics: {str(e)}"

# Example usage with user input
if __name__ == "__main__":
    genre = input("Enter a genre: ").strip()
    topic = input("Enter a theme for the song: ").strip()
    prompt = f"Write a {genre} song verse about {topic}."
    
    lyrics = generate_lyrics(prompt)
    print("\nGenerated Lyrics:\n", lyrics)
