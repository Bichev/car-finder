import React, { useState } from 'react'
import { Search, Car, MapPin, Calendar, DollarSign, Loader } from 'lucide-react'

const SearchForm = ({ onSearch, isLoading }) => {
  const [formData, setFormData] = useState({
    make: 'Honda',
    model: 'Accord',
    yearMin: 2018,
    yearMax: 2023,
    priceMin: 18000,
    priceMax: 28000,
    zipCode: '33101'
  })

  const [errors, setErrors] = useState({})

  const carMakes = [
    'Honda', 'Toyota', 'BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 
    'Acura', 'Infiniti', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia',
    'Ford', 'Chevrolet', 'Cadillac', 'Buick', 'Mazda', 'Subaru'
  ]

  const carModels = {
    Honda: ['Accord', 'Civic', 'CR-V', 'Pilot', 'Odyssey', 'Passport', 'Ridgeline'],
    Toyota: ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Prius', '4Runner', 'Tacoma'],
    BMW: ['3 Series', '5 Series', 'X3', 'X5', 'X1', '7 Series', 'Z4'],
    'Mercedes-Benz': ['C-Class', 'E-Class', 'GLE', 'GLC', 'S-Class', 'A-Class'],
    Audi: ['A4', 'A6', 'Q5', 'Q7', 'A3', 'Q3', 'A8'],
    Lexus: ['ES', 'IS', 'RX', 'NX', 'GX', 'LS', 'LX'],
    Acura: ['TLX', 'MDX', 'RDX', 'ILX', 'NSX'],
    Infiniti: ['Q50', 'Q60', 'QX60', 'QX80', 'Q70'],
    Volkswagen: ['Jetta', 'Passat', 'Tiguan', 'Atlas', 'Golf', 'Arteon'],
    Nissan: ['Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Titan'],
    Hyundai: ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Genesis', 'Palisade'],
    Kia: ['Forte', 'Optima', 'Sorento', 'Sportage', 'Telluride', 'Stinger'],
    Ford: ['F-150', 'Escape', 'Explorer', 'Mustang', 'Edge', 'Expedition'],
    Chevrolet: ['Silverado', 'Equinox', 'Malibu', 'Tahoe', 'Camaro', 'Traverse'],
    Cadillac: ['Escalade', 'XT5', 'CT6', 'ATS', 'CTS', 'XT4'],
    Buick: ['Enclave', 'Encore', 'LaCrosse', 'Regal', 'Envision'],
    Mazda: ['Mazda3', 'Mazda6', 'CX-5', 'CX-9', 'MX-5 Miata', 'CX-30'],
    Subaru: ['Outback', 'Forester', 'Impreza', 'Legacy', 'Ascent', 'Crosstrek']
  }

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 15 }, (_, i) => currentYear - i)

  const validateForm = () => {
    const newErrors = {}

    if (!formData.make) newErrors.make = 'Please select a make'
    if (!formData.model) newErrors.model = 'Please select a model'
    if (formData.yearMin > formData.yearMax) {
      newErrors.yearRange = 'Start year must be less than or equal to end year'
    }
    if (formData.priceMin >= formData.priceMax) {
      newErrors.priceRange = 'Minimum price must be less than maximum price'
    }
    if (!/^\d{5}$/.test(formData.zipCode)) {
      newErrors.zipCode = 'Please enter a valid 5-digit ZIP code'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      onSearch(formData)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    // Clear specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }))
    }
  }

  return (
    <div className="card p-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full mb-4">
          <Car className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Start Your AI-Powered Search</h3>
        <p className="text-gray-600">Configure your search criteria and let our AI find the perfect vehicles</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Vehicle Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Car className="w-4 h-4 inline mr-2" />
              Make
            </label>
            <select
              className="select-field"
              value={formData.make}
              onChange={(e) => {
                handleInputChange('make', e.target.value)
                // Reset model when make changes
                handleInputChange('model', carModels[e.target.value]?.[0] || '')
              }}
            >
              {carMakes.map(make => (
                <option key={make} value={make}>{make}</option>
              ))}
            </select>
            {errors.make && <p className="text-red-500 text-sm mt-1">{errors.make}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model
            </label>
            <select
              className="select-field"
              value={formData.model}
              onChange={(e) => handleInputChange('model', e.target.value)}
            >
              {(carModels[formData.make] || []).map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
            {errors.model && <p className="text-red-500 text-sm mt-1">{errors.model}</p>}
          </div>
        </div>

        {/* Year Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Calendar className="w-4 h-4 inline mr-2" />
            Year Range
          </label>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <select
                className="select-field"
                value={formData.yearMin}
                onChange={(e) => handleInputChange('yearMin', parseInt(e.target.value))}
              >
                {years.map(year => (
                  <option key={year} value={year}>{year} (Start)</option>
                ))}
              </select>
            </div>
            <div>
              <select
                className="select-field"
                value={formData.yearMax}
                onChange={(e) => handleInputChange('yearMax', parseInt(e.target.value))}
              >
                {years.map(year => (
                  <option key={year} value={year}>{year} (End)</option>
                ))}
              </select>
            </div>
          </div>
          {errors.yearRange && <p className="text-red-500 text-sm mt-1">{errors.yearRange}</p>}
        </div>

        {/* Price Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <DollarSign className="w-4 h-4 inline mr-2" />
            Price Range
          </label>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <input
                type="number"
                className="input-field"
                placeholder="Min Price"
                value={formData.priceMin}
                onChange={(e) => handleInputChange('priceMin', parseInt(e.target.value) || 0)}
                min="0"
                step="1000"
              />
            </div>
            <div>
              <input
                type="number"
                className="input-field"
                placeholder="Max Price"
                value={formData.priceMax}
                onChange={(e) => handleInputChange('priceMax', parseInt(e.target.value) || 0)}
                min="0"
                step="1000"
              />
            </div>
          </div>
          <div className="flex justify-between text-sm text-gray-500 mt-1">
            <span>${formData.priceMin?.toLocaleString() || '0'}</span>
            <span>${formData.priceMax?.toLocaleString() || '0'}</span>
          </div>
          {errors.priceRange && <p className="text-red-500 text-sm mt-1">{errors.priceRange}</p>}
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <MapPin className="w-4 h-4 inline mr-2" />
            ZIP Code
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="Enter ZIP code (e.g., 33101)"
            value={formData.zipCode}
            onChange={(e) => handleInputChange('zipCode', e.target.value)}
            maxLength="5"
          />
          <p className="text-sm text-gray-500 mt-1">
            We'll search for vehicles in your area and provide regional market insights
          </p>
          {errors.zipCode && <p className="text-red-500 text-sm mt-1">{errors.zipCode}</p>}
        </div>

        {/* Search Summary */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
          <h4 className="font-medium text-gray-900 mb-2">Search Summary</h4>
          <p className="text-sm text-gray-600">
            Looking for <span className="font-semibold">{formData.make} {formData.model}</span> vehicles 
            from <span className="font-semibold">{formData.yearMin}-{formData.yearMax}</span> in the 
            <span className="font-semibold"> ${formData.priceMin?.toLocaleString()}-${formData.priceMax?.toLocaleString()}</span> price 
            range near <span className="font-semibold">{formData.zipCode}</span>
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full btn-primary text-lg py-4 group"
        >
          {isLoading ? (
            <>
              <Loader className="w-5 h-5 mr-3 animate-spin" />
              AI Search in Progress...
            </>
          ) : (
            <>
              <Search className="w-5 h-5 mr-3 group-hover:scale-110 transition-transform" />
              Start AI-Powered Search
            </>
          )}
        </button>

        {/* Demo Notice */}
        <div className="text-center">
          <p className="text-sm text-gray-500">
            ⚡ This demo searches Cars.com and provides AI market analysis
          </p>
        </div>
      </form>
    </div>
  )
}

export default SearchForm 