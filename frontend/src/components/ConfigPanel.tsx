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

                {/* SL/TP */}
                <div className="config-section">
                    <h4>Stop Loss / Take Profit</h4>

                    <div className="config-item">
                        <label>Stop Loss</label>
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
                        <label>Take Profit</label>
                        <input
                            type="number"
                            min={1}
                            max={100}
                            value={config.take_profit_percent}
                            onChange={(e) => onUpdate({ take_profit_percent: Number(e.target.value) })}
                        />
                        <span className="hint">%</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
