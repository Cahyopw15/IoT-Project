import numpy as np
import pandas as pd
from scipy.fft import fft

# Parameter data
duration = 180  # Durasi 3 menit (180 detik)
sampling_rate = 10  # Sampling setiap 0.1 detik
time = np.linspace(0, duration, duration * sampling_rate, endpoint=False)

# Membuat nilai sensor dengan pola acak tetapi perlahan naik/turun
#np.random.seed(42)  # Seed untuk reproduksibilitas
sensor_signal = [20]  # Nilai awal
for _ in range(1, len(time)):
    change = np.random.uniform(-0.01, 0.01) * 1000  # Perubahan kecil
    if np.random.rand() > 0.5:  # Keputusan naik atau turun
        sensor_signal.append(sensor_signal[-1] + abs(change))  # Naik perlahan
    else:
        sensor_signal.append(sensor_signal[-1] - abs(change)) # Turun perlahan

# Konversi ke array
sensor_signal = np.array(sensor_signal)

# Menghitung FFT (magnitude saja untuk interpretasi)
fft_values = np.abs(fft(sensor_signal))[:len(sensor_signal) // 2]  / 1000# Setengah spektrum (frekuensi positif)
frequencies = np.fft.fftfreq(len(sensor_signal), d=1/sampling_rate)[:len(sensor_signal) // 2] / 10000

# Membuat DataFrame
data = pd.DataFrame({
    'Time (s)': time,
    'Sensor Signal': sensor_signal,
    'FFT Magnitude': np.interp(time, frequencies, fft_values)  # Interpolasi untuk waktu yang sama
})

# Menampilkan sebagian data
print(data.head())

# Menyimpan ke file CSV
data.to_csv("sensor_signal_random_stable.csv", index=False)
print("Data berhasil disimpan sebagai 'sensor_signal_random_stable.csv'.")



#visualisasikan keduanya
plt.figure(figsize=(12, 6))
plt.plot(data['Time (s)'], data['Sensor Signal'], label='Sensor Signal', color='blue')
plt.title('Sensor Signal Data', fontsize=16)
plt.xlabel('Time (seconds)', fontsize=14)
plt.ylabel('Muscle Activity Level', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

plt.figure(figsize=(12, 6))
plt.plot(data['Time (s)'], data['FFT Magnitude'], label='FFT Magnitude', color='red')
plt.title('FFT of Sensor Signal Data', fontsize=16)
plt.xlabel('Frequency (Hz)', fontsize=14)
plt.ylabel('Amplitude', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()