import React from 'react'

const AnimatedCard = ({ children, className = "", delay = 0 }) => {
  return (
    <div 
      className={`transform transition-all duration-700 hover:scale-105 hover:-translate-y-2 hover:shadow-2xl hover:shadow-blue-500/20 ${className}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="relative group">
        {/* Glow effect on hover */}
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl blur opacity-0 group-hover:opacity-30 transition duration-1000"></div>
        
        {/* Card content */}
        <div className="relative bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-3xl p-8 hover:bg-slate-800/70 transition-all duration-300">
          {children}
        </div>
      </div>
    </div>
  )
}

export default AnimatedCard 