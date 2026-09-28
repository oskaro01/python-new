# Ecommerce Profit Calculator

Tiny side quest: a Python-only UI calculator for ecommerce campaign profit.

Run it from the repository root:

```powershell
python my_python_work/side_quests/ecommerce_profit_calculator/app.py
```

No install is needed. It uses Python's built-in `tkinter` UI library.

## Inputs

```text
S = Selling price per order
C = Product cost per order
O = Other costs per order
A = Total ad spend
N = Number of orders
```

## Main Formula

```text
Final Profit = (S - C - O) * N - A
```

Example:

```text
(2500 - 1200 - 300) * 20 - 10000
= 1000 * 20 - 10000
= 10000
```

## Useful Metrics

```text
Revenue = S * N
Total cost per order = C + O
Profit before ads per order = S - (C + O)
ROAS = Revenue / Ad Spend
CPA = Ad Spend / Orders
Actual profit per order = Profit before ads - CPA
```

## Break-even ROAS

For ROAS, break-even means:

```text
Revenue / Ad Spend = break-even point
```

The maximum ad spend per order is the profit before ads:

```text
P = S - (C + O)
```

So:

```text
Break-even ROAS = S / P
```

Example:

```text
S = 2500
P = 1000
Break-even ROAS = 2500 / 1000 = 2.5
```

If your ROAS is above `2.5`, this sample campaign is profitable. If it is
below `2.5`, it is losing money.

## Why This Is Outside Django

This is a small Python practice tool, not part of the dictionary web app.
Later, the same formula logic could be reused inside a web dashboard.
