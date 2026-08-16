"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/data/data_loader.py  -  File Reading Layer
========================================================================
  Owner:  ____________________
  Status: *** FULLY IMPLEMENTED - DO NOT STUB THIS OUT ***

  WHY THIS FILE IS ALREADY WRITTEN
    Every other module depends on this one. If it were left as a stub,
    nobody could test anything. It is also shared boilerplate - there is
    no learning value in five people each writing their own CSV reader.

  RUBRIC COVERAGE
    [x] Files          - really opens and parses the files in data/
    [x] Collections    - returns lists of dicts; builds tuples and sets
    [x] Loops          - iterates rows
    [x] Conditionals   - if/else for blank lines and missing files
    [x] Functions      - seven load_* functions
    [x] Library import - pathlib, csv

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.data.data_loader
========================================================================
"""

import csv
from pathlib import Path

# ----------------------------------------------------------------------
#  WHERE THE DATA LIVES
#
#  __file__                     -> .../smart_energy/app/data/data_loader.py
#  Path(__file__).resolve()     -> absolute version of the above
#  .parent                      -> .../smart_energy/app/data
#  .parent.parent               -> .../smart_energy/app
#  .parent.parent.parent        -> .../smart_energy      <-- project root
#
#  Building the path this way means the app works no matter which
#  directory you launch it from. Never hardcode "C:/Users/..." here.
# ----------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _read_rows(filename, base_dir=None):
    """
    Read one delimited data file and return its rows as a list of dicts.

    This is the single place where file reading actually happens - every
    public load_* function below is a thin wrapper around it.

    Args:
        filename (str): file name only, e.g. "appliances.csv"
        base_dir (Path, optional): folder to read from. Defaults to
            data/. Tests pass tests/test_data/ here instead.

    Returns:
        list[dict]: one dict per data row, keyed by the header names.
                    All values are strings at this stage - the calling
                    function is responsible for converting numbers.

    Raises:
        FileNotFoundError: with a message naming the exact path tried,
            which saves a lot of guessing when a teammate's checkout is
            missing a file.

    ------------------------------------------------------------------
    IF YOUR CLASS HAS NOT COVERED THE csv MODULE
    ------------------------------------------------------------------
    Replace the body below with this - it behaves identically, using
    only open(), a loop, .strip() and .split(','):

        path = (base_dir or DATA_DIR) / filename
        if not path.exists():
            raise FileNotFoundError("Data file not found: " + str(path))

        rows = []
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        headers = lines[0].strip().split(",")
        for line in lines[1:]:
            line = line.strip()
            if line == "":          # skip blank lines
                continue
            values = line.split(",")
            if len(values) != len(headers):
                continue            # skip malformed lines
            row = {}
            for i in range(len(headers)):
                row[headers[i]] = values[i]
            rows.append(row)
        return rows

    CAUTION: the manual version breaks if any field itself contains a
    comma (e.g. a note reading "cheap, but noisy"). The sample data
    avoids commas inside fields precisely so both versions work.
    ------------------------------------------------------------------
    """
    path = (base_dir or DATA_DIR) / filename

    if not path.exists():
        raise FileNotFoundError(
            "Data file not found: " + str(path) +
            "\nCheck that you are running from the smart_energy/ root."
        )

    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip fully blank lines, which DictReader yields as all-None
            if any(value not in (None, "") for value in row.values()):
                rows.append(row)
    return rows


def load_appliances(base_dir=None):
    """
    Load the appliance catalogue.

    Returns:
        list[dict]: {"name": str, "category": str,
                     "default_watts": float,
                     "typical_hours_per_day": float}

    Used by: Appliance.from_name(), and the /api/appliances route that
    fills the frontend dropdown.
    """
    rows = _read_rows("appliances.csv", base_dir)
    for row in rows:
        row["default_watts"] = float(row["default_watts"])
        row["typical_hours_per_day"] = float(row["typical_hours_per_day"])
    return rows


def load_tariffs(base_dir=None, filename="tariffs.csv"):
    """
    Load the electricity tariff bands, sorted by min_kwh ascending.

    Returns:
        list[dict]: {"band_name": str, "min_kwh": float, "max_kwh": float,
                     "rate_ghs_per_kwh": float, "service_charge_ghs": float}

    NOTE ON ACCURACY: the shipped rates are illustrative for development.
    Confirm current published PURC rates before quoting any cost figure
    in your written report.

    Used by: TariffService.
    """
    rows = _read_rows(filename, base_dir)
    for row in rows:
        row["min_kwh"] = float(row["min_kwh"])
        row["max_kwh"] = float(row["max_kwh"])
        row["rate_ghs_per_kwh"] = float(row["rate_ghs_per_kwh"])
        row["service_charge_ghs"] = float(row["service_charge_ghs"])
    rows.sort(key=lambda r: r["min_kwh"])
    return rows


def load_solar_panels(base_dir=None):
    """Load the solar panel catalogue. Used by: Solar."""
    rows = _read_rows("solar_panels.csv", base_dir)
    for row in rows:
        row["rated_watts"] = float(row["rated_watts"])
        row["efficiency_percent"] = float(row["efficiency_percent"])
        row["area_m2"] = float(row["area_m2"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["lifespan_years"] = int(row["lifespan_years"])
    return rows


def load_wind_turbines(base_dir=None):
    """Load the wind turbine catalogue. Used by: Wind."""
    rows = _read_rows("wind_turbines.csv", base_dir)
    for row in rows:
        row["rated_kw"] = float(row["rated_kw"])
        row["rotor_diameter_m"] = float(row["rotor_diameter_m"])
        row["cut_in_speed_ms"] = float(row["cut_in_speed_ms"])
        row["rated_speed_ms"] = float(row["rated_speed_ms"])
        row["cut_out_speed_ms"] = float(row["cut_out_speed_ms"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["lifespan_years"] = int(row["lifespan_years"])
    return rows


def load_biomass_systems(base_dir=None):
    """Load the biomass system catalogue. Used by: Biomass."""
    rows = _read_rows("biomass_systems.csv", base_dir)
    for row in rows:
        row["rated_kw"] = float(row["rated_kw"])
        row["calorific_value_mj_per_kg"] = float(row["calorific_value_mj_per_kg"])
        row["conversion_efficiency_percent"] = float(row["conversion_efficiency_percent"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["lifespan_years"] = int(row["lifespan_years"])
    return rows


def load_hydro_systems(base_dir=None):
    """Load the hydropower system catalogue. Used by: Hydropower."""
    rows = _read_rows("hydro_systems.csv", base_dir)
    for row in rows:
        row["rated_kw"] = float(row["rated_kw"])
        row["min_head_m"] = float(row["min_head_m"])
        row["min_flow_m3s"] = float(row["min_flow_m3s"])
        row["turbine_efficiency_percent"] = float(row["turbine_efficiency_percent"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["lifespan_years"] = int(row["lifespan_years"])
    return rows


def load_emission_factors(base_dir=None, filename="emission_factors.csv"):
    """
    Load CO2 emission factors as a ready-to-use lookup dictionary.

    Returns:
        dict: {"grid": 0.380, "solar": 0.045, ...} - source key mapped
              to kg CO2 per kWh.

    Returned as a dict rather than a list because every caller looks it
    up by source name; nobody needs to iterate it in order.

    Used by: CarbonCalculator, EnergySource.calculate_emissions().
    """
    rows = _read_rows(filename, base_dir)
    factors = {}
    for row in rows:
        factors[row["source"].strip().lower()] = float(row["kg_co2_per_kwh"])
    return factors


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DATA LOADER SELF-TEST")
    print("=" * 60)
    print("Project root:", PROJECT_ROOT)
    print("Data folder :", DATA_DIR)

    loaders = [
        ("appliances", load_appliances),
        ("tariffs", load_tariffs),
        ("solar panels", load_solar_panels),
        ("wind turbines", load_wind_turbines),
        ("biomass systems", load_biomass_systems),
        ("hydro systems", load_hydro_systems),
    ]

    for label, fn in loaders:
        try:
            rows = fn()
            print("\n" + label.upper() + " - " + str(len(rows)) + " rows")
            print("  first row:", rows[0])
        except FileNotFoundError as e:
            print("\n" + label.upper() + " - FAILED:", e)

    print("\nEMISSION FACTORS")
    print(" ", load_emission_factors())

    # Proves the file extension is irrelevant - .csv and .txt with the
    # same contents parse to exactly the same Python objects.
    print("\n" + "-" * 60)
    print("EXTENSION CHECK (.csv vs .txt)")
    fixtures = PROJECT_ROOT / "tests" / "test_data"
    as_csv = _read_rows("appliances_test.csv", fixtures)
    as_txt = _read_rows("appliances_test.txt", fixtures)
    print("  identical:", as_csv == as_txt)
    print("-" * 60)
