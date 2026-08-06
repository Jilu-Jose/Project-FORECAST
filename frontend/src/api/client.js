import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export async function uploadAudit(file, companyName, sector) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('company_name', companyName);
  if (sector) formData.append('sector', sector);

  const response = await api.post('/audit/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

// ----------------- FAKE DATA INJECTION -----------------
const demoReport = {
  id: 'demo',
  company_name: 'Acme Corp',
  sector: 'SaaS',
  status: 'complete',
  n8n_status: 'Workflow Complete',
  created_at: new Date().toISOString(),
  summary: {
    critical_count: 3,
    warning_count: 8,
    info_count: 15,
  },
  assumptions: [
    { metric: 'Growth Rate (YoY)', value: '22%', unit: '', benchmark_range: '18%', confidence: 0.95 },
    { metric: 'CAC', value: '$450', unit: '', benchmark_range: '$500', confidence: 0.90 },
    { metric: 'Churn Rate', value: '5.2%', unit: '', benchmark_range: '4.0%', confidence: 0.88 },
  ],
  formula_anomalies: [
    { issue_type: 'circular_reference', sheet: 'Revenue', cell: 'D45', severity: 'critical', description: 'Circular Reference Detected in MRR calculation', category: 'Logic Error', confidence: 0.99 },
    { issue_type: 'hardcoded_value', sheet: 'Payroll', cell: 'F12:F100', severity: 'critical', description: 'Hardcoded Growth Rates', category: 'Logic Error', confidence: 0.95 },
    { issue_type: 'inconsistent_formula', sheet: 'CapEx', cell: 'B5', severity: 'warning', description: 'Inconsistent Formula Structure', category: 'Logic Error', confidence: 0.85 },
    { issue_type: 'missing_link', sheet: 'Debt_Schedule', cell: 'H20', severity: 'warning', description: 'Missing Link to Balance Sheet', category: 'Logic Error', confidence: 0.80 },
    { issue_type: 'unmatched_liability', sheet: 'Sheet1', cell: 'D45', severity: 'critical', description: 'Debit value of $45,200 lacks corresponding credit', category: 'Reconciliation', confidence: 0.99 },
    { issue_type: 'expense_spike', sheet: 'OpEx_Q3', cell: 'F12', severity: 'high', description: 'Marketing overhead increased 315% MoM', category: 'Variance', confidence: 0.90 },
    { issue_type: 'duplicate_invoice', sheet: 'Vendors', cell: 'B89', severity: 'medium', description: 'Inv-2023-884 appears twice', category: 'Data Integrity', confidence: 0.95 },
  ],
  scenario_results: [
    { input_metric: 'Runway', output_metric: 'Months', baseline_value: '18.5', perturbed_value: '17.3', delta_pct: -0.064 },
    { input_metric: 'Eng Hiring (Q3)', output_metric: 'Headcount', baseline_value: '4 roles', perturbed_value: '8 roles', delta_pct: 1.0 },
    { input_metric: 'Base Salary Avg', output_metric: '$', baseline_value: '135k', perturbed_value: '145k', delta_pct: 0.074 },
    { input_metric: 'ARR (End of Year)', output_metric: '$', baseline_value: '4.2M', perturbed_value: '4.5M', delta_pct: 0.071 },
    { input_metric: 'ACV (Enterprise)', output_metric: '$', baseline_value: '45k', perturbed_value: '42k', delta_pct: -0.066 },
  ],
  report_markdown: `# Q3 Financial Integrity Assessment\n\n## Executive Summary\n\nThis report outlines the findings from the comprehensive Q3 financial audit. Overall, the financial health remains robust, adhering strictly to internal compliance frameworks and external regulatory standards. However, specific areas require immediate remediation to prevent potential fiscal leakage in Q4.\n\nWhile core revenue streams have stabilized, operational inefficiencies in the logistics and vendor management sectors must be addressed.`
};

export async function getAuditStatus(jobId) {
  if (jobId === 'demo') return { status: 'complete', current_agent: 'report', n8n_status: 'Workflow Complete' };
  const response = await api.get(`/audit/status/${jobId}`);
  return response.data;
}

export async function getAuditReport(jobId) {
  if (jobId === 'demo') return demoReport;
  const response = await api.get(`/audit/report/${jobId}`);
  return response.data;
}

export function getDownloadUrl(jobId, format = 'pdf') {
  if (jobId === 'demo') return '#';
  return `${API_BASE}/audit/report/${jobId}/download?format=${format}`;
}

export async function getAuditHistory(limit = 50, offset = 0) {
  const response = await api.get('/history', { params: { limit, offset } });
  
  // Inject demo run at the top
  const demoHistoryItem = {
    id: 'demo',
    company_name: 'Q3_Financials_Audit_v2',
    original_filename: 'Q3_Financials_Audit_v2.xlsx',
    sector: 'SaaS',
    status: 'complete',
    created_at: new Date().toISOString(),
    critical_count: 3,
    warning_count: 8,
    info_count: 15,
  };
  
  response.data.items = [demoHistoryItem, ...response.data.items];
  return response.data;
}
// --------------------------------------------------------

export async function getCompanyHistory(company) {
  const response = await api.get(`/history/${encodeURIComponent(company)}`);
  return response.data;
}

export async function getDiff(id1, id2) {
  const response = await api.get(`/diff/${id1}/${id2}`);
  return response.data;
}
export default api;
