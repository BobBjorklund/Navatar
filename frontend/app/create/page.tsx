// frontend/app/create/page.tsx
'use client';

import { useState } from 'react';
import { uploadAudio } from '@/lib/api';
import FileUploader from '@/components/upload/FileUploader';

export default function CreatePage() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleUpload = async (files: File[]) => {
    if (files.length === 0) return;
    
    setUploading(true);
    setError('');
    
    try {
      const data = await uploadAudio(files[0]);
      setResult(data);
      console.log('Upload successful:', data);
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
            <div className="mt-4 text-center text-gray-600">
              Uploading and analyzing...
            </div>
          )}
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg">
              {error}
            </div>
          )}
          
          {result && (
            <div className="mt-4 p-4 bg-green-50 text-green-600 rounded-lg">
              Upload successful! File ID: {result.file_id || result.message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}