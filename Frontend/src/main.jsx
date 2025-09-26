import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import { BrowserRouter } from 'react-router-dom'

import { AuthProvider } from './context/AuthContext.jsx'
import { EchoProvider } from './context/EchoNetContext'
import { CidProvider } from './context/CidContext'
import { ConverterProvider } from './context/ConverterContext'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ConverterProvider>
          <EchoProvider>
            <CidProvider>
              <App />
            </CidProvider>
          </EchoProvider>
        </ConverterProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
