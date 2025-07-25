import React from 'react'

const ShimmerText = ({ children, className = "" }) => {
  return (
    <div className={`relative inline-block group ${className}`}>
      <span className="relative z-10">{children}</span>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -skew-x-12 opacity-0 group-hover:opacity-100 group-hover:animate-shimmer transition-opacity duration-300"></div>
    </div>
  )
}

export default ShimmerText 