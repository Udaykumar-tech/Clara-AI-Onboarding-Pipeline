import whisper
import os

def transcribe_audio(audio_path, output_dir, transcript_name):
    model = whisper.load_model("base")

    result = model.transcribe(audio_path)

    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, transcript_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print("Transcript saved:", output_path)


if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.abspath(__file__))

    audio_file = os.path.join(base_dir, "datasets", "demo", "demo_call_001.m4a")
    output_folder = os.path.join(base_dir, "datasets", "demo")
    transcript_file = "transcript_001.txt"

    transcribe_audio(audio_file, output_folder, transcript_file)