import type { Opportunity } from '../services/api';
import { useConfigStore } from '../store';

interface OpportunitiesTableProps {
    opportunities: Opportunity[];
    onTrade: (marketId: string, capital: number, ratioYes: number, ratioNo: number) => void;
    loading?: boolean;
}

export function OpportunitiesTable({ opportunities, onTrade, loading }: OpportunitiesTableProps) {
    const { capitalPerTrade, ratioYes, ratioNo } = useConfigStore();

    const getScoreColor = (score: number) => {
        if (score >= 8) return 'score-high';
        if (score >= 5) return 'score-medium';
        return 'score-low';
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
                    <p>Aucune opportunité détectée</p>
                    <span>Lancez un scan pour détecter des opportunités</span>
                </div>
            </div>
        );
    }

    return (
        <div className="table-container">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Marché</th>
                        <th>Prix YES/NO</th>
                        <th>Scores Détail</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {opportunities.map((opp, index) => (
                        <tr key={opp.market_id + '-' + index}>
                            <td>
                                <div className={`score-badge ${getScoreColor(opp.total_score)}`}>
                                    {opp.total_score}
                                </div>
                            </td>
                            <td>
                                <div className="market-name" title={opp.market_name}>
                                    {opp.market_name.length > 50
                                        ? opp.market_name.substring(0, 50) + '...'
                                        : opp.market_name}
                                </div>
                            </td>
                            <td>
                                <span className="price-yes">{opp.price_yes?.toFixed(3)}</span>
                                {' / '}
                                <span className="price-no">{opp.price_no?.toFixed(3)}</span>
                            </td>
                            <td>
                                <div className="score-details">
                                    <span title="Divergence">D:{opp.divergence_score?.toFixed(1)}</span>
                                    <span title="Volume">V:{opp.volume_score?.toFixed(1)}</span>
                                    <span title="Liquidité">L:{opp.liquidity_score?.toFixed(1)}</span>
                                </div>
                            </td>
                            <td>
                                <button
                                    className="btn btn-primary btn-sm"
                                    onClick={() => onTrade(opp.market_id, capitalPerTrade, ratioYes, ratioNo)}
                                >
                                    Trader ${capitalPerTrade}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
