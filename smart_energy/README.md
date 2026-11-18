# Smart Energy Source Comparison System

Compare any two energy sources — grid, solar, small wind, biomass, hydropower — against a household's actual appliance load, on cost, carbon and reliability.

# Project Structure 
The system uses OOP (object-oriented design): an abstract EnergySource class defines a 
common interface (energy, cost, maintenance, and emissions calculations), implemented 
separately by five subclasses; GridElectricity, Solar, Wind, Biomass, and Hydropower. This way, 
the comparison engine can treat any two sources identically without needing to know their 
internal formulas. A Flask backend was used to connect this logic through a REST API, through 
a browser-based frontend made with html, css and javascript where the user builds their energy 
profile and views results. We leveraged OpenStreetMap and Open-meteo APIs in our “services” 
module for validating locations and fetching location-specific data used for precise calculation 
using predefined data files. Our “recommendation” module scores and ranks sources against the 
selected user preferences and displays the one with the best that aligns with the selected 
preference. 

# Likely Applications 
The core use case is residential energy planning in Ghana, but this project structure generalizes 
to several adjacent scenarios: 

● Household energy decisions: homeowners evaluating whether solar, wind, or another 
alternative is worth the upfront investment given their actual appliance usage, rather than a 
generic national average. 
● Small business and institutional planning: Guesthouses, schools, or small workshops with 
predictable daily loads assessing backup or supplementary generation options. 
● NGO and rural electrification programs: Screening which renewable source best fits a 
community's location and consumption profile before committing to installation. 
● Educational and policy use: Demonstrating how tariff structure, climate data, and system 
lifespan interact to determine payback period for public communication and awareness around 
Ghana's energy transition. 
● Extension to other West African contexts: The tariff and emissions data could be extended 
beyond Ghana and the underlying logic would apply directly to neighboring countries with 
similar climate conditions.


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

