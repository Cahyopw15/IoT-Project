from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import serial
from collections import deque
from scipy.fft import fft
from PIL import ImageGrab

cutoff_frequency = 10.0  # Frekuensi cutoff filter dalam Hz
sampling_rate = 100.0  

class EGM_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoring Sinyal Elektromiografi pada Otot Manusia")
        self.root.geometry("1000x800")
        
        # Setup serial communication with Arduino   
        self.serial_port = serial.Serial('COM6', 9600)  # Sesuaikan dengan port Arduino Anda
        self.navbar = tk.Menu(root)
        self.root.config(menu=self.navbar)

        # Menu "File"
        self.file_menu = tk.Menu(self.navbar, tearoff=0)
        self.navbar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Data", command=self.open_csv_file)  # Menghubungkan fungsi open_csv_file
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.destroy)
        
        # Menu "Options"
        self.options_menu = tk.Menu(self.navbar, tearoff=0)
        self.navbar.add_cascade(label="Options", menu=self.options_menu)
        self.options_menu.add_command(label="Start", command=self.start) 
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Stop", command=self.stop)
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Reset", command=self.reset)

        # Menu "Save"
        self.save_menu = tk.Menu(self.navbar, tearoff=0)
        self.navbar.add_cascade(label="Save", menu=self.save_menu)
        self.save_menu.add_command(label="Save Data", command=self.save_data)
        self.save_menu.add_command(label="Save Image", command=self.save_image)

        # Menu "Analysis"
        self.analysis_menu = tk.Menu(self.navbar, tearoff=0)
        self.navbar.add_cascade(label="Analysis", menu=self.analysis_menu)
        self.analysis_menu.add_command(label="Calculate FFT and Mean", command=self.calculate_fft_and_mean)

        # Footer Menu
        self.footer_frame = ttk.Frame(root)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
        self.result_label = ttk.Label(self.footer_frame, text="Mean FFT: N/A", anchor="e")
        self.result_label.pack(side=tk.BOTTOM, padx=550)

        self.status_label = ttk.Label(root, text="Status Kondisi: Tidak diketahui", anchor="w", font=("Helvetica", 9))
        self.status_label.pack(side=tk.BOTTOM, padx=300)

        # Create the plot
        self.fig, self.ax2 = plt.subplots(1, 1, figsize=(12, 4))
        self.ax2.set_title('Sinyal Elektromiografi')
        self.ax2.set_xlabel('Waktu')
        self.ax2.set_ylabel('Amplitudo')
        self.line2, = self.ax2.plot([], [], lw=2)

        # Create the canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Initialize data deque for the plot
        self.data2 = deque(maxlen=1000)
        self.timestamp_data = deque(maxlen=1000)

        self.animation_running = False  # Initialize the animation_running attribute

        # Variables to store mean FFT and status
        self.mean_fft = None
        self.status = "Tidak diketahui"

    def animation(self):
        def update_plot():
            if self.animation_running:  # Check if animation is running
                # Read data from serial
                data = self.serial_port.readline().decode('ascii').strip()

                if data:
                    try:
                        # Process data  
                        value = float(data)
                        self.data2.append(value)
                        self.timestamp_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

                        # Update plot
                        self.line2.set_data(range(len(self.data2)), self.data2)
                        self.ax2.relim()
                        self.ax2.autoscale_view()
                        self.canvas.draw()
                        self.canvas.flush_events()

                        print(f"Received data: {data}")  # Debugging: Print received data
                    except ValueError:
                        print(f"Invalid data received: {data}")  # Debugging: Print invalid data

                # Call this function again after 100ms
                self.root.after(100, update_plot)
        
        # Call the update_plot function initially
        update_plot()

    def save_image(self):
        x0 = self.root.winfo_rootx()
        y0 = self.root.winfo_rooty()
        x1 = x0 + self.root.winfo_width()
        y1 = y0 + self.root.winfo_height()

        # Ensure the "record" directory exists
        os.makedirs("record", exist_ok=True)

        # Generate a unique filename using current timestamp
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"record/screenshot_{now}.png"

        # Capture and save the image
        im = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        im.save(filename)
        print(f"Screenshot saved as {filename}")

    def save_data(self):
        # Ensure the "record" directory exists
        os.makedirs("record", exist_ok=True)

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the filename with the timestamp
        filename = f"record/data_{timestamp}.csv"

        # Combine data2 and timestamps into a DataFrame
        df = pd.DataFrame({
            'Timestamp': list(self.timestamp_data),
            'Sinyal Elektromiografi': list(self.data2)
        })

        # Save the DataFrame to a CSV file
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    # Untuk membuka file yang sudah tersimpan   
    def open_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                # Membaca file CSV
                df = pd.read_csv(file_path)
                # Menampilkan data sebagai grafik
                self.plot_excel_data(df)
                messagebox.showinfo("Success", "CSV file successfully opened")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file\n{e}")

    def plot_excel_data(self, df):
        # Memperbarui plot dengan data dari file Excel atau CSV
        self.data2.clear()
        self.timestamp_data.clear()

        # Mengasumsikan bahwa data di kolom kedua untuk plot kedua
        if 'Timestamp' in df.columns and 'EGM Signal 2' in df.columns:
            self.timestamp_data.extend(df['Timestamp'])
            self.data2.extend(df['EGM Signal 2'])
        else:
            messagebox.showerror("Error", "The CSV file does not contain the required columns")

        self.line2.set_data(range(len(self.data2)), self.data2)
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas.draw()
        self.canvas.flush_events()

    def calculate_fft_and_mean(self):
        if len(self.data2) > 0:
            # Convert deque to numpy array
            data_array = np.array(self.data2)

            # Perform FFT
            yf = fft(data_array)
            xf = np.fft.fftfreq(len(data_array))

            # Calculate mean of the absolute values of FFT
            self.mean_fft = np.mean(np.abs(yf))

            # Update status based on mean FFT value
            if self.mean_fft > 234:
                self.status = "Kelelahan"
            else:
                self.status = "Tidak Kelelahan"

            # Display the mean FFT value and status
            self.result_label.config(text=f"Mean FFT: {self.mean_fft:.2f}")
            self.status_label.config(text=f"Status Kondisi: {self.status}")

    def start(self):
        if not self.animation_running:
            self.animation_running = True
            self.animation()
            print("Animation started")  # Debugging: Print status

    def stop(self):
        self.animation_running = False
        print("Animation stopped")  # Debugging: Print status

    def reset(self):
        self.data2.clear()
        self.timestamp_data.clear()
        self.line2.set_data([], [])
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas.draw()
        self.canvas.flush_events()
        self.result_label.config(text="Mean FFT: N/A")
        self.status_label.config(text="Status Kondisi: Tidak diketahui")
        self.mean_fft = None
        self.status = "Tidak diketahui"
        print("Data reset")  # Debugging: Print status

    def on_closing(self):
        if self.serial_port:
            self.serial_port.close()
        self.root.destroy()

# Kemudian, dalam kode yang memanggil EGM_GUI:
if __name__ == "__main__":
    root = tk.Tk()
    app = EGM_GUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
