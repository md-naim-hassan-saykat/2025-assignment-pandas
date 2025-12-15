import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    merged = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        how="left"
    )

    return merged.rename(columns={
        "code_x": "code_dep",
        "name_x": "name_dep",
        "code_y": "code_reg",
        "name_y": "name_reg",
    })[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    return referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left"
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    cols = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]

    return (
        referendum_and_areas
        .groupby("name_reg")[cols]
        .sum()
        .reset_index()
    )


def plot_referendum_map(referendum_result_by_regions):
    gdf_regions = gpd.read_file("data/regions.geojson")

    gdf = gdf_regions.merge(
        referendum_result_by_regions,
        left_on="nom",
        right_on="name_reg",
        how="left"
    )

    gdf["ratio"] = gdf["Choice A"] / (
        gdf["Choice A"] + gdf["Choice B"]
    )

    gdf.plot(column="ratio", legend=True)

    return gdf


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
