from faster_whisper import WhisperModel
import pyaudio
import wave
import os
import logging
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioTranscriptionError(Exception):
    """Custom exception for audio transcription errors"""
    pass

@contextmanager
def audio_stream(p, **kwargs):
    """Context manager for handling audio stream"""
    stream = p.open(**kwargs)
    try:
        yield stream
    finally:
        stream.stop_stream()
        stream.close()

def record_chunk(p, stream, file_path, chunk_length=0.5):
    """Record audio chunk with error handling"""
    try:
        frames = []
        buffer_size = 2048  # Consistent buffer size
        for _ in range(0, int(16000 / buffer_size * chunk_length)):
            data = stream.read(buffer_size, exception_on_overflow=False)
            frames.append(data)

        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        raise AudioTranscriptionError(f"Error recording audio chunk: {str(e)}")

def main():
    try:
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Choose and load model
        model_size = "medium.en"
        logger.info("Loading model...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        logger.info("Model loaded successfully")

        # Audio stream parameters
        stream_params = {
            'format': pyaudio.paInt16,  # Consistent with record_chunk
            'channels': 1,
            'rate': 16000,
            'input': True,
            'frames_per_buffer': 2048
        }

        logger.info("Starting recording...")
        with audio_stream(p, **stream_params) as stream:
            accumulated_transcription = ""  # Initialize an empty string to accumulate transcriptions
            while True:
                chunk_file = "temp_chunk.wav"
                try:
                    record_chunk(p, stream, chunk_file)
                    segments, info = model.transcribe(chunk_file, beam_size=5)

                    for seg in segments:
                        transcription = seg.text
                        logger.info(f"Transcription: {transcription}")
                        accumulated_transcription += transcription + " "
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(chunk_file):
                        os.remove(chunk_file)

    except KeyboardInterrupt:
        logger.info("Stopping transcription...")
        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)
    except AudioTranscriptionError as e:
        logger.error(f"Transcription error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        p.terminate()

if __name__ == "__main__":
    main()
