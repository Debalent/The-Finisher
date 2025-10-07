import React, { useState } from 'react';

function App() {
  const [form, setForm] = useState({ genre: 'hip-hop', bpm: 90, mood: 'energetic', theme: 'love' });
  const [loading, setLoading] = useState(false);
  const [lyrics, setLyrics] = useState('');

  const update = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const generate = async (e) => {
    e && e.preventDefault();
    setLoading(true);
    setLyrics('Generating...');
    try {
      const resp = await fetch('http://localhost:8000/api/lyrics/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, bpm: Number(form.bpm) })
      });
      if (!resp.ok) throw new Error('Server error');
      const data = await resp.json();
      setLyrics(data.lyrics + '\n\n' + data.timestamp);
    } catch (err) {
      setLyrics('Failed to generate lyrics — is the backend running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-3xl">
        <div className="bg-gradient-to-br from-purple-800 to-indigo-700 rounded-2xl shadow-2xl p-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">🎵 The Finisher <span className="text-sm font-normal opacity-80">React MVP</span></h1>
          <p className="mb-6 text-indigo-200">Generate mood & BPM aligned lyric suggestions.</p>

          <form onSubmit={generate} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="text-sm text-indigo-100">Genre</span>
              <input value={form.genre} onChange={e => update('genre', e.target.value)} className="mt-1 block w-full rounded-md bg-indigo-900 border-transparent focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2" />
            </label>

            <label className="block">
              <span className="text-sm text-indigo-100">BPM</span>
              <input type="number" value={form.bpm} onChange={e => update('bpm', e.target.value)} min={40} max={240} className="mt-1 block w-full rounded-md bg-indigo-900 p-2" />
            </label>

            <label className="block">
              <span className="text-sm text-indigo-100">Mood</span>
              <input value={form.mood} onChange={e => update('mood', e.target.value)} className="mt-1 block w-full rounded-md bg-indigo-900 p-2" />
            </label>

            <label className="block">
              <span className="text-sm text-indigo-100">Theme</span>
              <input value={form.theme} onChange={e => update('theme', e.target.value)} className="mt-1 block w-full rounded-md bg-indigo-900 p-2" />
            </label>

            <div className="sm:col-span-2 flex gap-3">
              <button disabled={loading} type="submit" className="bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-2 px-4 rounded">{loading ? 'Generating...' : 'Generate Lyrics'}</button>
              <button type="button" onClick={() => navigator.clipboard.writeText(lyrics).catch(()=>{})} className="bg-transparent border border-indigo-400 text-indigo-100 py-2 px-3 rounded">Copy</button>
            </div>
          </form>

          <section className="mt-6">
            <h2 className="text-lg font-semibold mb-2">Generated Lyrics</h2>
            <pre className="whitespace-pre-wrap bg-indigo-900/60 p-4 rounded text-indigo-50 min-h-[120px]">{lyrics || 'No lyrics yet — press Generate.'}</pre>
          </section>
        </div>
        <p className="mt-4 text-center text-sm text-gray-400">Backend: FastAPI — Endpoint: <code className="bg-gray-800 px-2 py-1 rounded">/api/lyrics/generate</code></p>
      </div>
    </div>
  );
}

export default App;
