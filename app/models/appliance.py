from app.data.data_loader import load_appliances


class Appliance:

    def __init__(self, name: str, power_rating_w: float, quantity: int,
                 hours_per_day: float):
        self.name = name
        self.power_rating_w = power_rating_w
        self.quantity = quantity
        self.hours_per_day = hours_per_day

    def calculate_daily_energy(self) -> float:
        return (self.power_rating_w * self.quantity * self.hours_per_day) / 1000

    def calculate_monthly_energy(self, days_in_period: int = 30) -> float:
        return self.calculate_daily_energy() * days_in_period

    @classmethod
    def from_name(cls, name: str, quantity: int,
                  hours_per_day: float = None) -> "Appliance":
        rows = load_appliances()
        match = next((r for r in rows if r["name"] == name), None)
        if match is None:
            raise ValueError(
                f"Unknown appliance: {name!r}. Not found in appliances.csv "
                f"— use the normal Appliance(...) constructor for custom "
                f"appliances instead of from_name()."
            )
        return cls(
            name=match["name"],
            power_rating_w=match["default_watts"],
            quantity=quantity,
            hours_per_day=hours_per_day if hours_per_day is not None
            else match["typical_hours_per_day"],
        )

    def __repr__(self) -> str:
        return (f"<Appliance {self.name!r} x{self.quantity} "
                f"{self.power_rating_w}W {self.hours_per_day}h/day>")
