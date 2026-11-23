from pathlib import Path
import pandas as pd

# --- Configuration ---
RAW_DIR = Path("data/raw_airports_data")
OUT_DIR = Path("data/airports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"large_airport", "medium_airport"}
# Optional: restrict to specific countries to keep the graph & METAR fetches small
# Example: COUNTRY_FILTER = ["FR", "GB", "DE", "ES", "IT"]
COUNTRY_FILTER = None


def preprocess_airports() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "airports.csv", low_memory=False)

    # We only keep the useful columns for the knowledge graph
    cols = [
        "icao_code",
        "iata_code",
        "name",
        "type",
        "municipality",
        "iso_country",
        "continent",
        "latitude_deg",
        "longitude_deg",
        "elevation_ft",
    ]
    df = df[cols].copy()

    # Filter to medium & large airports with valid ICAO codes (needed for METAR join)
    df = df[df["type"].isin(ALLOWED_TYPES)]
    df["icao_code"] = df["icao_code"].astype("string").str.strip().str.upper()
    df["iata_code"] = df["iata_code"].astype("string").str.strip().str.upper()
    df = df.dropna(subset=["icao_code", "name", "latitude_deg", "longitude_deg"])
    df = df[df["icao_code"].str.match(r"^[A-Z0-9]{4}$", na=False)]

    if COUNTRY_FILTER:
        df = df[df["iso_country"].isin(COUNTRY_FILTER)]

    df = df.drop_duplicates(subset=["icao_code"]).reset_index(drop=True)
    df.to_csv(OUT_DIR / "airports.csv", index=False, encoding="utf-8")
    print(f"Saved {len(df)} airports -> {OUT_DIR / 'airports.csv'}")
    return df


def preprocess_routes(airports_df: pd.DataFrame) -> None:
    df = pd.read_csv(RAW_DIR / "routes.csv", low_memory=False)

    # Keep only useful route columns (airport coords/cities are already in airports.csv)
    cols = [
        "airline_iata",
        "airline_name",
        "src_iata",
        "dst_iata",
        "stops",
        "distance_km",
    ]
    df = df[cols].copy()

    df["src_iata"] = df["src_iata"].astype("string").str.strip().str.upper()
    df["dst_iata"] = df["dst_iata"].astype("string").str.strip().str.upper()

    # Map IATA -> ICAO using the cleaned airports table so all IRIs use ICAO
    iata_to_icao = (
        airports_df.dropna(subset=["iata_code"])
        .drop_duplicates(subset=["iata_code"])
        .set_index("iata_code")["icao_code"]
        .to_dict()
    )
    df["src_icao"] = df["src_iata"].map(iata_to_icao)
    df["dst_icao"] = df["dst_iata"].map(iata_to_icao)

    # Drop routes linking to missing/filtered-out airports or self-loops
    df = df.dropna(subset=["src_icao", "dst_icao"])
    df = df[df["src_icao"] != df["dst_icao"]]
    df = df.drop_duplicates().reset_index(drop=True)

    # Add a simple route_id for clean RDF resource IRIs
    df.insert(0, "route_id", [f"R{i+1:06d}" for i in range(len(df))])

    df.to_csv(OUT_DIR / "routes.csv", index=False, encoding="utf-8")
    print(f"Saved {len(df)} routes -> {OUT_DIR / 'routes.csv'}")


if __name__ == "__main__":
    airports = preprocess_airports()
    preprocess_routes(airports)
