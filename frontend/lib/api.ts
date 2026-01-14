// frontend/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function uploadAudio(file: File) {
  const formData = new FormData();
  formData.append('audio', file);

  const response = await fetch(`${API_URL}/api/upload/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
}

export async function generateVoicePack(data: any) {
  const response = await fetch(`${API_URL}/api/generate/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Generation failed');
  }

  return response.json();
}