import React, { useState, useEffect, useRef, Fragment } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Shield, 
  Cpu, 
  Play,
  Zap,
  Terminal as TerminalIcon,
  CheckCircle,
  GitBranch
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { Agent } from '../types';

// Mock Data
const INITIAL_AGENTS: Agent[] = [
  { id: '1', name: 'ProductManager', role: 'Product Manager', status: 'idle', model: 'GPT-4 Turbo' },
  { id: '2', name: 'Architect', role: 'Architect', status: 'idle', model: 'Claude 3.5 Sonnet' },
  { id: '3', name: 'Engineer-1', role: 'Engineer', status: 'idle', model: 'GPT-4' },
  { id: '4', name: 'QA-Bot', role: 'QA', status: 'idle', model: 'Llama 3 70B' },
  { id: '5', name: 'DevOps-Bot', role: 'DevOps', status: 'idle', model: 'Claude 3.5 Sonnet' },
];

const METRICS_DATA = [
  { time: '10:00', tokens: 120, quality: 85 },
  { time: '10:05', tokens: 450, quality: 88 },
  { time: '10:10', tokens: 890, quality: 92 },
  { time: '10:15', tokens: 670, quality: 90 },
  { time: '10:20', tokens: 230, quality: 95 },
  { time: '10:25', tokens: 540, quality: 94 },
  { time: '10:30', tokens: 800, quality: 96 },
];

const LOG_MOCK = [
  { id: '1', timestamp: '10:00:01', agentId: 'System', message: 'AdvancedAI DevTeam initialized.', type: 'info' },
  { id: '2', timestamp: '10:00:02', agentId: 'Orchestrator', message: 'Agents connected via Redis Pub/Sub.', type: 'info' },
  { id: '3', timestamp: '10:00:03', agentId: 'DevOps', message: 'Kubernetes cluster ready.', type: 'success' },
];

interface AgentCardProps {
    agent: Agent;
}

