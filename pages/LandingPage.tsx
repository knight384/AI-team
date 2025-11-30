
import React from 'react';
import GlobeHero from '../components/visuals/GlobeHero';
import { WebGPUScene } from '../components/visuals/WebGPUScene';
import { motion } from 'framer-motion';

export const LandingPage = () => {
  return (
    <div className="bg-[#0a0613] min-h-screen">
      {/* Intro Scene */}
      <section className="h-screen w-full relative">
        <WebGPUScene />
      </section>

      {/* Hero Section with Globe */}
      <GlobeHero />

      {/* Features Section based on PDF */}
      <section className="py-24 px-6 max-w-7xl mx-auto" id="features">
        <div className="text-center mb-16">
           <h2 className="text-3xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50">Enterprise Features</h2>
           <p className="text-white/60 max-w-2xl mx-auto">Better than MGX. Built for production-ready code generation.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
               title="Race Mode" 
               description="Multi-model ensemble approach running GPT-4, Claude 3.5, and Llama simultaneously to select the best code."
               icon="🏎️"
            />
            <FeatureCard 
               title="DevOps Integrated" 
               description="Auto-generated Dockerfiles, Kubernetes manifests, and Terraform scripts for instant deployment."
               icon="🚢"
            />
             <FeatureCard 
               title="Security First" 
               description="Integrated SAST scanning, dependency vulnerability checks, and GDPR compliance validation."
               icon="🔒"
            />
        </div>
      </section>
    </div>
  );
};

const FeatureCard = ({ title, description, icon }: { title: string, description: string, icon: string }) => (
    <motion.div 
       whileHover={{ y: -5 }}
       className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-brand-purple/50 transition-colors"
    >
        <div className="text-4xl mb-4">{icon}</div>
        <h3 className="text-xl font-bold mb-2 text-white">{title}</h3>
        <p className="text-white/60 leading-relaxed">{description}</p>
    </motion.div>
);
