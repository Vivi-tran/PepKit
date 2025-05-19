import pandas as pd

# Example: Load a CSV bundled with the package
import importlib.resources as pkg_resources

with pkg_resources.files(__package__).joinpath("example.csv").open("r") as f:
    example_df = pd.read_csv(f)
