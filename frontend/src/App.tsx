import { useState } from 'react';
import { useStatus, useTradingStatus, usePositions, useOpportunities, useConfig, useWebSocket } from './hooks';
import { StatCard } from './components/StatCard';
import { PositionsTable } from './components/PositionsTable';
import { OpportunitiesTable } from './components/OpportunitiesTable';
import { TradingControls } from './components/TradingControls';
import { ConfigPanel } from './components/ConfigPanel';
import { useNotificationStore } from './store';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'scanner' | 'settings'>('dashboard');

  // Data hooks
  const { status } = useStatus();
  useWebSocket(); // Initialize WebSocket connection
  const { status: tradingStatus, start, stop, pause, resume, panic } = useTradingStatus();
  const { positions, close: closePosition } = usePositions();
  const { opportunities, scanning, scan } = useOpportunities();
  const { config, update: updateConfig } = useConfig();
  const notifications = useNotificationStore((s) => s.notifications);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const isRunning = tradingStatus?.is_running || false;
  const isPaused = tradingStatus?.is_paused || false;

  return (
    <div className="app">
      {/* Notifications */}
      <div className="notifications">
        {notifications.map((n) => (
          <div key={n.id} className={`notification notification-${n.type}`}>
            {n.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <span className="logo">⚖️</span>
          <h1>Polymarket Equilibrage Bot</h1>
          <span className="version">v0.2.0</span>
        </div>

        {/* Trading Controls in Header */}
        <TradingControls
          isRunning={isRunning}
          isPaused={isPaused}
          onStart={start}
          onStop={stop}
          onPause={pause}
          onResume={resume}
          onPanic={panic}
        />
      </header>

      {/* Navigation */}
      <nav className="nav">
        <button
          className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button
          className={`nav-btn ${activeTab === 'scanner' ? 'active' : ''}`}
          onClick={() => setActiveTab('scanner')}
        >
          🔍 Scanner
        </button>
        <button
          className={`nav-btn ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </nav>

      {/* Main Content */}
      <main className="main">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            {/* Stats Grid */}
            <div className="stats-grid">
              <StatCard
                title="Capital Total"
                value={formatCurrency(status?.total_capital || 0)}
                subtitle={`Disponible: ${formatCurrency(status?.capital_available || 0)}`}
              />
              <StatCard
                title="Capital Engagé"
                value={formatCurrency(status?.capital_engaged || 0)}
                subtitle={`${positions.length} positions actives`}
              />
              <StatCard
                title="P&L Total"
                value={formatCurrency(tradingStatus?.total_pnl || 0)}
                trend={(tradingStatus?.total_pnl ?? 0) >= 0 ? 'up' : 'down'}
                trendValue={`${status?.total_pnl_percent?.toFixed(2) || 0}%`}
              />
              <StatCard
                title="Opportunités"
                value={opportunities.length}
                subtitle={`Top: ${opportunities[0]?.score || 0}/10`}
              />
            </div>

            {/* Positions Section */}
            <section className="section">
              <div className="section-header">
                <h2>🎯 Positions Actives</h2>
                <span className="badge">{positions.length}</span>
              </div>
              <PositionsTable
                positions={positions}
                onClose={closePosition}
              />
            </section>

            {/* Top Opportunities */}
            <section className="section">
              <div className="section-header">
                <h2>🔥 Top Opportunités</h2>
                <button
                  className="btn btn-primary"
                  onClick={scan}
                  disabled={scanning}
                >
                  {scanning ? '⏳ Scan...' : '🔄 Scanner'}
                </button>
              </div>
              <OpportunitiesTable
                opportunities={opportunities.slice(0, 5)}
                onTrade={() => { }}
              />
            </section>
          </div>
        )}

        {activeTab === 'scanner' && (
          <div className="scanner">
            <section className="section">
              <div className="section-header">
                <h2>🔍 Scanner Avancé</h2>
                <button
                  className="btn btn-primary"
                  onClick={scan}
                  disabled={scanning}
                >
                  {scanning ? '⏳ Scan en cours...' : '🔍 Lancer le Scan'}
                </button>
              </div>
              <p className="section-info">
                Scan parallèle avec scoring multi-critères: Divergence (40%) + Volume (20%) + Liquidité (20%) + Timing (10%) + Activité (10%)
              </p>
              <OpportunitiesTable
                opportunities={opportunities}
                onTrade={() => { }}
              />
            </section>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="settings">
            {config ? (
              <ConfigPanel config={config} onUpdate={updateConfig} />
            ) : (
              <div className="loading-state">Chargement de la configuration...</div>
            )}

            <section className="section">
              <h3>📝 Configuration Wallet</h3>
              <p className="info-text">
                ⚠️ Configurez votre wallet dans le fichier <code>.env</code>
              </p>
              <pre className="code-block">
                {`WALLET_ADDRESS=votre_adresse
WALLET_PRIVATE_KEY=votre_clé_privée`}
              </pre>
            </section>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <span>Polymarket Equilibrage Bot v0.2.0</span>
        <span className="separator">•</span>
        <span className={`status-dot ${isRunning ? 'running' : 'stopped'}`} />
        <span>{isRunning ? 'Bot actif' : 'Bot arrêté'}</span>
      </footer>
    </div>
  );
}

export default App;
