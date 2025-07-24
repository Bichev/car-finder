import React from 'react'

const FeatureCard = ({ icon, title, description, color = 'blue' }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    purple: 'text-purple-600 bg-purple-100',
    green: 'text-green-600 bg-green-100',
    red: 'text-red-600 bg-red-100',
    indigo: 'text-indigo-600 bg-indigo-100',
    cyan: 'text-cyan-600 bg-cyan-100',
    yellow: 'text-yellow-600 bg-yellow-100',
    pink: 'text-pink-600 bg-pink-100'
  }

  return (
    <div className="card p-6 group hover:shadow-2xl transition-all duration-300">
      <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4 ${colorClasses[color]} group-hover:scale-110 transition-transform duration-300`}>
        {icon}
      </div>
      
      <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
        {title}
      </h3>
      
      <p className="text-gray-600 leading-relaxed">
        {description}
      </p>
    </div>
  )
}

export default FeatureCard 