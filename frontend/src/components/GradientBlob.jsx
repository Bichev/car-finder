import React from 'react'

const GradientBlob = ({ className = "" }) => {
  return (
    <div className={`absolute pointer-events-none ${className}`}>
      {/* Main blob */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-purple-400/30 to-pink-400/30 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
      
      {/* Secondary blob */}
      <div className="absolute top-40 right-10 w-72 h-72 bg-gradient-to-r from-yellow-400/30 to-red-400/30 rounded-full mix-blend-multiply filter blur-xl animate-blob" style={{ animationDelay: '2s' }}></div>
      
      {/* Tertiary blob */}
      <div className="absolute bottom-20 left-20 w-72 h-72 bg-gradient-to-r from-green-400/30 to-blue-400/30 rounded-full mix-blend-multiply filter blur-xl animate-blob" style={{ animationDelay: '4s' }}></div>
    </div>
  )
}

export default GradientBlob 