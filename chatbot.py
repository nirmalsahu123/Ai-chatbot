from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# Retrieve API key and assistant details
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "AI Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("Groq API key not found in .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Define system prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, 
which has real-time up-to-date information from the internet.
*** Provide answers in a professional way. Use correct grammar, punctuation, and sentence structure. ***
*** Just answer the question based on the provided data in a professional manner. ***"""

SystemChatBot = [{"role": "system", "content": System}]

# Load chat history
try:
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data/ChatLog.json", "w") as f:
        dump([], f, indent=4)

# Function to get real-time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    # Format the information into a string
    data = (
        f"Please use this real-time information if needed:\n"
        f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
        f"Time: {hour} hours, {minute} minutes, {second} seconds\n"
    )
    return data

# Function to clean up AI response
def AnswerModifier(Answer):
    """Removes empty lines from the response."""
    lines = Answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Chatbot function
def ChatBot(query):
    """Handles the chat and returns AI-generated response."""
    try:
        # Load chat history
        with open(r"Data/ChatLog.json", "r") as f:
            messages = load(f)

        # Append user query
        messages.append({"role": "user", "content": f"{query}"})

        # Make a request to the Groq API
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # AI model to use
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False,  # Set to False for non-streaming
        )

        # Retrieve response
        Answer = completion.choices[0].message.content if completion.choices else "No response from AI."

        # Remove unnecessary symbols
        Answer = Answer.replace("</s>", "").strip()

        # Append AI response to chat log
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat history
        with open(r"Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)
    
    except Exception as e:
        print(f"Error: {e}")

        # Reset chat log in case of errors
        with open(r"Data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        
        return "An error occurred. Please try again."

# Run chatbot in a loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        print(ChatBot(user_input))

