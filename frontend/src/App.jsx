import React, { useState, useEffect } from 'react'
import { Search, Car, TrendingUp, Zap, AlertCircle, CheckCircle, Clock, DollarSign, Target, Users, Briefcase, Shield, Globe, ArrowRight, Star, Crown, Gem, Wrench, Gavel, Monitor, ChefHat, PieChart, BarChart3, Award, Rocket, Eye, Heart, MessageCircle, Phone, Mail, ExternalLink, Play, Sparkles, Trophy, Lightbulb, Cpu, Palette, Building, Home, Factory, ShoppingCart } from 'lucide-react'
import SearchForm from './components/SearchForm'
import ResultsDisplay from './components/ResultsDisplay'
import ProgressTracker from './components/ProgressTracker'
import FeatureCard from './components/FeatureCard'
import TextReveal from './components/TextReveal'
import ShimmerText from './components/ShimmerText'
import FloatingParticles from './components/FloatingParticles'
import MagneticButton from './components/MagneticButton'
import GradientBlob from './components/GradientBlob'
import AnimatedCard from './components/AnimatedCard'
import CountingNumber from './components/CountingNumber'
import TypewriterText from './components/TypewriterText'
import toast, { Toaster } from 'react-hot-toast'

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
    document.getElementById('demo-section')?.scrollIntoView({ behavior: 'smooth' })
  }

  const scrollToContact = () => {
    document.getElementById('contact-section')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      <Toaster position="top-right" />
      
      {/* React Bits Animated Background Effects */}
      <FloatingParticles count={30} color="#3b82f6" />
      <GradientBlob className="opacity-40" />
      
      {/* Navigation */}
      {/* <nav className="fixed top-0 w-full bg-slate-900/80 backdrop-blur-lg border-b border-slate-700/50 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white">ArbitrageAI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#opportunities" className="text-slate-300 hover:text-white transition-colors">Opportunities</a>
              <a href="#demo-section" className="text-slate-300 hover:text-white transition-colors">Demo</a>
              <a href="#contact-section" className="text-slate-300 hover:text-white transition-colors">Contact</a>
              <button 
                onClick={scrollToContact}
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all transform hover:scale-105"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav> */}

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto text-center">
          <TextReveal delay={300}>
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 text-blue-400 text-sm mb-6">
              <Sparkles className="w-4 h-4 mr-2" />
              <ShimmerText>AI-Powered Arbitrage Platform</ShimmerText>
            </div>
          </TextReveal>
          
          <TextReveal delay={600}>
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              <ShimmerText>Turn Arbitrage Markets</ShimmerText>
              {/* <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text">
                <ShimmerText> Inefficiencies</ShimmerText>
              </span> */}
              <br />
              <ShimmerText>Into Profit</ShimmerText>
            </h1>
          </TextReveal>
          
          <TextReveal delay={900}>
            <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Discover hidden arbitrage opportunities across multiple industries using advanced AI automation. 
              From luxury collectibles to B2B equipment - unlock profits that others miss.
            </p>
          </TextReveal>
          
          <TextReveal delay={1200}>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-12 mb-16 mt-8">
              {/* Demo Button with Badge */}
              <div className="relative group pt-8 pb-4">
                {/* Hot Badge - Much higher positioning */}
                <div className="absolute top-0 -right-4 z-40 transform rotate-12">
                  <div className="bg-gradient-to-r from-red-500 to-orange-500 text-white text-xs px-3 py-1.5 rounded-full font-bold shadow-xl animate-pulse hover:animate-bounce border-2 border-white/20">
                    🔥 HOT
                  </div>
                </div>
                <MagneticButton 
                  onClick={scrollToDemo}
                  className="relative overflow-hidden border-2 border-slate-600/80 bg-slate-800/40 backdrop-blur-sm text-slate-300 hover:text-white hover:border-blue-400/60 hover:bg-slate-700/60 px-10 py-5 rounded-2xl transition-all duration-300 flex items-center font-semibold text-lg shadow-2xl hover:shadow-blue-500/25 group"
                >
                  {/* Button glow effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <Play className="w-6 h-6 mr-3 animate-float relative z-10" />
                  <span className="relative z-10">
                    <ShimmerText>See Live Demo</ShimmerText>
                  </span>
                  <ArrowRight className="w-6 h-6 ml-3 transform group-hover:translate-x-2 transition-transform duration-300 relative z-10" />
                </MagneticButton>
              </div>

              {/* Opportunities Button with Badges */}
              <div className="relative group pt-8 pb-4 px-6">
                {/* Popular Badge - Left top, much higher */}
                <div className="absolute top-0 -right-2 z-40 transform rotate-12">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs px-3 py-1.5 rounded-full font-bold shadow-xl animate-pulse hover:animate-bounce border-2 border-white/20">
                    ⭐ POPULAR
                  </div>
                </div>
                {/* Premium Badge - Right top, much higher */}
                {/* <div className="absolute top-0 -right-2 z-40 transform rotate-12">
                  <div className="bg-gradient-to-r from-yellow-500 to-yellow-400 text-yellow-900 text-xs px-3 py-1.5 rounded-full font-bold shadow-xl animate-pulse hover:animate-bounce border-2 border-yellow-200/30">
                    👑 PREMIUM
                  </div>
                </div> */}
                <MagneticButton 
                  onClick={() => document.getElementById('opportunities').scrollIntoView({ behavior: 'smooth' })}
                  className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-10 py-5 rounded-2xl transition-all duration-300 transform hover:scale-105 flex items-center font-semibold text-lg shadow-2xl hover:shadow-purple-500/40 group border border-white/10"
                >
                  {/* Button shimmer effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  <Eye className="w-6 h-6 mr-3 animate-float relative z-10" style={{ animationDelay: '0.5s' }} />
                  <span className="relative z-10">
                    <ShimmerText>Explore Opportunities</ShimmerText>
                  </span>
                  <ArrowRight className="w-6 h-6 ml-3 transform group-hover:translate-x-2 transition-transform duration-300 relative z-10" />
                </MagneticButton>
              </div>
            </div>
          </TextReveal>

          {/* Success Indicators */}
          <TextReveal delay={1500}>
            <div className="flex flex-wrap items-center justify-center gap-6 mb-8">
              <div className="relative group">
                <div className="flex items-center px-6 py-3 bg-green-500/15 border border-green-500/30 rounded-full hover:bg-green-500/25 transition-all duration-300 hover:scale-110 cursor-pointer shadow-lg hover:shadow-green-500/20 backdrop-blur-sm">
                  <CheckCircle className="w-5 h-5 text-green-400 mr-3 animate-pulse" />
                  <span className="text-green-400 text-sm font-semibold">
                    <ShimmerText>Automated Scrapping</ShimmerText>
                  </span>
                </div>
                {/* Glow effect */}
                <div className="absolute inset-0 bg-green-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-50 transition-opacity duration-300 -z-10"></div>
              </div>
              <div className="relative group">
                <div className="flex items-center px-6 py-3 bg-blue-500/15 border border-blue-500/30 rounded-full hover:bg-blue-500/25 transition-all duration-300 hover:scale-110 cursor-pointer shadow-lg hover:shadow-blue-500/20 backdrop-blur-sm">
                  <TrendingUp className="w-5 h-5 text-blue-400 mr-3 animate-pulse" style={{ animationDelay: '0.2s' }} />
                  <span className="text-blue-400 text-sm font-semibold">
                    <ShimmerText>Real-Time Perplexity Insights</ShimmerText>
                  </span>
                </div>
                {/* Glow effect */}
                <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-50 transition-opacity duration-300 -z-10"></div>
              </div>
              <div className="relative group">
                <div className="flex items-center px-6 py-3 bg-purple-500/15 border border-purple-500/30 rounded-full hover:bg-purple-500/25 transition-all duration-300 hover:scale-110 cursor-pointer shadow-lg hover:shadow-purple-500/20 backdrop-blur-sm">
                  <Zap className="w-5 h-5 text-purple-400 mr-3 animate-pulse" style={{ animationDelay: '0.4s' }} />
                  <span className="text-purple-400 text-sm font-semibold">
                    <ShimmerText>AI Market Analytics</ShimmerText>
                  </span>
                </div>
                {/* Glow effect */}
                <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-50 transition-opacity duration-300 -z-10"></div>
              </div>
            </div>
          </TextReveal>

          {/* Success Metrics */}
          {/* <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="text-3xl font-bold text-blue-400 mb-2">$50K+</div>
              <div className="text-slate-300 text-sm">Average Monthly Profit</div>
            </div>
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="text-3xl font-bold text-purple-400 mb-2">70%</div>
              <div className="text-slate-300 text-sm">Margin Potential</div>
            </div>
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="text-3xl font-bold text-green-400 mb-2">24/7</div>
              <div className="text-slate-300 text-sm">Automated Scanning</div>
            </div>
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6">
              <div className="text-3xl font-bold text-yellow-400 mb-2">5+</div>
              <div className="text-slate-300 text-sm">Industry Verticals</div>
            </div>
          </div> */}
        </div>
        <TextReveal delay={200}>
            <div className="text-center mb-6">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                <ShimmerText>Unlock Profit in Every Market</ShimmerText>
              </h2>
              <TypewriterText 
                text="Our AI-powered platform identifies arbitrage opportunities across multiple high-value markets, giving you the edge to profit from price inefficiencies that others miss."
                speed={30}
                delay={1000}
                className="text-xl text-slate-300 max-w-3xl mx-auto block"
              />
            </div>
          </TextReveal>
      </section>

      {/* Arbitrage Opportunities Section */}
      <section id="opportunities" className="py-20 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">


          {/* Collectibles & Alternative Assets */}
          <TextReveal delay={600}>
            <AnimatedCard className="mb-20" delay={200}>
              <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl p-8 border border-blue-500/20">
              <div className="flex items-center mb-6">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl mr-4 animate-float">
                  <Crown className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-white">
                    <ShimmerText>Collectibles & Alternative Assets</ShimmerText>
                  </h3>
                  <p className="text-blue-300">
                    <ShimmerText>Luxury watches, trading cards, sneakers, NFTs, and premium collectibles</ShimmerText>
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div className="space-y-4">
                  <div className="flex items-center text-white">
                    <TrendingUp className="w-5 h-5 text-green-400 mr-3" />
                    <span className="font-semibold">20-50% price disparities across platforms</span>
                  </div>
                  <div className="flex items-center text-white">
                    <Globe className="w-5 h-5 text-blue-400 mr-3" />
                    <span className="font-semibold">Global marketplace scanning</span>
                  </div>
                  <div className="flex items-center text-white">
                    <Zap className="w-5 h-5 text-yellow-400 mr-3" />
                    <span className="font-semibold">Instant authenticity verification</span>
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50 hover:bg-slate-800/70 transition-all duration-300 hover:scale-105 group">
                  <h4 className="text-lg font-semibold text-white mb-4">
                    <ShimmerText>Success Example</ShimmerText>
                  </h4>
                  <p className="text-slate-300 mb-4">
                    "Found a Rolex Submariner listed for $8,500 on a European auction site. 
                    Same model selling for $12,000+ in US markets. Net profit: $2,800 after fees."
                  </p>
                  <div className="text-green-400 font-bold text-xl group-hover:animate-pulse">
                    +<CountingNumber end={33} duration={1500} suffix="%" />ROI
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Gem className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Luxury Watches</div>
                  <div className="text-slate-400 text-sm">Rolex, Patek Philippe</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Palette className="w-8 h-8 text-pink-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Trading Cards</div>
                  <div className="text-slate-400 text-sm">Pokémon, Sports, Magic</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Trophy className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Premium Sneakers</div>
                  <div className="text-slate-400 text-sm">Jordan, Yeezy, Off-White</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Cpu className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Digital Assets</div>
                  <div className="text-slate-400 text-sm">NFTs, Domains, Crypto</div>
                </div>
              </div>
              </div>
            </AnimatedCard>
          </TextReveal>

          {/* B2B Equipment & Machinery */}
          <TextReveal delay={800}>
            <AnimatedCard className="mb-20" delay={400}>
              <div className="bg-gradient-to-r from-orange-600/20 to-red-600/20 rounded-3xl p-8 border border-orange-500/20">
              <div className="flex items-center mb-6">
                <div className="p-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl mr-4 animate-float" style={{ animationDelay: '1s' }}>
                  <Wrench className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-white">
                    <ShimmerText>B2B Equipment & Machinery</ShimmerText>
                  </h3>
                  <p className="text-orange-300">
                    <ShimmerText>Medical equipment, construction tools, restaurant gear, IT hardware</ShimmerText>
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div className="space-y-4">
                  <div className="flex items-center text-white">
                    <DollarSign className="w-5 h-5 text-green-400 mr-3" />
                    <span className="font-semibold">40-70% profit margins on liquidations</span>
                  </div>
                  <div className="flex items-center text-white">
                    <Building className="w-5 h-5 text-blue-400 mr-3" />
                    <span className="font-semibold">Business closure opportunities</span>
                  </div>
                  <div className="flex items-center text-white">
                    <Shield className="w-5 h-5 text-purple-400 mr-3" />
                    <span className="font-semibold">Verified seller credentials</span>
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50 hover:bg-slate-800/70 transition-all duration-300 hover:scale-105 group">
                  <h4 className="text-lg font-semibold text-white mb-4">
                    <ShimmerText>Success Example</ShimmerText>
                  </h4>
                  <p className="text-slate-300 mb-4">
                    "Acquired commercial kitchen equipment from restaurant closure for $15K. 
                    Resold individual pieces to multiple buyers for $38K total."
                  </p>
                  <div className="text-green-400 font-bold text-xl group-hover:animate-pulse">
                    +<CountingNumber end={153} duration={1500} suffix="%" />ROI
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Heart className="w-8 h-8 text-red-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Medical Equipment</div>
                  <div className="text-slate-400 text-sm">Imaging, Lab, Surgical</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Home className="w-8 h-8 text-orange-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Construction Tools</div>
                  <div className="text-slate-400 text-sm">Excavators, Generators</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <ChefHat className="w-8 h-8 text-green-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Restaurant Equipment</div>
                  <div className="text-slate-400 text-sm">Ovens, Refrigeration</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center">
                  <Monitor className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">IT Hardware</div>
                  <div className="text-slate-400 text-sm">Servers, Networking</div>
                </div>
              </div>
              </div>
            </AnimatedCard>
          </TextReveal>

          {/* Government Surplus & Auctions */}
          <TextReveal delay={1000}>
            <AnimatedCard className="mb-20" delay={600}>
              <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 rounded-3xl p-8 border border-green-500/20">
              <div className="flex items-center mb-6">
                <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl mr-4 animate-float" style={{ animationDelay: '2s' }}>
                  <Gavel className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-white">
                    <ShimmerText>Government Surplus & Auctions</ShimmerText>
                  </h3>
                  <p className="text-green-300">
                    <ShimmerText>Federal, state, and local government asset disposals</ShimmerText>
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div className="space-y-4">
                  <div className="flex items-center text-white">
                    <Award className="w-5 h-5 text-yellow-400 mr-3" />
                    <span className="font-semibold">50-80% below retail pricing</span>
                  </div>
                  <div className="flex items-center text-white">
                    <Shield className="w-5 h-5 text-green-400 mr-3" />
                    <span className="font-semibold">Verified government sources</span>
                  </div>
                  <div className="flex items-center text-white">
                    <Clock className="w-5 h-5 text-blue-400 mr-3" />
                    <span className="font-semibold">Real-time auction monitoring</span>
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50 hover:bg-slate-800/70 transition-all duration-300 hover:scale-105 group">
                  <h4 className="text-lg font-semibold text-white mb-4">
                    <ShimmerText>Success Example</ShimmerText>
                  </h4>
                  <p className="text-slate-300 mb-4">
                    "Won a lot of surplus laptops at government auction for $1,200. 
                    After refurbishment, sold 50 units at $180 each."
                  </p>
                  <div className="text-green-400 font-bold text-xl group-hover:animate-pulse">
                    +<CountingNumber end={650} duration={1500} suffix="%" />ROI
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/30 rounded-lg p-4 text-center hover:bg-slate-800/50 transition-all duration-300 hover:scale-105">
                  <Car className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Fleet Vehicles</div>
                  <div className="text-slate-400 text-sm">Police, Municipal</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center hover:bg-slate-800/50 transition-all duration-300 hover:scale-105">
                  <Factory className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Heavy Equipment</div>
                  <div className="text-slate-400 text-sm">Tractors, Machinery</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center hover:bg-slate-800/50 transition-all duration-300 hover:scale-105">
                  <Monitor className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Electronics</div>
                  <div className="text-slate-400 text-sm">Computers, Radios</div>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-4 text-center hover:bg-slate-800/50 transition-all duration-300 hover:scale-105">
                  <ShoppingCart className="w-8 h-8 text-pink-400 mx-auto mb-2" />
                  <div className="text-white font-semibold">Seized Assets</div>
                  <div className="text-slate-400 text-sm">Jewelry, Luxury Items</div>
                </div>
              </div>
              </div>
            </AnimatedCard>
          </TextReveal>

          {/* Platform Features */}
          <div className="bg-slate-800/30 rounded-3xl p-8 border border-slate-700/50">
            <h3 className="text-3xl font-bold text-white text-center mb-12">
              Why Our Platform Dominates the Market
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Rocket className="w-8 h-8 text-white" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-3">AI-Powered Analysis</h4>
                <p className="text-slate-300">
                  Advanced machine learning algorithms analyze market trends, pricing patterns, 
                  and identify opportunities with 95% accuracy.
                </p>
              </div>
              
              <div className="text-center">
                <div className="p-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Globe className="w-8 h-8 text-white" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-3">Global Marketplace Coverage</h4>
                <p className="text-slate-300">
                  Monitor 500+ marketplaces, auction sites, and specialty platforms 
                  across multiple countries and time zones.
                </p>
              </div>
              
              <div className="text-center">
                <div className="p-4 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-3">Real-Time Alerts</h4>
                <p className="text-slate-300">
                  Get instant notifications when profitable opportunities emerge, 
                  ensuring you never miss a high-margin deal.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo-section" className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              See the Platform in Action
            </h2>
            <p className="text-xl text-slate-300">
              Experience our vehicle discovery demo - just one example of our arbitrage technology
            </p>
          </div>

          {/* Search Interface */}
          {!showDemo && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-8">
                <SearchForm onSearch={handleSearch} isLoading={isSearching} />
              </div>
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

      {/* ROI Calculator Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-3xl p-8 border border-blue-500/20">
            <div className="text-center mb-8">
              <h3 className="text-3xl font-bold text-white mb-4">Calculate Your Profit Potential</h3>
              <p className="text-slate-300">See how much you could earn with our arbitrage platform</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-800/50 rounded-xl p-6 text-center">
                <div className="text-2xl font-bold text-green-400 mb-2">Conservative</div>
                <div className="text-4xl font-bold text-white mb-4">$5,000</div>
                <div className="text-slate-300 text-sm mb-4">Monthly Net Profit</div>
                <ul className="text-left space-y-2 text-slate-300 text-sm">
                  <li>• 10 deals per month</li>
                  <li>• $500 average profit</li>
                  <li>• 25% success rate</li>
                </ul>
              </div>
              
              <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-xl p-6 text-center border-2 border-blue-500/30">
                <div className="text-2xl font-bold text-blue-400 mb-2">Realistic</div>
                <div className="text-4xl font-bold text-white mb-4">$25,000</div>
                <div className="text-slate-300 text-sm mb-4">Monthly Net Profit</div>
                <ul className="text-left space-y-2 text-slate-300 text-sm">
                  <li>• 50 deals per month</li>
                  <li>• $1,250 average profit</li>
                  <li>• 40% success rate</li>
                </ul>
              </div>
              
              <div className="bg-slate-800/50 rounded-xl p-6 text-center">
                <div className="text-2xl font-bold text-purple-400 mb-2">Aggressive</div>
                <div className="text-4xl font-bold text-white mb-4">$75,000</div>
                <div className="text-slate-300 text-sm mb-4">Monthly Net Profit</div>
                <ul className="text-left space-y-2 text-slate-300 text-sm">
                  <li>• 100 deals per month</li>
                  <li>• $1,875 average profit</li>
                  <li>• 60% success rate</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact-section" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Start Your Arbitrage Empire?
          </h2>
          <p className="text-xl text-slate-300 mb-8">
            Join successful entrepreneurs who are already profiting from market inefficiencies
          </p>
          
          <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="text-left">
                <h3 className="text-2xl font-bold text-white mb-4">Get Your Custom Solution</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                    Industry-specific arbitrage platform
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                    Custom marketplace integrations
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                    AI-powered profit optimization
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                    24/7 monitoring and alerts
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                    Complete deployment and training
                  </li>
                </ul>
              </div>
              
              <div className="space-y-4">
                <a
                  href="mailto:vl.bichev@gmail.com"
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-4 rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all transform hover:scale-105 flex items-center justify-center font-semibold"
                >
                  <Mail className="w-5 h-5 mr-2" />
                  Get Custom Quote
                </a>
                
                <a
                  href="https://www.vladbichev.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full border border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 px-8 py-4 rounded-xl transition-all flex items-center justify-center font-semibold"
                >
                  <ExternalLink className="w-5 h-5 mr-2" />
                  View Portfolio
                </a>
                
                <div className="text-center pt-4">
                  <p className="text-slate-400 text-sm">
                    Free consultation
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4">
              ArbitrageAI Platform
            </h3>
            <p className="text-slate-300 mb-6 max-w-2xl mx-auto">
              Revolutionizing arbitrage discovery through AI and automation
            </p>
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-6">
              <Heart className="w-4 h-4 mr-2" />
              Made by
              <a 
                href="https://www.vladbichev.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 font-medium transition-colors duration-200 ml-1"
              >
                Vladimir Bichev
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App 