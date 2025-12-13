import type { ScannerConfig } from '../services/api';

interface ConfigPanelProps {
    config: ScannerConfig;
    onUpdate: (updates: Partial<ScannerConfig>) => void;
}

export function ConfigPanel({ config, onUpdate }: ConfigPanelProps) {
    return (
        <div className="config-panel">
            <h3>⚙️ Configuration Trading</h3>

            <div className="config-grid">
                {/* Auto Trading Master Switch */}
                <div className="config-section" style={{ border: '1px solid #00ff00', background: 'rgba(0, 255, 0, 0.05)' }}>
                    <h4>🤖 Trading Automatique</h4>
                    <div className="config-item" style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                        <label style={{ margin: 0 }}>Autoriser les achats</label>
                        <input
                            type="checkbox"
                            checked={config.auto_trading_enabled}
                            onChange={(e) => onUpdate({ auto_trading_enabled: e.target.checked })}
                            style={{ width: '20px', height: '20px', cursor: 'pointer' }}
                        />
                    </div>
                    <small style={{ color: '#aaa' }}>
                        Si décoché : Le bot scanne uniquement (Mode Surveillance).
                        <br />
                        Si coché : Le bot prend position automatiquement.
                    </small>
                </div>

                {/* Trading thresholds */}
                <div className="config-section">
                    <h4>Seuils</h4>

                    <div className="config-item">
                        <label>Score min pour trader</label>
                        <input
                            type="number"
                            min={1}
                            max={10}
                            value={config.min_score_to_trade}
                            onChange={(e) => onUpdate({ min_score_to_trade: Number(e.target.value) })}
                        />
                        <span className="hint">/10</span>
                    </div>

                    <div className="config-item">
                        <label>Score min à afficher</label>
                        <input
                            type="number"
                            min={1}
                            max={10}
                            value={config.min_score_to_show}
                            onChange={(e) => onUpdate({ min_score_to_show: Number(e.target.value) })}
                        />
                        <span className="hint">/10</span>
                    </div>
                </div>

                {/* Capital */}
                <div className="config-section">
                    <h4>Capital</h4>

                    <div className="config-item">
                        <label>$ par trade</label>
                        <input
                            type="number"
                            min={10}
                            max={10000}
                            value={config.max_capital_per_trade}
                            onChange={(e) => onUpdate({ max_capital_per_trade: Number(e.target.value) })}
                        />
                    </div>

                    <div className="config-item">
                        <label>Max positions</label>
                        <input
                            type="number"
                            min={1}
                            max={20}
                            value={config.max_active_positions}
                            onChange={(e) => onUpdate({ max_active_positions: Number(e.target.value) })}
                        />
                    </div>
                </div>

                {/* Ratios */}
                <div className="config-section">
                    <h4>Ratio YES/NO</h4>

                    <div className="config-item">
                        <label>YES %</label>
                        <input
                            type="number"
                            min={0}
                            max={100}
                            value={config.default_ratio_yes}
                            onChange={(e) => onUpdate({
                                default_ratio_yes: Number(e.target.value),
                                default_ratio_no: 100 - Number(e.target.value)
                            })}
                        />
                    </div>

                    <div className="ratio-bar-small">
                        <div className="yes" style={{ width: `${config.default_ratio_yes}%` }}>
                            {config.default_ratio_yes}%
                        </div>
                        <div className="no" style={{ width: `${config.default_ratio_no}%` }}>
                            {config.default_ratio_no}%
                        </div>
                    </div>
                </div>

                {/* Exit Strategy */}
                <div className="config-section" style={{ minWidth: '300px' }}>
                    <h4>🧠 Stratégie de Sortie</h4>

                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9em', color: '#888' }}>Modèle de Sortie</label>
                        <select
                            value={config.exit_model || 'GLOBAL'}
                            onChange={(e) => onUpdate({ exit_model: e.target.value as 'GLOBAL' | 'INDEPENDENT' })}
                            className="strategy-select"
                            style={{
                                width: '100%',
                                padding: '8px',
                                background: '#333',
                                color: 'white',
                                border: '1px solid #444',
                                borderRadius: '4px'
                            }}
                        >
                            <option value="GLOBAL">Global P&L (Classique)</option>
                            <option value="INDEPENDENT">Smart Exit (Legging Out)</option>
                        </select>
                    </div>

                    {config.exit_model === 'INDEPENDENT' ? (
                        <div className="smart-exit-config" style={{ padding: '10px', background: 'rgba(0, 255, 0, 0.05)', borderRadius: '4px', border: '1px solid rgba(0, 255, 0, 0.2)' }}>
                            <div className="config-item">
                                <label>Cut Loser (Drawdown)</label>
                                <input
                                    type="number"
                                    min={1}
                                    max={99}
                                    value={config.leg_stop_loss_percent || 0}
                                    onChange={(e) => onUpdate({ leg_stop_loss_percent: Number(e.target.value) })}
                                />
                                <span className="hint">%</span>
                            </div>
                            <small style={{ display: 'block', color: '#aaa', marginBottom: '10px' }}>Vend la jambe perdante si elle chute de X%.</small>

                            <div className="config-item">
                                <label>Take Winner (Price)</label>
                                <input
                                    type="number"
                                    min={0.5}
                                    max={1.0}
                                    step={0.01}
                                    value={config.leg_take_profit_price || 0}
                                    onChange={(e) => onUpdate({ leg_take_profit_price: Number(e.target.value) })}
                                />
                                <span className="hint">$</span>
                            </div>
                            <small style={{ display: 'block', color: '#aaa' }}>Vend la jambe gagnante si elle atteint X $.</small>
                        </div>
                    ) : (
                        <>
                            <div className="config-item">
                                <label>Stop Loss Global</label>
                                <input
                                    type="number"
                                    min={1}
                                    max={50}
                                    value={config.stop_loss_percent}
                                    onChange={(e) => onUpdate({ stop_loss_percent: Number(e.target.value) })}
                                />
                                <span className="hint">%</span>
                            </div>

                            <div className="config-item">
                                <label>Take Profit Global</label>
                                <input
                                    type="number"
                                    min={1}
                                    max={100}
                                    value={config.take_profit_percent}
                                    onChange={(e) => onUpdate({ take_profit_percent: Number(e.target.value) })}
                                />
                                <span className="hint">%</span>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
