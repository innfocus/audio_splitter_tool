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
        Process audio file and return timestamped sentences with millisecond precision
        """
        # Get detailed transcription with timestamps
        result = self.model.transcribe(
            audio_path,
            word_timestamps=True,
            verbose=False
        )
        
        # Process segments into our desired format
        sentences = []
        for segment in result["segments"]:
            # Convert to milliseconds for more precise timing
            start_ms = int(segment["start"] * 1000)
            end_ms = int(segment["end"] * 1000)
            duration_ms = end_ms - start_ms
            
            sentences.append({
                "sentence": segment["text"].strip(),
                "duration": self._format_duration_ms(duration_ms),
                "start": self._format_duration_ms(start_ms),
                "end": self._format_duration_ms(end_ms),
                "start_ms": start_ms,
                "end_ms": end_ms,
                "duration_ms": duration_ms
            })
            
        return sentences
    
    def _format_duration_ms(self, milliseconds):
        """Convert milliseconds to HH:MM:SS.mmm format"""
        seconds = milliseconds / 1000
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        ms = int((seconds % 1) * 1000)
        seconds = int(seconds)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"
    
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
            start_ms = sentence["start_ms"]
            end_ms = sentence["end_ms"]
            
            # Extract the segment
            segment = audio[start_ms:end_ms]
            
            # Generate output filename
            filename = f"segment_{i:03d}_{start_ms}_{end_ms}.mp3"
            output_path = os.path.join(output_dir, filename)
            
            # Export the segment
            segment.export(output_path, format="mp3")

def main():
    # Initialize the splitter
    splitter = AudioSplitter()
    
    # Process audio file
    audio_path = "./audio.mp3"
    output_json = "output.json"
    output_dir = "split_segments"
    
    # Process and save timestamps
    sentences = splitter.process_audio(audio_path)
    splitter.save_to_json(sentences, output_json)
    
    # Split audio into segments
    splitter.split_audio_by_sentences(audio_path, sentences, output_dir)

if __name__ == "__main__":
    main()