import time
import datetime
import json
import yfinance as yf  # <-- Fetch real-time stock data
from dotenv import dotenv_values
from groq import Groq
from googlesearch import search

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq API client
client = Groq(api_key=GroqAPIKey)

# System Prompt
System = f"""Hello, I am {Username}, and you are {Assistantname}, an advanced AI assistant.
*** Reply professionally, use correct grammar, and do not provide notes. ***
*** Always respond in English, even if the question is in Hindi. ***
"""

# Load chat history
try:
    with open("Data/ChatLog.json", "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []

# Function to get real-time date and time
def get_realtime_info():
    now = datetime.datetime.now()
    return f"Real-time info: {now.strftime('%A, %B %d, %Y, %H:%M:%S')}"

# Function to fetch stock price
def get_stock_price(company_name):
    """Fetch stock price directly from Yahoo Finance"""
    try:
        stock = yf.Ticker(company_name)
        history = stock.history(period="1d")
        
        if history.empty:
            return f"Stock symbol '{company_name}' not found. Please check manually."
        
        price = history["Close"].iloc[-1]  # Get last closing price
        return f"Current stock price of {company_name}: ₹{price:.2f}"
    
    except Exception as e:
        return f"Error fetching stock price for '{company_name}': {str(e)}"

# Function to perform a Google Search with delay
def google_search(query):
    try:
        results = list(search(query, num_results=5))
        time.sleep(2)  # Delay to avoid 429 errors
        response = "Search results:\n"
        for i, result in enumerate(results, 1):
            response += f"{i}. {result.title}\n{result.description}\n\n"
        return response.strip()
    except Exception as e:
        return f"Google Search Error: {str(e)}"

# AI Chatbot Function
def chatbot(query):
    global messages

    if not query.strip():
        return "You didn't enter anything! Please type your query."

    messages.append({"role": "user", "content": query})

    # Check if the query is about stock prices
    if "stock price of" in query.lower():
        company_name = query.replace("stock price of", "").strip().upper()  # Extract company name
        return get_stock_price(company_name)

    # Perform Google search and get AI response
    search_results = google_search(query)

    # Prepare system instructions
    system_messages = [
        {"role": "system", "content": System},
        {"role": "system", "content": get_realtime_info()},
        {"role": "system", "content": search_results},
    ]

    # Request AI response
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=system_messages + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
        )

        answer = ""
        for chunk in completion:
            content = getattr(chunk.choices[0].delta, "content", "")
            if content:
                answer += content

    except Exception as e:
        return f"Error generating AI response: {str(e)}"

    answer = answer.replace("</s>", "").strip()
    messages.append({"role": "assistant", "content": answer})

    # Save chat history
    with open("Data/ChatLog.json", "w") as f:
        json.dump(messages, f, indent=4)

    return answer

# Run the chatbot
if __name__ == "__main__":
    while True:
        user_input = input("Enter your query: ")
        print(chatbot(user_input))
