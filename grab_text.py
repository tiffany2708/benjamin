import subprocess, sys, tempfile, time, re
from pathlib import Path
from faster_whisper import WhisperModel
from playwright.sync_api import sync_playwright

MODEL_SIZE = "small"
PROFILE_DIR = Path(__file__).resolve().parent / "browser_profile"

def login(url):
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_data_dir=str(PROFILE_DIR), headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(url)
        input("Залогинься и нажми Enter здесь...")
        ctx.close()

def grab(url, out_dir, headed):
    found = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_data_dir=str(PROFILE_DIR), headless=not headed, locale="ru-RU", args=["--autoplay-policy=no-user-gesture-required"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        def on_resp(r):
            try:
                if "json" in r.headers.get("content-type","").lower():
                    txt = r.text().replace("\\/","/")
                    for m in re.findall(r'https://vd\d+\.okcdn\.ru/[^"\'\\\s]+', txt):
                        u = m.split("&bytes=")[0]
                        if u not in found: found.append(u)
            except: pass
        page.on("response", on_resp)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        for _ in range(15):
            try: page.locator("video").first.click(timeout=500)
            except: pass
            page.wait_for_timeout(1000)
        cookies = ctx.cookies()
        hdr = "Cookie: " + "; ".join(f"{c['name']}={c['value']}" for c in cookies) + "\r\nReferer: " + url + "\r\nUser-Agent: Mozilla/5.0\r\n"
        audio = out_dir / "audio.wav"
        for u in found:
            if "m3u8" not in u: continue
            print("HLS:", u[:80])
            try:
                subprocess.run(["ffmpeg","-y","-loglevel","error","-headers",hdr,"-i",u,"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",str(audio)], check=True)
                ctx.close()
                return audio
            except Exception as e:
                print("err:", e)
        ctx.close()
    raise RuntimeError("Не нашёл m3u8")

def transcribe(path):
    m = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(path), language="ru")
    return "\n".join(s.text.strip() for s in segs if s.text.strip())

def main():
    args = sys.argv[1:]
    if not args:
        print("python grab_text.py --login [URL]")
        print('python grab_text.py "ССЫЛКА" [--show]')
        return
    if args[0] == "--login":
        login(args[1] if len(args)>1 else "https://dzen.ru")
        return
    url = args[0]
    headed = "--show" in args
    with tempfile.TemporaryDirectory() as td:
        a = grab(url, Path(td), headed)
        print(transcribe(a))

if __name__ == "__main__":
    main()
