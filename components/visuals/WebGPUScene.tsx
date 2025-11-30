
import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Stars, Float, Sparkles } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';

const AnimatedMesh = () => {
    const mesh = useRef<THREE.Mesh>(null);
    
    useFrame((state) => {
        if(mesh.current) {
            mesh.current.rotation.x = state.clock.elapsedTime * 0.2;
            mesh.current.rotation.y = state.clock.elapsedTime * 0.1;
        }
    });

    return (
        <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
            <mesh ref={mesh}>
                <torusKnotGeometry args={[1, 0.3, 128, 32]} />
                <meshStandardMaterial 
                    color="#9b87f5" 
                    roughness={0.1}
                    metalness={0.8}
                    emissive="#5b47a5"
                    emissiveIntensity={0.5}
                    wireframe={true}
                />
            </mesh>
        </Float>
    );
};

const SceneContent = () => {
    return (
        <>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} color="#ffffff" />
            <pointLight position={[-10, -10, -10]} intensity={1} color="#9b87f5" />
            
            <AnimatedMesh />
            
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
            <Sparkles count={200} scale={10} size={2} speed={0.4} opacity={0.5} color="#00ffff" />
            
            <fog attach="fog" args={['#0a0613', 5, 20]} />
        </>
    );
};

export const WebGPUScene = () => {
  const titleWords = 'Build Your Dreams'.split(' ');
  const subtitle = 'AI-powered creativity for the next generation.';
  const [visibleWords, setVisibleWords] = useState(0);
  const [subtitleVisible, setSubtitleVisible] = useState(false);
  const [delays, setDelays] = useState<number[]>([]);
  const [subtitleDelay, setSubtitleDelay] = useState(0);

  useEffect(() => {
    setDelays(titleWords.map(() => Math.random() * 0.07));
    setSubtitleDelay(Math.random() * 0.1);
  }, [titleWords.length]);

  useEffect(() => {
    if (visibleWords < titleWords.length) {
      const timeout = setTimeout(() => setVisibleWords(visibleWords + 1), 600);
      return () => clearTimeout(timeout);
    } else {
      const timeout = setTimeout(() => setSubtitleVisible(true), 800);
      return () => clearTimeout(timeout);
    }
  }, [visibleWords, titleWords.length]);

  return (
    <div className="h-screen w-full relative bg-black overflow-hidden">
      {/* Overlay Content */}
      <div className="absolute inset-0 z-10 pointer-events-none flex flex-col items-center justify-center">
        <div className="text-3xl md:text-5xl xl:text-6xl 2xl:text-7xl font-extrabold text-center px-4">
          <div className="flex space-x-2 lg:space-x-4 overflow-hidden text-white justify-center flex-wrap">
            {titleWords.map((word, index) => (
              <div
                key={index}
                className={index < visibleWords ? 'fade-in' : ''}
                style={{ 
                    animationDelay: `${index * 0.13 + (delays[index] || 0)}s`, 
                    opacity: index < visibleWords ? 1 : 0,
                    transition: 'opacity 0.5s ease-out'
                }}
              >
                {word}
              </div>
            ))}
          </div>
        </div>
        <div className="text-sm md:text-xl xl:text-2xl mt-6 overflow-hidden text-white/80 font-light tracking-wide text-center px-4 max-w-2xl">
          <div
            className={subtitleVisible ? 'fade-in-subtitle' : ''}
            style={{ 
                animationDelay: `${titleWords.length * 0.13 + 0.2 + subtitleDelay}s`, 
                opacity: subtitleVisible ? 1 : 0,
                transition: 'opacity 0.8s ease-out'
            }}
          >
            {subtitle}
          </div>
        </div>
      </div>

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20">
         <motion.div 
            animate={{ y: [0, 10, 0], opacity: [0.5, 1, 0.5] }} 
            transition={{ repeat: Infinity, duration: 2 }}
            className="text-white/50 text-sm flex flex-col items-center gap-2"
         >
            Scroll to explore
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 5V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M6 12L11 17L16 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
         </motion.div>
      </div>

      {/* 3D Scene */}
      <Canvas className="absolute inset-0 z-0" camera={{ position: [0, 0, 5], fov: 45 }}>
         <SceneContent />
      </Canvas>
    </div>
  );
};
