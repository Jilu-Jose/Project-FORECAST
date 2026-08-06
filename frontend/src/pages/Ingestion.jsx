import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, MoreVertical, AlertCircle, CheckCircle } from 'lucide-react';
import { uploadAudit, getAuditHistory } from '../api/client';

export default function Ingestion() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [companyName, setCompanyName] = useState('');
  const [sector, setSector] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [recentUploads, setRecentUploads] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await getAuditHistory(3); // Fetch top 3 recent for ingestion page
      setRecentUploads(data.items || []);
    } catch (err) {
      console.error("Failed to load history");
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      // Default company name from filename
      const name = acceptedFiles[0].name.split('.')[0].replace(/[-_]/g, ' ');
      setCompanyName(name);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    multiple: false,
  });

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!file) return;

    // Use filename if companyName isn't set
    const finalCompanyName = companyName.trim() || file.name.split('.')[0];

    setUploading(true);
    setError(null);

    try {
      const result = await uploadAudit(file, finalCompanyName, sector || null);
      navigate(`/audit/${result.job_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Is the backend running?');
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Data Ingestion</h2>
        <p className="page-subtitle">Securely upload and process your audit files.</p>
      </div>

      <div 
        {...getRootProps()}
        className="upload-zone"
        style={{ borderColor: isDragActive ? 'var(--primary)' : '#cbd5e0', marginBottom: '3rem' }}
      >
        <input {...getInputProps()} />
        <div className="upload-icon-wrapper">
          {file ? <FileSpreadsheet size={28} /> : <Upload size={28} />}
        </div>
        
        {file ? (
          <>
            <div className="upload-title">{file.name}</div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB — Ready to process
            </p>
            <button 
              className="btn btn-primary" 
              onClick={(e) => {
                e.stopPropagation();
                handleSubmit();
              }}
              disabled={uploading}
              style={{ marginTop: '1rem', minWidth: '160px' }}
            >
              {uploading ? 'Processing...' : 'Run Audit'}
            </button>
          </>
        ) : (
          <>
            <div className="upload-title">
              {isDragActive ? 'Drop file here' : 'Select files to upload or drag and drop them here'}
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Supported formats: CSV, XLSX, JSON. Max size: 500MB.
            </p>
            <button className="btn btn-primary" style={{ marginTop: '1rem', padding: '0.6rem 2rem' }}>
              Browse Files
            </button>
          </>
        )}
        
        {error && <p style={{ color: 'var(--status-critical-text)', marginTop: '1rem' }}>{error}</p>}
      </div>

      <h3 className="section-title">Recent Uploads</h3>
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Size</th>
              <th>Upload Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recentUploads.map((run) => (
              <tr key={run.id} onClick={() => navigate(`/audit/${run.id}`)} style={{ cursor: 'pointer' }}>
                <td style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                  <FileSpreadsheet size={16} color="var(--text-muted)" />
                  {run.original_filename || `${run.company_name} Data.xlsx`}
                </td>
                <td style={{ color: 'var(--text-muted)' }}>—</td>
                <td>{new Date(run.created_at).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute:'2-digit', hour12: false })}</td>
                <td>
                  <span className={`badge ${
                    run.status === 'complete' ? 'badge-success' :
                    run.status === 'error' ? 'badge-critical' :
                    'badge-warning'
                  }`}>
                    {run.status === 'complete' && <CheckCircle size={12} />}
                    {run.status === 'error' && <AlertCircle size={12} />}
                    {run.status === 'complete' ? 'Complete' : run.status === 'error' ? 'Parse Error' : 'Processing'}
                  </span>
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                    <MoreVertical size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {recentUploads.length === 0 && (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  No recent uploads found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
