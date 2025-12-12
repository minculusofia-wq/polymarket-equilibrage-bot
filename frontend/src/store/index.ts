import { create } from 'zustand';

interface TradingState {
    isRunning: boolean;
    isPaused: boolean;
    autoTradingEnabled: boolean;
    setTradingState: (running: boolean, paused: boolean, autoEnabled: boolean) => void;
}

export const useTradingStore = create<TradingState>((set) => ({
    isRunning: false,
    isPaused: false,
    autoTradingEnabled: false,
    setTradingState: (running, paused, autoEnabled) => set({
        isRunning: running,
        isPaused: paused,
        autoTradingEnabled: autoEnabled,
    }),
}));

interface ConfigStore {
    // Settings
    minScoreToTrade: number;
    minScoreToShow: number;
    capitalPerTrade: number;
    maxPositions: number;
    ratioYes: number;
    ratioNo: number;
    stopLossPercent: number;
    takeProfitPercent: number;

    // Actions
    setConfig: (config: Partial<ConfigStore>) => void;
}

export const useConfigStore = create<ConfigStore>((set) => ({
    minScoreToTrade: 7,
    minScoreToShow: 3,
    capitalPerTrade: 100,
    maxPositions: 5,
    ratioYes: 50,
    ratioNo: 50,
    stopLossPercent: 10,
    takeProfitPercent: 15,

    setConfig: (config) => set((state) => ({ ...state, ...config })),
}));

interface NotificationStore {
    notifications: Array<{
        id: number;
        type: 'success' | 'error' | 'info' | 'warning';
        message: string;
    }>;
    addNotification: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
    removeNotification: (id: number) => void;
}

let notificationId = 0;

export const useNotificationStore = create<NotificationStore>((set) => ({
    notifications: [],

    addNotification: (type, message) => {
        const id = ++notificationId;
        set((state) => ({
            notifications: [...state.notifications, { id, type, message }],
        }));
        setTimeout(() => {
            set((state) => ({
                notifications: state.notifications.filter((n) => n.id !== id),
            }));
        }, 5000);
    },

    removeNotification: (id) =>
        set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
        })),
}));
