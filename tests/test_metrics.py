from retailiq.analytics.metrics import calculate_metrics
from retailiq.sample_data import write_transactions


def test_metrics_reconcile_to_source(tmp_path):
    path = tmp_path / "transactions.csv"
    write_transactions(path, rows=25, seed=42)
    metrics = calculate_metrics(path)
    assert metrics["dataset"]["transaction_count"] == 25
    assert metrics["kpis"]["total_revenue"] > 0
    assert metrics["kpis"]["total_profit"] > 0
    assert metrics["kpis"]["profit_margin_pct"] < 100
