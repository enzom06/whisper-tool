import requests
import pyaudio
import wave
import time
import asyncio
from utils import get_response, async_get_response, send_audio

import keyboard

import pyaudio
import wave
import keyboard
import threading

class AudioRecorder:
    def __init__(self, output_filename='code/test.wav'):
        self.recording_active = False
        self.output_filename = output_filename
        # Mappage des touches pour démarrer et arrêter l'enregistrement
        keyboard.add_hotkey('ctrl+alt+r', self.start_recording)
        keyboard.add_hotkey('ctrl+alt+s', self.stop_recording)

    def record_audio(self):
        # Paramètres d'enregistrement
        FORMAT = pyaudio.paInt16  # Format des données audio (16 bits PCM)
        CHANNELS = 1              # Mono
        RATE = 16000              # Fréquence d'échantillonnage (16 kHz)
        CHUNK = 1024              # Nombre de données audio traitées à la fois
        WAVE_OUTPUT_FILENAME = self.output_filename  # Nom de fichier pour enregistrement

        audio = pyaudio.PyAudio()

        # Ouverture du canal d'enregistrement
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        print("Enregistrement en cours... Appuyez sur Ctrl+Alt+S pour arrêter.")

        frames = []

        # Capture des frames d'audio
        while self.recording_active:
            data = stream.read(CHUNK)
            frames.append(data)
        

        print("Enregistrement terminé.")

        # Arrêt et fermeture du flux
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Sauvegarde de l'enregistrement sous forme de fichier WAV
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        self.recording_active = False

    # Fonction pour démarrer l'enregistrement dans un thread
    def start_recording(self):
        self.recording_active = True
        threading.Thread(target=self.record_audio).start()

    # Fonction pour arrêter l'enregistrement
    def stop_recording(self):
        if self.recording_active:
            self.recording_active = False
            keyboard.unhook_all()
            time.sleep(0.1)
    def __del__(self):
        keyboard.unhook_all()
        self.stop_recording()

# Création d'une instance de la classe AudioRecorder
recorder = AudioRecorder('./data/records/test.wav')

recorder.start_recording()

while recorder.recording_active:
    time.sleep(1)

# Utilisation de la fonction
sending_result = send_audio(
    "https://localhost:5000/transcribe",
    "C:/Users/monte/Documents/projet/whisper-tool/data/records/test.wav",
    "medium")
print(sending_result, end="\n\n")
result = get_response(
    id=sending_result["id"],
    url="https://localhost:5000/transcribe"
)
print(result)



