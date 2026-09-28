"""Small Tkinter UI for ecommerce campaign profit math."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import tkinter as tk
from tkinter import messagebox, ttk


MONEY = Decimal("0.01")
RATIO = Decimal("0.01")


@dataclass
class ProfitInputs:
    selling_price: Decimal
    product_cost: Decimal
    other_costs: Decimal
    ad_spend: Decimal
    orders: Decimal


@dataclass
class ProfitResults:
    revenue: Decimal
    total_cost_per_order: Decimal
    profit_before_ads_per_order: Decimal
    roas: Decimal | None
    cpa: Decimal
    actual_profit_per_order: Decimal
    final_profit: Decimal
    break_even_roas: Decimal | None
    max_break_even_ad_spend: Decimal


def calculate_profit(data: ProfitInputs) -> ProfitResults:
    revenue = data.selling_price * data.orders
    total_cost_per_order = data.product_cost + data.other_costs
    profit_before_ads = data.selling_price - total_cost_per_order
    roas = revenue / data.ad_spend if data.ad_spend else None
    cpa = data.ad_spend / data.orders
    actual_profit = profit_before_ads - cpa
    final_profit = (profit_before_ads * data.orders) - data.ad_spend
    break_even_roas = None

    if profit_before_ads > 0:
        # Break-even ROAS means revenue divided by the maximum ad spend.
        break_even_roas = data.selling_price / profit_before_ads

    return ProfitResults(
        revenue=revenue,
        total_cost_per_order=total_cost_per_order,
        profit_before_ads_per_order=profit_before_ads,
        roas=roas,
        cpa=cpa,
        actual_profit_per_order=actual_profit,
        final_profit=final_profit,
        break_even_roas=break_even_roas,
        max_break_even_ad_spend=profit_before_ads * data.orders,
    )


def parse_decimal(value: str, field_name: str) -> Decimal:
    cleaned = value.replace(",", "").strip()

    if not cleaned:
        raise ValueError(f"{field_name} is required.")

    try:
        number = Decimal(cleaned)
    except InvalidOperation as error:
        raise ValueError(f"{field_name} must be a number.") from error

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return number


def money(value: Decimal) -> str:
    return f"{value.quantize(MONEY, rounding=ROUND_HALF_UP):,}"


def ratio(value: Decimal | None) -> str:
    if value is None:
        return "No ad spend"
    return str(value.quantize(RATIO, rounding=ROUND_HALF_UP))


class ProfitCalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ecommerce Profit Calculator")
        self.root.geometry("620x620")
        self.root.minsize(560, 560)

        self.inputs: dict[str, tk.StringVar] = {
            "selling_price": tk.StringVar(value="2500"),
            "product_cost": tk.StringVar(value="1200"),
            "other_costs": tk.StringVar(value="300"),
            "ad_spend": tk.StringVar(value="10000"),
            "orders": tk.StringVar(value="20"),
        }
        self.outputs: dict[str, tk.StringVar] = {}

        self.build_ui()
        self.calculate()

    def build_ui(self):
        self.root.configure(bg="#d8dde5")

        header = tk.Frame(self.root, bg="#4267a9")
        header.pack(fill="x")
        tk.Label(
            header,
            text="Ecommerce Profit Calculator",
            bg="#4267a9",
            fg="white",
            font=("Segoe UI", 16, "bold"),
            padx=18,
            pady=12,
        ).pack(anchor="w")

        shell = tk.Frame(self.root, bg="#d8dde5", padx=18, pady=18)
        shell.pack(fill="both", expand=True)

        input_panel = self.panel(shell, "Inputs")
        input_panel.pack(fill="x", pady=(0, 12))

        fields = [
            ("Selling price per order", "selling_price"),
            ("Product cost per order", "product_cost"),
            ("Other costs per order", "other_costs"),
            ("Total ad spend", "ad_spend"),
            ("Number of orders", "orders"),
        ]

        for row, (label, key) in enumerate(fields):
            ttk.Label(input_panel, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(input_panel, textvariable=self.inputs[key], width=22).grid(
                row=row, column=1, sticky="ew", pady=4
            )

        input_panel.columnconfigure(1, weight=1)

        button_row = tk.Frame(shell, bg="#d8dde5")
        button_row.pack(fill="x", pady=(0, 12))
        ttk.Button(button_row, text="Calculate", command=self.calculate).pack(side="left")
        ttk.Button(button_row, text="Sample", command=self.fill_sample).pack(side="left", padx=8)
        ttk.Button(button_row, text="Clear", command=self.clear).pack(side="left")

        result_panel = self.panel(shell, "Results")
        result_panel.pack(fill="both", expand=True)

        result_fields = [
            ("Total revenue", "revenue"),
            ("Total cost per order", "total_cost_per_order"),
            ("Profit before ads per order", "profit_before_ads_per_order"),
            ("ROAS", "roas"),
            ("CPA", "cpa"),
            ("Actual profit per order after ads", "actual_profit_per_order"),
            ("Final profit after ads", "final_profit"),
            ("Break-even ROAS", "break_even_roas"),
            ("Max break-even ad spend", "max_break_even_ad_spend"),
        ]

        for row, (label, key) in enumerate(result_fields):
            self.outputs[key] = tk.StringVar(value="-")
            ttk.Label(result_panel, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Label(result_panel, textvariable=self.outputs[key], font=("Segoe UI", 10, "bold")).grid(
                row=row, column=1, sticky="e", pady=4
            )

        result_panel.columnconfigure(1, weight=1)

        note = (
            "Break-even ROAS = Selling Price / Profit Before Ads. "
            "Example: 2500 / 1000 = 2.5"
        )
        tk.Label(shell, text=note, bg="#d8dde5", fg="#49576a", wraplength=560).pack(anchor="w", pady=(12, 0))

    def panel(self, parent: tk.Widget, title: str) -> ttk.LabelFrame:
        panel = ttk.LabelFrame(parent, text=title, padding=14)
        return panel

    def read_inputs(self) -> ProfitInputs:
        data = ProfitInputs(
            selling_price=parse_decimal(self.inputs["selling_price"].get(), "Selling price"),
            product_cost=parse_decimal(self.inputs["product_cost"].get(), "Product cost"),
            other_costs=parse_decimal(self.inputs["other_costs"].get(), "Other costs"),
            ad_spend=parse_decimal(self.inputs["ad_spend"].get(), "Ad spend"),
            orders=parse_decimal(self.inputs["orders"].get(), "Orders"),
        )

        if data.selling_price <= 0:
            raise ValueError("Selling price must be greater than zero.")
        if data.orders <= 0:
            raise ValueError("Orders must be greater than zero.")

        return data

    def calculate(self):
        try:
            results = calculate_profit(self.read_inputs())
        except ValueError as error:
            messagebox.showerror("Check inputs", str(error))
            return

        self.outputs["revenue"].set(money(results.revenue))
        self.outputs["total_cost_per_order"].set(money(results.total_cost_per_order))
        self.outputs["profit_before_ads_per_order"].set(money(results.profit_before_ads_per_order))
        self.outputs["roas"].set(ratio(results.roas))
        self.outputs["cpa"].set(money(results.cpa))
        self.outputs["actual_profit_per_order"].set(money(results.actual_profit_per_order))
        self.outputs["final_profit"].set(money(results.final_profit))
        self.outputs["break_even_roas"].set(ratio(results.break_even_roas))
        self.outputs["max_break_even_ad_spend"].set(money(results.max_break_even_ad_spend))

    def fill_sample(self):
        sample = {
            "selling_price": "2500",
            "product_cost": "1200",
            "other_costs": "300",
            "ad_spend": "10000",
            "orders": "20",
        }

        for key, value in sample.items():
            self.inputs[key].set(value)

        self.calculate()

    def clear(self):
        for value in self.inputs.values():
            value.set("")

        for value in self.outputs.values():
            value.set("-")


def main():
    root = tk.Tk()
    ProfitCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
