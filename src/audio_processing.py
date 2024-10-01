import os
import tempfile
import soundfile as sf

from gtts import gTTS


def transcribe_audio(audio, whisper_model, sample_rate):
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
        sf.write(temp_audio_file.name, audio, sample_rate)
        result = whisper_model.transcribe(temp_audio_file.name)

    os.unlink(temp_audio_file.name)
    return result['text']


def text_to_speach(text, lang='pl'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        tts.save(temp_audio_file.name)
        return temp_audio_file.name
