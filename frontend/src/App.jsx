import { useState } from 'react';
import { Play, Download, RefreshCw, Film, Zap, CheckCircle } from 'lucide-react';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');
  const [jobId, setJobId] = useState('');

  const handler = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/render', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setRes(data.message);
        setDownloadUrl(data.download_url);
        setJobId(data.job_id);
      } else {
        setRes('Error: ' + (data.error || data.details || 'Unknown error occurred'));
      }
    } catch (err) {
      setRes('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setQuery('');
    setRes('');
    setDownloadUrl('');
    setJobId('');
  };

  const downloadVideo = () => {
    if (downloadUrl) {
      window.open(`http://127.0.0.1:5000${downloadUrl}`, '_blank');
    }
  };

  if (res) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="w-full max-w-4xl mx-auto">
          {/* Success Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Video Generated Successfully</h2>
            <p className="text-gray-600">{res}</p>
          </div>

          {downloadUrl && (
            <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm mb-8">
              <div className="text-center mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Your Animation</h3>
                <p className="text-gray-500">Preview and download your video</p>
              </div>
              
              {/* Video Preview */}
              <div className="mb-6">
                <video 
                  controls 
                  className="w-full max-w-2xl mx-auto rounded-lg border border-gray-200"
                  style={{ maxHeight: '500px' }}
                >
                  <source src={`http://127.0.0.1:5000${downloadUrl}`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
              
              {/* Download Button */}
              <div className="flex justify-center">
                <button
                  className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium"
                  onClick={downloadVideo}
                >
                  <Download className="w-4 h-4" />
                  Download Video
                </button>
              </div>
            </div>
          )}
          
          {/* Make Another Query Button */}
          <div className="text-center">
            <button
              className="inline-flex items-center gap-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium border border-gray-200"
              onClick={reset}
            >
              <RefreshCw className="w-4 h-4" />
              Create Another Animation
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-lg mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-100 rounded-xl mb-6">
            <Film className="w-7 h-7 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            Manim Generator
          </h1>
          <p className="text-gray-600 text-lg">
            Create mathematical animations with AI
          </p>
        </div>

        {!loading ? (
          <div className="space-y-6">
            {/* Input Card */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Animation Description
                  </label>
                  <textarea
                    placeholder="Describe your animation (e.g., 'animate a sine wave')"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-400"
                    rows="3"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handler()}
                  />
                </div>
                
                <button
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  onClick={handler}
                  disabled={!query.trim()}
                >
                  <Zap className="w-4 h-4" />
                  Generate Animation
                </button>
              </div>
            </div>

            {/* Info Cards */}
          
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm text-center">
            <div className="space-y-6">
              {/* Simple loading spinner */}
              <div className="inline-block w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
              
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-gray-900">
                  Generating Animation
                </h3>
                <p className="text-gray-600">
                  "{query}"
                </p>
                <p className="text-sm text-gray-500">
                  This may take some time depending on the complexity of your animation.
                </p>
              </div>
              
              <div className="text-xs text-gray-400 max-w-sm mx-auto">
                Creating Manim code and rendering your video...
              </div>
              
              <button
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors duration-200 text-sm font-medium border border-gray-200"
                onClick={() => {
                  setLoading(false);
                  setRes('');
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

}

export default App;