// frontend/app/page.tsx
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <h1 className="text-6xl font-bold text-gray-900">
          Navatar
        </h1>
        <p className="text-3xl font-semibold text-indigo-600">
          Turn Right For What?
        </p>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Create custom Waze voice packs using AI. Upload any audio,
          clone the voice, and get your personalized navigation assistant.
        </p>
        
        <div className="pt-8">
          <Link
            href="/create"
            className="inline-block bg-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition-colors"
          >
            Create Your Voice Pack
          </Link>
        </div>

        <div className="pt-12 grid md:grid-cols-3 gap-6 text-left">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="font-semibold text-lg mb-2">1. Upload Audio</h3>
            <p className="text-gray-600">
              Upload any audio or video file with the voice you want to clone
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="font-semibold text-lg mb-2">2. Customize</h3>
            <p className="text-gray-600">
              Edit phrases and create multi-voice conversations
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="font-semibold text-lg mb-2">3. Download</h3>
            <p className="text-gray-600">
              Get your custom voice pack ready for Waze
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}