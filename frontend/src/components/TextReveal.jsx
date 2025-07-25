import React, { useEffect, useState } from 'react'

const TextReveal = ({ children, className = "", delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <div className={`overflow-hidden ${className}`}>
      <div
        className={`transform transition-all duration-1000 ease-out ${
          isVisible
            ? 'translate-y-0 opacity-100'
            : 'translate-y-8 opacity-0'
        }`}
      >
        {children}
      </div>
    </div>
  )
}

export default TextReveal 