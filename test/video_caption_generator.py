#!/usr/bin/env python3
"""
Video Caption Generator

This script takes a video file as input and generates an output video with 
automatic captions/subtitles overlaid on it using speech recognition.

Usage:
    python video_caption_generator.py input_video.mp4 output_video.mp4

Dependencies:
    - moviepy: For video processing
    - speech_recognition: For audio transcription
    - pydub: For audio processing
    - whisper: For advanced speech recognition (optional but recommended)
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
import speech_recognition as sr
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import check_for_optional_components
from pydub import AudioSegment
from pydub.silence import split_on_silence
import whisper


class VideoCaptionGenerator:
    def __init__(self, video_path, output_path, model_size="base"):
        """
        Initialize the video caption generator.
        
        Args:
            video_path (str): Path to input video file
            output_path (str): Path for output video file
            model_size (str): Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.video_path = video_path
        self.output_path = output_path
        self.model_size = model_size
        self.temp_dir = tempfile.mkdtemp()
        
        # Load Whisper model
        print(f"Loading Whisper model ({model_size})...")
        self.whisper_model = whisper.load_model(model_size)
        
    def extract_audio(self):
        """Extract audio from video file."""
        print("Extracting audio from video...")
        
        # Load video and extract audio
        video = VideoFileClip(self.video_path)
        audio_path = os.path.join(self.temp_dir, "audio.wav")
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        video.close()
        
        return audio_path
    
    def transcribe_audio_whisper(self, audio_path):
        """
        Transcribe audio using OpenAI Whisper for better accuracy.
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            list: List of subtitle segments with timing and text
        """
        print("Transcribing audio with Whisper...")
        
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(audio_path)
        
        # Extract segments with timing
        subtitles = []
        for segment in result["segments"]:
            subtitle = {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            }
            subtitles.append(subtitle)
            
        return subtitles
    
    def transcribe_audio_speechrecognition(self, audio_path):
        """
        Fallback transcription using speech_recognition library.
        Less accurate but doesn't require internet for some engines.
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            list: List of subtitle segments with timing and text
        """
        print("Transcribing audio with speech_recognition...")
        
        # Load audio
        audio = AudioSegment.from_wav(audio_path)
        
        # Split audio on silence
        chunks = split_on_silence(
            audio,
            min_silence_len=500,  # 500ms of silence
            silence_thresh=audio.dBFS - 14,
            keep_silence=500
        )
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        subtitles = []
        current_time = 0
        
        for i, chunk in enumerate(chunks):
            # Export chunk to temporary file
            chunk_path = os.path.join(self.temp_dir, f"chunk_{i}.wav")
            chunk.export(chunk_path, format="wav")
            
            # Calculate timing
            chunk_duration = len(chunk) / 1000.0  # Convert to seconds
            start_time = current_time
            end_time = current_time + chunk_duration
            
            try:
                # Recognize speech in chunk
                with sr.AudioFile(chunk_path) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data)
                    
                    if text.strip():
                        subtitles.append({
                            "start": start_time,
                            "end": end_time,
                            "text": text.strip()
                        })
                        
            except sr.UnknownValueError:
                # Could not understand audio
                pass
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                
            current_time = end_time
            
            # Clean up chunk file
            os.remove(chunk_path)
            
        return subtitles
    
    def create_subtitle_clips(self, video, subtitles):
        """
        Create text clips for subtitles.
        
        Args:
            video: MoviePy VideoFileClip object
            subtitles (list): List of subtitle segments
            
        Returns:
            list: List of TextClip objects
        """
        print("Creating subtitle clips...")
        
        subtitle_clips = []
        
        for subtitle in subtitles:
            # Create text clip
            txt_clip = TextClip(
                subtitle["text"],
                fontsize=50,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(video.w * 0.8, None),  # 80% of video width
                font='Arial-Bold'
            ).set_position(('center', video.h * 0.85)).set_duration(
                subtitle["end"] - subtitle["start"]
            ).set_start(subtitle["start"])
            
            subtitle_clips.append(txt_clip)
            
        return subtitle_clips
    
    def generate_captioned_video(self):
        """Generate the final video with captions."""
        try:
            # Extract audio
            audio_path = self.extract_audio()
            
            # Transcribe audio (try Whisper first, fallback to speech_recognition)
            try:
                subtitles = self.transcribe_audio_whisper(audio_path)
            except Exception as e:
                print(f"Whisper transcription failed: {e}")
                print("Falling back to speech_recognition...")
                subtitles = self.transcribe_audio_speechrecognition(audio_path)
            
            if not subtitles:
                print("No speech detected in the video.")
                return False
                
            print(f"Generated {len(subtitles)} subtitle segments")
            
            # Load video
            print("Processing video...")
            video = VideoFileClip(self.video_path)
            
            # Create subtitle clips
            subtitle_clips = self.create_subtitle_clips(video, subtitles)
            
            # Composite video with subtitles
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # Write final video
            print(f"Writing output video to {self.output_path}...")
            final_video.write_videofile(
                self.output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Clean up
            video.close()
            final_video.close()
            
            print(f"✅ Successfully created captioned video: {self.output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating captioned video: {e}")
            return False
        
        finally:
            # Clean up temporary files
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)


def main():
    """Main function to handle command line arguments and run the caption generator."""
    parser = argparse.ArgumentParser(
        description="Generate captions for video files automatically"
    )
    parser.add_argument(
        "input_video",
        help="Path to input video file"
    )
    parser.add_argument(
        "output_video",
        help="Path for output video file with captions"
    )
    parser.add_argument(
        "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_video):
        print(f"❌ Error: Input video file '{args.input_video}' not found.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_video)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate captioned video
    generator = VideoCaptionGenerator(
        args.input_video, 
        args.output_video, 
        args.model
    )
    
    success = generator.generate_captioned_video()
    
    if success:
        print("\n🎉 Caption generation completed successfully!")
    else:
        print("\n💥 Caption generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
