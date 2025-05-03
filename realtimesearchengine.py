from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

# Retrieve API key and assistant details
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} with real-time information access.
*** Do not tell the time until I ask. ***
*** Always reply in English, even if the question is in Hindi. ***
*** Do not provide notes or mention your training data. ***
"""

# Load chat history
try:
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
except:
    messages = []

def GoogleSearch(query):
    results = search(query, num_results=5)
    Answer = f"Search results for '{query}':\n[start]\n"
    for i in results:
        Answer += f"URL: {i}\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
]

def Information():
    current_date_time = datetime.datetime.now()
    return f"Date: {current_date_time.strftime('%Y-%m-%d')}, Time: {current_date_time.strftime('%H:%M:%S')}"

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Append user's query to chat log
    messages.append({"role": "user", "content": prompt})

    # Add search results to context
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
    )

    Answer = ""
    for chunk in completion:
        if hasattr(chunk.choices[0], "message") and chunk.choices[0].message.content:
            Answer += chunk.choices[0].message.content

    Answer = Answer.replace("</s>", "").strip()

    # Append AI response to chat log
    messages.append({"role": "assistant", "content": Answer})

    # Save updated chat history
    with open(r"Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))



