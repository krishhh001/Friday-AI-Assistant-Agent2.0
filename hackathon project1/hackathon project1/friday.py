import os
import subprocess
import pyautogui
import speech_recognition as sr
import pyttsx3
import webbrowser
import openai
import mysql.connector
import datetime
from urllib.parse import quote
import sympy as sp
import re
import traceback
import google.generativeai as genai
import requests

from dotenv import load_dotenv #changed

load_dotenv() #changed

############################################################################################
import os
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "❌ Gemini API key is missing!\n"
        "Please create a .env file in your project folder with:\n"
        "GEMINI_API_KEY=your_actual_key_here"
    )

def gemini_chat(prompt):
    """Send a prompt to Gemini API and return the response text."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract the text from the response
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "⚠ No response text found.")
    
    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP Error: {e}"
    except requests.exceptions.RequestException as e:
        return f"❌ Request failed: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"

###############################################################################################################

# ==== CONFIGURATION ====
# Set your Gemini API key here, or use an environment variable for better security
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDEhh9GqfY5CF1hs0EZb6i4zOIMFcTiqlU')  # <-- Use the GEMINI_API_KEY environment variable

# No genai.configure for older SDKs
# ==== TEXT TO SPEECH ====
engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
# Use the first available voice instead of hardcoding index 2
if voices:
    engine.setProperty('voice', voices[0].id)

def speak(text):
    print(f"Friday: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("[TTS ERROR]", e)

# ==== LISTEN COMMAND ====
def listen_command():
    recognizer = sr.Recognizer()
    try:
        print("🎤 Attempting to access microphone...")
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            command = recognizer.recognize_google(audio)
            print(f"🗣 You said: {command}")
            return str(command).lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
        speak("Couldn't hear you. Please type your command:")
        command = input("Type here: ")
        return command.lower()
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        speak("Couldn't hear you. Please type your command:")
        command = input("Type here: ")
        return command.lower()
    except Exception as e:
        print(f"Microphone error: {e}")
        speak("Couldn't hear you. Please type your command:")
        command = input("Type here: ")
        return command.lower()

# ==== SYSTEM TASK CONTROL ====
def execute_command(command):
    try:
        if "open" in command:
            app_name = command.replace("open", "").strip()
            speak(f"Opening {app_name}")
            pyautogui.hotkey('ctrl', 'esc')  # Open Start menu
            pyautogui.typewrite(app_name)
            pyautogui.press('enter')
        elif "close" in command:
            app_name = command.replace("close", "").strip()
            if "chrome" in app_name:
                speak("Closing Chrome")
                os.system("taskkill /f /im chrome.exe")
            elif "notepad" in app_name:
                speak("Closing Notepad")
                os.system("taskkill /f /im notepad.exe")
            else:
                # Try to close any app by guessing its process name
                exe_name = app_name.replace(" ", "") + ".exe"
                speak(f"Trying to close {app_name} (process: {exe_name})")
                print(f"Trying to close process: {exe_name}")
                result = os.system(f"taskkill /f /im {exe_name}")
                if result != 0:
                    speak(f"Could not close {app_name}. The process {exe_name} may not exist or is named differently.")
        elif "volume up" in command:
            pyautogui.press("volumeup")
            speak("Volume up")
        elif "volume down" in command:
            pyautogui.press("volumedown")
            speak("Volume down")
        elif "mute" in command:
            pyautogui.press("volumemute")
            speak("Volume muted")
    except Exception as e:
        speak("System command failed.")
        print("[System Error]", e)

# ==== MATH SOLVER ====
def solve_math(command):
    try:
        # Remove trigger words and extra spaces
        expression = command.lower().replace("solve", "").replace("calculate", "").strip()
        # Try to parse and evaluate with sympy
        try:
            # Replace common words and symbols
            expression = expression.replace("x", "*").replace("^", "**")
            # Remove 'what is', 'the value of', etc.
            for phrase in ["what is ", "the value of ", "?", "equals", "=", "find "]:
                expression = expression.replace(phrase, "")
            result = sp.sympify(expression)
            speak(f"The answer is {result}")
        except Exception:
            # Fallback: Use OpenAI to solve if sympy fails
            speak("Let me try to solve it using AI.")
            answer = gemini_chat(f"Solve this math problem: {command}")
            answer = answer.strip() if answer else ""
            speak(f"AI says: {answer}")
    except Exception as e:
        speak("Couldn't solve the math problem.")
        print("[Math Error]", e)

# ==== CODE GENERATOR ====
def generate_code(command):
    prompt = f"Write a Python program to {command.replace('code', '').replace('program', '').strip()}"
    try:
        speak("Generating code, please wait.")
        code = gemini_chat(prompt)
        code = code.strip() if code else ""
        speak("Here is the code:")
        print("\n" + code)
    except Exception as e:
        speak("Code generation failed.")
        print("[Gemini Code Error]", e)

# ==== MYSQL SUPPORT ====
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "your_database_name"
}

# Store the current database name globally
current_database = MYSQL_CONFIG["database"]

def connect_mysql(database=None):
    try:
        config = MYSQL_CONFIG.copy()
        if database:
            config["database"] = database
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        speak(f"Database error: {err}")
        return None

# New: Create database and table from user command
def create_database_from_command(command):
    try:
        # Extract the subject (e.g., students, employees)
        subject = command.lower().replace("create a database for", "").replace("create database for", "").replace("create a database", "").replace("create database", "").strip()
        if not subject:
            speak("Please specify what the database is for, like students or employees.")
            return
        db_name = f"friday_{subject.replace(' ', '_')}"
        speak(f"Creating a database for {subject}.")
        # Use OpenAI to generate a table schema
        prompt = f"Generate a MySQL CREATE TABLE statement for a table called {subject} with appropriate columns. Only output the SQL statement."
        sql = gemini_chat(prompt)
        print("[DEBUG] Generated SQL:", sql)
        if not sql:
            speak("Failed to get table schema from AI.")
            print("[DEBUG] No SQL returned from Gemini.")
            return
        sql = sql.strip()
        match = re.search(r'CREATE TABLE (\w+)', sql, re.IGNORECASE)
        table_name = match.group(1) if match else subject
        # Connect to MySQL (no database yet)
        conn = connect_mysql(database=None)
        if not conn:
            speak("Could not connect to MySQL server.")
            print("[DEBUG] MySQL connection failed.")
            return
        cursor = conn.cursor() if conn else None
        if not cursor:
            speak("Could not get MySQL cursor.")
            conn.close()
            print("[DEBUG] MySQL cursor failed.")
            return
        # Create database
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        except Exception as e:
            speak("Failed to create database.")
            print("[DEBUG] Exception during CREATE DATABASE:", e)
            traceback.print_exc()
            cursor.close()
            conn.close()
            return
        cursor.close()
        conn.close()
        # Now connect to the new database and create the table
        conn2 = connect_mysql(database=db_name)
        if not conn2:
            speak(f"Could not connect to the new database {db_name}.")
            print(f"[DEBUG] Connection to new database {db_name} failed.")
            return
        cursor2 = conn2.cursor()
        try:
            cursor2.execute(sql)
            conn2.commit()
        except Exception as e:
            speak("Failed to create table. Check the SQL syntax.")
            print("[DEBUG] Exception during CREATE TABLE:", e)
            print("[DEBUG] SQL attempted:", sql)
            traceback.print_exc()
            cursor2.close()
            conn2.close()
            return
        cursor2.close()
        conn2.close()
        global current_database
        current_database = db_name
        speak(f"Database '{db_name}' and table '{table_name}' created. Now using this database.")
    except Exception as e:
        speak("Failed to create database or table.")
        print("[Create DB Error]", e)
        traceback.print_exc()

def handle_mysql_query(command):
    try:
        conn = connect_mysql(database=current_database)
        if not conn:
            return
        cursor = conn.cursor()
        sql = command.replace("run query", "").replace("mysql", "").strip()
        cursor.execute(sql)
        if sql.lower().startswith("select"):
            results = cursor.fetchall()
            if results:
                for row in results[:5]:
                    print(row)
                    speak(str(row))
            else:
                speak("Query ran successfully. No results.")
        else:
            conn.commit()
            speak("Query executed successfully.")
        cursor.close()
        conn.close()
    except Exception as e:
        speak("Failed to run SQL command.")
        print("[MySQL Error]", e)

def nl_to_sql(command):
    speak("Translating your request into SQL...")
    try:
        table_info = f"Assume the database has tables relevant to the current context."
        prompt = f"{table_info} Convert the following request to SQL: {command}"
        sql = gemini_chat(prompt)
        sql = sql.strip() if sql else ""
        print("SQL Generated:", sql)
        handle_mysql_query("run query " + sql)
    except Exception as e:
        speak("Couldn't translate to SQL.")
        print("[NL to SQL Error]", e)

# ==== WEB SEARCH / AI QUERY ====
def handle_query(command):
    try:
        if "search" in command:
            query = command.replace("search", "").strip().replace(" ", "+")
            speak(f"Searching for {query}")
            url = f"https://www.google.com/search?q={quote(query)}"
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            if os.path.exists(chrome_path):
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
                webbrowser.get('chrome').open_new_tab(url)
            else:
                webbrowser.open_new_tab(url)
        else:
            speak("Let me find the answer for you.")
            try:
                answer = gemini_chat(command)
                answer = answer.strip() if answer else ""
                speak(answer)
                print("Gemini Answer:", answer)
            except Exception as e:
                speak("Something went wrong with Gemini.")
                print("[Gemini Error]", e)
                import traceback
                traceback.print_exc()
    except Exception as e:
        speak("Something went wrong with Gemini.")
        print("[Gemini Error]", e)
        import traceback
        traceback.print_exc()

def gemini_chat(prompt, system=None, timeout=15):
    api_key = GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1000
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=timeout)
        resp.raise_for_status()
        result = resp.json()
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print("[Gemini REST Error]", e)
        import traceback
        traceback.print_exc()
        return None

# ==== MAIN LOOP ====
def main():
    print("Starting Friday voice assistant...")
    try:
        speak("Hello, I am Friday. How can I assist you?")
        print("Friday is ready to listen!")
        while True:
            command = listen_command()
            if not command:
                continue
            elif "exit" in command or "stop" in command:
                speak("Goodbye!")
                break
            elif command.startswith("create a database") or command.startswith("create database"):
                create_database_from_command(command)
            elif any(word in command for word in ["open", "close", "volume"]):
                execute_command(command)
            elif "solve" in command or "calculate" in command or any(char.isdigit() for char in command):
                solve_math(command)
            elif "code" in command or "program" in command:
                generate_code(command)
            elif "run query" in command or "mysql" in command:
                handle_mysql_query(command)
            elif "database" in command or "sql" in command:
                nl_to_sql(command)
            else:
                handle_query(command)
    except Exception as e:
        print(f"Error in main loop: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

