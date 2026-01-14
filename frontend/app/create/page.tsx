// frontend/app/create/page.tsx
'use client';

import { useState } from 'react';
import { uploadAudio } from '@/lib/api';
import FileUploader from '@/components/upload/FileUploader';

interface Voice {
  id: string;
  name: string;
  duration: number;
  total_speaking_time: number;
  num_segments: number;
}

interface UploadResult {
  file_id: string;
  duration: number;
  transcript: string;
  voices: Voice[];
  message: string;
}

export default function CreatePage() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string>('');

  const handleUpload = async (files: File[]) => {
    if (files.length === 0) return;
    
    setUploading(true);
    setError('');
    setResult(null);
    
    try {
      const data = await uploadAudio(files[0]);
      setResult(data);
    } catch (err) {
      setError('Failed to upload file. Please try again.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            Create Voice Pack
          </h1>
          <p className="text-gray-600 mt-2">
            Upload audio or video to get started
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-8">
          <FileUploader onUpload={handleUpload} disabled={uploading} />
          
          {uploading && (
            <div className="mt-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <p className="mt-2 text-gray-600">
                Analyzing audio and detecting voices...
              </p>
            </div>
          )}
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg">
              {error}
            </div>
          )}
          
          {result && (
            <div className="mt-8 space-y-6">
              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-900">
                  ✓ {result.message}
                </h3>
                <p className="text-sm text-green-700 mt-1">
                  Duration: {result.duration}s
                </p>
              </div>

              {result.transcript && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Transcript Preview
                  </h3>
                  <p className="text-sm text-gray-600 italic">
                    "{result.transcript}..."
                  </p>
                </div>
              )}

              <div>
                <h3 className="font-semibold text-gray-900 mb-4">
                  Detected Voices
                </h3>
                <div className="grid gap-4">
                  {result.voices.map((voice) => (
                    <div 
                      key={voice.id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-indigo-400 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {voice.name}
                          </h4>
                          <p className="text-sm text-gray-500 mt-1">
                            {voice.num_segments} segments • {voice.total_speaking_time}s total
                          </p>
                        </div>
                        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
                          Use This Voice
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4">
                <button className="w-full py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700">
                  Continue to Phrase Editor →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}