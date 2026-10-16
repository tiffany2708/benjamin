import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel


MODEL_SIZE = "small"


def download_audio(url: str, output_dir: Path) -> Path:
    output_template = str(output_dir / "audio.%(ext)s")

    command = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-o", output_template,
        "--no-playlist",
        url,
    ]

    subprocess.run(command, check=True)

    audio_files = list(output_dir.glob("audio.*"))

    if not audio_files:
        raise RuntimeError("Не удалось скачать аудио.")

    return audio_files[0]


def transcribe(audio_path: Path) -> str:
    print("Распознаю речь...")

    start_time = time.time()

    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(
        str(audio_path),
        language="ru",
    )

    texts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            texts.append(text)

    elapsed = time.time() - start_time

    print(f"Язык: {info.language}")
    print(f"Время распознавания: {elapsed:.1f} сек.")

    return "\n".join(texts)

def transcribe_url(url: str) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        print("Извлекаю аудио из видео...")

        audio_path = download_audio(url, temp_dir)

        return transcribe(audio_path)

def main():
    if len(sys.argv) != 2:
        print("Использование:")
        print('python transcribe.py "URL"')
        sys.exit(1)

    url = sys.argv[1]

    text = transcribe_url(url)

    print()
    print(text)
    print()
    print("Временные файлы удалены.")


if __name__ == "__main__":
    main()
