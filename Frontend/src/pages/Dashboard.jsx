import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { checkHealth, getIngestedFiles, sendChatQuery, uploadDocument, ingestWebsiteUrl, webSearch, openSourcePdf } from '../services/api';

export default function Dashboard() {
  const [health, setHealth] = useState({ status: 'checking', message: 'Checking backend...' });
  const [files, setFiles] = useState([]);
  const [filesLoading, setFilesLoading] = useState(true);
  const [urlInput, setUrlInput] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [messages, setMessages] = useState([]);
  const [webSearchingMsgId, setWebSearchingMsgId] = useState(null);
  const [searchPhase, setSearchPhase] = useState(0);

  const fileInputRef = useRef(null);
  const chatBottomRef = useRef(null);

  // Poll backend health status
  useEffect(() => {
    const fetchHealth = async () => {
      const status = await checkHealth();
      setHealth(status);
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Fetch ingested files list
  const fetchFiles = async () => {
    setFilesLoading(true);
    try {
      const fileList = await getIngestedFiles();
      if (Array.isArray(fileList)) {
        setFiles(fileList);
      }
    } catch (err) {
      console.log('Could not fetch files from backend');
    } finally {
      setFilesLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Handle File Upload
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage({ type: 'info', text: `Uploading ${file.name}...` });

    try {
      const res = await uploadDocument(file);
      setUploadMessage({ type: 'success', text: res.message || `${file.name} uploaded successfully!` });
      if (!files.includes(file.name)) {
        setFiles(prev => [file.name, ...prev]);
      }
      fetchFiles();
    } catch (err) {
      const errorDetail = err.response?.data?.detail || 'Failed to upload document. Please check that the backend is running.';
      setUploadMessage({ type: 'error', text: errorDetail });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Handle URL Ingestion
  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!urlInput.trim()) return;

    const targetUrl = urlInput.trim();
    setUploadMessage({ type: 'info', text: `Ingesting ${targetUrl}...` });
    try {
      const res = await ingestWebsiteUrl(targetUrl);
      setUploadMessage({ type: 'success', text: res.message || 'URL ingested successfully!' });
      if (!files.includes(targetUrl)) {
        setFiles(prev => [targetUrl, ...prev]);
      }
      setUrlInput('');
      fetchFiles();
    } catch (err) {
      const errorDetail = err.response?.data?.detail || 'Invalid URL format or failed to ingest. Check the backend connection.';
      setUploadMessage({ type: 'error', text: errorDetail });
    }
  };

  // Handle Chat Submit
  const handleSendChat = async (e) => {
    e?.preventDefault();
    if (!query.trim() || loading) return;

    const userText = query.trim();
    const newMsg = {
      id: Date.now(),
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await sendChatQuery(userText);
      const isIrrelevant = res.status === 'failed';
      const aiMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        text: res.message || 'No response returned from assistant.',
        file_name: res.file_name,
        page_number: res.page_number,
        chunk_id: res.chunk_id,
        isFailed: isIrrelevant,
        isIrrelevant,
        originalQuery: userText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        text: 'Unable to reach backend service. Please verify the server is running on http://localhost:8000.',
        isFailed: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  // Web Search phases for animated status text
  const searchPhases = [
    'Initiating web search...',
    'Scanning search engines...',
    'Crawling web pages...',
    'Extracting relevant content...',
    'Analyzing results...',
    'Compiling sources...',
    'Almost there...',
  ];

  // Handle Web Search
  const handleWebSearch = async (originalQuery, aiMsgId) => {
    setWebSearchingMsgId(aiMsgId);
    setSearchPhase(0);

    // Cycle through search phases every 3s to keep user engaged
    const phaseInterval = setInterval(() => {
      setSearchPhase(prev => {
        const next = prev + 1;
        return next < searchPhases.length ? next : prev;
      });
    }, 3000);

    try {
      const res = await webSearch(originalQuery);

      // Build a web search result message
      const answer = res.response?.message || '';
      const webMsg = {
        id: Date.now(),
        sender: 'ai',
        isWebSearch: true,
        text: answer || res.message || 'Here are the web search results:',
        urls: res.urls || res.results || res.links || [],
        file_name: res.response?.file_name || null,
        page_number: res.response?.page_number || null,
        chunk_id: res.response?.chunk_id || null,
        originalQuery,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, webMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now(),
        sender: 'ai',
        text: 'Web search failed. The backend may be unreachable or the search timed out.',
        isFailed: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      clearInterval(phaseInterval);
      setWebSearchingMsgId(null);
      setSearchPhase(0);
    }
  };

  // Handle View PDF Source
  const handleViewSource = async (fileName, pageNumber) => {
    if (!fileName || !pageNumber) return;
    
    setUploadMessage({ type: 'info', text: `Opening ${fileName} (Page ${pageNumber})...` });
    try {
      // Mapping file_name -> pdf_name, page_number -> start_page, defaulting no_of_pages to 1
      await openSourcePdf(fileName, pageNumber, 1);
      setTimeout(() => setUploadMessage(null), 3000); // Clear success message after 3s
    } catch (err) {
      setUploadMessage({ type: 'error', text: 'Failed to load PDF source pages. Backend may be unreachable.' });
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-white text-slate-900 font-['Hanken_Grotesk',sans-serif]">
      {/* TopAppBar */}
      <header className="flex justify-between items-center w-full px-6 border-b border-slate-200 bg-white h-14 z-20 shrink-0 shadow-xs animate-fade-in">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center text-white font-bold text-lg shadow-sm transition-transform hover:scale-110">
            S
          </div>
          <span className="font-semibold text-lg tracking-widest text-slate-900">SMART RAG</span>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-3 py-1 bg-slate-50 border border-slate-200 rounded-full">
            <span className={`w-2 h-2 rounded-full ${
              health.status === 'healthy' ? 'bg-emerald-400 animate-breathe' :
              health.status === 'offline' ? 'bg-rose-400' : 'bg-amber-400 animate-pulse'
            }`}></span>
            <span className="font-['JetBrains_Mono',monospace] text-xs text-slate-600 font-medium">
              {health.status === 'healthy' ? 'Service healthy' :
               health.status === 'offline' ? 'Backend offline' : 'Checking status...'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/login" className="text-xs font-medium text-slate-600 hover:text-amber-600 transition-colors">
              Sign In
            </Link>
            <Link to="/signup" className="text-xs font-medium px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-all shadow-xs hover:shadow-md hover:scale-[1.02] active:scale-[0.98]">
              Create Account
            </Link>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* SideNavBar */}
        <aside className="w-[320px] h-full border-r border-slate-200 bg-slate-50 p-4 flex flex-col gap-5 overflow-y-auto z-10 shrink-0 animate-fade-in">
          <div className="animate-fade-in-up">
            <h3 className="font-['JetBrains_Mono',monospace] text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Ingest Document
            </h3>
            {/* Upload Dropzone */}
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-300 hover:border-amber-500 bg-white rounded-xl flex flex-col items-center justify-center p-5 gap-2 cursor-pointer hover:bg-amber-50/50 transition-all text-center group"
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                accept=".pdf,.doc,.docx,.md,.txt" 
                className="hidden" 
              />
              <span className="material-symbols-outlined text-slate-400 group-hover:text-amber-600 text-3xl transition-all group-hover:scale-110">
                upload_file
              </span>
              <span className="text-xs font-medium text-slate-700">
                {uploading ? 'Processing file...' : 'Drop file or click to browse'}
              </span>
              <div className="flex gap-1.5 font-['JetBrains_Mono',monospace] text-[11px] text-slate-400">
                <span className="px-1.5 py-0.5 bg-slate-100 rounded">.pdf</span>
                <span className="px-1.5 py-0.5 bg-slate-100 rounded">.doc</span>
                <span className="px-1.5 py-0.5 bg-slate-100 rounded">.md</span>
                <span className="px-1.5 py-0.5 bg-slate-100 rounded">.txt</span>
              </div>
            </div>
          </div>

          {/* URL Bar */}
          <div className="animate-fade-in-up stagger-2">
            <h3 className="font-['JetBrains_Mono',monospace] text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Ingest Web URL
            </h3>
            <form onSubmit={handleUrlSubmit} className="relative">
              <input 
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://example.com/docs"
                className="w-full bg-white border border-slate-200 rounded-xl pl-3 pr-10 py-2 text-xs font-['JetBrains_Mono',monospace] text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all shadow-2xs"
              />
              <button 
                type="submit" 
                className="absolute right-1.5 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-amber-600 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <span className="material-symbols-outlined text-base">arrow_forward</span>
              </button>
            </form>
          </div>

          {/* Status Message Alert */}
          {uploadMessage && (
            <div className={`p-2.5 rounded-xl text-xs font-medium flex items-center justify-between animate-fade-in-up ${
              uploadMessage.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
              uploadMessage.type === 'error' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
              'bg-amber-50 text-amber-700 border border-amber-200 animate-pulse'
            }`}>
              <div className="flex items-center gap-1.5 truncate">
                <span className="material-symbols-outlined text-sm shrink-0">
                  {uploadMessage.type === 'success' ? 'check_circle' : uploadMessage.type === 'error' ? 'error' : 'sync'}
                </span>
                <span className="truncate">{uploadMessage.text}</span>
              </div>
              <button onClick={() => setUploadMessage(null)} className="text-slate-400 hover:text-slate-600 shrink-0 ml-2">
                <span className="material-symbols-outlined text-xs">close</span>
              </button>
            </div>
          )}

          {/* Sources List */}
          <div className="flex flex-col gap-2 flex-1 animate-fade-in-up stagger-3">
            <div className="flex items-center justify-between">
              <h3 className="font-['JetBrains_Mono',monospace] text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Knowledge Base Sources ({files.length})
              </h3>
              <button onClick={fetchFiles} className="text-slate-400 hover:text-amber-600 transition-colors hover:rotate-180 duration-500" title="Refresh files">
                <span className="material-symbols-outlined text-sm">refresh</span>
              </button>
            </div>

            <div className="flex flex-col gap-1.5 overflow-y-auto max-h-[300px] pr-1">
              {filesLoading ? (
                /* Skeleton loading state */
                <>
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center gap-2.5 p-2.5 bg-white border border-slate-200 rounded-xl">
                      <div className="w-5 h-5 rounded animate-skeleton shrink-0" />
                      <div className="flex-1 h-3 rounded animate-skeleton" />
                    </div>
                  ))}
                </>
              ) : files.length === 0 ? (
                /* Empty state */
                <div className="flex flex-col items-center justify-center py-8 text-center animate-fade-in">
                  <span className="material-symbols-outlined text-3xl text-slate-300 mb-2">folder_open</span>
                  <p className="text-xs text-slate-400 font-medium">No sources ingested yet</p>
                  <p className="text-[10px] text-slate-400 mt-1">Upload a document or paste a URL above</p>
                </div>
              ) : (
                files.map((file, idx) => (
                  <div key={idx} className="flex items-center gap-2.5 p-2.5 bg-white border border-slate-200 rounded-xl hover:border-amber-300 hover:shadow-sm transition-all shadow-2xs group animate-fade-in-up" style={{ animationDelay: `${idx * 0.05}s` }}>
                    <span className="material-symbols-outlined text-amber-500 text-base">
                      {file.startsWith('http') ? 'link' : 'description'}
                    </span>
                    <span className="font-['JetBrains_Mono',monospace] text-xs text-slate-700 truncate flex-1" title={file}>
                      {file}
                    </span>
                    <span className="material-symbols-outlined text-emerald-500 text-sm">check_circle</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Chat Console Area */}
        <main className="flex-1 flex flex-col h-full bg-slate-50/50 relative overflow-hidden">
          {/* Header Bar */}
          <div className="border-b border-slate-200 px-6 py-3 bg-white flex items-center justify-between shrink-0">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Interactive RAG Console</h2>
              <p className="text-xs text-slate-500">Retrieval-Augmented Contextual Intelligence</p>
            </div>

            <button 
              onClick={() => setMessages([])} 
              disabled={messages.length === 0}
              className="text-xs font-medium text-slate-500 hover:text-rose-600 disabled:opacity-40 disabled:cursor-not-allowed px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-rose-50 transition-all flex items-center gap-1.5"
            >
              <span className="material-symbols-outlined text-sm">delete_sweep</span>
              Clear Chat
            </button>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-6 my-auto animate-fade-in">
                <div className="w-14 h-14 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center mb-4 animate-float">
                  <span className="material-symbols-outlined text-3xl">smart_toy</span>
                </div>
                <h3 className="text-lg font-semibold text-slate-800 mb-1">RAG Knowledge Assistant Ready</h3>
                <p className="text-xs text-slate-500 max-w-sm mb-6">
                  Ask questions about your uploaded documents or web links. Contextually verified citations will be attached.
                </p>

                <div className="grid grid-cols-2 gap-2 max-w-lg w-full">
                  {[
                    "What are the main findings in the document?",
                    "Summarize key technical points",
                    "List any mentioned code snippets",
                    "What are the limitations described?"
                  ].map((sample, i) => (
                    <button
                      key={i}
                      onClick={() => { setQuery(sample); }}
                      className="p-3 text-left text-xs bg-white hover:bg-amber-50/50 border border-slate-200 hover:border-amber-400 rounded-xl text-slate-700 transition-all shadow-2xs hover:shadow-sm hover:scale-[1.02] active:scale-[0.98] animate-fade-in-up"
                      style={{ animationDelay: `${i * 0.08}s` }}
                    >
                      "{sample}"
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 max-w-3xl animate-fade-in-up ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}>
                  {msg.sender === 'ai' && (
                    <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 text-sm font-semibold shadow-xs">
                      <span className="material-symbols-outlined text-base">smart_toy</span>
                    </div>
                  )}

                  <div className="flex flex-col gap-1.5">
                    <div className={`p-4 rounded-2xl text-sm leading-relaxed shadow-2xs ${
                      msg.sender === 'user'
                        ? 'bg-slate-900 text-white rounded-tr-none'
                        : msg.isFailed
                        ? 'bg-rose-50 text-rose-800 border border-rose-200 rounded-tl-none'
                        : 'bg-white text-slate-800 border border-slate-200 rounded-tl-none'
                    }`}>
                      {msg.text}
                    </div>

                    {/* Web Search button for irrelevant responses */}
                    {msg.sender === 'ai' && msg.isIrrelevant && msg.originalQuery && (
                      <button
                        onClick={() => handleWebSearch(msg.originalQuery, msg.id)}
                        disabled={webSearchingMsgId !== null}
                        className="mt-1 inline-flex items-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 hover:border-blue-300 text-blue-700 rounded-xl text-xs font-semibold transition-all hover:shadow-sm hover:scale-[1.02] active:scale-[0.98] w-fit animate-fade-in-up disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <span className="material-symbols-outlined text-sm">travel_explore</span>
                        {webSearchingMsgId === msg.id ? 'Searching...' : 'Search the Web for results'}
                      </button>
                    )}

                    {/* Web Search Results — Collapsible Dropdown */}
                    {msg.isWebSearch && msg.urls && msg.urls.length > 0 && (
                      <div className="mt-2 flex flex-col gap-0 max-w-lg">
                        {/* Source citation */}
                        {msg.file_name && (
                          <div className="flex items-center gap-2 mb-2">
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-100/70 border border-blue-200 rounded-full font-['JetBrains_Mono',monospace] text-[11px] text-blue-800">
                              <span className="material-symbols-outlined text-xs">language</span>
                              <span>Source: <strong>{msg.file_name}</strong></span>
                              {msg.page_number && <span className="opacity-70">· Page {msg.page_number}</span>}
                            </span>
                          </div>
                        )}

                        {/* Dropdown toggle */}
                        <button
                          onClick={() => {
                            setMessages(prev => prev.map(m =>
                              m.id === msg.id ? { ...m, urlsExpanded: !m.urlsExpanded } : m
                            ));
                          }}
                          className="flex items-center justify-between gap-2 px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl text-xs font-semibold text-blue-700 transition-all cursor-pointer group"
                        >
                          <div className="flex items-center gap-1.5">
                            <span className="material-symbols-outlined text-sm">travel_explore</span>
                            Web Sources ({msg.urls.length})
                          </div>
                          <span className={`material-symbols-outlined text-sm transition-transform duration-300 ${msg.urlsExpanded ? 'rotate-180' : ''}`}>
                            expand_more
                          </span>
                        </button>

                        {/* Collapsible URL list */}
                        <div
                          className="overflow-hidden transition-all duration-400 ease-in-out"
                          style={{
                            maxHeight: msg.urlsExpanded ? `${msg.urls.length * 80 + 16}px` : '0px',
                            opacity: msg.urlsExpanded ? 1 : 0,
                          }}
                        >
                          <div className="flex flex-col gap-1.5 pt-2">
                            {msg.urls.map((urlItem, idx) => {
                              const url = typeof urlItem === 'string' ? urlItem : (urlItem.url || urlItem.link || urlItem.href);
                              const title = typeof urlItem === 'object' ? (urlItem.title || urlItem.name || url) : url;
                              const snippet = typeof urlItem === 'object' ? (urlItem.snippet || urlItem.description || '') : '';
                              return (
                                <a
                                  key={idx}
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="group flex items-start gap-3 p-3 bg-white hover:bg-blue-50/60 border border-slate-200 hover:border-blue-300 rounded-xl transition-all shadow-2xs hover:shadow-md cursor-pointer"
                                >
                                  <div className="w-7 h-7 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center shrink-0 mt-0.5 group-hover:bg-blue-200 transition-colors">
                                    <span className="material-symbols-outlined text-sm">language</span>
                                  </div>
                                  <div className="flex flex-col gap-0.5 min-w-0 flex-1">
                                    <span className="text-xs font-semibold text-slate-800 group-hover:text-blue-700 truncate transition-colors">
                                      {title}
                                    </span>
                                    {snippet && (
                                      <span className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                                        {snippet}
                                      </span>
                                    )}
                                    <span className="text-[10px] text-blue-500 font-['JetBrains_Mono',monospace] truncate mt-0.5">
                                      {url}
                                    </span>
                                  </div>
                                  <span className="material-symbols-outlined text-sm text-slate-300 group-hover:text-blue-500 transition-colors shrink-0 mt-1">
                                    open_in_new
                                  </span>
                                </a>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* AI Source Citation Badge — only for RAG responses, not web search */}
                    {msg.sender === 'ai' && !msg.isWebSearch && msg.file_name && (
                      <div className="flex items-center gap-2 mt-0.5">
                        {msg.file_name.toLowerCase().endsWith('.pdf') && msg.page_number ? (
                          <button
                            onClick={() => handleViewSource(msg.file_name, msg.page_number)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-100/70 hover:bg-amber-200/80 border border-amber-200 hover:border-amber-400 rounded-full font-['JetBrains_Mono',monospace] text-[11px] text-amber-800 transition-all cursor-pointer shadow-2xs hover:shadow-sm"
                            title="Click to view source PDF"
                          >
                            <span className="material-symbols-outlined text-xs">picture_as_pdf</span>
                            <span>Source: <strong>{msg.file_name}</strong></span>
                            <span className="opacity-70">· Page {msg.page_number}</span>
                          </button>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-100/70 border border-amber-200 rounded-full font-['JetBrains_Mono',monospace] text-[11px] text-amber-800">
                            <span className="material-symbols-outlined text-xs">bookmark</span>
                            <span>Source: <strong>{msg.file_name}</strong></span>
                            {msg.page_number && <span className="opacity-70">· Page {msg.page_number}</span>}
                          </span>
                        )}
                      </div>
                    )}

                    <span className={`text-[10px] text-slate-400 px-1 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.timestamp}
                    </span>
                  </div>
                </div>
              ))
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex gap-3 max-w-xl mr-auto animate-fade-in-up">
                <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-base animate-spin">sync</span>
                </div>
                <div className="p-4 bg-white border border-slate-200 rounded-2xl rounded-tl-none flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-bounce"></span>
                    <span className="w-2 h-2 rounded-full bg-amber-500 animate-bounce [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 rounded-full bg-amber-600 animate-bounce [animation-delay:0.4s]"></span>
                  </div>
                  <span className="text-xs text-slate-500 font-['JetBrains_Mono',monospace]">Retrieving chunks from ChromaDB...</span>
                </div>
              </div>
            )}

            {/* Web Search Loading Indicator */}
            {webSearchingMsgId !== null && (
              <div className="flex gap-3 max-w-xl mr-auto animate-fade-in-up">
                <div className="w-8 h-8 rounded-lg bg-blue-500 text-white flex items-center justify-center shrink-0 animate-pulse-glow">
                  <span className="material-symbols-outlined text-base animate-orbit">travel_explore</span>
                </div>
                <div className="p-4 bg-white border border-blue-200 rounded-2xl rounded-tl-none flex flex-col gap-3 min-w-[280px]">
                  {/* Animated status text */}
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 web-search-dot"></span>
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 web-search-dot"></span>
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 web-search-dot"></span>
                    </div>
                    <span className="text-xs text-blue-700 font-semibold font-['JetBrains_Mono',monospace] transition-all">
                      {searchPhases[searchPhase]}
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full h-1 bg-blue-100 rounded-full overflow-hidden">
                    <div className="h-full w-1/3 bg-gradient-to-r from-blue-400 via-blue-500 to-blue-400 rounded-full animate-progress-indeterminate"></div>
                  </div>

                  {/* Animated radar graphic */}
                  <div className="flex items-center gap-3">
                    <div className="relative w-8 h-8">
                      <div className="absolute inset-0 rounded-full border-2 border-blue-200"></div>
                      <div className="absolute inset-1 rounded-full border border-blue-100"></div>
                      <div className="absolute inset-0 rounded-full border-t-2 border-transparent border-t-blue-500 animate-radar"></div>
                      <div className="absolute inset-[10px] rounded-full bg-blue-500"></div>
                    </div>
                    <span className="text-[11px] text-slate-400 font-['JetBrains_Mono',monospace]">
                      This may take a moment...
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>

          {/* Input Dock */}
          <div className="p-4 bg-white border-t border-slate-200 shrink-0">
            <form onSubmit={handleSendChat} className="relative flex items-center max-w-4xl mx-auto">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about your knowledge base..."
                className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-4 pr-14 py-3.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all shadow-inner"
              />
              <button
                type="submit"
                disabled={!query.trim() || loading}
                className="absolute h-10 w-10 right-2 p-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-40 disabled:hover:bg-amber-500 text-white rounded-[50%] transition-all shadow-xs hover:shadow-md hover:scale-105 active:scale-95"
              >
                <span className="flex items-center justify-center material-symbols-outlined text-lg">send</span>
              </button>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
