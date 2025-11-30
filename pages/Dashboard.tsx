
import React, { useState, useEffect, useRef, Fragment } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Shield, 
  Code, 
  MessageSquare, 
  Play,
  Database,
  Terminal as TerminalIcon,
  Cpu
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

const AgentCard = ({ agent }: { agent: Agent }) => {
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

export const Dashboard = () => {
  const [agents, setAgents] = useState(INITIAL_AGENTS);
  const [logs, setLogs] = useState<{ id: string; timestamp: string; agentId: string; message: string; type: string; }[]>(LOG_MOCK);
  const [prompt, setPrompt] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
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
    
    // Simulate Workflow Steps
    const addLog = (source: string, msg: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
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
        addLog('Architect', 'System Design finalized. Architecture diagrams generated.', 'success');
        
        setAgents(prev => prev.map(a => a.role === 'Engineer' ? { ...a, status: 'working', currentTask: 'Generating backend boilerplate (FastAPI)...' } : a));
        addLog('Orchestrator', 'Initiating RACE MODE: 3 models generating code in parallel.', 'warning');
     }, 7000);

     // Step 4: Complete
     setTimeout(() => {
        setAgents(prev => prev.map(a => a.role === 'Engineer' ? { ...a, status: 'completed', currentTask: undefined } : a));
        addLog('Engineer-1', 'Backend API implementation completed. Tests passing.', 'success');
        
        setAgents(prev => prev.map(a => a.role === 'QA' ? { ...a, status: 'working', currentTask: 'Running E2E tests and security scan...' } : a));
        addLog('Orchestrator', 'Triggering QA Agent workflow.', 'info');
     }, 10500);

     // Step 5: Finish
     setTimeout(() => {
        setAgents(prev => prev.map(a => a.role === 'QA' ? { ...a, status: 'completed', currentTask: undefined } : a));
        addLog('QA-Bot', 'All tests passed. Security score: 98/100.', 'success');
        setAgents(prev => prev.map(a => a.role === 'DevOps' ? { ...a, status: 'working', currentTask: 'Deploying to staging environment...' } : a));
     }, 14000);
     
     setTimeout(() => {
        setAgents(prev => prev.map(a => a.role === 'DevOps' ? { ...a, status: 'completed' } : a));
        addLog('DevOps-Bot', 'Deployment successful. URL: https://staging.project-x.com', 'success');
        setIsProcessing(false);
     }, 17000);
  };

  return (
    <div className="min-h-screen bg-[#0a0613] text-white font-sans selection:bg-[#9b87f5]/30">
        {/* Header */}
        <header className="border-b border-white/5 bg-[#0a0613]/50 backdrop-blur-md sticky top-0 z-50">
           <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-xl">
                 <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#9b87f5] to-[#5b47a5] flex items-center justify-center">
                    <Cpu size={18} className="text-white" />
                 </div>
                 AdvancedAI <span className="text-[#9b87f5]">DevTeam</span>
              </div>
              <div className="flex items-center gap-4">
                 <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    System Operational
                 </div>
                 <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center border border-white/5">
                    <span className="text-xs font-bold">JD</span>
                 </div>
              </div>
           </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-6 h-[calc(100vh-4rem)]">
            {/* Left Column: Agents & Metrics */}
            <div className="col-span-12 lg:col-span-8 flex flex-col gap-6 h-full overflow-hidden">
                {/* Agent Fleet */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 h-40 shrink-0">
                   {agents.map(agent => (
                      <Fragment key={agent.id}>
                        <AgentCard agent={agent} />
                      </Fragment>
                   ))}
                </div>

                {/* Metrics & Main View */}
                <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6 min-h-0">
                    <div className="bg-[#130f24] rounded-2xl border border-white/5 p-6 flex flex-col">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="font-semibold flex items-center gap-2">
                               <Activity size={18} className="text-[#9b87f5]" />
                               Real-time Performance
                            </h3>
                            <select className="bg-black/20 border border-white/10 rounded-lg text-xs px-2 py-1 outline-none">
                               <option>Last 30 mins</option>
                            </select>
                        </div>
                        <div className="flex-1 w-full min-h-0">
                           <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={METRICS_DATA}>
                                 <defs>
                                    <linearGradient id="colorTokens" x1="0" y1="0" x2="0" y2="1">
                                       <stop offset="5%" stopColor="#9b87f5" stopOpacity={0.3}/>
                                       <stop offset="95%" stopColor="#9b87f5" stopOpacity={0}/>
                                    </linearGradient>
                                 </defs>
                                 <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                                 <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#ffffff50', fontSize: 10}} />
                                 <YAxis axisLine={false} tickLine={false} tick={{fill: '#ffffff50', fontSize: 10}} />
                                 <Tooltip 
                                    contentStyle={{backgroundColor: '#1a1625', borderColor: '#ffffff10', borderRadius: '8px'}}
                                    itemStyle={{color: '#fff'}}
                                 />
                                 <Area type="monotone" dataKey="tokens" stroke="#9b87f5" strokeWidth={2} fillOpacity={1} fill="url(#colorTokens)" />
                              </AreaChart>
                           </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="bg-[#130f24] rounded-2xl border border-white/5 p-6 flex flex-col">
                        <h3 className="font-semibold flex items-center gap-2 mb-6">
                           <Shield size={18} className="text-green-400" />
                           Security & Quality
                        </h3>
                        <div className="space-y-6">
                           <div>
                              <div className="flex justify-between text-sm mb-2">
                                 <span className="text-white/60">Code Quality Score</span>
                                 <span className="font-mono text-[#9b87f5]">96/100</span>
                              </div>
                              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                 <div className="h-full bg-gradient-to-r from-[#9b87f5] to-[#7e61e7] w-[96%]" />
                              </div>
                           </div>
                           <div>
                              <div className="flex justify-between text-sm mb-2">
                                 <span className="text-white/60">Test Coverage</span>
                                 <span className="font-mono text-green-400">88%</span>
                              </div>
                              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                 <div className="h-full bg-green-400 w-[88%]" />
                              </div>
                           </div>
                           <div>
                              <div className="flex justify-between text-sm mb-2">
                                 <span className="text-white/60">Security Vulnerabilities</span>
                                 <span className="font-mono text-white">0 Critical</span>
                              </div>
                              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                 <div className="h-full bg-white/20 w-full" />
                              </div>
                           </div>
                        </div>
                    </div>
                </div>

                {/* Input Area */}
                <div className="h-24 bg-[#130f24] rounded-2xl border border-white/5 p-2 flex gap-2 shrink-0">
                    <textarea 
                       value={prompt}
                       onChange={(e) => setPrompt(e.target.value)}
                       placeholder="Describe the software you want to build..." 
                       className="flex-1 bg-transparent border-none resize-none focus:ring-0 p-3 text-sm placeholder:text-white/20"
                       disabled={isProcessing}
                    />
                    <button 
                       onClick={handleStart}
                       disabled={!prompt || isProcessing}
                       className={`px-6 rounded-xl font-medium transition-all flex items-center gap-2 ${
                          !prompt || isProcessing 
                          ? 'bg-white/5 text-white/20 cursor-not-allowed' 
                          : 'bg-[#9b87f5] text-white hover:bg-[#8b77e5] shadow-lg shadow-[#9b87f5]/20'
                       }`}
                    >
                       {isProcessing ? (
                          <Activity className="animate-spin" size={20} />
                       ) : (
                          <>
                             <Play size={20} fill="currentColor" />
                             Start Build
                          </>
                       )}
                    </button>
                </div>
            </div>

            {/* Right Column: Logs/Terminal */}
            <div className="col-span-12 lg:col-span-4 bg-[#0f0b1e] rounded-2xl border border-white/10 flex flex-col overflow-hidden h-full">
               <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                     <TerminalIcon size={16} className="text-white/40" />
                     <span className="text-sm font-mono text-white/60">System Logs</span>
                  </div>
                  <div className="flex gap-1.5">
                     <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                     <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                     <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
                  </div>
               </div>
               
               <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-3 custom-scrollbar">
                  {logs.map((log) => (
                     <div key={log.id} className="flex gap-3 animate-fade-in">
                        <span className="text-white/30 shrink-0">{log.timestamp}</span>
                        <div className="flex-1">
                           <span className={`font-bold mr-2 ${
                              log.agentId === 'System' ? 'text-blue-400' :
                              log.agentId === 'Error' ? 'text-red-400' :
                              'text-[#9b87f5]'
                           }`}>
                              [{log.agentId}]
                           </span>
                           <span className={
                              log.type === 'error' ? 'text-red-400' :
                              log.type === 'success' ? 'text-green-400' :
                              log.type === 'warning' ? 'text-yellow-400' :
                              'text-white/70'
                           }>
                              {log.message}
                           </span>
                        </div>
                     </div>
                  ))}
                  <div ref={logsEndRef} />
               </div>
            </div>
        </main>
    </div>
  );
};
