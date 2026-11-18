from typing import Dict, Any, List


class RecommendationEngine:

    priority_weights = {
        "cost": {"financial": 0.6, "environmental": 0.1, "payback": 0.3},
        "payback": {"financial": 0.2, "environmental": 0.1, "payback": 0.7},
        "carbon": {"financial": 0.2, "environmental": 0.7, "payback": 0.1},
        "independence": {"financial": 0.3, "environmental": 0.3, "payback": 0.4},
        "balanced": {"financial": 0.34, "environmental": 0.33, "payback": 0.33},
    }

    _savings_per_point_ghs = 500
    _emissions_per_point_kg = 500

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
        return max(low, min(high, value))

    def calculate_score(self, comparison_result: Dict[str, Any],
                          priority: str) -> float:
        weights = self.priority_weights.get(priority, self.priority_weights["balanced"])

        lifetime_savings = comparison_result.get("lifetime_savings_ghs", 0)
        payback_years = comparison_result.get("payback_years", float("inf"))


        emissions_kg = comparison_result.get(
            "total_emissions_kg", comparison_result.get("emissions_kg", 0)
        )


        coverage = comparison_result.get("coverage_percent", 100.0)
        coverage_multiplier = max(0.0, min(coverage / 100.0, 1.0))

        financial_score = self._clamp(lifetime_savings / self._savings_per_point_ghs)

        if payback_years == float("inf"):
            payback_score = 0.0
        else:
            payback_score = self._clamp(10 - payback_years)

        environmental_score = self._clamp(10 - (emissions_kg / self._emissions_per_point_kg))

        overall = (
            financial_score * weights["financial"]
            + environmental_score * weights["environmental"]
            + payback_score * weights["payback"]
        )
        return round(overall * coverage_multiplier, 2)

    def rank_sources(self, comparison_results: Dict[str, Any],
                       priority: str) -> List[Dict[str, Any]]:
        scored = []
        for key in ("source_a", "source_b"):
            result = comparison_results[key]
            score = self.calculate_score(result, priority)
            scored.append({"source_name": result["source_name"], "score": score})

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored

    def recommend_source(self, comparison_results: Dict[str, Any],
                           priority: str) -> Dict[str, Any]:
        ranked = self.rank_sources(comparison_results, priority)
        top = ranked[0]

        weights = self.priority_weights.get(priority, self.priority_weights["balanced"])
        dominant_factor = max(weights, key=weights.get)
        factor_labels = {
            "financial": "long-term cost savings",
            "environmental": "lower carbon emissions",
            "payback": "a faster payback period",
        }

        if len(ranked) > 1 and ranked[0]["score"] == ranked[1]["score"]:
            reason = (
                f"{top['source_name']} and {ranked[1]['source_name']} scored "
                f"equally for this profile under a '{priority}' priority — "
                f"consider other factors like installation feasibility."
            )
        else:
            reason = (
                f"{top['source_name']} scored highest ({top['score']}/10) for "
                f"this usage profile under a '{priority}' priority, driven "
                f"mainly by {factor_labels[dominant_factor]}."
            )

        return {
            "recommended": top["source_name"],
            "reason": reason,
            "scores": ranked,
        }
