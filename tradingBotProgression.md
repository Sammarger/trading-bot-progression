# Samuel Margerison - Algorithmic Trading Bots

This project documents my journey in learning about the QuantConnect API and it's features.

## Introductory Bot Build

The `intro-bot` buys SPY when not already invested and the current time meets or exceeds a predefined entry time, calculating the number of shares to purchase based on available cash and current price. It sells SPY if the current price is either 10% above or 10% below the entry price, resetting the next entry time after selling. The algorithm operates from February 3, 2023, to February 3, 2024, with an initial cash allocation of $100,000, using Interactive Brokers as the brokerage model under a margin account.

![alt text](screenshots/intro-bot-graph.png)

## Trailing Stop Loss Build
