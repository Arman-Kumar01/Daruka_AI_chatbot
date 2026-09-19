import React, { useState, useEffect, useRef } from 'react'

// Production API base URL — set VITE_API_BASE_URL in Vercel environment variables
// to your Render backend URL, e.g. https://darukaa-ai.onrender.com
// In development (npm run dev), this is empty so Vite proxy handles /api/* routing
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
import {
  Sprout,
  Compass,
  FileCode,
  MessageSquare,
  Sparkles,
  Database,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Layers,
  ChevronRight,
  TrendingUp,
  Sliders,
  Send,
  HelpCircle,
  BookOpen,
  Info
} from 'lucide-react'

export default function App() {
  // Navigation & View states
  const [activeInputTab, setActiveInputTab] = useState('chat') // 'chat' | 'form' | 'json'
  const [activeRightTab, setActiveRightTab] = useState('diagnostics') // 'diagnostics' | 'rag_explorer' | 'sources'

  // Data & Execution states
  const [sessionId, setSessionId] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [systemHealth, setSystemHealth] = useState(null)
  const [sourcesList, setSourcesList] = useState([])
  const [demoScenarios, setDemoScenarios] = useState([])

  // Environmental Assessment Output
  const [assessmentData, setAssessmentData] = useState(null)

  // Structured Form Input State
  const [formState, setFormState] = useState({
    region: 'semi-arid',
    latitude: 31.5,
    longitude: 35.2,
    soil_ph: 6.2,
    organic_carbon_percent: 0.3,
    moisture_percent: 12.0,
    land_use: 'monoculture wheat',
    rainfall: 'low',
    temperature_c: 31.0,
    species_richness: 'low',
    habitat_diversity: 'low',
    pollinator_presence: 'low',
    pollution: 'medium',
    deforestation: 'low',
    pesticide_intensity: 'high'
  })

  // Raw JSON input
  const [jsonText, setJsonText] = useState('')

  const chatContainerRef = useRef(null)
  const chatEndRef = useRef(null)
  const isNearBottomRef = useRef(true)
  const userJustSentRef = useRef(false)

  // Initial Load: Check health, load sources and scenarios
  useEffect(() => {
    fetchHealth()
    fetchSources()
    fetchScenarios()
    // Initialize JSON editor with default form state
    syncFormToJson(formState)
  }, [])

  const handleChatScroll = () => {
    const container = chatContainerRef.current
    if (!container) return
    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight
    // If within 80px of bottom, consider user is at bottom
    isNearBottomRef.current = distanceFromBottom <= 80
  }

  const scrollToBottom = (behavior = 'smooth') => {
    requestAnimationFrame(() => {
      const container = chatContainerRef.current
      if (container) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior
        })
      }
    })
  }

  // Smoothly auto-scroll when new message arrives or loading changes,
  // without fighting the user if they manually scrolled up to read older messages
  useEffect(() => {
    if (userJustSentRef.current || isNearBottomRef.current) {
      scrollToBottom('smooth')
      userJustSentRef.current = false
    }
  }, [chatMessages, loading])

  // When switching to conversational chat tab, scroll to bottom if at bottom
  useEffect(() => {
    if (activeInputTab === 'chat' && isNearBottomRef.current) {
      scrollToBottom('auto')
    }
  }, [activeInputTab])

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/health`)
      if (res.ok) {
        const data = await res.json()
        setSystemHealth(data)
      }
    } catch (e) {
      console.warn('Backend not yet reachable on /api/health', e)
    }
  }

  const fetchSources = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sources`)
      if (res.ok) {
        const data = await res.json()
        setSourcesList(data.sources || [])
      }
    } catch (e) {
      console.warn('Failed to load sources', e)
    }
  }

  const fetchScenarios = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/scenarios`)
      if (res.ok) {
        const data = await res.json()
        setDemoScenarios(data.scenarios || [])
      }
    } catch (e) {
      console.warn('Failed to load demo scenarios', e)
    }
  }

  const syncFormToJson = (f) => {
    const formatted = {
      region: f.region || undefined,
      coordinates: f.latitude ? { latitude: Number(f.latitude), longitude: Number(f.longitude) } : undefined,
      soil: {
        ph: f.soil_ph ? Number(f.soil_ph) : undefined,
        organic_carbon_percent: f.organic_carbon_percent !== '' ? Number(f.organic_carbon_percent) : undefined,
        moisture_percent: f.moisture_percent !== '' ? Number(f.moisture_percent) : undefined
      },
      land_use: f.land_use || undefined,
      rainfall: f.rainfall || undefined,
      temperature_c: f.temperature_c ? Number(f.temperature_c) : undefined,
      biodiversity: {
        species_richness: f.species_richness || undefined,
        habitat_diversity: f.habitat_diversity || undefined,
        pollinator_presence: f.pollinator_presence || undefined
      },
      human_impact: {
        pollution: f.pollution || undefined,
        deforestation: f.deforestation || undefined,
        pesticide_intensity: f.pesticide_intensity || undefined
      }
    }
    setJsonText(JSON.stringify(formatted, null, 2))
  }

  const handleFormChange = (key, value) => {
    const updated = { ...formState, [key]: value }
    setFormState(updated)
    syncFormToJson(updated)
  }

  const loadScenario = (scenario) => {
    const d = scenario.data
    const newForm = {
      region: d.region || '',
      latitude: d.coordinates?.latitude || 31.5,
      longitude: d.coordinates?.longitude || 35.2,
      soil_ph: d.soil?.ph ?? 6.2,
      organic_carbon_percent: d.soil?.organic_carbon_percent ?? 0.3,
      moisture_percent: d.soil?.moisture_percent ?? 12.0,
      land_use: d.land_use || '',
      rainfall: d.rainfall || '',
      temperature_c: d.temperature_c ?? 25.0,
      species_richness: d.biodiversity?.species_richness || 'low',
      habitat_diversity: d.biodiversity?.habitat_diversity || 'low',
      pollinator_presence: d.biodiversity?.pollinator_presence || 'low',
      pollution: d.human_impact?.pollution || 'low',
      deforestation: d.human_impact?.deforestation || 'low',
      pesticide_intensity: d.human_impact?.pesticide_intensity || 'low'
    }
    setFormState(newForm)
    syncFormToJson(newForm)

    // Also trigger direct analysis
    executeStructuredAnalysis(d)
  }

  const executeStructuredAnalysis = async (structuredPayload) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(structuredPayload)
      })
      if (!res.ok) throw new Error(`Server returned status ${res.status}`)
      const data = await res.json()
      setAssessmentData(data)
      setSessionId(data.session_id)
      setActiveRightTab('diagnostics')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChatSubmit = async (e) => {
    e?.preventDefault()
    if (!chatInput.trim()) return

    const userQuery = chatInput.trim()
    setChatInput('')
    userJustSentRef.current = true
    isNearBottomRef.current = true
    setChatMessages((prev) => [...prev, { role: 'user', content: userQuery }])
    scrollToBottom('smooth')
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userQuery
        })
      })
      if (!res.ok) throw new Error(`Chat API error: ${res.status}`)
      const data = await res.json()
      setSessionId(data.session_id)
      setAssessmentData(data)

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.scientific_summary,
          missingInfo: data.missing_information,
          clarifyingQuestions: data.clarifying_questions
        }
      ])
    } catch (e) {
      setError(e.message)
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error connecting to Environmental Scientist reasoning engine: ${e.message}` }
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleJsonSubmit = () => {
    try {
      const parsed = JSON.parse(jsonText)
      executeStructuredAnalysis(parsed)
    } catch (e) {
      setError(`JSON syntax error: ${e.message}`)
    }
  }

  const resetSession = () => {
    setSessionId(null)
    setChatMessages([])
    setAssessmentData(null)
    setError(null)
    isNearBottomRef.current = true
    userJustSentRef.current = false
  }

  return (
    <div className="min-h-screen lg:h-screen lg:overflow-hidden flex flex-col bg-[#090d16] text-slate-100">
      {/* Top Navbar */}
      <header className="shrink-0 border-b border-white/10 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white font-display">Darukaa.Earth</h1>
              <span className="text-[11px] font-semibold uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                AI Biodiversity Intelligence
              </span>
            </div>
            <p className="text-xs text-slate-400">Multi-Variable Ecological Reasoning & Scientific Grounding Engine</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Status badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-white/5 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>RAG Active: {systemHealth ? `${systemHealth.indexed_chunks} Chunks` : 'Indexed'}</span>
            <span className="text-slate-500">•</span>
            <span className="text-emerald-400">FAO / IPCC / UNEP</span>
          </div>

          <button
            onClick={resetSession}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors border border-white/5"
            title="Clear current conversational state and memory"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>

          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="hidden md:flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-medium border border-emerald-500/30 transition-colors"
          >
            <span>OpenAPI Docs</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </header>

      {/* Demo Scenario Quick-Launcher Bar */}
      <div className="shrink-0 bg-slate-900/40 border-b border-white/5 px-6 py-2.5 flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-slate-400 font-medium flex items-center gap-1 shrink-0">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Challenge Scenarios:
        </span>
        {demoScenarios.map((sc, idx) => (
          <button
            key={sc.id}
            onClick={() => loadScenario(sc)}
            className="shrink-0 px-3 py-1.5 rounded-lg bg-slate-800/70 hover:bg-slate-750 border border-white/10 hover:border-emerald-500/40 text-slate-200 transition-all flex items-center gap-1.5 group"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>{sc.name}</span>
            <ChevronRight className="w-3 h-3 text-slate-500 group-hover:text-emerald-400 transition-colors" />
          </button>
        ))}
      </div>

      {/* Main Split Layout */}
      <main className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-6 p-4 lg:p-6 max-w-[1700px] w-full mx-auto">
        {/* Left Column: Input Modes (Chat / Structured Form / JSON) */}
        <section className="lg:col-span-5 flex flex-col min-h-0 h-[620px] lg:h-full">
          <div className="glass-panel p-4 flex flex-col flex-1 min-h-0 h-full">
            {/* Input Mode Navigation Tabs */}
            <div className="shrink-0 flex items-center justify-between border-b border-white/10 pb-3 mb-4">
              <div className="flex items-center gap-1 p-1 bg-slate-950/60 rounded-xl border border-white/5">
                <button
                  onClick={() => setActiveInputTab('chat')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeInputTab === 'chat'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Conversational</span>
                </button>
                <button
                  onClick={() => setActiveInputTab('form')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeInputTab === 'form'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Sliders className="w-3.5 h-3.5" />
                  <span>Structured Form</span>
                </button>
                <button
                  onClick={() => setActiveInputTab('json')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeInputTab === 'json'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5" />
                  <span>JSON Mode</span>
                </button>
              </div>

              <div className="text-[11px] text-slate-400 flex items-center gap-1">
                <Compass className="w-3 h-3 text-cyan-400" />
                <span>{formState.region || 'Offline GIS Ready'}</span>
              </div>
            </div>

            {/* TAB 1: Conversational Chat */}
            {activeInputTab === 'chat' && (
              <div className="flex-1 flex flex-col min-h-0">
                {/* Chat Message Stream */}
                <div
                  ref={chatContainerRef}
                  onScroll={handleChatScroll}
                  className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden pr-1 space-y-4"
                >
                  {chatMessages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
                      <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3">
                        <MessageSquare className="w-6 h-6" />
                      </div>
                      <h2 className="text-sm font-semibold text-slate-200 mb-1">AI Environmental Scientist Active</h2>
                      <p className="text-xs text-slate-400 max-w-sm mb-4">
                        State your land conditions or environmental observations. The system retains multi-turn memory and detects missing variables before synthesizing multi-variable ecological recommendations.
                      </p>
                      <div className="flex flex-col gap-2 w-full max-w-xs text-left">
                        <button
                          onClick={() => setChatInput('Biodiversity is declining on my land.')}
                          className="text-xs p-2.5 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-white/5 text-slate-300 transition-colors"
                        >
                          "Biodiversity is declining on my land."
                        </button>
                        <button
                          onClick={() =>
                            setChatInput(
                              'In a semi-arid region, my soil organic carbon is 0.3%, rainfall is low, and crop is monoculture wheat.'
                            )
                          }
                          className="text-xs p-2.5 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-white/5 text-slate-300 transition-colors"
                        >
                          "Semi-arid, SOC 0.3%, low rainfall, monoculture wheat."
                        </button>
                      </div>
                    </div>
                  ) : (
                    chatMessages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                      >
                        <div
                          className={`max-w-[90%] rounded-2xl p-4 text-xs leading-relaxed break-words ${
                            msg.role === 'user'
                              ? 'bg-emerald-600/30 border border-emerald-500/40 text-emerald-100'
                              : 'bg-slate-800/80 border border-white/10 text-slate-200'
                          }`}
                        >
                          <div className="font-semibold text-[11px] mb-1 opacity-70">
                            {msg.role === 'user' ? 'User' : 'AI Environmental Scientist'}
                          </div>
                          <div className="whitespace-pre-wrap">{msg.content}</div>

                          {/* Missing Info Prompt within Chat */}
                          {msg.clarifyingQuestions && msg.clarifyingQuestions.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-white/10">
                              <span className="text-[11px] font-semibold text-amber-400 flex items-center gap-1 mb-2">
                                <HelpCircle className="w-3 h-3" /> Clarification Required for Exact Modeling:
                              </span>
                              <ul className="space-y-1 text-slate-300">
                                {msg.clarifyingQuestions.map((q, qIdx) => (
                                  <li key={qIdx} className="flex items-start gap-1.5">
                                    <span className="text-amber-400 font-bold">•</span>
                                    <span>{q}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}

                  {loading && (
                    <div className="flex items-center gap-2 text-xs text-slate-400 py-2">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
                      <span>Retrieving scientific literature & reasoning across variables...</span>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Input Bar */}
                <form onSubmit={handleChatSubmit} className="shrink-0 mt-3 pt-3 border-t border-white/10 flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Describe ecosystem conditions or answer clarifying questions..."
                    className="flex-1 bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
                  />
                  <button
                    type="submit"
                    disabled={loading || !chatInput.trim()}
                    className="shrink-0 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-medium flex items-center gap-1.5 transition-colors shadow-lg shadow-emerald-500/20"
                  >
                    <span>Send</span>
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </form>
              </div>
            )}

            {/* TAB 2: Structured Form Input */}
            {activeInputTab === 'form' && (
              <div className="flex-1 min-h-0 overflow-y-auto pr-1 space-y-4 text-xs">
                {/* Soil Health Section */}
                <div className="p-3.5 rounded-xl bg-slate-950/50 border border-white/5 space-y-3">
                  <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
                    <Sprout className="w-3.5 h-3.5" /> 1. Soil Health Indicators
                  </div>
                  <div className="grid grid-cols-3 gap-2.5">
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Soil pH</label>
                      <input
                        type="number"
                        step="0.1"
                        value={formState.soil_ph}
                        onChange={(e) => handleFormChange('soil_ph', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. 6.2"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">SOC (%)</label>
                      <input
                        type="number"
                        step="0.05"
                        value={formState.organic_carbon_percent}
                        onChange={(e) => handleFormChange('organic_carbon_percent', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. 0.3"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Moisture (%)</label>
                      <input
                        type="number"
                        step="1"
                        value={formState.moisture_percent}
                        onChange={(e) => handleFormChange('moisture_percent', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. 12"
                      />
                    </div>
                  </div>
                </div>

                {/* Climate & Region Section */}
                <div className="p-3.5 rounded-xl bg-slate-950/50 border border-white/5 space-y-3">
                  <div className="font-semibold text-cyan-400 flex items-center gap-1.5">
                    <Compass className="w-3.5 h-3.5" /> 2. Climate & Geography
                  </div>
                  <div className="grid grid-cols-3 gap-2.5">
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Region / Biome</label>
                      <input
                        type="text"
                        value={formState.region}
                        onChange={(e) => handleFormChange('region', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. semi-arid"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Rainfall</label>
                      <select
                        value={formState.rainfall}
                        onChange={(e) => handleFormChange('rainfall', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                      >
                        <option value="low">Low (drought-prone)</option>
                        <option value="medium">Medium (seasonal)</option>
                        <option value="high">High (frequent rain)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Temp (°C)</label>
                      <input
                        type="number"
                        step="1"
                        value={formState.temperature_c}
                        onChange={(e) => handleFormChange('temperature_c', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. 31"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2.5 pt-1">
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Latitude</label>
                      <input
                        type="number"
                        step="0.01"
                        value={formState.latitude}
                        onChange={(e) => handleFormChange('latitude', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Longitude</label>
                      <input
                        type="number"
                        step="0.01"
                        value={formState.longitude}
                        onChange={(e) => handleFormChange('longitude', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                      />
                    </div>
                  </div>
                </div>

                {/* Land Use & Biodiversity */}
                <div className="p-3.5 rounded-xl bg-slate-950/50 border border-white/5 space-y-3">
                  <div className="font-semibold text-amber-400 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5" /> 3. Land Use & Biodiversity Status
                  </div>
                  <div className="grid grid-cols-2 gap-2.5">
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Land Use / Crop</label>
                      <input
                        type="text"
                        value={formState.land_use}
                        onChange={(e) => handleFormChange('land_use', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. monoculture wheat"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Species Richness</label>
                      <select
                        value={formState.species_richness}
                        onChange={(e) => handleFormChange('species_richness', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                      >
                        <option value="low">Low (severely degraded)</option>
                        <option value="medium">Medium</option>
                        <option value="high">High (healthy)</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2.5">
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Habitat Diversity</label>
                      <input
                        type="text"
                        value={formState.habitat_diversity}
                        onChange={(e) => handleFormChange('habitat_diversity', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                        placeholder="e.g. fragmented patches"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[11px] mb-1">Pollution Level</label>
                      <select
                        value={formState.pollution}
                        onChange={(e) => handleFormChange('pollution', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 rounded-lg px-2.5 py-1.5 text-slate-200"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium (chemical runoff)</option>
                        <option value="high">High (heavy agrochemicals)</option>
                      </select>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    const parsed = JSON.parse(jsonText)
                    executeStructuredAnalysis(parsed)
                  }}
                  disabled={loading}
                  className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-white transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Execute Multi-Variable Diagnostic</span>
                </button>
              </div>
            )}

            {/* TAB 3: JSON Mode */}
            {activeInputTab === 'json' && (
              <div className="flex-1 min-h-0 flex flex-col justify-between">
                <div className="text-[11px] text-slate-400 mb-2 flex items-center justify-between">
                  <span>Structured JSON Input Payload:</span>
                  <button
                    onClick={() => syncFormToJson(formState)}
                    className="text-emerald-400 hover:underline"
                  >
                    Reset to Form
                  </button>
                </div>
                <textarea
                  value={jsonText}
                  onChange={(e) => setJsonText(e.target.value)}
                  className="w-full flex-1 min-h-[380px] bg-slate-950 font-mono text-xs text-emerald-300 p-3 rounded-xl border border-white/10 focus:outline-none focus:border-emerald-500/50"
                  spellCheck="false"
                />
                <button
                  onClick={handleJsonSubmit}
                  disabled={loading}
                  className="mt-3 w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-medium text-xs text-white transition-colors"
                >
                  Analyze JSON Payload
                </button>
              </div>
            )}
          </div>
        </section>

        {/* Right Column: Scientific Diagnostics & Evidence Grounding Engine */}
        <section className="lg:col-span-7 flex flex-col min-h-0 h-[620px] lg:h-full">
          <div className="glass-panel p-5 flex flex-col flex-1 min-h-0 h-full">
            {/* View switcher on the right side */}
            <div className="shrink-0 flex items-center justify-between border-b border-white/10 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-cyan-400"></div>
                <h2 className="text-sm font-bold tracking-tight text-white font-display">
                  Ecological Intelligence Dashboard
                </h2>
              </div>

              <div className="flex items-center gap-1.5 p-1 bg-slate-950/60 rounded-xl border border-white/5 text-xs">
                <button
                  onClick={() => setActiveRightTab('diagnostics')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    activeRightTab === 'diagnostics'
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Diagnostic & Interventions
                </button>
                <button
                  onClick={() => setActiveRightTab('rag_explorer')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    activeRightTab === 'rag_explorer'
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Inspect RAG Evidence
                </button>
                <button
                  onClick={() => setActiveRightTab('sources')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    activeRightTab === 'sources'
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Literature Catalog ({sourcesList.length})
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 mb-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* TAB: DIAGNOSTICS & RECOMMENDATIONS */}
            {activeRightTab === 'diagnostics' && (
              <div className="flex-1 min-h-0 overflow-y-auto pr-1 space-y-6">
                {!assessmentData ? (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
                    <Database className="w-10 h-10 text-slate-600 mb-3" />
                    <h3 className="text-sm font-semibold text-slate-300 mb-1">Awaiting Ecological Input</h3>
                    <p className="text-xs text-slate-500 max-w-sm">
                      Select one of the challenge demo scenarios above, or submit conditions via chat or form to generate a multi-variable diagnosis.
                    </p>
                  </div>
                ) : (
                  <>
                    {/* Missing Information Alert if any */}
                    {assessmentData.missing_information && assessmentData.missing_information.length > 0 && (
                      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs space-y-2">
                        <div className="font-semibold flex items-center gap-1.5 text-amber-300">
                          <AlertTriangle className="w-4 h-4 text-amber-400" />
                          <span>Missing Critical Variables for Comprehensive Diagnostic:</span>
                        </div>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                          {assessmentData.missing_information.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Section 1: 5 Pillars Assessment */}
                    <div className="space-y-3">
                      <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Current Environmental Assessment (5 Pillars)</span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2.5 text-xs">
                        <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                          <span className="text-[11px] text-emerald-400 font-semibold block mb-1">Soil Health</span>
                          <p className="text-slate-300 font-mono text-[11px]">
                            pH: {assessmentData.environmental_assessment?.soil?.ph} | SOC: {assessmentData.environmental_assessment?.soil?.organic_carbon_percent}
                          </p>
                          <p className="text-slate-400 text-[10px] mt-1 line-clamp-2">
                            {assessmentData.environmental_assessment?.soil?.status}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                          <span className="text-[11px] text-cyan-400 font-semibold block mb-1">Climate & Rain</span>
                          <p className="text-slate-300 font-mono text-[11px]">
                            {assessmentData.environmental_assessment?.climate?.region}
                          </p>
                          <p className="text-slate-400 text-[10px] mt-1">
                            Rainfall: {assessmentData.environmental_assessment?.climate?.rainfall} | Temp: {assessmentData.environmental_assessment?.climate?.temperature}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                          <span className="text-[11px] text-amber-400 font-semibold block mb-1">Land Use</span>
                          <p className="text-slate-300 text-[11px]">
                            {assessmentData.environmental_assessment?.land_use?.current_practice}
                          </p>
                          <p className="text-slate-400 text-[10px] mt-1">
                            Fragmentation: {assessmentData.environmental_assessment?.land_use?.fragmentation_risk}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                          <span className="text-[11px] text-purple-400 font-semibold block mb-1">Biodiversity</span>
                          <p className="text-slate-300 text-[11px]">
                            Richness: {assessmentData.environmental_assessment?.biodiversity?.species_richness}
                          </p>
                          <p className="text-slate-400 text-[10px] mt-1">
                            Habitats: {assessmentData.environmental_assessment?.biodiversity?.habitat_diversity}
                          </p>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5 col-span-2 md:col-span-2">
                          <span className="text-[11px] text-rose-400 font-semibold block mb-1">Anthropogenic Pressure</span>
                          <p className="text-slate-300 text-[11px]">
                            Pollution: {assessmentData.environmental_assessment?.human_impact?.pollution} | Deforestation: {assessmentData.environmental_assessment?.human_impact?.deforestation}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Section 2: Key Multi-Variable Interactions */}
                    <div className="space-y-2.5">
                      <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                        <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Key Multi-Variable Interactions (Reasoning Core)</span>
                      </div>
                      <div className="space-y-2">
                        {assessmentData.key_interactions?.map((inter, idx) => (
                          <div
                            key={idx}
                            className="p-3.5 rounded-xl bg-slate-900/80 border border-cyan-500/20 text-xs text-slate-200 leading-relaxed shadow-sm"
                          >
                            <div className="font-semibold text-cyan-300 text-[11px] mb-1">
                              Interaction {idx + 1}
                            </div>
                            <p>{inter}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Section 3: Actionable Grounded Recommendations */}
                    <div className="space-y-3">
                      <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Recommended Actions ({assessmentData.recommendations?.length || 0})</span>
                      </div>
                      <div className="space-y-3.5">
                        {assessmentData.recommendations?.map((rec, idx) => (
                          <div
                            key={idx}
                            className="p-4 rounded-xl bg-slate-900/90 border border-white/10 hover:border-emerald-500/40 transition-all space-y-3"
                          >
                            {/* Header: Action Title + Horizon & Confidence badges */}
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-2.5">
                              <h4 className="text-xs font-bold text-white flex items-start gap-1.5">
                                <span className="text-emerald-400 font-mono">{idx + 1}.</span>
                                <span>{rec.action}</span>
                              </h4>
                              <div className="flex items-center gap-1.5 shrink-0">
                                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 flex items-center gap-1">
                                  <Clock className="w-3 h-3" /> {rec.time_horizon}
                                </span>
                                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                                  {rec.confidence}
                                </span>
                              </div>
                            </div>

                            {/* Why & Scientific Mechanism */}
                            <div className="space-y-1.5 text-xs">
                              <div>
                                <span className="text-slate-400 font-medium">Ecological Rationale: </span>
                                <span className="text-slate-200">{rec.why}</span>
                              </div>
                              <div>
                                <span className="text-emerald-400 font-medium">Scientific Mechanism: </span>
                                <span className="text-slate-300 leading-relaxed">{rec.scientific_mechanism}</span>
                              </div>
                            </div>

                            {/* Interacting Variables Badges */}
                            <div className="flex flex-wrap items-center gap-1.5 pt-1">
                              <span className="text-[10px] text-slate-500 uppercase font-semibold">Variables:</span>
                              {rec.interacting_variables?.map((v, vIdx) => (
                                <span
                                  key={vIdx}
                                  className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-white/5"
                                >
                                  {v}
                                </span>
                              ))}
                            </div>

                            {/* Impacted Metrics */}
                            <div className="p-2.5 rounded-lg bg-slate-950/70 border border-white/5 space-y-1">
                              <span className="text-[10px] text-cyan-400 font-semibold uppercase tracking-wider block">
                                Measured Quantitative Impact Targets:
                              </span>
                              <div className="flex flex-wrap gap-2 text-xs">
                                {rec.impacted_metrics?.map((metric, mIdx) => (
                                  <span key={mIdx} className="text-slate-200 font-mono text-[11px] bg-slate-900 px-2 py-0.5 rounded">
                                    ✓ {metric}
                                  </span>
                                ))}
                              </div>
                            </div>

                            {/* Evidence Citation Preview */}
                            {rec.evidence && rec.evidence.length > 0 && (
                              <div className="text-[11px] text-slate-400 border-t border-white/5 pt-2 flex items-center justify-between">
                                <span className="flex items-center gap-1">
                                  <BookOpen className="w-3 h-3 text-emerald-400" />
                                  <span>Grounded by: <strong className="text-slate-200">{rec.evidence[0].organization}</strong> ({rec.evidence[0].year})</span>
                                </span>
                                {rec.evidence[0].url && (
                                  <a
                                    href={rec.evidence[0].url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-emerald-400 hover:underline flex items-center gap-0.5"
                                  >
                                    <span>Source Citation</span>
                                    <ExternalLink className="w-2.5 h-2.5" />
                                  </a>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* TAB: INSPECT RAG EVIDENCE */}
            {activeRightTab === 'rag_explorer' && (
              <div className="flex-1 min-h-0 overflow-y-auto pr-1 space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-white/10 text-slate-400 text-xs mb-3 flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-white">RAG Evidence Grounding Layer</span>
                    <p className="text-[11px]">
                      Demonstrates real semantic retrieval, cosine similarity matching, and provenance from indexed literature.
                    </p>
                  </div>
                  {assessmentData?.retrieval_metadata && (
                    <div className="text-right font-mono text-[11px] text-emerald-400">
                      Query: {assessmentData.retrieval_metadata.retrieval_query || assessmentData.retrieval_metadata.query}
                    </div>
                  )}
                </div>

                {assessmentData?.evidence?.map((ev, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-white/10 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-200 text-xs">{ev.title}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                        {ev.quantitative_metric || 'Relevance Verified'}
                      </span>
                    </div>
                    <div className="text-slate-400 text-[11px] flex items-center gap-2">
                      <span className="text-emerald-400 font-semibold">{ev.organization}</span>
                      <span>•</span>
                      <span>{ev.year}</span>
                      {ev.url && (
                        <>
                          <span>•</span>
                          <a href={ev.url} target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline flex items-center gap-1">
                            DOI / Official Report Link <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        </>
                      )}
                    </div>
                    <p className="text-slate-300 leading-relaxed bg-slate-950/60 p-2.5 rounded-lg border border-white/5 font-mono text-[11px]">
                      "{ev.finding}"
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* TAB: FULL BIBLIOGRAPHIC SOURCES CATALOG */}
            {activeRightTab === 'sources' && (
              <div className="flex-1 min-h-0 overflow-y-auto pr-1 space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-white/10 text-slate-400 mb-3">
                  <span className="font-semibold text-white">Authoritative Knowledge Base Index</span>
                  <p className="text-[11px]">
                    All scientific claims in Darukaa are strictly retrieved from peer-reviewed journals, FAO World Soil reports, IPCC Climate & Land reports, UNEP water quality frameworks, and IPBES assessments.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {sourcesList.map((s, idx) => (
                    <div key={idx} className="p-3.5 rounded-xl bg-slate-900/90 border border-white/5 flex flex-col justify-between">
                      <div>
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block mb-1">
                          {s.organization} ({s.year})
                        </span>
                        <h4 className="font-semibold text-white text-xs mb-1.5">{s.title}</h4>
                        <p className="text-[11px] text-slate-400 mb-2">Topic: {s.topic}</p>
                      </div>
                      <div className="border-t border-white/5 pt-2 flex items-center justify-between">
                        <span className="text-[10px] text-slate-500">Traceable Reference</span>
                        {s.url && (
                          <a
                            href={s.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-cyan-400 hover:underline flex items-center gap-1 text-[11px]"
                          >
                            View Source <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="shrink-0 border-t border-white/5 bg-slate-950/80 px-6 py-3 text-center text-xs text-slate-500">
        Darukaa.Earth AI Biodiversity Intelligence System — Built for Darukaa Hackathon. Grounded in FAO, IPCC, UNEP, IPBES & Peer-Reviewed Ecology.
      </footer>
    </div>
  )
}
