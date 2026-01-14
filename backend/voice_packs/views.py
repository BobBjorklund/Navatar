from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def health_check(request):
    """Health check endpoint for keeping Render warm"""
    return Response({'status': 'healthy'})

@api_view(['POST'])
def upload_audio(request):
    """Upload and analyze audio file"""
    # TODO: Implement
    return Response({'message': 'Upload endpoint - to be implemented'})

@api_view(['POST'])
def generate_voice_pack(request):
    """Generate voice pack ZIP"""
    # TODO: Implement
    return Response({'message': 'Generate endpoint - to be implemented'})
