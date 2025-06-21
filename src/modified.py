import subprocess
import datetime
import webbrowser
import wikipedia
import speech_recognition as sr
import os
import random
import threading
import time
import requests
from tts import get_text , play_audio , speak
from ollama import ask_ollama
import threading

# === Initialize Text-to-Speech ===
# engine = pyttsx3.init()
# engine.setProperty('rate', 160)
# voices = engine.getProperty('voices')
# if voices:
#     engine.setProperty('voice', voices[0].id)


def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 0.
        audio = recognizer.listen(source, phrase_time_limit=4) 
    try:
        command = recognizer.recognize_google(audio, language='en-US')
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech service is unavailable.")
        return ""

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")

def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)  # Up to 3 sentences for fuller answers
        speak(f"According to Wikipedia: {summary}")
    except wikipedia.DisambiguationError:
        speak("That has multiple meanings. Could you please be more specific?")
    except wikipedia.PageError:
        speak("I couldn't find any Wikipedia page for that topic.")
    except Exception:
        speak("I am having trouble accessing Wikipedia right now.")

def open_google(query):
    url = f"https://www.google.com/search?q={query}"
    speak(f"Searching Google for {query}")
    webbrowser.open(url)

def open_youtube():
    speak("Opening YouTube")
    webbrowser.open("https://www.youtube.com")

def play_music():
    music_folder = r"C:\Users\ABHAYA\apci\shaky"
    if not os.path.exists(music_folder):
        speak("Music folder not found.")
        return

    songs = [file for file in os.listdir(music_folder) if file.endswith(('.mp3', '.wav'))]
    if not songs:
        speak("No music files found in the folder.")
        return

    song_to_play = random.choice(songs)
    song_path = os.path.join(music_folder, song_to_play)
    speak(f"Playing {song_to_play}.")

    try:
        # Initialize mixer
        pygame.mixer.init()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0)  # Ensure it plays only once

        # Wait until either song finishes or 30 seconds pass
        start_time = time.time()
        while pygame.mixer.music.get_busy():
            if time.time() - start_time > 30:
                break
            time.sleep(1)

        # Force stop after 30 seconds or when done
        pygame.mixer.music.stop()
        pygame.mixer.quit()  # Important: release the audio device
    except Exception as e:
        speak(f"Failed to play music due to error: {e}")


    def play_and_stop():
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        time.sleep(30)  # Play for 30 seconds without blocking main thread
        pygame.mixer.music.stop()

    threading.Thread(target=play_and_stop, daemon=True).start()

# === Dictionary of Q&A ===
qa_dictionary = {
    "who are you": "Hello, I’m CYRUS, your cognitive AI support system.",
    "what is your name": "I am called Cyrus, your assistant.",
    "who created you": "I was created by a talented student team at Government College of Engineering Kannur.",
    "what can you do": "I can tell the time, search Wikipedia, open Google or YouTube, play music, answer questions, and much more.",
    "hi hello": "Hello! How can I help you today?",
    "hello": "Hello! How can I help you today?",
    "hey": "Hello! How can I help you today?",
    "hi": "Hi there! I'm ready to assist you.",
    "how are you": "I'm functioning perfectly. Thanks for asking!",
    "tell me a joke": "Why don’t programmers like nature? It has too many bugs! Haha.",
    "what is python": 
        "Python is a powerful, high-level programming language used for web development, "
        "data science, automation, and more. It’s known for its readability and versatility.",
    # APCI SPECIFIC
    "what is apci": "APCI is the International Conference on Advancements in Power, Communication, and Intelligent Systems.",
    "where is apci 2025": "It is at Government College of Engineering Kannur, Kerala, India.",
    "when is apci 2025": "APCI 2025 is on June 27 and 28, 2025.",
    "is apci 2025 offline": "APCI 2025 will be held in hybrid mode – both online and offline.",
    "who can attend the conference": "Researchers, engineers, scientists, and students from around the world.",
    "how to register": "You can register through the official conference website under the 'Registration' section.",
    "is ieee involved": "Yes, APCI 2025 is technically co-sponsored by IEEE Kerala Section.",
    "is there a submission deadline": "Yes, the notification of acceptance is extended to April 7, 2025.",
    "can i present my research": "Yes, authors are welcome to submit papers to present their research.",
    "what is the aim of the conference": "To share research developments and bring together academia and industry.",
    "how many tracks are there": "There are 10 technical tracks covering various domains.",
    "can i attend virtually": "Yes, you can attend the conference online in hybrid mode.",
    "who to contact for queries": "You can check the 'Contact Us' section on the conference website.",

    # Track-specific questions
    "what is track 1": "Track 1 is Power and Renewable Energy Systems. It includes smart grids, power quality, and energy management.",
    "what is track 2": "Track 2 is Electric Drives and Power Converters. It covers electric vehicles, power converter topologies, and control.",
    "what is track 3": "Track 3 is Sensors, Control, and Automation. It deals with biomedical applications, instrumentation, and automation systems.",
    "what is track 4": "Track 4 is VLSI. It includes analog/digital design, devices, ASIC/FPGA, nanoelectronics, and quantum computing.",
    "what is track 5": "Track 5 is Embedded Systems and IoT. It covers microcontroller systems, IoT devices, WSN, and robotics.",
    "what is track 6": "Track 6 is Signal Processing. Topics include image, video, audio, biomedical signals, and pattern recognition.",
    "what is track 7": "Track 7 is Communication Systems. It includes wireless, satellite, optical communication, and antennas.",
    "what is track 8": "Track 8 is Artificial Intelligence and Machine Learning. It covers NLP, generative AI, big data, and virtual reality.",
    "what is track 9": "Track 9 is Cloud Computing. It focuses on cloud systems and high performance computing.",
    "what is track 10": "Track 10 is Cyber Security and Cryptography. It deals with data security, privacy, and encryption methods.",

    # Extra clarifications
    "can i submit ai paper in other tracks": "Yes, if your AI work fits better with another topic, you can choose that relevant track.",
    "are topics limited to listed tracks": "No, the conference welcomes papers beyond listed topics if related to power, communication, or intelligent systems."

    
}

def process_command(query):
    if query == "":
        return

    # === Dictionary Check First ===
    if query in qa_dictionary:
        speak(qa_dictionary[query])
        return

    # elif "time" in query:
    #     tell_time()
    # elif "wikipedia" in query:
    #     topic = query.replace("wikipedia", "").strip()
    #     if topic:
    #         search_wikipedia(topic)
    #     else:
    #         speak("What should I search on Wikipedia?")
    # elif "google" in query:
    #     topic = query.replace("google", "").strip()
    #     if topic:
    #         open_google(topic)
    #     else:
    #         speak("What should I search on Google?")
    # elif "youtube" in query:
    #     open_youtube()
    # elif "music" in query or "song" in query:
    #     play_music()
    # elif "weather" in query:
    #     speak("Checking the weather...")
    #     response = ask_ollama("What's the weather like today?")
    #     speak(response)
    # elif any(word in query for word in ["exit", "quit", "stop", "goodbye", "bye"]):
    #     speak("Goodbye! Have a great day.")
    #     exit()
    else:
        speak("Let me think about that.")
        response = ask_ollama(query)
        speak(response)

def main():
    speak("Hello, I’m CYRUS, your cognitive AI support system.")
    while True:
        query = listen_command()
        process_command(query)

if __name__ == "__main__":
    main()
