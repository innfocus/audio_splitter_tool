# Audio Sentence Splitter

A Python tool that transcribes audio files, splits them into sentences, and provides precise timing information with millisecond accuracy. The tool uses OpenAI's Whisper for transcription and generates both a JSON timing file and individual audio segments for each sentence.

## Features

-   Transcribe audio files using OpenAI's Whisper
-   Split audio into sentence-level segments
-   Millisecond-precise timing information
-   JSON output with detailed timing data
-   Individual audio files for each sentence
-   Support for multiple audio formats

## Prerequisites

-   Python 3.11 or higher
-   FFmpeg installed on your system
-   macOS, Linux, or Windows

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/audio-sentence-splitter.git
```

2. Create and activate a virtual environment:

For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install FFmpeg:

For macOS:

```bash
brew install ffmpeg
```

For Windows:

```bash
choco install ffmpeg
```

4. Install the required Python packages:

```bash
pip install -r requirements.txt
```

5. Install Python certificates (for macOS/Linux):

```bash
cd "/Applications/Python 3.11/Install Certificates.command"
./Install Certificates.command
```

## Project Structure

audio-sentence-splitter/

├── myenv/ # Virtual environment

├── README.md # This file

├── requirements.txt # Python dependencies

├── main.py # Main script

├── output.json # Generated timing data

└── split_segments/ # Directory for audio segments

## Usage

1. Place your audio file in the root directory of the project.
2. Update the `audio_path` variable in `main.py` to the path of your audio file.

```python
audio_path = "./audio.mp3"
```

3. Run the script:

```bash
python main.py
```

4. The script will generate `output.json` with the timing data and save the audio segments to the `split_segments` directory.

## Output Format

### JSON Output

The `output.json` file contains an array of objects, each representing a sentence in the audio file. The objects have the following properties:

```json
{
	"sentence": "sentence text",
	"duration": "HH:MM:SS.MS",
	"start": "HH:MM:SS.MS",
	"end": "HH:MM:SS.MS",
	"start_ms": "milliseconds",
	"end_ms": "milliseconds",
	"duration_ms": "milliseconds"
}
```

### Audio Segments

Audio segments are saved as: `segment_001_0_5234.mp3`, where:

-   `001`: Segment number
-   `0`: Start time in milliseconds
-   `5234`: End time in milliseconds

## Configuration

You can adjust the following parameters in `main.py`:

1. Whisper model size:

```python
splitter = AudioSplitter(model_size="base") # Options: tiny, base, small, medium, large
```

2. Output paths:

```python
output_json = "output.json"
output_dir = "split_segments"
```

## Troubleshooting

### SSL Certificate Issues

If you encounter SSL certificate errors, the script includes a bypass:

```python
AudioSegment.converter = "/usr/local/bin/ffmpeg" # Use the path from which ffmpeg
```

## Dependencies

-   openai-whisper
-   pydub
-   torch
-   ffmpeg-python
-   numpy<2.0
-   certifi
