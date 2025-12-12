import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ==================== TYPES ====================

export interface BotStatus {
    status: string;
    wallet_configured: boolean;
    total_capital: number;
    capital_engaged: number;
    capital_available: number;
    active_positions: number;
    total_pnl: number;
    total_pnl_percent: number;
    opportunities_count: number;
    best_opportunity_score: number;
    timestamp: string;
}

export interface TradingStatus {
    is_running: boolean;
    is_paused: boolean;
    auto_trading_enabled: boolean;
    active_positions: number;
    total_pnl: number;
}

export interface ScannerConfig {
    auto_trading_enabled: boolean;
    scan_interval_seconds: number;
    max_markets_per_scan: number;
    min_score_to_trade: number;
    min_score_to_show: number;
    min_volume_24h: number;
    min_liquidity: number;
    max_active_positions: number;
    max_capital_per_trade: number;
    max_total_capital: number;
    default_ratio_yes: number;
    default_ratio_no: number;
    stop_loss_percent: number;
    take_profit_percent: number;
    exit_model: 'GLOBAL' | 'INDEPENDENT';
    leg_stop_loss_percent: number;
    leg_take_profit_price: number;
}

export interface Position {
    id: number;
    market_id: string;
    market_name: string;
    entry_price_yes: number;
    entry_price_no: number;
    amount_yes: number;
    amount_no: number;
    current_price_yes: number | null;
    current_price_no: number | null;
    current_value_yes: number | null;
    current_value_no: number | null;
    pnl: number;
    pnl_percent: number;
    status: string;
    active_side: string;
    created_at: string;
    closed_at: string | null;
}

export interface Opportunity {
    market_id: string;
    market_name: string;
    price_yes: number;
    price_no: number;
    divergence_score: number;
    volume_score: number;
    liquidity_score: number;
    timing_score: number;
    activity_score: number;
    total_score: number;
    volume_24h: number;
    liquidity: number;
    hours_to_resolution: number | null;
    analyzed_at: string;
}

export interface ScanResult {
    scanned_count: number;
    opportunities_found: number;
    scan_duration_seconds: number;
    opportunities: Opportunity[];
}

export interface Trade {
    id: number;
    position_id: number;
    market_name: string;
    side: string;
    type: string;
    amount: number;
    price: number;
    total_value: number;
    executed_at: string;
}

// ==================== DASHBOARD ====================

export const getStatus = async (): Promise<BotStatus> => {
    const response = await api.get('/api/status');
    return response.data;
};

export const healthCheck = async () => {
    const response = await api.get('/health');
    return response.data;
};

// ==================== TRADING CONTROL ====================

export const getTradingStatus = async (): Promise<TradingStatus> => {
    const response = await api.get('/api/trading/status');
    return response.data;
};

export const startTrading = async () => {
    const response = await api.post('/api/trading/start');
    return response.data;
};

export const stopTrading = async () => {
    const response = await api.post('/api/trading/stop');
    return response.data;
};

export const pauseTrading = async () => {
    const response = await api.post('/api/trading/pause');
    return response.data;
};

export const resumeTrading = async () => {
    const response = await api.post('/api/trading/resume');
    return response.data;
};

export const panicCloseAll = async () => {
    const response = await api.post('/api/trading/panic');
    return response.data;
};

export const closePosition = async (positionId: number) => {
    const response = await api.post(`/api/trading/close/${positionId}`);
    return response.data;
};

// ==================== SCANNER ====================

export const getOpportunities = async (minScore: number = 1): Promise<Opportunity[]> => {
    const response = await api.get('/api/scanner/opportunities', {
        params: { min_score: minScore },
    });
    return response.data;
};

export const triggerScan = async (limit: number = 100): Promise<ScanResult> => {
    const response = await api.post('/api/scanner/scan', null, {
        params: { limit },
    });
    return response.data;
};

export const getScannerConfig = async (): Promise<ScannerConfig> => {
    const response = await api.get('/api/scanner/config');
    return response.data;
};

export const updateScannerConfig = async (config: Partial<ScannerConfig>): Promise<ScannerConfig> => {
    const response = await api.put('/api/scanner/config', config);
    return response.data;
};

// ==================== POSITIONS ====================

export const getPositions = async (status?: string): Promise<Position[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/positions', { params });
    return response.data;
};

export const getActivePositions = async (): Promise<Position[]> => {
    const response = await api.get('/api/positions/active');
    return response.data;
};

// ==================== TRADES ====================

export const getRecentTrades = async (limit: number = 20): Promise<Trade[]> => {
    const response = await api.get('/api/trades/recent', {
        params: { limit },
    });
    return response.data;
};

export default api;
