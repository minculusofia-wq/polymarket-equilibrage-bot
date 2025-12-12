interface TradingControlsProps {
    isRunning: boolean;
    isPaused: boolean;
    onStart: () => void;
    onStop: () => void;
    onPause: () => void;
    onResume: () => void;
    onPanic: () => void;
}

export function TradingControls({
    isRunning,
    isPaused,
    onStart,
    onStop,
    onPause,
    onResume,
    onPanic,
}: TradingControlsProps) {
    return (
        <div className="trading-controls">
            <div className="control-status">
                <span className={`status-dot ${isRunning ? (isPaused ? 'paused' : 'running') : 'stopped'}`} />
                <span className="status-text">
                    {isRunning ? (isPaused ? 'En pause' : 'Actif') : 'Arrêté'}
                </span>
            </div>

            <div className="control-buttons">
                {!isRunning ? (
                    <button className="btn btn-success" onClick={onStart}>
                        ▶️ Démarrer
                    </button>
                ) : (
                    <>
                        {isPaused ? (
                            <button className="btn btn-primary" onClick={onResume}>
                                ▶️ Reprendre
                            </button>
                        ) : (
                            <button className="btn btn-warning" onClick={onPause}>
                                ⏸️ Pause
                            </button>
                        )}
                        <button className="btn btn-secondary" onClick={onStop}>
                            ⏹️ Arrêter
                        </button>
                    </>
                )}

                <button className="btn btn-danger btn-panic" onClick={onPanic}>
                    🚨 PANIC
                </button>
            </div>
        </div>
    );
}
