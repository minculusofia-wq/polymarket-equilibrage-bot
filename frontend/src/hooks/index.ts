import { useState, useEffect, useCallback } from 'react';
import {
    getStatus,
    getTradingStatus,
    getActivePositions,
    getOpportunities,
    getScannerConfig,
    triggerScan,
    startTrading,
    stopTrading,
    pauseTrading,
    resumeTrading,
    panicCloseAll,
    closePosition,
    updateScannerConfig,
    type BotStatus,
    type TradingStatus,
    type Position,
    type Opportunity,
    type ScannerConfig,
} from '../services/api';
import { useNotificationStore, useTradingStore, useConfigStore } from '../store';

// Hook for WebSocket
export { useWebSocket } from './websocket';


// Hook for bot status
export function useStatus(refreshInterval = 10000) {
    const [status, setStatus] = useState<BotStatus | null>(null);
    const [loading, setLoading] = useState(true);

    const refresh = useCallback(async () => {
        try {
            const data = await getStatus();
            setStatus(data);
        } catch (err) {
            console.error('Status error:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refresh();
        const interval = setInterval(refresh, refreshInterval);
        return () => clearInterval(interval);
    }, [refresh, refreshInterval]);

    return { status, loading, refresh };
}

// Hook for trading status
export function useTradingStatus(refreshInterval = 5000) {
    const [status, setStatus] = useState<TradingStatus | null>(null);
    const setTradingState = useTradingStore((s) => s.setTradingState);
    const addNotification = useNotificationStore((s) => s.addNotification);

    const refresh = useCallback(async () => {
        try {
            const data = await getTradingStatus();
            setStatus(data);
            setTradingState(data.is_running, data.is_paused, data.auto_trading_enabled);
        } catch (err) {
            console.error('Trading status error:', err);
        }
    }, [setTradingState]);

    const start = useCallback(async () => {
        try {
            await startTrading();
            addNotification('success', '🤖 Trading automatique démarré');
            refresh();
        } catch (err) {
            addNotification('error', 'Erreur démarrage trading');
        }
    }, [refresh, addNotification]);

    const stop = useCallback(async () => {
        try {
            await stopTrading();
            addNotification('info', '🛑 Trading arrêté');
            refresh();
        } catch (err) {
            addNotification('error', 'Erreur arrêt trading');
        }
    }, [refresh, addNotification]);

    const pause = useCallback(async () => {
        try {
            await pauseTrading();
            addNotification('info', '⏸️ Trading en pause');
            refresh();
        } catch (err) {
            addNotification('error', 'Erreur pause trading');
        }
    }, [refresh, addNotification]);

    const resume = useCallback(async () => {
        try {
            await resumeTrading();
            addNotification('success', '▶️ Trading repris');
            refresh();
        } catch (err) {
            addNotification('error', 'Erreur reprise trading');
        }
    }, [refresh, addNotification]);

    const panic = useCallback(async () => {
        try {
            const result = await panicCloseAll();
            addNotification('warning', `🚨 PANIC: ${result.positions_closed} positions fermées`);
            refresh();
        } catch (err) {
            addNotification('error', 'Erreur panic close');
        }
    }, [refresh, addNotification]);

    useEffect(() => {
        refresh();
        const interval = setInterval(refresh, refreshInterval);
        return () => clearInterval(interval);
    }, [refresh, refreshInterval]);

    return { status, refresh, start, stop, pause, resume, panic };
}

// Hook for positions
export function usePositions(refreshInterval = 5000) {
    const [positions, setPositions] = useState<Position[]>([]);
    const [loading, setLoading] = useState(true);
    const addNotification = useNotificationStore((s) => s.addNotification);

    const refresh = useCallback(async () => {
        try {
            const data = await getActivePositions();
            setPositions(data);
        } catch (err) {
            console.error('Positions error:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const close = useCallback(async (positionId: number) => {
        try {
            await closePosition(positionId);
            addNotification('success', 'Position fermée');
            refresh();
        } catch (err) {
            addNotification('error', 'Erreur fermeture position');
        }
    }, [refresh, addNotification]);

    useEffect(() => {
        refresh();
        const interval = setInterval(refresh, refreshInterval);
        return () => clearInterval(interval);
    }, [refresh, refreshInterval]);

    return { positions, loading, refresh, close };
}

// Hook for opportunities
export function useOpportunities(refreshInterval = 15000) {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [scanning, setScanning] = useState(false);
    const addNotification = useNotificationStore((s) => s.addNotification);

    const refresh = useCallback(async () => {
        try {
            const data = await getOpportunities(1);
            setOpportunities(data);
        } catch (err) {
            console.error('Opportunities error:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const scan = useCallback(async () => {
        setScanning(true);
        try {
            const result = await triggerScan(100);
            addNotification('success', `Scan: ${result.opportunities_found} opportunités en ${result.scan_duration_seconds.toFixed(1)}s`);
            setOpportunities(result.opportunities);
        } catch (err) {
            addNotification('error', 'Erreur scan');
        } finally {
            setScanning(false);
        }
    }, [addNotification]);

    useEffect(() => {
        refresh();
        const interval = setInterval(refresh, refreshInterval);
        return () => clearInterval(interval);
    }, [refresh, refreshInterval]);

    return { opportunities, loading, scanning, refresh, scan };
}

// Hook for scanner config
export function useConfig() {
    const [config, setConfig] = useState<ScannerConfig | null>(null);
    const [loading, setLoading] = useState(true);
    const addNotification = useNotificationStore((s) => s.addNotification);
    const setStoreConfig = useConfigStore((s) => s.setConfig);

    const refresh = useCallback(async () => {
        try {
            setLoading(true); // Ensure loading state is true at start
            const data = await getScannerConfig();
            if (data) {
                setConfig(data);
                setStoreConfig({
                    minScoreToTrade: data.min_score_to_trade,
                    minScoreToShow: data.min_score_to_show,
                    capitalPerTrade: data.max_capital_per_trade,
                    maxPositions: data.max_active_positions,
                    ratioYes: data.default_ratio_yes,
                    ratioNo: data.default_ratio_no,
                    stopLossPercent: data.stop_loss_percent,
                    takeProfitPercent: data.take_profit_percent,
                });
            } else {
                console.error('Config data is null/undefined');
                addNotification('error', 'Configuration vide reçue');
            }
        } catch (err) {
            console.error('Config error:', err);
            addNotification('error', 'Erreur chargement configuration');
        } finally {
            setLoading(false);
        }
    }, [setStoreConfig, addNotification]);

    const update = useCallback(async (updates: Partial<ScannerConfig>) => {
        try {
            const newConfig = await updateScannerConfig(updates);
            setConfig(newConfig);
            addNotification('success', 'Configuration mise à jour');
        } catch (err) {
            addNotification('error', 'Erreur mise à jour config');
        }
    }, [addNotification]);

    useEffect(() => {
        refresh();
    }, [refresh]);

    return { config, loading, refresh, update };
}
