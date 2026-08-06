import { Loader2 } from 'lucide-react';

export default function Loader({ message = "Processing Audit..." }) {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center',
      minHeight: '60vh',
      gap: '1.5rem',
      color: 'var(--text-muted)'
    }}>
      <div style={{ position: 'relative' }}>
        <div style={{
          position: 'absolute',
          inset: '-8px',
          background: 'var(--primary)',
          opacity: 0.15,
          borderRadius: '50%',
          animation: 'pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
        }} />
        <Loader2 size={48} color="var(--primary)" className="spin" style={{ position: 'relative' }} />
      </div>
      <div style={{
        fontSize: '1.1rem',
        fontWeight: 500,
        color: 'var(--text-main)',
        animation: 'pulse-text 2s infinite',
        letterSpacing: '0.5px'
      }}>
        {message}
      </div>
      <style>{`
        @keyframes pulse-ring {
          0% { transform: scale(0.8); opacity: 0.5; }
          100% { transform: scale(2); opacity: 0; }
        }
        @keyframes pulse-text {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
