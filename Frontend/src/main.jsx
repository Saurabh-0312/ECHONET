import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import { BrowserRouter } from 'react-router-dom'

import { AuthProvider } from './context/AuthContext.jsx'
import { EchoProvider } from './context/EchoNetContext'
import { CidProvider } from './context/CidContext'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <EchoProvider>
          <CidProvider>
          <App />
          </CidProvider>
        </EchoProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
