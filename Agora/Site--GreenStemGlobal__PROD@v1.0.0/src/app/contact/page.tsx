'use client'

import { useState } from 'react'
import Hero from '@/components/Hero'
import { Mail, Phone, MapPin, Send } from 'lucide-react'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    type: 'buyer',
    message: '',
    consent: false
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.consent) {
      setError('Please accept the privacy policy to continue.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setSuccess(true)
        setFormData({
          name: '',
          email: '',
          company: '',
          type: 'buyer',
          message: '',
          consent: false
        })
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to send message. Please try again.')
      }
    } catch (err) {
      setError('Failed to send message. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const target = e.target as HTMLInputElement
      setFormData(prev => ({ ...prev, [name]: target.checked }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }

  return (
    <>
      <Hero
        title="Get in Touch"
        subtitle="Start your journey to transparent, sustainable agricultural trade."
      />

      <section className="py-20 bg-white">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8 mb-12">
              {/* Contact Info */}
              <div className="card text-center">
                <Mail className="h-8 w-8 text-leaf mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Email</h3>
                <p className="text-sm text-gray-600">info@greenstemglobal.com</p>
              </div>
              <div className="card text-center">
                <Phone className="h-8 w-8 text-leaf mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Phone</h3>
                <p className="text-sm text-gray-600">+49 30 1234 5678</p>
              </div>
              <div className="card text-center">
                <MapPin className="h-8 w-8 text-leaf mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Office</h3>
                <p className="text-sm text-gray-600">Berlin, Germany</p>
              </div>
            </div>

            {/* Contact Form */}
            <div className="card max-w-2xl mx-auto">
              <h2 className="text-2xl font-display font-bold mb-6">Send us a Message</h2>
              
              {success && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
                  Thank you for your message! We'll get back to you within 24 hours.
                </div>
              )}

              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium mb-1">
                      Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      required
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-leaf"
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium mb-1">
                      Email *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-leaf"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="company" className="block text-sm font-medium mb-1">
                      Company
                    </label>
                    <input
                      type="text"
                      id="company"
                      name="company"
                      value={formData.company}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-leaf"
                    />
                  </div>
                  <div>
                    <label htmlFor="type" className="block text-sm font-medium mb-1">
                      I am a *
                    </label>
                    <select
                      id="type"
                      name="type"
                      required
                      value={formData.type}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-leaf"
                    >
                      <option value="buyer">Buyer</option>
                      <option value="investor">Investor</option>
                      <option value="farmer">Farmer</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium mb-1">
                    Message *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={5}
                    value={formData.message}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-leaf"
                  />
                </div>

                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="consent"
                    name="consent"
                    checked={formData.consent}
                    onChange={handleChange}
                    className="mt-1 mr-2"
                    required
                  />
                  <label htmlFor="consent" className="text-sm text-gray-600">
                    I agree to the processing of my personal data in accordance with the{' '}
                    <a href="/legal/privacy" className="text-leaf hover:underline">
                      Privacy Policy
                    </a>
                    . *
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full btn-primary flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span>Sending...</span>
                  ) : (
                    <>
                      Send Message
                      <Send className="h-4 w-4 ml-2" />
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
