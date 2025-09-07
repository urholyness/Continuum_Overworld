'use client';

import { useState } from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import axios from 'axios';

// Configure Amplify
if (process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID && process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID) {
  Amplify.configure({
    Auth: {
      region: process.env.NEXT_PUBLIC_COGNITO_REGION,
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID,
      userPoolWebClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID,
    }
  });
}

export default function AdminOpsForm() {
  const [formData, setFormData] = useState({
    type: 'inspection',
    note: ''
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const convertToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  };

  const handleSubmit = async (e: React.FormEvent, token: string) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');

    try {
      // Convert files to base64
      const mediaBase64 = await Promise.all(
        selectedFiles.map(file => convertToBase64(file))
      );

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/ops`,
        {
          type: formData.type,
          note: formData.note,
          media_base64: mediaBase64
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.ok) {
        setMessage('Operation event added successfully!');
        setFormData({ type: 'inspection', note: '' });
        setSelectedFiles([]);
        // Reset file input
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      }
    } catch (error) {
      console.error('Error submitting ops event:', error);
      setMessage('Error submitting operation event. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Authenticator>
      {({ signOut, user }) => (
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <div className="bg-gradient-to-r from-farm-green to-sky-blue text-white py-8">
            <div className="container mx-auto px-4 flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold">Admin Operations Log</h1>
                <p className="text-lg mt-2">Two Butterflies Homestead</p>
              </div>
              <div className="text-right">
                <p className="text-sm mb-2">Admin: {user?.username}</p>
                <button
                  onClick={signOut}
                  className="bg-white text-farm-green px-4 py-2 rounded hover:bg-gray-100"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="container mx-auto px-4 py-8">
            <div className="max-w-2xl mx-auto">
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold mb-6">Log Farm Operation</h2>
                
                <form onSubmit={(e) => handleSubmit(e, user?.signInUserSession?.idToken?.jwtToken || '')}>
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Operation Type
                    </label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-farm-green focus:border-transparent"
                      required
                    >
                      <option value="inspection">Inspection</option>
                      <option value="planting">Planting</option>
                      <option value="fertilizing">Fertilizing</option>
                      <option value="irrigation">Irrigation</option>
                      <option value="pest_control">Pest Control</option>
                      <option value="harvesting">Harvesting</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="weather_event">Weather Event</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes / Description
                    </label>
                    <textarea
                      value={formData.note}
                      onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-farm-green focus:border-transparent"
                      placeholder="Describe the operation performed..."
                      required
                    />
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Photos (Optional)
                    </label>
                    <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg">
                      <div className="space-y-1 text-center">
                        <svg
                          className="mx-auto h-12 w-12 text-gray-400"
                          stroke="currentColor"
                          fill="none"
                          viewBox="0 0 48 48"
                          aria-hidden="true"
                        >
                          <path
                            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                            strokeWidth={2}
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                        <div className="flex text-sm text-gray-600">
                          <label
                            htmlFor="file-upload"
                            className="relative cursor-pointer bg-white rounded-md font-medium text-farm-green hover:text-green-700 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-farm-green"
                          >
                            <span>Upload files</span>
                            <input
                              id="file-upload"
                              name="file-upload"
                              type="file"
                              className="sr-only"
                              multiple
                              accept="image/*"
                              onChange={handleFileChange}
                            />
                          </label>
                          <p className="pl-1">or drag and drop</p>
                        </div>
                        <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                      </div>
                    </div>
                    {selectedFiles.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm text-gray-700">Selected files:</p>
                        <ul className="mt-2 text-sm text-gray-600">
                          {selectedFiles.map((file, index) => (
                            <li key={index}>• {file.name}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {message && (
                    <div className={`mb-6 p-4 rounded-lg ${
                      message.includes('success') 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {message}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={submitting}
                    className={`w-full py-3 px-4 rounded-lg text-white font-medium ${
                      submitting
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-farm-green hover:bg-green-700'
                    }`}
                  >
                    {submitting ? 'Submitting...' : 'Log Operation'}
                  </button>
                </form>
              </div>

              {/* Quick Links */}
              <div className="mt-8 grid grid-cols-2 gap-4">
                <a
                  href="/farms/2BH"
                  className="bg-white rounded-lg shadow p-4 text-center hover:shadow-lg transition-shadow"
                >
                  <span className="text-farm-green font-medium">View Public Page</span>
                </a>
                <a
                  href="/buyers/2BH"
                  className="bg-white rounded-lg shadow p-4 text-center hover:shadow-lg transition-shadow"
                >
                  <span className="text-sky-blue font-medium">Buyer Dashboard</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </Authenticator>
  );
}