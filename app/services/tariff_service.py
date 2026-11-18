from app.data.data_loader import load_tariffs


class TariffService:

    def __init__(self, utility: str = "ECG", customer_category: str = "Residential"):
        self.utility = utility
        self.customer_category = customer_category
        self.tariff_rows = load_tariffs()
        self.bands = self._select_bands()

    def _select_bands(self) -> list:
        bands = [
            row for row in self.tariff_rows
            if row["utility"] == self.utility
            and row["customer_category"] == self.customer_category
        ]
        bands.sort(key=lambda r: r["min_kwh"])
        if not bands:
            raise ValueError(
                f"No tariff bands for utility={self.utility!r}, "
                f"category={self.customer_category!r}"
            )
        return bands

    def get_applicable_tariff(self, monthly_consumption_kwh: float) -> float:
        for band in self.bands:
            if band["min_kwh"] <= monthly_consumption_kwh <= band["max_kwh"]:
                return band["rate_ghs_per_kwh"]
        return self.bands[-1]["rate_ghs_per_kwh"]

    def get_marginal_rate(self, monthly_consumption_kwh: float) -> float:
        return self.get_applicable_tariff(monthly_consumption_kwh)

    def calculate_monthly_cost(self, monthly_consumption_kwh: float) -> float:
        if monthly_consumption_kwh <= 0:
            return 0.0

        remaining = monthly_consumption_kwh
        total = 0.0
        previous_ceiling = 0.0

        for band in self.bands:
            if remaining <= 0:
                break
            band_width = band["max_kwh"] - previous_ceiling
            units_in_band = min(remaining, band_width)
            total += units_in_band * band["rate_ghs_per_kwh"]
            remaining -= units_in_band
            previous_ceiling = band["max_kwh"]

        if remaining > 0:
            total += remaining * self.bands[-1]["rate_ghs_per_kwh"]

        return total

    def calculate_annual_cost(self, annual_consumption_kwh: float) -> float:
        if annual_consumption_kwh <= 0:
            return 0.0
        return self.calculate_monthly_cost(annual_consumption_kwh / 12.0) * 12.0

    def effective_rate(self, annual_consumption_kwh: float) -> float:
        if annual_consumption_kwh <= 0:
            return 0.0
        return self.calculate_annual_cost(annual_consumption_kwh) / annual_consumption_kwh

    def breakdown(self, monthly_consumption_kwh: float) -> dict:
        remaining = monthly_consumption_kwh
        previous_ceiling = 0.0
        lines = []
        total = 0.0

        for band in self.bands:
            if remaining <= 0:
                break
            band_width = band["max_kwh"] - previous_ceiling
            units = min(remaining, band_width)
            subtotal = units * band["rate_ghs_per_kwh"]
            lines.append({
                "band": f"{int(previous_ceiling)}-{int(band['max_kwh'])} kWh",
                "units": round(units, 2),
                "rate": band["rate_ghs_per_kwh"],
                "subtotal": round(subtotal, 2),
            })
            total += subtotal
            remaining -= units
            previous_ceiling = band["max_kwh"]

        return {
            "monthly_kwh": round(monthly_consumption_kwh, 2),
            "total_cost": round(total, 2),
            "effective_rate": round(total / monthly_consumption_kwh, 4)
            if monthly_consumption_kwh else 0.0,
            "marginal_rate": self.get_marginal_rate(monthly_consumption_kwh),
            "bands": lines,
        }
