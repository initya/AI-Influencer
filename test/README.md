# Video Caption Generator

A Python script that automatically generates captions/subtitles for videos using speech recognition and overlays them on the video output.

## Features

- 🎤 **Automatic Speech Recognition**: Uses OpenAI Whisper for high-quality audio transcription
- 🎬 **Video Processing**: Overlays captions directly on the video with customizable styling
- 🔄 **Fallback Support**: Falls back to Google Speech Recognition if Whisper fails
- ⚡ **Multiple Model Sizes**: Choose from different Whisper model sizes based on speed vs accuracy needs
- 🎨 **Styled Captions**: White text with black outline for good visibility

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add FFmpeg to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## Usage

### Basic Usage

```bash
python video_caption_generator.py input_video.mp4 output_video.mp4
```

### Advanced Usage

```bash
# Use a larger Whisper model for better accuracy (slower)
python video_caption_generator.py input_video.mp4 output_video.mp4 --model large

# Use a smaller model for faster processing (less accurate)
python video_caption_generator.py input_video.mp4 output_video.mp4 --model tiny
```

### Available Whisper Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny  | 39 MB | Fastest | Basic |
| base  | 74 MB | Fast | Good (default) |
| small | 244 MB | Medium | Better |
| medium| 769 MB | Slow | Very Good |
| large | 1550 MB | Slowest | Best |

## Examples

### Example 1: Basic Video Captioning
```bash
python video_caption_generator.py "my_video.mp4" "my_video_with_captions.mp4"
```

### Example 2: High-Quality Captions
```bash
python video_caption_generator.py "presentation.mp4" "presentation_captioned.mp4" --model large
```

### Example 3: Quick Processing
```bash
python video_caption_generator.py "meeting.mp4" "meeting_captioned.mp4" --model tiny
```

## How It Works

1. **Audio Extraction**: Extracts audio track from the input video
2. **Speech Recognition**: Transcribes audio using OpenAI Whisper
3. **Subtitle Generation**: Creates timed text segments with proper formatting
4. **Video Composition**: Overlays subtitles on the original video
5. **Output**: Saves the final video with embedded captions

## Supported Formats

### Input Formats
- MP4, AVI, MOV, MKV, WMV, FLV
- Any format supported by FFmpeg

### Output Format
- MP4 (H.264 video, AAC audio)

## Troubleshooting

### Common Issues

**1. "FFmpeg not found" error**
- Make sure FFmpeg is installed and added to your system PATH
- Restart your terminal/command prompt after installation

**2. "No module named 'moviepy'" error**
- Run: `pip install -r requirements.txt`

**3. "Could not request results" error**
- This happens with the fallback Google Speech Recognition when internet is unavailable
- Whisper works offline, so this shouldn't affect the primary transcription method

**4. Poor caption accuracy**
- Try using a larger Whisper model: `--model large`
- Ensure your audio is clear and has minimal background noise

**5. Slow processing**
- Use a smaller model: `--model tiny` or `--model base`
- Consider the trade-off between speed and accuracy

### Performance Tips

- **For faster processing**: Use `--model tiny`
- **For better accuracy**: Use `--model large`
- **Balanced option**: Use `--model base` (default)
- Clear audio with minimal background noise will improve results

## Caption Styling

The script generates captions with the following default styling:
- **Font**: Arial Bold
- **Size**: 50px
- **Color**: White text with black outline
- **Position**: Bottom center (85% down from top)
- **Width**: 80% of video width

To customize styling, modify the `create_subtitle_clips` method in the script.

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script.
