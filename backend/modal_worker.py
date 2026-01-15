# backend/modal_worker.py

import modal
from pathlib import Path

# Create Modal app
app = modal.App("navatar")

# Define the container image with all dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(
        "torch==2.8.0",
        "torchaudio==2.8.0",
        "openai-whisper",
        "pyannote.audio",
        "ffmpeg-python",
    )
    .apt_install("ffmpeg")
)

@app.function(
    image=image,
    memory=2048,  # 2GB RAM
    timeout=600,  # 10 minutes max
    secrets=[
        modal.Secret.from_name("huggingface-token")  # We'll create this
    ]
)
def process_audio(audio_bytes: bytes, filename: str):
    """
    Process audio file: transcribe and detect speakers
    
    Args:
        audio_bytes: Raw audio file bytes
        filename: Original filename (for extension)
    
    Returns:
        dict with 'voices', 'transcript', 'duration'
    """
    import os
    import tempfile
    import whisper
    import ffmpeg
    import torch
    import torchaudio
    from pyannote.audio import Pipeline
    
    print(f"Processing audio file: {filename}")
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Save uploaded file
        original_path = tmpdir / filename
        with open(original_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Convert to WAV
        wav_path = tmpdir / "audio.wav"
        print(f"Converting to WAV...")
        
        ffmpeg.input(str(original_path)) \
            .output(
                str(wav_path),
                acodec='pcm_s16le',
                ar=16000,
                ac=1
            ) \
            .overwrite_output() \
            .run(capture_stdout=True, capture_stderr=True)
        
        # Get duration
        probe = ffmpeg.probe(str(wav_path))
        duration = float(probe['format']['duration'])
        print(f"Audio duration: {duration}s")
        
        # Load Whisper model
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("small")
        
        # Transcribe
        print("Transcribing audio...")
        transcript_result = whisper_model.transcribe(str(wav_path))
        
        # Load pyannote pipeline
        print("Loading pyannote pipeline...")
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        
        try:
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=hf_token
            )
            
            # Load audio for pyannote
            waveform, sample_rate = torchaudio.load(str(wav_path))
            
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            
            if sample_rate != 16000:
                waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
            
            # Run speaker diarization
            print("Running speaker diarization...")
            diarization = diarization_pipeline({
                "waveform": waveform,
                "sample_rate": 16000,
            })
            
            # Extract voices
            voices = {}
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                if speaker not in voices:
                    voices[speaker] = {
                        'id': speaker,
                        'segments': [],
                        'total_duration': 0
                    }
                
                voices[speaker]['segments'].append({
                    'start': turn.start,
                    'end': turn.end,
                    'duration': turn.end - turn.start
                })
                voices[speaker]['total_duration'] += turn.end - turn.start
            
            # Extract voice samples
            voice_samples = []
            for speaker_id, voice_data in voices.items():
                longest = max(voice_data['segments'], key=lambda x: x['duration'])
                
                # Extract sample segment
                sample_path = tmpdir / f"voice_{speaker_id}.wav"
                
                ffmpeg.input(str(wav_path), ss=longest['start'], t=longest['duration']) \
                    .output(str(sample_path)) \
                    .overwrite_output() \
                    .run(capture_stdout=True, capture_stderr=True)
                
                # Read sample as bytes to return
                with open(sample_path, 'rb') as f:
                    sample_bytes = f.read()
                
                voice_samples.append({
                    'id': speaker_id,
                    'name': f"Voice {speaker_id[-1]}",
                    'sample_audio': sample_bytes,  # Return audio bytes
                    'duration': round(longest['duration'], 2),
                    'total_speaking_time': round(voice_data['total_duration'], 2),
                    'num_segments': len(voice_data['segments'])
                })
            
        except Exception as e:
            print(f"Diarization failed: {e}, using single voice")
            # Fallback to single voice
            with open(wav_path, 'rb') as f:
                sample_bytes = f.read()
            
            voice_samples = [{
                'id': 'SPEAKER_00',
                'name': 'Voice A',
                'sample_audio': sample_bytes,
                'duration': round(duration, 2),
                'total_speaking_time': round(duration, 2),
                'num_segments': 1
            }]
        
        print(f"Processing complete. Found {len(voice_samples)} voice(s)")
        
        return {
            'duration': round(duration, 2),
            'transcript': transcript_result['text'][:500],
            'voices': voice_samples,
            'message': f"Detected {len(voice_samples)} voice(s)"
        }


# For local testing
@app.local_entrypoint()
def test():
    """Test the function locally"""
    # Read a test audio file
    with open("test.mp3", "rb") as f:
        audio_bytes = f.read()
    
    result = process_audio.remote(audio_bytes, "test.mp3")
    print(result)