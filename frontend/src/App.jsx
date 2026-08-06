import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Ingestion from './pages/Ingestion';
import History from './pages/History';
import Overview from './pages/Overview';
import Findings from './pages/Findings';
import Scenarios from './pages/Scenarios';
import Reports from './pages/Reports';
import Workflow from './pages/Workflow';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Ingestion />} />
          <Route path="/history" element={<History />} />
          <Route path="/audit/:jobId" element={<Overview />} />
          <Route path="/audit/:jobId/findings" element={<Findings />} />
          <Route path="/audit/:jobId/scenarios" element={<Scenarios />} />
          <Route path="/audit/:jobId/reports" element={<Reports />} />
          <Route path="/audit/:jobId/workflow" element={<Workflow />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
