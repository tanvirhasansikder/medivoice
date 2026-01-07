# ------------------------------------------------------------
# voice_input.py — Advanced Voice Input for MediVoice
# ------------------------------------------------------------

import speech_recognition as sr
import sounddevice as sd
import numpy as np
import streamlit as st


def get_voice_input(lang_code="en", preferred_phrases=None):
    lang_map = {
        "english": "en", "en": "en",
        "bengali": "bn", "bangla": "bn", "bn": "bn"
    }
    lang = lang_map.get((lang_code or "en").lower(), "en")
    recognizer = sr.Recognizer()

    def extract_transcript(result):
        if not result:
            return None
        if isinstance(result, str):
            return result.strip()
        if isinstance(result, dict):
            alternatives = result.get("alternative", [])
            for alt in alternatives:
                transcript = (alt.get("transcript") or "").strip()
                if transcript:
                    return transcript
        return None

    def recognize_audio(audio_data, primary_lang, fallback_lang=None, phrases=None):
        def _recognize(lang):
            try:
                return recognizer.recognize_google(
                    audio_data,
                    language=lang,
                    show_all=True,
                    preferred_phrases=phrases
                )
            except sr.RequestError:
                st.error("⚠ Google Speech API not reachable. Check your internet.")
                return ""
        primary_result = extract_transcript(_recognize(primary_lang))
        if primary_result:
            return primary_result, False
        if fallback_lang:
            fallback_result = extract_transcript(_recognize(fallback_lang))
            if fallback_result:
                return fallback_result, True
        return None, False

    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Please speak now.")
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                st.warning("⏱ No voice detected. Try speaking louder or closer.")
                return ""

            fallback_lang = "bn" if lang == "en" else "en"
            text, used_fallback = recognize_audio(audio, lang, fallback_lang, preferred_phrases)
            if text:
                if used_fallback:
                    st.info("🔁 Switched language and understood you.")
                st.success(f"🗣 You said: {text}")
                return text

            st.error("❌ Sorry, I couldn't understand what you said.")
            return ""

    except Exception as mic_error:
        st.warning(f"🎧 Microphone unavailable. Switching to fallback mode. ({mic_error})")

        SAMPLE_RATE = 16000
        DURATION = 5
        try:
            st.info(f"🎙 Recording {DURATION} seconds (fallback)...")
            recording = sd.rec(
                int(DURATION * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype=np.int16
            )
            sd.wait()

            audio_data = sr.AudioData(
                recording.tobytes(),
                SAMPLE_RATE,
                2
            )

            fallback_lang = "bn" if lang == "en" else "en"
            text, used_fallback = recognize_audio(audio_data, lang, fallback_lang, preferred_phrases)
            if text:
                if used_fallback:
                    st.info("🔁 Switched language and understood you.")
                st.success(f"🗣 You said: {text}")
                return text

            st.error("❌ Fallback recording couldn't understand your speech.")
            return ""

        except Exception as fallback_error:
            st.error(f"❌ Fallback recording failed. ({fallback_error})")
            return ""
