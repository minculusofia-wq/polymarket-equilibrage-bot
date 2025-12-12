import type { ReactNode } from 'react';

interface StatCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    icon?: ReactNode;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: string;
    className?: string;
}

export function StatCard({
    title,
    value,
    subtitle,
    icon,
    trend,
    trendValue,
    className = ''
}: StatCardProps) {
    const trendColors = {
        up: 'text-emerald-400',
        down: 'text-red-400',
        neutral: 'text-gray-400',
    };

    return (
        <div className={`stat-card ${className}`}>
            <div className="stat-card-header">
                <span className="stat-card-title">{title}</span>
                {icon && <span className="stat-card-icon">{icon}</span>}
            </div>

            <div className="stat-card-value">{value}</div>

            {(subtitle || trendValue) && (
                <div className="stat-card-footer">
                    {subtitle && <span className="stat-card-subtitle">{subtitle}</span>}
                    {trend && trendValue && (
                        <span className={`stat-card-trend ${trendColors[trend]}`}>
                            {trend === 'up' && '↑'}
                            {trend === 'down' && '↓'}
                            {trendValue}
                        </span>
                    )}
                </div>
            )}
        </div>
    );
}
