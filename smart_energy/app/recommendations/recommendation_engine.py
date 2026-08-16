"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/recommendations/recommendation_engine.py  -  Scoring & Verdict
========================================================================
  Owner:  ____________________
  Build order: STAGE 5 (needs ComparisonEngine's output shape)

  WHAT THIS CLASS DOES
    Turns a comparison dictionary into an answer: which source, why,
    and how confident.

  THE HARD PART IS NOT CODE - IT IS JUSTIFYING THE WEIGHTS
    Deciding that cost is worth 40% and carbon 30% is a VALUE
    JUDGEMENT, not a calculation. Two defensible weightings can pick
    different winners from identical data.

    So: make the weights visible in the UI, let the user pick a
    priority, and state plainly in your report that the ranking depends
    on them. An engine that hides its weights behind a confident
    "RECOMMENDED" badge is doing something dishonest, however good the
    arithmetic underneath is.

  RUBRIC COVERAGE
    [x] Collections (weight dicts, score lists, tuples)
    [x] Conditionals - if/else, match-case, ternary
    [x] Loops   [x] Functions

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.recommendations.recommendation_engine
========================================================================
"""


class RecommendationEngine:
    """Scores and ranks sources from a comparison result."""

    # Four weighting profiles. Each dict MUST sum to 1.0 - add an
    # assertion in __init__ if you want the guarantee enforced.
    #
    # These numbers are OUR choices. Argue for them in the report or
    # change them - but do not present them as objective.
    PRIORITY_WEIGHTS = {
        "cost": {"cost": 0.60, "carbon": 0.10,
                 "reliability": 0.20, "independence": 0.10},
        "environment": {"cost": 0.15, "carbon": 0.55,
                        "reliability": 0.15, "independence": 0.15},
        "reliability": {"cost": 0.20, "carbon": 0.10,
                        "reliability": 0.55, "independence": 0.15},
        "balanced": {"cost": 0.35, "carbon": 0.25,
                     "reliability": 0.25, "independence": 0.15},
    }

    # How dependable each source is in practice, 0-1. Grid scores badly
    # because of outages; hydro and biomass score well because they are
    # dispatchable; solar and wind sit in between because they are
    # intermittent without storage.
    #
    # These are ESTIMATES. If you can find published Ghanaian
    # reliability data, use it and cite it - that would turn a guess
    # into evidence and noticeably strengthen the report.
    RELIABILITY_SCORES = {
        "grid": 0.62,
        "solar": 0.75,
        "wind": 0.45,
        "biomass": 0.85,
        "hydro": 0.88,
    }

    def __init__(self, priority="balanced"):
        """
        Args:
            priority (str): a key of PRIORITY_WEIGHTS

        Raises:
            ValueError: for an unknown priority, listing the valid ones.

        HINT
            Validate, then store both self.priority and
            self.weights = self.PRIORITY_WEIGHTS[priority].
        """
        # [IMPLEMENT ME]  (~6 lines)
        raise NotImplementedError("RecommendationEngine.__init__")

    def normalise(self, value, best, worst, higher_is_better=True):
        """
        Scale a raw value onto 0-100.

        Args:
            value (float): the figure to score
            best, worst (float): the range's endpoints
            higher_is_better (bool): False for cost and emissions, where
                lower wins

        Returns:
            float: 0-100

        WHY NORMALISATION IS NECESSARY
            You cannot add GHS 45,000 to 878 kg CO2 to 92% coverage -
            different units, wildly different magnitudes. Whichever has
            the biggest raw numbers would dominate any weighted sum.
            Mapping everything to 0-100 first is what makes the weights
            mean what they claim to mean.

        FORMULA
            higher_is_better: (value - worst) / (best - worst) * 100
            else:             (worst - value) / (worst - best) * 100

        GUARDS
            best == worst -> return 50.0 (no basis to prefer either).
            Clamp the result into [0, 100] - a value outside the given
            range would otherwise score above 100 or below 0.
        """
        # [IMPLEMENT ME]  (~12 lines)
        raise NotImplementedError("RecommendationEngine.normalise")

    def score_source(self, source_data, comparison_ranges):
        """
        Weighted 0-100 score for one source.

        Args:
            source_data (dict): one side of comparison["sources"]
            comparison_ranges (dict): the best/worst values across BOTH
                sources for each dimension, so scores are relative to
                what was actually on offer

        Returns:
            dict: {"total": float,
                   "components": {"cost": ..., "carbon": ...,
                                  "reliability": ..., "independence": ...}}

        THE FOUR DIMENSIONS
            cost         - lifetime cost, LOWER is better
            carbon       - lifetime emissions, LOWER is better
            reliability  - RELIABILITY_SCORES x coverage, HIGHER better
            independence - the EnergyCalculator independence score

        HINT
            Normalise each dimension, multiply by its weight, sum.
            Return the components too - a total with no breakdown is
            unexplainable, and "why did it pick that?" is the first
            question anyone will ask in your demo.
        """
        # [IMPLEMENT ME]  (~22 lines)
        raise NotImplementedError("RecommendationEngine.score_source")

    def recommend(self, comparison):
        """
        THE MAIN METHOD. Pick a winner from a comparison result.

        Args:
            comparison (dict): output of ComparisonEngine.compare()

        Returns:
            dict:
                winner            (str)  source name
                winner_key        (str)
                scores            (dict) {"a": {...}, "b": {...}}
                margin            (float) points between them
                confidence        (str)  "high"/"moderate"/"marginal"
                priority          (str)
                weights           (dict)  the weighting used - EXPOSED
                                          deliberately, never hidden
                reasons           (list[str]) plain-language points
                caveats           (list[str]) honest limitations

        *** confidence IS A match-case OPPORTUNITY ***
            margin >= 20 -> "high"
            margin >= 8  -> "moderate"
            else         -> "marginal"

        THE caveats FIELD IS NOT OPTIONAL DECORATION
            Populate it properly. Examples worth generating:
              - "Weather data unavailable; solar output is a seasonal
                 estimate." (when context data_source == "estimated")
              - "Wind speeds inland in Ghana are typically below this
                 turbine's rated speed."
              - "Hydropower requires a suitable stream on the property."
              - "Tariff rates are illustrative; verify against PURC."
              - "Scores depend on the weighting shown; a different
                 priority may favour the other option."

            A tool that states its limits is more useful, and more
            credible in a viva, than one that projects false certainty.

        WHEN THE MARGIN IS TINY
            Say so. "These two are close - the decision may come down
            to factors outside this model" is a legitimate output and a
            better one than picking a winner by 0.3 points and calling
            it a recommendation.
        """
        # [IMPLEMENT ME]  (~40 lines)
        raise NotImplementedError("RecommendationEngine.recommend")

    def generate_reasons(self, winner_data, loser_data, winner_score,
                         loser_score):
        """
        Plain-language justification lines.

        Returns:
            list[str]

        WRITE FOR A HOMEOWNER, NOT A MARKER
            Bad:  "Lifetime cost differential: -42150.00 GHS"
            Good: "Saves about GHS 42,000 over 25 years compared with
                   staying on the grid."

        HINT
            Compare each dimension in turn; append a sentence only where
            the difference is material (say, more than 10%). Three sharp
            reasons beat eight trivial ones.

        FORMATTING TIP
            Thousands separators help a lot:
                "GHS {:,.0f}".format(42150)   ->  "GHS 42,150"
        """
        # [IMPLEMENT ME]  (~20 lines)
        raise NotImplementedError("RecommendationEngine.generate_reasons")

    def rank_all(self, comparisons):
        """
        Rank several sources at once.

        Args:
            comparisons (list[dict]): output of
                ComparisonEngine.compare_all_sources()

        Returns:
            list[tuple]: [(rank, source_key, score), ...] sorted best
                first - tuples because the triple is fixed and ordered.

        OPTIONAL - build after recommend() works.
        """
        # [IMPLEMENT ME]  (~12 lines)
        raise NotImplementedError("RecommendationEngine.rank_all")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("RECOMMENDATION ENGINE SELF-TEST")
    print("=" * 62)

    def check(label, fn, expected=None):
        try:
            result = fn()
            note = ""
            if expected is not None and isinstance(result, (int, float)):
                note = "  [OK]" if abs(result - expected) < 0.01 else \
                       "  [WRONG - expected " + str(expected) + "]"
            print("  " + label.ljust(36) + str(result) + note)
        except NotImplementedError:
            print("  " + label.ljust(36) + "not yet implemented")
        except Exception as e:
            print("  " + label.ljust(36) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("\n[0] Weights must each sum to 1.0")
    for name, weights in RecommendationEngine.PRIORITY_WEIGHTS.items():
        total = sum(weights.values())
        flag = "[OK]" if abs(total - 1.0) < 0.001 else "[PROBLEM]"
        print("  " + name.ljust(14) + str(round(total, 3)) + "  " + flag)

    print("\n[1] Normalisation")
    try:
        eng = RecommendationEngine("balanced")
        check("cost 20000, best 10000 worst 50000",
              lambda: eng.normalise(20000, 10000, 50000, False), 75.0)
        check("cost at the best end -> 100",
              lambda: eng.normalise(10000, 10000, 50000, False), 100.0)
        check("cost at the worst end -> 0",
              lambda: eng.normalise(50000, 10000, 50000, False), 0.0)
        check("coverage 90, best 100 worst 50",
              lambda: eng.normalise(90, 100, 50, True), 80.0)
        check("best == worst -> 50",
              lambda: eng.normalise(30, 30, 30, True), 50.0)
        check("out of range -> clamped, not >100",
              lambda: eng.normalise(5000, 10000, 50000, False), 100.0)
    except NotImplementedError:
        print("  __init__ not yet implemented")

    print("\n[2] Priority validation")
    for p in ["cost", "environment", "reliability", "balanced"]:
        try:
            RecommendationEngine(p)
            print("  " + p.ljust(16) + "[OK]")
        except NotImplementedError:
            print("  " + p.ljust(16) + "not yet implemented")
        except Exception as e:
            print("  " + p.ljust(16) + "ERROR: " + type(e).__name__)
    try:
        RecommendationEngine("vibes")
        print("  unknown priority [PROBLEM] no error raised")
    except ValueError:
        print("  unknown priority [OK] ValueError")
    except NotImplementedError:
        print("  unknown priority not yet implemented")

    print("\n[3] Full recommendation (needs ComparisonEngine)")
    try:
        from app.models.appliance import Appliance
        from app.models.energy_profile import EnergyProfile
        from app.calculators.comparison_engine import ComparisonEngine

        profile = EnergyProfile("Berekuso")
        profile.add_appliance(Appliance("Refrigerator", 150, 1, 24))
        profile.add_appliance(Appliance("Ceiling Fan", 75, 3, 10))

        comparison = ComparisonEngine().compare(profile, "grid", "solar",
                                                location="Berekuso")
        for priority in ["cost", "environment", "balanced"]:
            try:
                rec = RecommendationEngine(priority).recommend(comparison)
                print("\n  priority = " + priority)
                print("    winner    :", rec.get("winner"))
                print("    confidence:", rec.get("confidence"))
                print("    reasons   :", rec.get("reasons"))
                print("    caveats   :", rec.get("caveats"))
            except NotImplementedError:
                print("  priority = " + priority + " -> blocked")

        print("\n  IMPORTANT: if the winner CHANGES between priorities,")
        print("  that is the engine working correctly, not a bug. Show")
        print("  exactly that in your demo - it proves the weights")
        print("  actually drive the outcome.")

    except NotImplementedError as e:
        print("  blocked: " + e.__str__())
    except Exception as e:
        print("  ERROR:", type(e).__name__, e)

    print("\n" + "=" * 62)
