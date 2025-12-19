import { useState } from 'react'
import Dashboard from './components/Dashboard'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
