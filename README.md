# airport-weather-kg

## Airport & Route Data Preprocessing

The raw Kaggle dataset (`Global Flights, Airports & Airlines`) is preprocessed offline via `scripts/preprocess_airports.py` to produce clean, RML-ready files in `data/airports/`:

- **Scope & Filtering:** Restricted `airports.csv` to `large_airport` and `medium_airport` entries with valid 4-character ICAO codes (required to join with METAR weather observations).
- **Redundancy Removal:** Dropped the standalone `airlines.csv` table, keeping airline details (`airline_iata`, `airline_name`) only where tied to an active route in `routes.csv`, and removed unused metadata columns.
- **Identifier Harmonization:** Standardized airport codes to uppercase and mapped route endpoints from IATA (`src_iata`, `dst_iata`) to ICAO (`src_icao`, `dst_icao`) so all graph entities share a consistent ICAO-based IRI strategy.
- **Integrity & Deduplication:** Removed routes referencing filtered-out/missing airports, dropped self-loops and duplicates, and generated a unique `route_id` for each route.

### Usage
Place the raw Kaggle CSVs in `data/raw_airports_data/`, then run:
```bash
python scripts/preprocess_airports.py