import type { Position } from '../services/api';

interface PositionsTableProps {
    positions: Position[];
    onClose: (id: number) => void;
    loading?: boolean;
}

export function PositionsTable({ positions, onClose, loading }: PositionsTableProps) {
    if (loading) {
        return (
            <div className="table-container">
                <div className="loading-spinner">Chargement des positions...</div>
            </div>
        );
    }

    if (positions.length === 0) {
        return (
            <div className="table-container">
                <div className="empty-state">
                    <p>Aucune position active</p>
                    <span>Scannez les marchés pour trouver des opportunités</span>
                </div>
            </div>
        );
    }

    return (
        <div className="table-container">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Marché</th>
                        <th>Entrée YES/NO</th>
                        <th>Actuel YES/NO</th>
                        <th>Montants</th>
                        <th>P&L</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {positions.map((pos) => (
                        <tr key={pos.id}>
                            <td>
                                <div className="market-name" title={pos.market_name}>
                                    {pos.market_name.length > 50
                                        ? pos.market_name.substring(0, 50) + '...'
                                        : pos.market_name}
                                </div>
                            </td>
                            <td>
                                <span className="price-yes">{pos.entry_price_yes?.toFixed(3)}</span>
                                {' / '}
                                <span className="price-no">{pos.entry_price_no?.toFixed(3)}</span>
                            </td>
                            <td>
                                <span className="price-yes">{pos.current_price_yes?.toFixed(3) || '-'}</span>
                                {' / '}
                                <span className="price-no">{pos.current_price_no?.toFixed(3) || '-'}</span>
                            </td>
                            <td>
                                <span className="amount">${pos.amount_yes?.toFixed(2)}</span>
                                {' / '}
                                <span className="amount">${pos.amount_no?.toFixed(2)}</span>
                            </td>
                            <td>
                                <div className={`pnl ${pos.pnl >= 0 ? 'positive' : 'negative'}`}>
                                    <span>${pos.pnl?.toFixed(2)}</span>
                                    <span className="pnl-percent">({pos.pnl_percent?.toFixed(2)}%)</span>
                                </div>
                            </td>
                            <td>
                                <button
                                    className="btn btn-danger btn-sm"
                                    onClick={() => onClose(pos.id)}
                                >
                                    Fermer
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
