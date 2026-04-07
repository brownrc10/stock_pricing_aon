from montecarlo import MonteCarloSimulation


def main():
    simulation = MonteCarloSimulation(
        stock_price=172.13,
        risk_free_rate=0.03577,
        dividend_yield=0.03202,
        volatility=0.2356,
    )
    simulation.simulation()


if __name__ == "__main__":
    main()
