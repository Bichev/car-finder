import React, { useState, useEffect } from 'react'
import { 
  Car, 
  Search, 
  Zap, 
  TrendingUp, 
  MapPin, 
  Bot, 
  Sparkles,
  ChevronDown,
  Play,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Calendar,
  Gauge,
  ExternalLink,
  Brain,
  Globe,
  BarChart3,
  Shield,
  Rocket,
  Users
} from 'lucide-react'
import SearchForm from './components/SearchForm'
import ProgressTracker from './components/ProgressTracker'
import ResultsDisplay from './components/ResultsDisplay'
import FeatureCard from './components/FeatureCard'
import toast from 'react-hot-toast'

function App() {
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [showDemo, setShowDemo] = useState(false)

  const handleSearch = async (searchParams) => {
    setIsSearching(true)
    setCurrentStep(0)
    setSearchResults(null)
    setShowDemo(true)

    try {
      // Step 1: Start search
      setCurrentStep(1)
      toast.loading('Starting vehicle search...', { id: 'search' })

      // Step 2: Scraping Cars.com
      setCurrentStep(2)
      toast.loading('Scraping Cars.com with AI automation...', { id: 'search' })

      const response = await fetch('/api/v1/search-execution/test/playwright', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          marketplace: 'cars_com',
          make: searchParams.make,
          model: searchParams.model,
          year_min: searchParams.yearMin,
          year_max: searchParams.yearMax,
          price_min: searchParams.priceMin,
          price_max: searchParams.priceMax,
          location_zip: searchParams.zipCode,
          headless: true,
          timeout_seconds: 90
        })
      })

      if (!response.ok) {
        throw new Error('Search failed')
      }

      const scrapingResult = await response.json()

      if (!scrapingResult.results.success) {
        throw new Error(scrapingResult.results.error || 'Failed to find vehicles')
      }

      // Step 3: AI Analysis
      setCurrentStep(3)
      toast.loading('Analyzing market data with AI...', { id: 'search' })

      const vehicleCount = scrapingResult.results.vehicles_found
      const analysisQuery = `I found ${vehicleCount} ${searchParams.make} ${searchParams.model} vehicles (${searchParams.yearMin}-${searchParams.yearMax}) in the $${searchParams.priceMin.toLocaleString()}-$${searchParams.priceMax.toLocaleString()} price range in ZIP code ${searchParams.zipCode}. Provide market analysis, value assessment, investment opportunity rating, and regional recommendations.`

      const analysisResponse = await fetch('/api/v1/search-execution/test/perplexity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: analysisQuery,
          model: 'sonar-pro',
          max_tokens: 800,
          timeout_seconds: 30
        })
      })

      if (!analysisResponse.ok) {
        throw new Error('Analysis failed')
      }

      const analysisResult = await analysisResponse.json()

      // Step 4: Complete
      setCurrentStep(4)
      
      setSearchResults({
        scraping: scrapingResult,
        analysis: analysisResult
      })

      toast.success(`Found ${vehicleCount} vehicles with AI insights!`, { id: 'search' })

    } catch (error) {
      console.error('Search error:', error)
      toast.error(`Search failed: ${error.message}`, { id: 'search' })
      setCurrentStep(0)
    } finally {
      // Set isSearching to false after a small delay to show completion
      setTimeout(() => {
        setIsSearching(false)
      }, 1000)
    }
  }

  const scrollToDemo = () => {
    document.getElementById('demo-section').scrollIntoView({ 
      behavior: 'smooth' 
    })
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:60px_60px]" />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/50 to-transparent" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            {/* Demo Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8 animate-pulse-slow">
              <Sparkles className="w-4 h-4 mr-2" />
              Live Demo Platform
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              AI-Powered
              <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Car Discovery
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Revolutionary platform that automates vehicle search and market analysis using 
              <span className="text-white font-semibold"> advanced web scraping</span> and 
              <span className="text-white font-semibold"> AI-powered insights</span>
            </p>

            {/* Value Propositions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto">
              <div className="flex items-center justify-center space-x-3 text-slate-300">
                <Bot className="w-6 h-6 text-blue-400" />
                <span>Automated Scraping</span>
              </div>
              <div className="flex items-center justify-center space-x-3 text-slate-300">
                <Brain className="w-6 h-6 text-purple-400" />
                <span>AI Market Analysis</span>
              </div>
              <div className="flex items-center justify-center space-x-3 text-slate-300">
                <TrendingUp className="w-6 h-6 text-cyan-400" />
                <span>Real-time Insights</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={scrollToDemo}
                className="btn-primary text-lg px-8 py-4 group"
              >
                <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                Try Live Demo
              </button>
              <a
                href="#features"
                className="btn-secondary text-lg px-8 py-4 bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                Learn More
              </a>
            </div>

            {/* Scroll Indicator */}
            <div className="mt-16 animate-bounce-gentle">
              <ChevronDown className="w-6 h-6 text-slate-400 mx-auto" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How AI Revolutionizes Car Discovery
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform combines cutting-edge web automation with advanced AI to deliver 
              insights that would take hours of manual research
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Bot className="w-8 h-8" />}
              title="Intelligent Web Scraping"
              description="Playwright automation navigates sites like a real user, bypassing anti-bot measures and extracting accurate data from Cars.com and other marketplaces."
              color="blue"
            />
            
            <FeatureCard
              icon={<Brain className="w-8 h-8" />}
              title="AI Market Analysis"
              description="Perplexity AI analyzes market trends, depreciation patterns, and regional factors to provide actionable investment insights."
              color="purple"
            />
            
            <FeatureCard
              icon={<TrendingUp className="w-8 h-8" />}
              title="Real-time Insights"
              description="Get instant market valuations, price comparisons, and opportunity ratings updated with the latest market conditions."
              color="green"
            />
            
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Anti-Detection Technology"
              description="Advanced browser fingerprinting and human-like behavior patterns ensure reliable data collection without getting blocked."
              color="red"
            />
            
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8" />}
              title="Competitive Analysis"
              description="Compare prices across multiple platforms and get detailed market positioning analysis for informed decision making."
              color="indigo"
            />
            
            <FeatureCard
              icon={<Globe className="w-8 h-8" />}
              title="Multi-Market Coverage"
              description="Search across different geographic regions with location-specific insights and regional market dynamics."
              color="cyan"
            />
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo-section" className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Experience AI Car Discovery
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See our AI-powered platform in action. Enter your search criteria and watch as we 
              automatically discover vehicles and provide intelligent market analysis.
            </p>
          </div>

          {/* Search Interface */}
          {!showDemo && (
            <div className="max-w-4xl mx-auto">
              <SearchForm onSearch={handleSearch} isLoading={isSearching} />
            </div>
          )}

          {/* Progress Tracker */}
          {showDemo && (
            <div className="max-w-6xl mx-auto">
              <ProgressTracker 
                currentStep={currentStep} 
                isSearching={isSearching}
                onReset={() => {
                  setShowDemo(false)
                  setSearchResults(null)
                  setCurrentStep(0)
                }}
              />
              
              {/* Results */}
              {searchResults && (
                <div className="mt-12">
                  <ResultsDisplay results={searchResults} />
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Perfect for Businesses & Entrepreneurs
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Whether you're a car dealer, investor, or marketplace owner, our AI platform 
                scales to meet your vehicle discovery and analysis needs.
              </p>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <Users className="w-6 h-6 text-blue-500 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Car Dealerships</h3>
                    <p className="text-gray-600">Automate inventory sourcing and competitive analysis</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <DollarSign className="w-6 h-6 text-green-500 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Investors & Flippers</h3>
                    <p className="text-gray-600">Identify undervalued vehicles with profit potential</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <Rocket className="w-6 h-6 text-purple-500 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Marketplace Platforms</h3>
                    <p className="text-gray-600">Enhanced search capabilities for your users</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl p-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500 rounded-full mb-6">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Ready to Scale Your Business?
                </h3>
                <p className="text-gray-600 mb-6">
                  This demo shows just a fraction of our platform's capabilities. 
                  Contact us to discuss custom solutions for your specific needs.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">API Integration</span>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Custom Data Sources</span>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">White-label Solutions</span>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Enterprise Support</span>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Car className="w-8 h-8 text-blue-400" />
              <span className="text-2xl font-bold">AI Car Finder</span>
            </div>
            <p className="text-slate-400 mb-6">
              Revolutionizing vehicle discovery through AI and automation
            </p>
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm">
              <AlertCircle className="w-4 h-4 mr-2" />
              Demo Platform - Contact us for production access
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App 