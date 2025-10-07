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

  const subscribe = async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/create-checkout-session', { method: 'POST' });
      if (!resp.ok) throw new Error('Checkout failed');
      const data = await resp.json();
      if (data.url) window.location.href = data.url;
    } catch (err) {
      console.error('Subscribe error', err);
      alert('Failed to create checkout session');
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-800 text-white p-6 flex items-center justify-center">
      <div className="w-full max-w-5xl">
        <header className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-yellow-400 rounded-xl flex items-center justify-center shadow-lg transform -rotate-12">🎶</div>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight">The Finisher</h1>
              <p className="text-sm text-indigo-200">AI songwriting sidekick — mood, BPM & rhyme-friendly lyrics</p>
            </div>
          </div>
          <nav>
            <button onClick={() => window.scrollTo(0,0)} className="text-sm px-3 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md shadow">Docs</button>
          </nav>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white/5 rounded-2xl p-6 backdrop-blur-sm border border-white/10 shadow-xl">
            <h2 className="text-lg font-semibold mb-3">Create lyrics</h2>
            <p className="text-sm text-indigo-200 mb-4">Tell me the vibe and I'll finish the verse. Tweak and copy the results.</p>

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

            <div className="sm:col-span-2 flex gap-3 items-center">
              <button disabled={loading} type="submit" className="bg-gradient-to-r from-pink-500 to-violet-500 hover:from-pink-400 hover:to-violet-400 text-white font-semibold py-2 px-4 rounded shadow-lg">{loading ? 'Generating...' : 'Generate Lyrics'}</button>
              <button type="button" onClick={() => navigator.clipboard.writeText(lyrics).catch(()=>{})} className="bg-transparent border border-white/20 text-white py-2 px-3 rounded">Copy</button>
              <button type="button" onClick={subscribe} className="ml-auto bg-yellow-400 text-gray-900 font-semibold py-2 px-4 rounded shadow">Subscribe</button>
            </div>
          </form>
          <div className="relative bg-gradient-to-br from-black/20 via-indigo-900/20 to-transparent rounded-2xl p-6 border border-white/5 shadow-xl">
            <div className="flex items-start justify-between">
              <h2 className="text-lg font-semibold">Generated Lyrics</h2>
              <div className="text-sm text-indigo-200">Provider: <span className="text-white">local</span></div>
            </div>

            <div className="mt-4">
              <pre className="whitespace-pre-wrap bg-black/40 p-4 rounded text-indigo-50 min-h-[260px]">{lyrics || 'No lyrics yet — press Generate.'}</pre>
            </div>

            <div className="mt-4 flex gap-3 text-sm text-indigo-200">
              <button onClick={() => { setLyrics(''); }} className="px-3 py-2 bg-white/5 rounded">Clear</button>
              <button onClick={() => navigator.clipboard.writeText(lyrics).catch(()=>{})} className="px-3 py-2 bg-white/5 rounded">Copy</button>
            </div>

            <div className="absolute -right-8 -top-8 opacity-30 animate-float">
              <svg width="120" height="120" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2v10" stroke="#F472B6" strokeWidth="1.5" strokeLinecap="round"/><circle cx="18" cy="18" r="3" stroke="#60A5FA" strokeWidth="1.5"/></svg>
            </div>
          </div>
        </div>

        <footer className="mt-8 text-center text-sm text-indigo-200">Built with ❤️ — try different genres, moods and BPM</footer>
      </div>
    </div>
  );
}

export default App;
