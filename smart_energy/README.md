# Smart Energy Source Comparison System

Compare any two energy sources — grid, solar, small wind, biomass, hydropower — against a household's actual appliance load, on cost, carbon and reliability.

**Status: architecture skeleton.** Every method is stubbed with a docstring, a formula and a hint. Nothing has logic yet. That is the point — the contract is fixed before anyone writes code, so five people cannot produce five incompatible guesses at what `calculate_energy()` returns.

---

## Get running in five minutes

```bash
git clone <your-repo-url>
cd smart_energy
pip install -r requirements.txt

# Confirm the data layer works — this one IS implemented
python3 -m app.data.data_loader
```

You should see all seven data files parse. If you get `FileNotFoundError`, you are in the wrong directory: every command runs from `smart_energy/`.

---

## How to run any module on its own

Every module has a `__main__` block that exercises its own class with sample values and prints the results.

```bash
python3 -m app.models.appliance
python3 -m app.calculators.financial_calculator
python3 -m app.services.tariff_service
```

**Use `-m` and the dotted path.** Running `python3 app/models/appliance.py` fails with `No module named 'app'` — Python needs the package root on its path, which `-m` handles.

Unimplemented methods report `not yet implemented` rather than crashing, so the whole package stays runnable from day one. Where a method has a hand-checkable answer, the self-test prints `[OK]` or `[WRONG — expected X]`.

---

## Module ownership

Put your name against a row. An owner still gets help, but pull requests touching their file need their review.

| File | Owns | Stage | Assignee |
|---|---|---|---|
| `app/models/appliance.py` | `Appliance` | 1 | ______ |
| `app/models/energy_profile.py` | `EnergyProfile` | 1 | ______ |
| `app/models/energy_source.py` | Base class + 5 subclasses | 1 | ______ |
| `app/services/weather_service.py` | Open-Meteo API | 2 | ______ |
| `app/services/location_service.py` | Geocoding | 2 | ______ |
| `app/services/tariff_service.py` | Banded tariffs | 2 | ______ |
| `app/calculators/energy_calculator.py` | Supply vs demand | 3 | ______ |
| `app/calculators/financial_calculator.py` | Cost, **recursive payback** | 3 | ______ |
| `app/calculators/carbon_calculator.py` | Emissions | 3 | ______ |
| `app/calculators/comparison_engine.py` | Orchestration | 4 | ______ |
| `app/recommendations/recommendation_engine.py` | Scoring | 5 | ______ |
| `app/routes/api.py` + frontend | Flask + HTML | any | ______ |
| `app/data/data_loader.py` | *already done* | — | — |

`energy_source.py` is by far the biggest file. Consider splitting it: one person owns the abstract base class and Grid + Solar, another takes Wind, Biomass and Hydropower.

## Build order

Bottom-up, so nobody waits on a stub to become real:

1. **Models** — no dependencies. Start here.
2. **Services** — parallel with stage 1.
3. **Calculators** — need 1 and 2.
4. **ComparisonEngine** — needs all of 3. Build last.
5. **RecommendationEngine** — needs 4's output shape.

**Routes and frontend can start immediately** and should. They only depend on the *shape* of the classes, not on the maths working. Whoever owns Flask should never be idle waiting for a calculator.

---

## Git workflow

```bash
git checkout -b feature/kwame-financial-calculator
# ... implement, test with python3 -m app.calculators.financial_calculator
git add app/calculators/financial_calculator.py
git commit -m "Implement payback recursion and LCOE"
git push -u origin feature/kwame-financial-calculator
# then open a pull request on GitHub
```

Rules that actually prevent lost work:

- **Never commit directly to `main`.** One person force-pushing over `main` on the night before submission has ruined more group projects than any bug.
- **One teammate reviews before merge.** Even a thirty-second look catches wrong units and broken signatures.
- **`git pull` before you start each session.** Merge conflicts are trivial when they are two hours old and miserable when they are five days old.
- **Never edit someone else's file on `main`** — open a PR and tag them.
- Commit `.gitignore` first, before anything else. `__pycache__` folders in a diff make review painful.

