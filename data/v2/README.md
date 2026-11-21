# V2 data bundle

Large CSV inputs and intermediate tables are stored compressed (`.csv.gz` or `.csv.xz`) to keep repository size manageable. Pandas `read_csv` detects these formats from the filename suffix. The V2 build script accepts raw Lens exports as either `.csv` or compressed `.csv.gz` files and writes uncompressed derived CSVs when run locally.

Raw Lens exports and the exact search expression are under `data/raw/lens_us/v2/` and `data/searches/`. Screening outputs and analysis tables are under `data/v2/`.
