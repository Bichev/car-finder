import React, { useState } from 'react'
import { 
  Car, 
  Brain, 
  ExternalLink, 
  MapPin, 
  Calendar, 
  Gauge, 
  DollarSign,
  TrendingUp,
  BarChart3,
  AlertCircle,
  CheckCircle,
  Eye,
  X,
  Sparkles
} from 'lucide-react'

const ResultsDisplay = ({ results }) => {
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [showAnalysis, setShowAnalysis] = useState(true)

  const { scraping, analysis } = results
  const vehicles = scraping?.results?.sample_vehicles || []
  const vehicleCount = scraping?.results?.vehicles_found || 0
  const aiAnalysis = analysis?.ai_analysis || ''

  // Format markdown-like text for better display
  const formatMarkdownText = (text) => {
    if (!text) return null
    
    const lines = text.split('\n')
    const elements = []
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      
      if (trimmedLine.startsWith('###')) {
        // H3 heading
        elements.push(
          <h3 key={index} className="text-lg font-bold text-gray-900 mt-6 mb-3 first:mt-0">
            {trimmedLine.replace('###', '').trim()}
          </h3>
        )
      } else if (trimmedLine.startsWith('##')) {
        // H2 heading
        elements.push(
          <h2 key={index} className="text-xl font-bold text-gray-900 mt-6 mb-4 first:mt-0">
            {trimmedLine.replace('##', '').trim()}
          </h2>
        )
      } else if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**')) {
        // Bold line
        elements.push(
          <p key={index} className="font-semibold text-gray-900 mb-2">
            {trimmedLine.replace(/\*\*/g, '')}
          </p>
        )
      } else if (trimmedLine.startsWith('- ')) {
        // Bullet point
        const bulletText = trimmedLine.replace('- ', '')
        const formattedBullet = bulletText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        elements.push(
          <li key={index} className="ml-4 mb-2 text-gray-700" dangerouslySetInnerHTML={{ __html: formattedBullet }} />
        )
      } else if (trimmedLine === '---') {
        // Divider
        elements.push(<hr key={index} className="my-4 border-gray-200" />)
      } else if (trimmedLine.length > 0) {
        // Regular paragraph with bold formatting
        const formattedText = trimmedLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        elements.push(
          <p key={index} className="mb-3 text-gray-700 leading-relaxed" dangerouslySetInnerHTML={{ __html: formattedText }} />
        )
      } else {
        // Empty line - add space
        elements.push(<div key={index} className="mb-2" />)
      }
    })
    
    return <div>{elements}</div>
  }

  const VehicleCard = ({ vehicle, onClick }) => (
    <div 
      className="card p-6 cursor-pointer group"
      onClick={() => onClick(vehicle)}
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h3>
          <p className="text-sm text-gray-500 flex items-center mt-1">
            <MapPin className="w-4 h-4 mr-1" />
            {vehicle.location || 'Location not specified'}
          </p>
        </div>
        <Eye className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center space-x-2">
          <DollarSign className="w-4 h-4 text-green-500" />
          <span className="font-bold text-green-600">
            ${vehicle.price?.toLocaleString() || 'N/A'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <Gauge className="w-4 h-4 text-blue-500" />
          <span className="text-gray-700">
            {vehicle.mileage?.toLocaleString() || 'N/A'} mi
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
          Cars.com
        </span>
        {vehicle.url && (
          <button className="text-blue-500 hover:text-blue-700 text-sm font-medium">
            View Listing →
          </button>
        )}
      </div>
    </div>
  )

  const VehicleModal = ({ vehicle, onClose }) => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {vehicle.year} {vehicle.make} {vehicle.model}
              </h2>
              <p className="text-gray-500 flex items-center mt-1">
                <MapPin className="w-4 h-4 mr-1" />
                {vehicle.location || 'Location not specified'}
              </p>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <DollarSign className="w-5 h-5 text-green-500" />
                <div>
                  <span className="text-sm text-gray-500">Price</span>
                  <p className="text-xl font-bold text-green-600">
                    ${vehicle.price?.toLocaleString() || 'Not specified'}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Gauge className="w-5 h-5 text-blue-500" />
                <div>
                  <span className="text-sm text-gray-500">Mileage</span>
                  <p className="text-lg font-semibold">
                    {vehicle.mileage?.toLocaleString() || 'Not specified'} miles
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Calendar className="w-5 h-5 text-purple-500" />
                <div>
                  <span className="text-sm text-gray-500">Year</span>
                  <p className="text-lg font-semibold">{vehicle.year}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Car className="w-5 h-5 text-indigo-500" />
                <div>
                  <span className="text-sm text-gray-500">Source</span>
                  <p className="text-lg font-semibold">{vehicle.source}</p>
                </div>
              </div>
            </div>
          </div>

          {vehicle.url && (
            <div className="border-t pt-6">
              <a
                href={vehicle.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary w-full"
              >
                <ExternalLink className="w-5 h-5 mr-2" />
                View Full Listing on Cars.com
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-8">
      {/* Results Summary */}
      <div className="card p-6">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mb-4">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Search Complete!</h2>
          <p className="text-lg text-gray-600">
            Found <span className="font-bold text-green-600">{vehicleCount}</span> vehicles 
            with AI-powered market analysis
          </p>
        </div>
      </div>

      {/* AI Analysis Section */}
      <div className="card">
        <div 
          className="p-6 cursor-pointer"
          onClick={() => setShowAnalysis(!showAnalysis)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Brain className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">AI Market Analysis</h3>
                <p className="text-gray-600">Powered by Perplexity AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-purple-500" />
              <span className="text-sm text-purple-600 font-medium">
                {showAnalysis ? 'Hide' : 'Show'} Analysis
              </span>
            </div>
          </div>
        </div>

        {showAnalysis && (
          <div className="px-6 pb-6">
                         <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6 border border-purple-100">
               <div className="prose prose-sm max-w-none">
                 {aiAnalysis ? (
                   <div className="text-gray-700 leading-relaxed">
                     {formatMarkdownText(aiAnalysis)}
                   </div>
                 ) : (
                   <div className="text-center text-gray-500">
                     <AlertCircle className="w-8 h-8 mx-auto mb-2" />
                     <p>AI analysis not available for this search</p>
                   </div>
                 )}
               </div>
             </div>

            {analysis?.citations && analysis.citations.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Sources:</h4>
                <div className="space-y-1">
                  {analysis.citations.slice(0, 3).map((citation, index) => (
                    <a
                      key={index}
                      href={citation}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-800 block truncate"
                    >
                      {citation}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Vehicle Results */}
      <div>
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Car className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Vehicle Listings</h3>
            <p className="text-gray-600">Click any vehicle to view details</p>
          </div>
        </div>

        {vehicles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {vehicles.map((vehicle, index) => (
              <VehicleCard
                key={vehicle.external_id || index}
                vehicle={vehicle}
                onClick={setSelectedVehicle}
              />
            ))}
          </div>
        ) : (
          <div className="card p-8 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Vehicles Found</h3>
            <p className="text-gray-600">
              Try adjusting your search criteria for better results
            </p>
          </div>
        )}

        {vehicleCount > vehicles.length && (
          <div className="mt-6 text-center">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-700">
                <strong>{vehicles.length}</strong> of <strong>{vehicleCount}</strong> vehicles shown. 
                This is a demo with limited results display.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Performance Stats */}
      <div className="card p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2" />
          Search Performance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{vehicleCount}</div>
            <div className="text-sm text-gray-500">Vehicles Found</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {scraping?.performance?.duration_seconds?.toFixed(1) || 'N/A'}s
            </div>
            <div className="text-sm text-gray-500">Scraping Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {analysis?.performance?.duration_seconds?.toFixed(1) || 'N/A'}s
            </div>
            <div className="text-sm text-gray-500">Analysis Time</div>
          </div>
        </div>
      </div>

      {/* Vehicle Detail Modal */}
      {selectedVehicle && (
        <VehicleModal
          vehicle={selectedVehicle}
          onClose={() => setSelectedVehicle(null)}
        />
      )}
    </div>
  )
}

export default ResultsDisplay 