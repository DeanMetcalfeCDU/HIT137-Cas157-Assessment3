# Question 1 - Audio Transcription App.

# Dependencies: use pip to install openai-whisper, moviepy, torch, soundfile, and transformers.

import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
import soundfile as sf
import whisper
import torch
import os
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# Encapsulation: Wrapping all the application functionality inside a class
class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trnscribr - Audio and Video Transcriber")
        self.root.geometry("600x400")

        # GUI Elements
        self.file_label = tk.Label(root, text="File:")
        self.file_label.pack()

        self.filepath_entry = tk.Entry(root, width=50)
        self.filepath_entry.pack()

        self.select_file_button = tk.Button(root, text="Select File", command=self.select_file)
        self.select_file_button.pack()

        self.output_label = tk.Label(root, text="Output Directory:")
        self.output_label.pack()

        self.outputpath_entry = tk.Entry(root, width=50)
        self.outputpath_entry.pack()

        self.select_output_button = tk.Button(root, text="Select Output Directory", command=self.select_output_directory)
        self.select_output_button.pack()

        self.transcribe_button = tk.Button(root, text="Transcribe", command=self.transcribe)
        self.transcribe_button.pack()

        self.output_textbox = tk.Text(root, height=10, width=50)
        self.output_textbox.pack()
        self.output_textbox.config(state=tk.DISABLED)  # Prevent typing

        self.clear_button = tk.Button(root, text="Clear", command=self.clear)
        self.clear_button.pack()

        # Variables to store file paths
        self.filepath = ""
        self.outputpath = ""

    # Polymorphism and Method Overriding: select_file is customized to handle both audio and video file formats.
    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Audio/Video files", "*.mp3 *.wav *.mp4 *.mkv *.avi")])
        self.filepath_entry.delete(0, tk.END)
        self.filepath_entry.insert(0, self.filepath)

    def select_output_directory(self):
        self.outputpath = filedialog.askdirectory()
        self.outputpath_entry.delete(0, tk.END)
        self.outputpath_entry.insert(0, self.outputpath)

    def transcribe(self):
        file_extension = os.path.splitext(self.filepath)[1].lower()

        # Check file type and handle video-to-audio conversion for videos
        if file_extension in [".mp4", ".mkv", ".avi"]:
            audio_file = self.convert_video_to_audio(self.filepath)
        elif file_extension in [".mp3", ".wav"]:
            audio_file = self.filepath
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return

        try:
            # Transcription process
            if audio_file.endswith('.wav'):
                transcription = self.transcribe_with_wav2vec(audio_file)
            else:
                transcription = self.transcribe_with_whisper(audio_file)

            self.output_textbox.config(state=tk.NORMAL)
            self.output_textbox.insert(tk.END, transcription)
            self.output_textbox.config(state=tk.DISABLED)

            # Ask the user if they want to save the transcription
            save_output = messagebox.askyesno("Save Output", "Do you want to save the transcription to a file?")
            if save_output:
                self.save_transcription(transcription)

            messagebox.showinfo("Success", "Transcription completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Transcription failed: {str(e)}")

    def convert_video_to_audio(self, video_file):
        try:
            clip = VideoFileClip(video_file)
            audio_file = "temp_audio.wav"
            clip.audio.write_audiofile(audio_file)
            return audio_file
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract audio from video: {str(e)}")
            return None

    def transcribe_with_whisper(self, audio_file):
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        return result["text"]

    def transcribe_with_wav2vec(self, audio_file):
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
        model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")

        # Load audio file
        audio_input, _ = sf.read(audio_file)
        input_values = processor(audio_input, return_tensors="pt", padding="longest").input_values

        # Perform transcription
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

        return transcription

    def save_transcription(self, transcription):
        if not self.outputpath:
            messagebox.showerror("Error", "No output directory selected.")
            return

        output_file = os.path.join(self.outputpath, "transcription.txt")
        try:
            with open(output_file, "w") as f:
                f.write(transcription)
            messagebox.showinfo("Success", f"Transcription saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transcription: {str(e)}")

    # Method Overriding: clear() is overridden to reset the application state
    def clear(self):
        self.filepath_entry.delete(0, tk.END)
        self.outputpath_entry.delete(0, tk.END)
        self.output_textbox.config(state=tk.NORMAL)
        self.output_textbox.delete(1.0, tk.END)
        self.output_textbox.config(state=tk.DISABLED)


# Initialize and run the application
root = tk.Tk()
app = TranscriberApp(root)
root.mainloop()
