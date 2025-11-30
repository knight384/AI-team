export interface Agent {
  id: string;
  name: string;
  role: 'Product Manager' | 'Architect' | 'Engineer' | 'QA' | 'DevOps' | 'Security';
  status: 'idle' | 'thinking' | 'working' | 'completed' | 'error';
  currentTask?: string;
  model: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  agentId: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export interface ProjectMetrics {
  codeQuality: number;
  testCoverage: number;
  securityScore: number;
  developmentTime: string;
}

export enum AgentModel {
  GPT4 = 'GPT-4 Turbo',
  CLAUDE = 'Claude 3.5 Sonnet',
  LLAMA = 'Llama 3 70B'
}