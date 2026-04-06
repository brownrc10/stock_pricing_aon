import numpy as np


def main():
    np.random.seed(42)
    current_stock = 172.13
    risk_free_rate = 0.03577
    dividend_yield = 0.03202
    volatillity = 0.2356
    T = 3.0
    trading_days = 252
    total_trading_days = int(T * trading_days)
    n_simulations = 1_000_000
    dt = 1 / trading_days
    Z = np.random.standard_normal((n_simulations, total_trading_days))
    daily_returns = np.exp(
        (risk_free_rate - dividend_yield - 0.5 * volatillity**2) * dt
        + volatillity * np.sqrt(dt) * Z
    )
    price_paths = current_stock * np.cumprod(daily_returns, axis=1)
    price_point = 300
    masked_price_paths = price_paths > price_point
    n_windows = total_trading_days - 20 + 1
    vested = np.zeros(n_simulations, dtype=bool)
    for t in range(n_windows):
        window = masked_price_paths[:, t : t + 20]
        vested |= window.all(axis=1)
    final_prices = price_paths[vested, -1]
    print(final_prices.shape)
    payouts = final_prices * 100
    present_values = payouts * np.exp(-risk_free_rate * T)
    fair_value = np.sum(present_values) / n_simulations
    vest_pct = vested.mean() * 100
    print(f"Fair Value: ${fair_value:.4f}")
    print(f"Vesting Percentag {vest_pct}")
    print(f"Avg final price of vested: {price_paths[vested, -1].mean():.2f}")
    print(f"Avg final price of all runs: {price_paths[:, -1].mean():.2f}")


if __name__ == "__main__":
    main()
