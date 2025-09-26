import time
import csv
from datetime import datetime

# ---------------- Audio settings ----------------
samplerate = 48000   # match your USB mic
blocksize = 1024
channels = 1
csv_file = "mic_db_log.csv"
# -------------------------------------------------

# Setup CSV file
with open(csv_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "dB"])

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)

    audio_data = indata[:, 0]

    # RMS to dB
    rms = np.sqrt(np.mean(audio_data**2))
    db = 20 * np.log10(rms + 1e-6) + 90  # Avoid log(0), add offset

    # Log to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, db])

    # ASCII visualization with minimum bar length
    bar_length = 50
    min_bar = int(0.3 * bar_length)  # minimum bar length
    rms_len = int(np.clip(rms * 10, 0, 1) * bar_length) + min_bar
    peak_len = int(np.clip(np.max(np.abs(audio_data)), 0, 1) * bar_length) 

    rms_bar = '█' * min(rms_len, bar_length)
    peak_bar = '█' * min(peak_len, bar_length)

    print(f"\rRMS: {rms_bar:<50} | Peak: {peak_bar:<50} | dB: {db:.2f}", end='', flush=True)

try:
    with sd.InputStream(callback=audio_callback,
                        channels=channels,
                        samplerate=samplerate,
                        blocksize=blocksize):
        print("🎤 Live audio monitor running... Press Ctrl+C to stop")
        print("RMS shows average sound level, Peak shows max amplitude")
        print("-" * 120)
        while True:
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n🛑 Stopped audio monitoring")

except Exception as e:
    print(f"\n❌ Error: {e}")
