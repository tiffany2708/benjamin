import time
from faster_whisper import WhisperModel

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

start = time.time()

segments, info = model.transcribe(
    "long_test.wav",
    language="ru"
)

with open("long_transcript.txt", "w", encoding="utf-8") as f:
    for segment in segments:
        f.write(segment.text.strip() + "\n")

elapsed = time.time() - start

print(f"Язык: {info.language}")
print(f"Длительность аудио: {info.duration:.1f} сек.")
print(f"Время распознавания: {elapsed:.1f} сек.")
print(f"Коэффициент: {elapsed / info.duration:.2f}x")
print("Результат сохранён в long_transcript.txt")
