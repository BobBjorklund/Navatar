# backend/voice_packs/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import uuid
from pathlib import Path
from django.conf import settings
import modal

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy'})

@api_view(['POST'])
def upload_audio(request):
    """Upload audio/video file, send to Modal for processing"""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    file_id = str(uuid.uuid4())
    
    try:
        # Read file into memory
        print(f"Uploading {audio_file.name} ({audio_file.size} bytes)")
        audio_bytes = audio_file.read()
        
        # Call Modal function
        print("Sending to Modal for processing...")
        process_audio = modal.Function.lookup("navatar", "process_audio")
        result = process_audio.remote(audio_bytes, audio_file.name)
        
        # Save voice samples locally for later generation
        temp_dir = Path(settings.TEMP_DIR)
        temp_dir.mkdir(exist_ok=True)
        
        for voice in result['voices']:
            sample_path = temp_dir / f"{file_id}_voice_{voice['id']}.wav"
            with open(sample_path, 'wb') as f:
                f.write(voice['sample_audio'])
            voice['sample_path'] = str(sample_path)
            del voice['sample_audio']  # Remove bytes from response
        
        result['file_id'] = file_id
        
        return Response(result)
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error processing audio: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def generate_voice_pack(request):
    """Generate voice pack ZIP - to be implemented"""
    return Response({'message': 'Generate endpoint - to be implemented'})