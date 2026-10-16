from faster_whisper import WhisperModel

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

segments, info = model.transcribe(
    "test_audio.m4a",
    language="ru"
)

print(f"Определённый язык: {info.language}")
print(f"Вероятность языка: {info.language_probability:.2f}")
print("\n--- ТЕКСТ ---\n")

for segment in segments:
    print(segment.text, end=" ")

print("\n")
