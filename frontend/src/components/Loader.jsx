export default function Loader({ message = "Processing Audit..." }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '60vh',
      gap: '2.5rem',
    }}>
      <span className="hourglass-loader" />
      <div style={{
        fontSize: '1.1rem',
        fontWeight: 500,
        color: 'var(--text-main)',
        animation: 'pulse-text 2s ease-in-out infinite',
        letterSpacing: '0.5px',
      }}>
        {message}
      </div>

      <style>{`
        /* From Uiverse.io by JaydipPrajapati1910 — recolored green */
        .hourglass-loader {
          box-sizing: border-box;
          display: inline-block;
          width: 50px;
          height: 80px;
          border-top: 5px solid var(--primary, #16a34a);
          border-bottom: 5px solid var(--primary, #16a34a);
          position: relative;
          background: linear-gradient(var(--primary, #16a34a) 30px, transparent 0) no-repeat;
          background-size: 2px 40px;
          background-position: 50% 0px;
          animation: spinx 5s linear infinite;
        }

        .hourglass-loader:before,
        .hourglass-loader:after {
          content: "";
          width: 40px;
          left: 50%;
          height: 35px;
          position: absolute;
          top: 0;
          transform: translateX(-50%);
          background: rgba(22, 163, 74, 0.25);
          border-radius: 0 0 20px 20px;
          background-size: 100% auto;
          background-repeat: no-repeat;
          background-position: 0 0px;
          animation: lqt 5s linear infinite;
        }

        .hourglass-loader:after {
          top: auto;
          bottom: 0;
          border-radius: 20px 20px 0 0;
          animation: lqb 5s linear infinite;
        }

        @keyframes lqt {
          0%, 100% {
            background-image: linear-gradient(var(--primary, #16a34a) 40px, transparent 0);
            background-position: 0% 0px;
          }
          50% {
            background-image: linear-gradient(var(--primary, #16a34a) 40px, transparent 0);
            background-position: 0% 40px;
          }
          50.1% {
            background-image: linear-gradient(var(--primary, #16a34a) 40px, transparent 0);
            background-position: 0% -40px;
          }
        }

        @keyframes lqb {
          0% {
            background-image: linear-gradient(var(--primary, #16a34a) 40px, transparent 0);
            background-position: 0 40px;
          }
          100% {
            background-image: linear-gradient(var(--primary, #16a34a) 40px, transparent 0);
            background-position: 0 -40px;
          }
        }

        @keyframes spinx {
          0%, 49% {
            transform: rotate(0deg);
            background-position: 50% 36px;
          }
          51%, 98% {
            transform: rotate(180deg);
            background-position: 50% 4px;
          }
          100% {
            transform: rotate(360deg);
            background-position: 50% 36px;
          }
        }

        @keyframes pulse-text {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}
