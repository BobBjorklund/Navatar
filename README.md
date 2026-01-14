# Navatar

**Turn Right For What?**

AI-powered custom Waze voice pack generator.

## Stack

- Frontend: Next.js (Vercel)
- Backend: Django (Render)
- Voice: ElevenLabs API

## Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py runserver
```

## Environment Variables

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL

### Backend (.env)
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `HUGGINGFACE_TOKEN` - Hugging Face token for pyannote
