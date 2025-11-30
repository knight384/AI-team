import React from 'react';
import GlobeHero from '../components/visuals/GlobeHero';
import { WebGPUScene } from '../components/visuals/WebGPUScene';
import { motion } from 'framer-motion';
import { Cpu, Shield, Zap, Layout, GitBranch, Terminal } from 'lucide-react';

const features = [
  {
    icon: <Zap className="w-6 h-6 text-[#9b87f5]" />,
    title: "Race Mode Architecture",
    description: "Parallel execution of GPT-4, Claude 3.5, and Llama 3 models to compete for the best code generation output."
  },
  {
    icon: <Terminal className="w-6 h-6 text-[#9b87f5]" />,
    title: "Complete DevOps Integration",
    description: "Auto-generated Dockerfiles, Kubernetes manifests, and CI/CD pipelines ready for production deployment."
  },
  {
    icon: <Cpu className="w-6 h-6 text-[#9b87f5]" />,
    title: "Autonomous Agents",
    description: "Specialized agents for Product Management, Architecture, Engineering, QA, and Security working in concert."
  },
  {
    icon: <Shield className="w-6 h-6 text-[#9b87f5]" />,
    title: "Enterprise Security",
    description: "Built-in automated security scanning, dependency vulnerability checks, and compliance reporting."
  },
  {
    icon: <GitBranch className="w-6 h-6 text-[#9b87f5]" />,
    title: "Version Control",
    description: "Seamless integration with GitHub/GitLab, including automated PR creation and code reviews."
  },
  {
    icon: <Layout className="w-6 h-6 text-[#9b87f5]" />,
    title: "Real-time Dashboard",
    description: "Watch your AI team work in real-time with visual workflow tracking and live terminal logs."
  }
];

export const LandingPage = () => {
  return (
    <div className="bg-[#0a0613] min-h-screen font-sans text-white selection:bg-[#9b87f5]/30">
      {/* Intro Scene */}
      <section className="h-screen w-full relative">
        <WebGPUScene />
      </section>

      {/* Hero Section with Globe */}
      <GlobeHero />

      {/* Features Section based on PDF */}
      <section className="py-24 px-6 max-w-7xl mx-auto relative z-10" id="features">
        <div className="text-center mb-16">
           <motion.span 
             initial={{ opacity: 0 }}
             whileInView={{ opacity: 1 }}
             className="text-[#9b87f5] text-sm font-mono tracking-wider uppercase"
           >
             Platform Capabilities
           </motion.span>
           <motion.h2 
             initial={{ opacity: 0, y: 20 }}
             whileInView={{ opacity: 1, y: 0 }}
             className="text-4xl md:text-5xl font-light mt-4 mb-6"
           >
             Beyond Simple <span className="text-[#9b87f5]">Code Generation</span>
           </motion.h2>
           <p className="text-white/60 max-w-2xl mx-auto text-lg">
             AdvancedAI DevTeam isn't just a chatbot. It's a comprehensive software development platform that handles the entire lifecycle.
           </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="p-8 rounded-2xl bg-[#151520] border border-white/5 hover:border-[#9b87f5]/50 transition-colors group"
            >
              <div className="w-12 h-12 rounded-full bg-[#9b87f5]/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-medium mb-3">{feature.title}</h3>
              <p className="text-white/50 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-[#050308]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-white font-bold text-xl tracking-tight">
            AI DevTeam
          </div>
          <div className="text-white/40 text-sm">
            © 2025 AdvancedAI DevTeam. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};