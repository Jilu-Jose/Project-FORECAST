import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MoreVertical, CheckCircle, AlertCircle, FileSpreadsheet, AlertTriangle, Trash2 } from 'lucide-react';
import { getAuditHistory, deleteAudit } from '../api/client';
import Loader from '../components/Loader';

export default function History() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await getAuditHistory();
      setHistory(data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this audit?')) return;
    try {
      await deleteAudit(id);
      fetchHistory();
    } catch (err) {
      console.error(err);
      alert('Failed to delete audit');
    }
  };

  if (loading) {
    return <Loader message="Loading history..." />;
  }

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Audit History</h2>
        <p className="page-subtitle">View past audit results and compare versions.</p>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Filename / Company</th>
              <th>Sector</th>
              <th>Upload Date</th>
              <th>Issues</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {history.map((run) => (
              <tr key={run.id} onClick={() => navigate(`/audit/${run.id}`)} style={{ cursor: 'pointer' }}>
                <td style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                  <FileSpreadsheet size={16} color="var(--text-muted)" />
                  {run.original_filename || `${run.company_name} Data.xlsx`}
                </td>
                <td style={{ color: 'var(--text-muted)' }}>{run.sector || '—'}</td>
                <td>{new Date(run.created_at).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {run.critical_count > 0 && <span style={{ color: 'var(--status-critical-text)', display: 'flex', alignItems: 'center', gap: 2, fontSize: '0.8rem', fontWeight: 600 }}><AlertTriangle size={12}/> {run.critical_count}</span>}
                    {run.warning_count > 0 && <span style={{ color: 'var(--status-warning-text)', display: 'flex', alignItems: 'center', gap: 2, fontSize: '0.8rem', fontWeight: 600 }}><AlertCircle size={12}/> {run.warning_count}</span>}
                    {run.critical_count === 0 && run.warning_count === 0 && run.status === 'complete' && <span style={{ color: 'var(--status-success-text)', fontSize: '0.8rem' }}>Clean</span>}
                  </div>
                </td>
                <td>
                  <span className={`badge ${
                    run.status === 'complete' ? 'badge-success' :
                    run.status === 'error' ? 'badge-critical' :
                    'badge-warning'
                  }`}>
                    {run.status === 'complete' && <CheckCircle size={12} />}
                    {run.status === 'error' && <AlertCircle size={12} />}
                    {run.status === 'complete' ? 'Complete' : run.status === 'error' ? 'Failed' : 'Processing'}
                  </span>
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button 
                    onClick={(e) => handleDelete(e, run.id)}
                    style={{ background: 'none', border: 'none', color: 'var(--status-critical-text)', cursor: 'pointer', opacity: 0.7 }}
                    onMouseOver={(e) => e.currentTarget.style.opacity = 1}
                    onMouseOut={(e) => e.currentTarget.style.opacity = 0.7}
                    title="Delete Audit"
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
