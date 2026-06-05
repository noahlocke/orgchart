# data/  (private — not committed)

Put your real org data here as `orgchart.csv`, then run `./build.sh` from the
repo root to generate `dist/orgchart.html`.

Everything in this folder except this README and `.gitkeep` is gitignored, so
your real data never gets committed or shared.

Required columns: `Name`, `Class`, `Manager`. Optional: `Job Title`.
See `examples/sample-org.csv` for the expected format.
