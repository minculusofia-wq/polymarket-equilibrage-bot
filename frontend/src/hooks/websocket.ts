import { useEffect, useRef, useCallback } from 'react';
import { useNotificationStore, useTradingStore } from '../store';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export function useWebSocket() {
    const ws = useRef<WebSocket | null>(null);
    const addNotification = useNotificationStore((s) => s.addNotification);
    const setTradingState = useTradingStore((s) => s.setTradingState);

    const connect = useCallback(() => {
        if (ws.current?.readyState === WebSocket.OPEN) return;

        try {
            ws.current = new WebSocket(WS_URL);

            ws.current.onopen = () => {
                console.log('WS Connected');
            };

            ws.current.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);

                    switch (message.type) {
                        case 'TRADING_STATUS':
                            setTradingState(
                                message.data.is_running,
                                message.data.is_paused,
                                message.data.auto_trading_enabled
                            );
                            break;

                        case 'SCAN_COMPLETE':
                            addNotification('info', `Scan: ${message.data.count} opportunités trouvées`);
                            break;

                        case 'POSITION_OPENED':
                            addNotification('success', `Position ouverte: ${message.data.market_name}`);
                            break;

                        case 'POSITION_CLOSED':
                            const pnl = message.data.pnl;
                            const type = pnl >= 0 ? 'success' : 'warning';
                            addNotification(type, `Position fermée: ${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}$ (${message.data.reason})`);
                            break;
                    }
                } catch (err) {
                    console.error('WS Message parsing error:', err);
                }
            };

            ws.current.onclose = () => {
                console.log('WS Disconnected. Reconnecting in 3s...');
                setTimeout(connect, 3000);
            };

            ws.current.onerror = (err) => {
                console.error('WS Error:', err);
                ws.current?.close();
            };
        } catch (err) {
            console.error('WS Connection error:', err);
        }
    }, [addNotification, setTradingState]);

    useEffect(() => {
        connect();
        return () => {
            ws.current?.close();
        };
    }, [connect]);

    return ws.current;
}
