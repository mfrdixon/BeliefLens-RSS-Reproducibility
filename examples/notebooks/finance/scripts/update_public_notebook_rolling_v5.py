"""Replace the public notebook's finance evaluation with rolling-v5 results."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
NOTEBOOK = HERE / "SPY_SGOV_public_reproduction.ipynb"


SECTION = """## 6. Recent rolling SPY/SGOV evaluation

This deployment study removes the stale-calibration concern by constructing a new measurement channel from 2025 observations. The initial blocks are **January–June 2025 calibration (122 trading sessions)**, **July–September prompt validation (64)** and **October–December conformal calibration (64)**. At the first decision in each 2026 trading week, all three boundaries advance together: the newest eligible sessions enter the conformal block and the oldest sessions leave calibration. Every 250-session window ends before its deployment date.

The fitted language model is frozen before the 2026 evaluation period. Stored observations are reused here, so this notebook makes no provider request. Because the provider's top alternatives did not expose every candidate on every record, the estimator uses the observable candidate probabilities together with missingness indicators and the reported residual-mass bound. It does **not** silently treat an unreturned candidate as having known zero probability.
"""


CODE = """from IPython.display import display

RV5 = BUNDLE.parent/'derived'/'rolling_v5'
channel_result = json.loads((RV5/'ROLLING_CHANNEL_RESULTS.json').read_text())
portfolio_result = json.loads((RV5/'ROLLING_PORTFOLIO_RESULTS.json').read_text())
fit_audit = pd.DataFrame(json.loads((RV5/'rolling_fit_audit.json').read_text()))
rolling = pd.read_csv(RV5/'rolling_portfolio_backtest.csv', parse_dates=['date'])

measurement_table = pd.DataFrame([
    ('Out-of-sample decisions', channel_result['test_records'], '2026 only'),
    ('Weekly calibration vintages', channel_result['weekly_refits'], 'all fitted on earlier observations'),
    ('State-recovery accuracy', channel_result['accuracy'], 'higher is better'),
    ('Multiclass log loss', channel_result['log_loss'], 'lower is better'),
    ('Conformal coverage', channel_result['conformal_coverage'], 'nominal level: 90%'),
    ('Mean prediction-set size', channel_result['mean_prediction_set_size'], 'out of three states'),
    ('Mean unobserved-mass bound', channel_result['mean_unobserved_mass_lower_bound'], 'top-k coarsening diagnostic'),
], columns=['Diagnostic', 'Value', 'Interpretation'])
display(measurement_table.style.format({'Value': lambda x: f'{x:.3f}' if isinstance(x, float) else str(x)}))

metric_rows = []
for strategy, values in portfolio_result['metrics'].items():
    metric_rows.append({
        'Strategy': strategy,
        'Annualized return': values['annualized_return'],
        'Annualized volatility': values['annualized_volatility'],
        'Excess Sharpe vs SGOV': values['excess_sharpe_vs_sgov'],
        'Maximum drawdown': values['maximum_drawdown_loss_magnitude'],
        'Annualized turnover': values['annualized_turnover'],
    })
portfolio_table = pd.DataFrame(metric_rows).set_index('Strategy')
display(portfolio_table.style.format({
    'Annualized return': '{:.1%}', 'Annualized volatility': '{:.1%}',
    'Excess Sharpe vs SGOV': lambda x: '—' if pd.isna(x) else f'{x:.2f}',
    'Maximum drawdown': '{:.1%}', 'Annualized turnover': '{:.1f}x',
}))

returns = {
    'BeliefLens': 'return_BeliefLens linear state allocation',
    'SPY': 'return_SPY buy-and-hold',
    '50/50': 'return_Fixed 50/50 SPY-SGOV',
}
colors = {'BeliefLens': '#0F766E', 'SPY': '#C2413B', '50/50': '#D4A72C'}
fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))
for name, column in returns.items():
    wealth = (1 + rolling[column]).cumprod()
    axes[0].plot(rolling.date, wealth, label=name, color=colors[name], lw=2)
axes[0].set_title('Growth of $1')
axes[0].set_ylabel('Portfolio value')
axes[0].legend(frameon=False)

axes[1].plot(rolling.date, rolling['weight_BeliefLens linear state allocation'], color=colors['BeliefLens'], lw=1.8, label='SPY weight')
axes[1].plot(rolling.date, rolling['entropy'], color='#64748B', lw=1.2, alpha=.85, label='Semantic entropy')
axes[1].set_title('Walk-forward allocation and uncertainty')
axes[1].set_ylim(0, 1.02)
axes[1].legend(frameon=False)

for name in ('BeliefLens', 'SPY'):
    wealth = (1 + rolling[returns[name]]).cumprod()
    drawdown = 1 - wealth / wealth.cummax()
    axes[2].plot(rolling.date, drawdown, label=name, color=colors[name], lw=2)
axes[2].set_title('Drawdown (loss magnitude)')
axes[2].set_ylabel('Drawdown')
axes[2].yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
axes[2].legend(frameon=False)

for ax in axes:
    ax.grid(alpha=.18)
    ax.tick_params(axis='x', rotation=30)
fig.tight_layout()
plt.show()

fit_audit[['deployment_date', 'window_start', 'window_end', 'selected_C', 'conformal_threshold']].tail(6)
"""


INTERPRETATION = """### Interpretation and limits

The simple prespecified allocation—SPY weight equal to *P*(Risk-on) + 0.5 *P*(Mixed), with the remainder in SGOV—produced a **1.32 excess Sharpe ratio**, compared with **1.12 for SPY**, while reducing annualized volatility from **14.1% to 6.7%** and maximum drawdown from **8.9% to 2.7%**. It earned a lower absolute return than fully invested SPY. A prespecified entropy/conformal shrinkage rule did not improve performance and is reported rather than discarded.

This is a short, single-period secondary portfolio illustration—not proof of persistent alpha. The important scientific result is that the semantic measurement channel is recent, rolls forward without look-ahead, and retains approximately nominal conformal coverage. The Sharpe difference has not been established as statistically significant and must not be described as an investment guarantee.
"""


def lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text())
    notebook["cells"][18]["source"] = lines(SECTION)
    notebook["cells"][19]["source"] = lines(CODE)
    notebook["cells"][19]["outputs"] = []
    notebook["cells"][19]["execution_count"] = None
    notebook["cells"][20]["source"] = lines(INTERPRETATION)
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
