# ------------------------------------------------------------
# voice_alert.py — Offline-Friendly TTS Playback for MediVoice
# ------------------------------------------------------------

import os
import platform
import subprocess
import tempfile

import pygame
from gtts import gTTS

try:
    import pyttsx3  # optional offline engine
except ImportError:
    pyttsx3 = None


def speak(text, lang_code="en"):
    """
    Convert text to speech and play it. Tries gTTS + pygame first,
    then falls back to offline engines so alerts still work when
    network access is unavailable.
    """

    lang_map = {
        "english": "en", "en": "en",
        "bengali": "bn", "bangla": "bn", "bn": "bn"
    }
    lang = lang_map.get(lang_code.lower(), "en")

    try:
        _speak_with_cloud_tts(text, lang)
        return
    except Exception as e:
        print(f"[Voice] Cloud TTS failed ({e}). Trying offline fallback...")

    if _speak_offline(text):
        return

    print("[Voice] Unable to play voice alert with any engine.")


def _speak_with_cloud_tts(text, lang):
    """Generate audio with gTTS and play via pygame or OS player."""
    tts = gTTS(text=text, lang=lang, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        audio_path = fp.name
        tts.save(audio_path)

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception:
        system = platform.system()
        if system == "Windows":
            os.system(f'start /min wmplayer "{audio_path}"')
        elif system == "Darwin":
            subprocess.run(["afplay", audio_path])
        else:
            os.system(f"mpg123 '{audio_path}' 2>/dev/null")
    finally:
        if os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except PermissionError:
                pass


def _speak_offline(text):
    """Use local engines (pyttsx3 or OS APIs) when gTTS is unavailable."""
    if pyttsx3 is not None:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception:
            pass

    system = platform.system()
    try:
        if system == "Windows":
            escaped = text.replace('"', "'")
            cmd = (
                'PowerShell -Command "Add-Type -AssemblyName System.Speech; '
                '$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                f'$speak.Speak(\\"{escaped}\\");"'
            )
            os.system(cmd)
            return True
        elif system == "Darwin":
            subprocess.run(["say", text])
            return True
        else:
            subprocess.run(["espeak", text])
            return True
    except Exception:
        return False
