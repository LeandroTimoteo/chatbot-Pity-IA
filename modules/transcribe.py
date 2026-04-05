import speech_recognition as sr

def transcribe_audio(audio_path):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="pt-BR")
        return text
    except sr.UnknownValueError:
        return "⚠️ Não foi possível entender o áudio."
    except sr.RequestError as e:
        return f"⚠️ Erro no serviço de reconhecimento: {e}"
    except Exception as e:
        return f"⚠️ Erro ao processar o áudio: {e}"
