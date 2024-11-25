import whisper
from pydub import AudioSegment
import json
from datetime import datetime
import ssl
import urllib.request
import os


# SSL certificate bypass if needed
ssl._create_default_https_context = ssl._create_unverified_context

class AudioSplitter:
    def __init__(self, model_size="base"):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        self.model = whisper.load_model(model_size)
        
    def process_audio(self, audio_path):
        """
        Process audio file and return timestamped sentences with second precision
        """
        # Get detailed transcription with timestamps
        result = self.model.transcribe(
            audio_path,
            word_timestamps=True,
            verbose=False,
        )
        
        # Process segments into our desired format
        sentences = []
        prev_end = 0
        for segment in result["segments"]:
            # Get timestamps in seconds
            start_sec = segment["start"]
            end_sec = segment["end"]
            
            # Always add break time to previous sentence
            if prev_end > 0:
                gap = start_sec - prev_end
                if sentences:  # If we have previous sentences
                    sentences[-1]["end_sec"] = start_sec  # Extend previous sentence end
                    sentences[-1]["end"] = self._format_duration(start_sec)
                    sentences[-1]["duration_sec"] = start_sec - sentences[-1]["start_sec"]
                    sentences[-1]["duration"] = self._format_duration(sentences[-1]["duration_sec"])
            
            duration_sec = end_sec - start_sec
            prev_end = end_sec
            
            sentences.append({
                "sentence": segment["text"].strip(),
                "duration": self._format_duration(duration_sec),
                "start": self._format_duration(start_sec),
                "end": self._format_duration(end_sec),
                "start_sec": start_sec,
                "end_sec": end_sec,
                "duration_sec": duration_sec
            })
            
        return sentences
    
    def _format_duration(self, seconds):
        """Convert seconds to HH:MM:SS.SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"
    
    def save_to_json(self, sentences, output_path):
        """Save processed sentences to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sentences, f, ensure_ascii=False, indent=2)

    def split_audio_by_sentences(self, audio_path, sentences, output_dir):
        """Split audio file into segments based on sentences"""
        audio = AudioSegment.from_file(audio_path)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Split audio for each sentence
        for i, sentence in enumerate(sentences):
            start_ms = int(sentence["start_sec"] * 1000)
            end_ms = int(sentence["end_sec"] * 1000)
            
            # Extract the segment
            segment = audio[start_ms:end_ms]
            
            # Generate output filename
            filename = f"segment_{i:03d}_{start_ms}_{end_ms}.mp3"
            output_path = os.path.join(output_dir, filename)
            
            # Export the segment
            segment.export(output_path, format="mp3")
