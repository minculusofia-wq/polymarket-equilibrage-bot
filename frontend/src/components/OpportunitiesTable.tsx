import { useState, useMemo } from 'react';
import type { Opportunity } from '../services/api';
import { useConfigStore } from '../store';

interface OpportunitiesTableProps {
    opportunities: Opportunity[];
    onTrade?: (marketId: string, amount: number, ratioYes: number, ratioNo: number) => void;
    loading?: boolean;
}

const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toFixed(0);
};

type SortField = 'score' | 'estimated_net_profit' | 'liquidity' | 'spread_percent';
type SortDirection = 'asc' | 'desc';

export function OpportunitiesTable({ opportunities, onTrade: _onTrade, loading }: OpportunitiesTableProps) {
    const { } = useConfigStore();

    // State for Sorting
    const [sortField, setSortField] = useState<SortField>('score');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

    // Dynamic processing
    const processedOpportunities = useMemo(() => {
        let items = [...opportunities];

        // 2. Sort
        items.sort((a, b) => {
            const aValue = a[sortField] || 0;
            const bValue = b[sortField] || 0;

            if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
            if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        return items;
    }, [opportunities, sortField, sortDirection]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('desc'); // Default to desc for new field
        }
    };

    const getSortIcon = (field: SortField) => {
        if (sortField !== field) return '↕';
        return sortDirection === 'asc' ? '↑' : '↓';
    };

    if (loading) {
        return (
            <div className="table-container">
                <div className="loading-spinner">Chargement des opportunités...</div>
            </div>
        );
    }

    if (opportunities.length === 0) {
        return (
            <div className="table-container">
                <div className="empty-state">
                    <p>Aucune opportunité détectée pour le moment.</p>
                    <small>Le scanner analyse les marchés en arrière-plan...</small>
                </div>
            </div>
        );
    }

    return (
        <div className="table-container">
            {/* Toolbar */}
            <div className="table-toolbar">
                <div className="toolbar-stats" style={{ width: '100%', textAlign: 'right' }}>
                    {processedOpportunities.length} opportunités (Filtres appliqués depuis Settings)
                </div>
            </div>

            <table className="data-table">
                <thead>
                    <tr>
                        <th>Market</th>
                        <th onClick={() => handleSort('score')} className="sortable">
                            Score {getSortIcon('score')}
                        </th>
                        <th>Prix YES/NO</th>
                        <th onClick={() => handleSort('spread_percent')} className="sortable">
                            Spread {getSortIcon('spread_percent')}
                        </th>
                        <th onClick={() => handleSort('estimated_net_profit')} className="sortable">
                            Rendement Net {getSortIcon('estimated_net_profit')}
                        </th>
                        <th onClick={() => handleSort('liquidity')} className="sortable">
                            Liquidité {getSortIcon('liquidity')}
                        </th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {processedOpportunities.map((op) => (
                        <tr key={op.market_id} className={op.score >= 8 ? 'high-score' : ''}>
                            <td className="market-name" title={op.market_name}>
                                <div className="market-name-text">
                                    {op.market_name.length > 60
                                        ? op.market_name.substring(0, 60) + '...'
                                        : op.market_name}
                                </div>
                                <div className="market-id">{op.market_id}</div>
                            </td>
                            <td>
                                <span className={`score score-${op.score}`}>
                                    {op.score}/10
                                </span>
                            </td>
                            <td>
                                <div className="prices">
                                    <span className="price-yes" title="YES">{op.price_yes?.toFixed(3)}</span>
                                    <span className="price-sep">/</span>
                                    <span className="price-no" title="NO">{op.price_no?.toFixed(3)}</span>
                                </div>
                            </td>
                            <td>
                                {op.spread_percent !== undefined ? (
                                    <span className={op.spread_percent > 0.05 ? 'text-danger' : 'text-success'}>
                                        {(op.spread_percent * 100).toFixed(1)}%
                                    </span>
                                ) : '-'}
                            </td>
                            <td>
                                {op.estimated_net_profit !== undefined ? (
                                    <span className={op.estimated_net_profit > 0 ? 'net-profit-pos' : 'net-profit-neg'}>
                                        {op.estimated_net_profit > 0 ? '+' : ''}{(op.estimated_net_profit * 100).toFixed(2)}%
                                    </span>
                                ) : '-'}
                            </td>
                            <td>
                                <div className="liquidity-cell">
                                    <span>${formatNumber(op.liquidity)}</span>
                                    <div className="liquidity-bar">
                                        <div
                                            className="liquidity-fill"
                                            style={{ width: `${Math.min(100, (op.liquidity / 100000) * 100)}%` }}
                                        />
                                    </div>
                                </div>
                            </td>
                            <td>
                                <button
                                    className="trade-btn"
                                    onClick={() => {
                                        const url = op.market_slug
                                            ? `https://polymarket.com/event/${op.market_slug}`
                                            : `https://polymarket.com/?q=${encodeURIComponent(op.market_name)}`;
                                        window.open(url, '_blank');
                                    }}
                                >
                                    Voir
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
