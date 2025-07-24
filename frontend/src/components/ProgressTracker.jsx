import React from 'react'
import { 
  Search, 
  Bot, 
  Brain, 
  CheckCircle, 
  Loader, 
  Car,
  RotateCcw 
} from 'lucide-react'

const ProgressTracker = ({ currentStep, isSearching, onReset }) => {
  const steps = [
    {
      id: 1,
      title: 'Initializing Search',
      description: 'Setting up AI automation parameters',
      icon: Search,
      color: 'blue'
    },
    {
      id: 2,
      title: 'Web Scraping',
      description: 'Playwright automation collecting vehicle data from Cars.com',
      icon: Bot,
      color: 'purple'
    },
    {
      id: 3,
      title: 'AI Analysis',
      description: 'Perplexity AI analyzing market trends and opportunities',
      icon: Brain,
      color: 'indigo'
    },
    {
      id: 4,
      title: 'Complete',
      description: 'Results ready with AI-powered insights',
      icon: CheckCircle,
      color: 'green'
    }
  ]

  const getStepStatus = (stepId) => {
    if (currentStep > stepId) return 'completed'
    if (currentStep === stepId) return 'active'
    return 'pending'
  }

  const getStatusIcon = (step) => {
    const status = getStepStatus(step.id)
    
    if (status === 'completed') {
      return <CheckCircle className="w-6 h-6 text-green-500" />
    }
    
    if (status === 'active') {
      return <Loader className="w-6 h-6 text-blue-500 animate-spin" />
    }
    
    const IconComponent = step.icon
    return <IconComponent className="w-6 h-6 text-gray-400" />
  }

  const getStepClasses = (step) => {
    const status = getStepStatus(step.id)
    const baseClasses = "relative p-6 rounded-xl border-2 transition-all duration-500"
    
    if (status === 'completed') {
      return `${baseClasses} bg-green-50 border-green-200 shadow-lg`
    }
    
    if (status === 'active') {
      return `${baseClasses} bg-blue-50 border-blue-300 shadow-xl scale-105 ring-2 ring-blue-200`
    }
    
    return `${baseClasses} bg-gray-50 border-gray-200`
  }

  const getProgressBarWidth = () => {
    if (currentStep === 0) return '0%'
    return `${((currentStep - 1) / (steps.length - 1)) * 100}%`
  }

  return (
    <div className="card p-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full mb-4">
          <Car className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">AI Search in Progress</h3>
                 <p className="text-gray-600">
           {currentStep === 4 && !isSearching
             ? 'Search completed! Review your results below.'
             : currentStep === 4 && isSearching
             ? 'Finalizing results and preparing insights...'
             : isSearching
             ? 'Our AI is working hard to find the best vehicles for you...'
             : 'Search completed! Review your results below.'
           }
         </p>
        
        {!isSearching && (
          <button
            onClick={onReset}
            className="mt-4 btn-secondary inline-flex items-center"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Start New Search
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Search Progress</span>
          <span className="text-sm text-gray-500">
            Step {currentStep} of {steps.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full transition-all duration-1000 ease-out"
            style={{ width: getProgressBarWidth() }}
          />
        </div>
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map((step, index) => (
          <div key={step.id} className={getStepClasses(step)}>
            {/* Step Number */}
            <div className="absolute -top-3 -left-3 w-8 h-8 bg-white rounded-full border-2 border-current flex items-center justify-center text-sm font-bold">
              {step.id}
            </div>
            
            {/* Status Icon */}
            <div className="flex justify-center mb-4">
              {getStatusIcon(step)}
            </div>
            
            {/* Step Content */}
            <div className="text-center">
              <h4 className="font-semibold text-gray-900 mb-2">{step.title}</h4>
              <p className="text-sm text-gray-600">{step.description}</p>
              
              {/* Active Step Animation */}
              {getStepStatus(step.id) === 'active' && (
                <div className="mt-4">
                  <div className="flex justify-center space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce animation-delay-200"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce animation-delay-400"></div>
                  </div>
                </div>
              )}
              
              {/* Completed Checkmark */}
              {getStepStatus(step.id) === 'completed' && (
                <div className="mt-4">
                  <div className="inline-flex items-center text-green-600 text-sm font-medium">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Completed
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Real-time Status Messages */}
      {isSearching && (
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100">
          <div className="text-center">
            <div className="inline-flex items-center text-blue-700 mb-2">
              <Loader className="w-5 h-5 mr-2 animate-spin" />
              <span className="font-medium">
                {currentStep === 1 && 'Initializing AI automation...'}
                {currentStep === 2 && 'Scraping vehicle listings from Cars.com...'}
                {currentStep === 3 && 'Analyzing market data with Perplexity AI...'}
                {currentStep === 4 && 'Finalizing results...'}
              </span>
            </div>
            <p className="text-sm text-blue-600">
              {currentStep === 1 && 'Setting up browser automation and search parameters'}
              {currentStep === 2 && 'Our Playwright bot is navigating Cars.com and extracting vehicle data'}
              {currentStep === 3 && 'AI is analyzing depreciation patterns, market trends, regional factors, and investment opportunities'}
              {currentStep === 4 && 'Preparing comprehensive results with actionable insights'}
            </p>
            
            {/* Detailed Perplexity Progress */}
            {currentStep === 3 && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-center space-x-2 text-purple-600">
                  <Brain className="w-4 h-4" />
                  <span className="text-sm font-medium">AI Analysis in Progress</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-purple-500">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                    <span>Market trend analysis</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse animation-delay-200"></div>
                    <span>Price depreciation patterns</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse animation-delay-400"></div>
                    <span>Regional market factors</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse animation-delay-600"></div>
                    <span>Investment opportunity rating</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Estimated Time */}
      {isSearching && currentStep < 4 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">
            ⏱️ Estimated completion: {currentStep <= 2 ? '60-90 seconds' : '30-45 seconds'}
          </p>
        </div>
      )}
      
      {/* Completion Message */}
      {currentStep === 4 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-green-600 font-medium">
            🎉 Analysis complete! Scroll down to view results
          </p>
        </div>
      )}
    </div>
  )
}

export default ProgressTracker 