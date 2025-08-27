import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Results from './pages/Results'
import Admin from './pages/Admin'

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="container mt-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/results/:jobId" element={<Results />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App