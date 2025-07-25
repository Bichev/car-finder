import React, { useState, useEffect } from 'react'

const TypewriterText = ({ text, speed = 50, delay = 0, className = "" }) => {
  const [displayText, setDisplayText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [started, setStarted] = useState(false)

  useEffect(() => {
    const startTimer = setTimeout(() => {
      setStarted(true)
    }, delay)

    return () => clearTimeout(startTimer)
  }, [delay])

  useEffect(() => {
    if (!started || currentIndex >= text.length) return

    const timer = setTimeout(() => {
      setDisplayText(prev => prev + text[currentIndex])
      setCurrentIndex(prev => prev + 1)
    }, speed)

    return () => clearTimeout(timer)
  }, [currentIndex, speed, text, started])

  return (
    <span className={className}>
      {displayText}
      <span className="animate-pulse text-blue-400">|</span>
    </span>
  )
}

export default TypewriterText 