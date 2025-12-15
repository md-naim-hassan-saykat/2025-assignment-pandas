"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    referendum = pd.read_csv(
        "data/referendum.csv",
        sep=";",
        dtype={"Department code": str},
    )
    regions = pd.read_csv("data/regions.csv", dtype={"code": str})
    departments = pd.read_csv(
        "data/departments.csv",
        dtype={"code": str, "region_code": str},
    )
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    merged = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        how="left",
        suffixes=("_dep", "_reg"),
    )

    merged = merged.rename(columns={
        "code_dep": "code_dep",
        "name_dep": "name_dep",
        "code_reg": "code_reg",
        "name_reg": "name_reg",
    })

    # In case merge created code_dep/name_dep as 'code'/'name'
    if "code_dep" not in merged.columns:
        merged = merged.rename(columns={"code": "code_dep", "name": "name_dep"})
    if "code_reg" not in merged.columns:
        merged = merged.rename(columns={"code_reg": "code_reg"})

    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    referendum = referendum.copy()
    regions_and_departments = regions_and_departments.copy()

    # CRITICAL FIX: zero-pad department codes
    referendum["Department code"] = (
        referendum["Department code"]
        .astype(str)
        .str.zfill(2)
    )

    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"]
        .astype(str)
        .str.zfill(2)
    )

    merged = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",   # keep only valid departments
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    cols = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]

    result = (
        referendum_and_areas
        .groupby("name_reg", as_index=False)[cols]
        .sum()
    )

    return result


def plot_referendum_map(referendum_result_by_regions):
    gdf_regions = gpd.read_file("data/regions.geojson")

    gdf = gdf_regions.merge(
        referendum_result_by_regions,
        left_on="nom",
        right_on="name_reg",
        how="left",
    )

    gdf["ratio"] = gdf["Choice A"] / (
        gdf["Choice A"] + gdf["Choice B"]
    )

    gdf.plot(column="ratio", legend=True)

    return gdf


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
