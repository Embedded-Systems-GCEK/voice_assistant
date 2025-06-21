import requests
import pygame  # For music control
import time
import re

file = "piper_output.wav"
ip = "192.168.31.17"
port = "10200"
end_point = "/api/text-to-speech"
voice = "en_US-lessac-medium"  # Default voice
piper_url = f"http://{ip}:{port}{end_point}?voice={voice}"

def save_to_file(response):
    with open(file, "wb") as f:
        f.write(response.content)
        # Play the audio
def play_audio(file="piper_output.wav"):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()


def speak(text):
    # Remove unwanted characters
    clean_text = re.sub(r'[*_`~#>\\-]', '', text)
    # remove Emojis
    clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', clean_text)
    # Break long text into 2-4 sentence chunks max
    sentences = [s.strip() for s in clean_text.replace('\n', ' ').split('.') if s.strip()]
    max_sentences = 4
    
    output_chunks = []
    chunk = []
    for sentence in sentences:
        chunk.append(sentence)
        if len(chunk) == max_sentences:
            output_chunks.append('. '.join(chunk) + '.')
            chunk = []
    if chunk:
        output_chunks.append('. '.join(chunk) + '.')

    for chunk_text in output_chunks:
        print(f"Cyrus: {chunk_text}")
        # Send to Piper HTTP API
        try:
            response = get_text(chunk_text)
            if response.ok:
                save_to_file(response)
                play_audio()
            else:
                print("Piper error:", response.text)
        except Exception as e:
            print("Piper request failed:", e)

def get_text(chunk_text):
    try:
        return requests.post(
            piper_url,
            data=chunk_text.encode('utf-8'),
            headers={'Content-Type': 'text/plain'}
        )
    except Exception as e:
        print("Piper request failed:", e)


if __name__ == "__main__":
    # TTS Test example
    text = "Hello, this is a test of the text  to speech system."
    speak(text)