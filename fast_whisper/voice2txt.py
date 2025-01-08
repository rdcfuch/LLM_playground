# https://github.com/SYSTRAN/faster-whisper

from faster_whisper import WhisperModel
import pyaudio,wave,os

def record_chunk(p, stream,file_path, chunk_length=0.5):
    frames = []
    for _ in range(0, int(16000 / 1024 * chunk_length)):
        data = stream.read(1024)
        frames.append(data)

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def main():
    # Choose model
    model_size = "medium.en"
    # model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    print("loading model ...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print("model loaded")
    p = pyaudio.PyAudio()
    # stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    accumulated_transcription = ""  # Initialize an empty string to accumulate transcriptions
    stream = p.open(format=pyaudio.paInt8,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=2048)  # Increase buffer size

    print("start recording...")
    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file)
            segments, info = model.transcribe(chunk_file, beam_size=5)

            for seg in segments:
                transcription = seg.text
                print(transcription)
            os.remove(chunk_file)

            # Append the new transcription to the accumulated transcription
            # accumulated_transcription += transcription + " "

    except KeyboardInterrupt:
        print("stopping....")
        # with open("log.txt", "w") as log_file:
        #     log_file.write(accumulated_transcription)

    finally:
        # print("Log:" + accumulated_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
