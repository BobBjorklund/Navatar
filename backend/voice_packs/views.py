# backend/voice_packs/views.py

# At the very top
import os
os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = '1'

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import uuid
from pathlib import Path
from django.conf import settings
import ffmpeg
import torch
import torchaudio

_whisper_model = None
_diarization_pipeline = None
_diarization_available = True  # Flag to track if pyannote works

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model...")
        import whisper
        _whisper_model = whisper.load_model("small")
    return _whisper_model

def get_diarization_pipeline():
    global _diarization_pipeline, _diarization_available
    
    if not _diarization_available:
        return None
    
    if _diarization_pipeline is None:
        try:
            print("Loading pyannote pipeline...")
            from pyannote.audio import Pipeline
            _diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=os.getenv("HUGGINGFACE_TOKEN")
            )
        except Exception as e:
            print(f"Speaker diarization unavailable: {e}")
            _diarization_available = False
            return None
    
    return _diarization_pipeline

@api_view(['POST'])
def upload_audio(request):
    """Upload audio/video file, extract audio, detect speakers"""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    file_id = str(uuid.uuid4())
    
    temp_dir = Path(settings.TEMP_DIR)
    temp_dir.mkdir(exist_ok=True)
    
    original_path = temp_dir / f"{file_id}_original{Path(audio_file.name).suffix}"
    with open(original_path, 'wb') as f:
        for chunk in audio_file.chunks():
            f.write(chunk)
    
    try:
        whisper_model = get_whisper_model()
        diarization_pipeline = get_diarization_pipeline()
        
        # Convert to WAV
        wav_path = temp_dir / f"{file_id}.wav"
        print(f"Converting to WAV: {wav_path}")
        
        ffmpeg.input(str(original_path)) \
            .output(str(wav_path), acodec='pcm_s16le', ar=16000, ac=1) \
            .overwrite_output() \
            .run(capture_stdout=True, capture_stderr=True)
        
        probe = ffmpeg.probe(str(wav_path))
        duration = float(probe['format']['duration'])
        
        # Try speaker diarization if available
        voice_samples = []
        
        if diarization_pipeline:
            print("Running speaker diarization...")
            try:
                waveform, sample_rate = torchaudio.load(str(wav_path))
                
                if waveform.shape[0] > 1:
                    waveform = waveform.mean(dim=0, keepdim=True)
                
                if sample_rate != 16000:
                    waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
                
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
                
                for speaker_id, voice_data in voices.items():
                    longest = max(voice_data['segments'], key=lambda x: x['duration'])
                    sample_path = temp_dir / f"{file_id}_voice_{speaker_id}.wav"
                    
                    ffmpeg.input(str(wav_path), ss=longest['start'], t=longest['duration']) \
                        .output(str(sample_path)) \
                        .overwrite_output() \
                        .run(capture_stdout=True, capture_stderr=True)
                    
                    voice_samples.append({
                        'id': speaker_id,
                        'name': f"Voice {speaker_id[-1]}",
                        'sample_path': str(sample_path),
                        'duration': round(longest['duration'], 2),
                        'total_speaking_time': round(voice_data['total_duration'], 2),
                        'num_segments': len(voice_data['segments'])
                    })
            except Exception as e:
                print(f"Diarization failed, using single voice: {e}")
        
        # Fallback: single voice if diarization unavailable or failed
        if not voice_samples:
            voice_samples = [{
                'id': 'SPEAKER_00',
                'name': 'Voice A',
                'sample_path': str(wav_path),
                'duration': round(duration, 2),
                'total_speaking_time': round(duration, 2),
                'num_segments': 1
            }]
        
        print("Transcribing audio...")
        result = whisper_model.transcribe(str(wav_path))
        
        return Response({
            'file_id': file_id,
            'duration': round(duration, 2),
            'transcript': result['text'][:500],
            'voices': voice_samples,
            'message': f"Detected {len(voice_samples)} voice(s)"
        })
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error processing audio: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})

@api_view(['POST'])
def generate_voice_pack(request):
    return Response({'message': 'Generate endpoint - to be implemented'})