const AgentCard = ({ agent }: AgentCardProps) => {
  const getStatusColor = (status: string) => {
    switch(status) {
      case 'thinking': return 'text-yellow-400 border-yellow-400/50 bg-yellow-400/10 shadow-[0_0_15px_rgba(250,204,21,0.2)]';
      case 'working': return 'text-green-400 border-green-400/50 bg-green-400/10 shadow-[0_0_15px_rgba(74,222,128,0.2)]';
      case 'error': return 'text-red-400 border-red-400/50 bg-red-400/10';
      case 'completed': return 'text-blue-400 border-blue-400/50 bg-blue-400/10';
      default: return 'text-gray-400 border-white/5 bg-white/5';
    }
  };

  const getStatusDot = (status: string) => {
     switch(status) {
      case 'thinking': return 'bg-yellow-400 animate-pulse';
      case 'working': return 'bg-green-400 animate-pulse';
      case 'error': return 'bg-red-400';
      case 'completed': return 'bg-blue-400';
      default: return 'bg-gray-600';
    }
  }

  return (
    <motion.div 
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`p-4 rounded-xl border ${getStatusColor(agent.status)} backdrop-blur-md transition-all h-full flex flex-col`}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
           <div className={`w-2 h-2 rounded-full ${getStatusDot(agent.status)}`} />
           <h3 className="font-bold text-sm tracking-wide">{agent.name}</h3>
        </div>
        <span className="text-[10px] uppercase opacity-70 border border-current px-1.5 py-0.5 rounded-full">
          {agent.status}
        </span>
      </div>
      <div className="flex-1">
         <div className="text-xs text-white/50 mb-1 font-medium">{agent.role}</div>
         <div className="text-[10px] text-white/30 font-mono bg-black/20 px-2 py-1 rounded w-fit">{agent.model}</div>
      </div>
      
      <AnimatePresence>
        {agent.currentTask && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 text-xs border-t border-white/10 pt-2 text-white/80"
          >
            <span className="text-brand-purple font-semibold">Current Task:</span>
            <p className="mt-1 opacity-80 leading-relaxed">{agent.currentTask}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const RaceModeVisualizer = ({ isActive }: { isActive: boolean }) => {
    return (
        <AnimatePresence>
            {isActive && (
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="col-span-12 lg:col-span-8 bg-[#130f24] rounded-2xl border border-[#9b87f5]/50 shadow-[0_0_30px_rgba(155,135,245,0.15)] p-6 mb-6"
                >
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-[#9b87f5]">
                            <Zap className="animate-pulse fill-current" />
                            <h3 className="font-bold text-lg">RACE MODE ACTIVE</h3>
                        </div>
                        <span className="text-xs bg-[#9b87f5]/20 text-[#9b87f5] px-2 py-1 rounded border border-[#9b87f5]/30">Multi-Model Ensemble</span>
                    </div>
                    <div className="space-y-4">
                        {['GPT-4 Turbo', 'Claude 3.5 Sonnet', 'Llama 3 70B'].map((model, i) => (
                            <div key={model} className="space-y-1">
                                <div className="flex justify-between text-xs text-white/70">
                                    <span>{model}</span>
                                    <span className="font-mono">Generating...</span>
                                </div>
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                    <motion.div 
                                        initial={{ width: 0 }}
                                        animate={{ width: '100%' }}
                                        transition={{ duration: 2 + i, repeat: Infinity, ease: "linear" }}
                                        className={`h-full bg-gradient-to-r ${
                                            i === 0 ? 'from-green-500 to-green-300' :
                                            i === 1 ? 'from-purple-500 to-purple-300' :
                                            'from-blue-500 to-blue-300'
                                        }`}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

export const Dashboard = () => {
  const [agents, setAgents] = useState(INITIAL_AGENTS);
  const [logs, setLogs] = useState<{ id: string; timestamp: string; agentId: string; message: string; type: string; }[]>(LOG_MOCK);
  const [prompt, setPrompt] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRaceMode, setIsRaceMode] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const handleStart = () => {
    if(!prompt) return;
    setIsProcessing(true);
    
    const addLog = (source: string, msg: string, type: string = 'info') => {
        setLogs(prev => [...prev, { id: Date.now().toString(), timestamp: new Date().toLocaleTimeString(), agentId: source, message: msg, type }]);
    };

    addLog('User', `New Requirement: ${prompt}`, 'info');

    // Step 1: PM Analyzes
    setTimeout(() => {
      setAgents(prev => prev.map(a => a.role === 'Product Manager' ? { ...a, status: 'thinking', currentTask: 'Parsing requirements and generating user stories...' } : a));
    }, 500);

    // Step 2: PM Completes, Architect Starts
    setTimeout(() => {
       setAgents(prev => prev.map(a => a.role === 'Product Manager' ? { ...a, status: 'completed', currentTask: undefined } : a));
       addLog('ProductManager', 'PRD Generated. Requirements validated.', 'success');
       
       setAgents(prev => prev.map(a => a.role === 'Architect' ? { ...a, status: 'working', currentTask: 'Designing Microservices Architecture and Database Schema...' } : a));
       addLog('Orchestrator', 'Handoff: PRD -> Architect Agent', 'info');
    }, 3500);

    // Step 3: Architect Completes, Engineers Race
    setTimeout(() => {
        setAgents(prev => prev.map(a => a.role === 'Architect' ? { ...a, status: 'completed', currentTask: undefined } : a));
        addLog('Architect', 'System Design finalized. Architecture event published.', 'success');
        
        setIsRaceMode(true);
        addLog('Orchestrator', 'INITIATING RACE MODE: Parallel execution on 3 models.', 'warning');
        setAgents(prev => prev.map(a => a.role === 'Engineer' ? { ...a, status: 'working', currentTask: 'RACE MODE: Generating Python backend via GPT-4...' } : a));
    }, 6500);

    // Step 4: Race Ends, QA Starts
    setTimeout(() => {
        setIsRaceMode(false);
        addLog('Orchestrator', 'Race Complete. Winner: GPT-4 Turbo (98% accuracy)', 'success');
        setAgents(prev => prev.map(a => a.role === 'Engineer' ? { ...a, status: 'completed', currentTask: undefined } : a));

        setAgents(prev => prev.map(a => a.role === 'QA' ? { ...a, status: 'working', currentTask: 'Running Unit Tests and Security Scan...' } : a));
        addLog('QA-Bot', 'Starting automated test suite...', 'info');
    }, 10000);

    // Step 5: QA Completes, DevOps Deploys
    setTimeout(() => {
        setAgents(prev => prev.map(a => a.role === 'QA' ? { ...a, status: 'completed', currentTask: undefined } : a));
        addLog('QA-Bot', 'All tests passed. Coverage: 92%.', 'success');
        
        setAgents(prev => prev.map(a => a.role === 'DevOps' ? { ...a, status: 'working', currentTask: 'Generating Kubernetes Manifests and Helm Charts...' } : a));
        addLog('DevOps-Bot', 'Building Docker images...', 'info');
    }, 13000);

    // Final
    setTimeout(() => {
        setAgents(prev => prev.map(a => a.role === 'DevOps' ? { ...a, status: 'completed', currentTask: undefined } : a));
        addLog('System', 'Project Deployed Successfully. Access at https://staging.api.dev', 'success');
        setIsProcessing(false);
    }, 16000);
  };

  return (
    <div className="min-h-screen bg-[#0a0613] text-white font-sans selection:bg-[#9b87f5]/30 p-6 pt-24 pb-10">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex justify-between items-end pb-6 border-b border-white/5">
          <div>
            <h1 className="text-3xl font-light tracking-tight">Mission Control</h1>
            <p className="text-white/40 mt-1 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                System Operational
            </p>
          </div>
          <div className="flex gap-4">
             <div className="bg-[#151520] px-4 py-2 rounded-lg border border-white/5 flex flex-col items-center">
                <span className="text-[10px] text-white/40 uppercase">Active Agents</span>
                <span className="text-xl font-bold">{agents.filter(a => a.status !== 'idle').length}</span>
             </div>
             <div className="bg-[#151520] px-4 py-2 rounded-lg border border-white/5 flex flex-col items-center">
                <span className="text-[10px] text-white/40 uppercase">Projects Built</span>
                <span className="text-xl font-bold">142</span>
             </div>
          </div>
        </header>

        {/* Input Section */}
        <section className="bg-[#151520] p-1 rounded-2xl border border-white/10 shadow-xl max-w-3xl mx-auto">
            <div className="relative flex items-center">
                <input 
                    type="text" 
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe your software project (e.g., 'A Kanban board with real-time collaboration')..."
                    className="w-full bg-transparent border-none text-white px-6 py-4 focus:ring-0 placeholder:text-white/20 text-lg"
                    onKeyDown={(e) => e.key === 'Enter' && handleStart()}
                />
                <button 
                    onClick={handleStart}
                    disabled={isProcessing || !prompt}
                    className={`mr-2 p-3 rounded-xl transition-all ${isProcessing || !prompt ? 'bg-white/5 text-white/20' : 'bg-[#9b87f5] text-white hover:shadow-[0_0_20px_rgba(155,135,245,0.4)]'}`}
                >
                    <Play size={20} fill="currentColor" className={isProcessing ? 'opacity-0' : ''} />
                    {isProcessing && <div className="absolute inset-0 m-auto w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>}
                </button>
            </div>
        </section>

        {/* Race Mode Visualization */}
        <div className="grid grid-cols-12 gap-6">
             <div className="col-span-12">
                 <RaceModeVisualizer isActive={isRaceMode} />
             </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-6 h-[600px]">
            
            {/* Agent Status Grid */}
            <div className="col-span-12 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 h-full content-start">
                {agents.map((agent) => (
                    <Fragment key={agent.id}>
                        <AgentCard agent={agent} />
                    </Fragment>
                ))}
                
                {/* Real-time Metrics Chart */}
                <div className="col-span-1 md:col-span-2 lg:col-span-3 bg-[#151520] rounded-xl border border-white/5 p-4 mt-auto">
                    <div className="flex items-center gap-2 mb-4">
                        <Activity className="text-[#9b87f5] w-4 h-4" />
                        <h3 className="text-xs uppercase font-bold text-white/40">System Performance</h3>
                    </div>
                    <div className="h-48 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={METRICS_DATA}>
                                <defs>
                                    <linearGradient id="colorTokens" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#9b87f5" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#9b87f5" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="time" stroke="rgba(255,255,255,0.2)" fontSize={10} />
                                <YAxis stroke="rgba(255,255,255,0.2)" fontSize={10} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#0a0613', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="tokens" stroke="#9b87f5" fillOpacity={1} fill="url(#colorTokens)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Terminal / Logs */}
            <div className="col-span-12 lg:col-span-4 bg-[#0d0d11] rounded-xl border border-white/10 flex flex-col overflow-hidden h-full shadow-2xl">
                <div className="bg-[#1a1a24] px-4 py-3 flex items-center justify-between border-b border-white/5">
                    <div className="flex items-center gap-2">
                        <TerminalIcon className="w-4 h-4 text-white/40" />
                        <span className="text-xs font-mono text-white/60">devteam-cli --watch</span>
                    </div>
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/50"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/50"></div>
                    </div>
                </div>
                <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-3 custom-scrollbar">
                    {logs.map((log) => (
                        <motion.div 
                            key={log.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex gap-3"
                        >
                            <span className="text-white/30 shrink-0 select-none">[{log.timestamp}]</span>
                            <div className="flex flex-col">
                                <span className={`font-bold mb-0.5 ${
                                    log.agentId === 'System' ? 'text-blue-400' :
                                    log.agentId === 'Orchestrator' ? 'text-purple-400' :
                                    log.agentId === 'DevOps' ? 'text-orange-400' :
                                    'text-green-400'
                                }`}>
                                    {log.agentId}
                                </span>
                                <span className={`${
                                    log.type === 'error' ? 'text-red-400' :
                                    log.type === 'success' ? 'text-green-300' :
                                    log.type === 'warning' ? 'text-yellow-300' :
                                    'text-white/70'
                                }`}>
                                    {log.message}
                                </span>
                            </div>
                        </motion.div>
                    ))}
                    <div ref={logsEndRef} />
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};