**Colab is for scratch experiments only** — checking an Open-Meteo response shape, sanity-testing a hydro formula. Never let the real implementation live there: it cannot import across files, has no branching, and simultaneous edits silently overwrite each other with no diff.

---

## Rubric map — where each requirement lives

| Requirement | Where | Note |
|---|---|---|
| **OOP: abstraction** | `EnergySource(ABC)` | `@abstractmethod` makes Python enforce it |
| **OOP: inheritance** | 5 subclasses of `EnergySource` | shared `__init__`, `calculate_emissions`, `lifetime_cost` |
| **OOP: polymorphism** | `ComparisonEngine.compare()` | same call, five physics implementations, zero `if source ==` |
| **OOP: encapsulation** | `Appliance`, `EnergyProfile` | validation in `__init__`; internals hidden behind methods |
| **Files** | `data_loader.py` + 7 data files | real parsing, not a docstring describing it |
| **Collections** | list (appliances), dict (factors), set (`get_appliance_categories`), tuple (coordinates, `get_largest_consumers`) | all four types |
| **Loops** | `calculate_total_energy`, `monthly_breakdown`, tariff bands | |
| **Conditionals: if/else** | validation throughout | |
| **Conditionals: match-case** | `set_direct_consumption`, `Wind.power_output`, `recommend` | **needs Python 3.10+** |
| **Conditionals: ternary** | `is_renewable`, `__str__` methods | |
| **Functions** | every module | |
| **2+ new libraries** | Flask, requests | in `requirements.txt` |
| **API data fetching** | `WeatherService` → Open-Meteo | no API key required |
| **Recursion** | `FinancialCalculator.calculate_payback_period` | **must stay recursive** |
| **GUI (HTML)** | Flask + `app/templates/index.html` | |

Check your Python version before starting — `match/case` needs 3.10 or newer:

```bash
python3 --version
```

---

## Things that will cost you marks if nobody catches them

**Tariff rates in `data/tariffs.csv` are illustrative.** Look up the current published PURC residential schedule, update the file, cite the source and effective date. Quoting invented tariffs as fact is exactly the sort of thing a marker checks.

**Renewables are not zero-carbon.** `emission_factors.csv` uses lifecycle factors, which is why solar reads 0.045 and not 0. If your report claims solar is carbon-free, the model contradicts you.

**Every simplification must be declared.** The stubs flag them where they occur — no discounting in LCOE, mean wind speed instead of a Weibull distribution, straight-line distance instead of haversine, even monthly consumption. A stated simplification is good engineering; an unstated one is an error.

**The recursion must stay recursive.** If someone flattens `calculate_payback_period` into a `while` loop during cleanup, you lose a rubric item. The self-test in that file checks for a self-call and warns you.

---

## Project structure

```
smart_energy/
├── run.py                    entry point — python3 run.py
├── requirements.txt
├── data/                     7 comma-separated data files
├── tests/test_data/          fixtures with round numbers
└── app/
    ├── config.py             all settings; API keys are ""
    ├── data/data_loader.py   IMPLEMENTED
    ├── models/               Appliance, EnergyProfile, EnergySource
    ├── services/             weather, location, tariff
    ├── calculators/          energy, financial, carbon, comparison
    ├── recommendations/      scoring and ranking
    ├── routes/api.py         Flask endpoints
    ├── templates/            index.html goes here
    └── static/               css/js go here
```

**On `.csv` vs `.txt`:** identical to Python. "CSV" just means comma-separated values; nothing treats the extension specially. `data_loader.py` uses the `csv` module with a commented manual `open()`/`.split(',')` alternative if your class hasn't covered it. The self-test parses the same content as `.csv` and `.txt` and proves the results match.
