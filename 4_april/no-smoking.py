# %% IMPORTS
import polars as pl
import altair as alt

# %% COLOUR VARIABLES

off_white = "#F9F6EE"
white = "white"
orange = "#F1A238"

# %% LOAD SMOKING AND VAPING DATA
smoking_df = pl.read_excel(
    source="adultsmokinghabitsingreatbritain2024.xlsx",
    sheet_name="Table_1",
    engine="xlsx2csv",
    engine_options={"skip_empty_lines": True},
    read_options={"has_header": True, "skip_rows": 7},
).head(-4)  # remove footer

vaping_df = pl.read_excel(
    source="ecigaretteuseingreatbritain2024.xlsx",
    sheet_name="Table_1",
    engine="xlsx2csv",
    engine_options={"skip_empty_lines": True},
    read_options={"has_header": True, "skip_rows": 11},
)

# %% CLEAN VAPING DATA
# rename key columns
# vaping df - remove any rows where 'Year' contains table or 'Year'
# keep only relevant columns
vaping_df = (
    vaping_df.rename(
        {vaping_df.columns[1]: "status", vaping_df.columns[-1]: "percentage"}
    )
    .remove(pl.col("Year").str.contains("Table") | pl.col("Year").str.contains("Year"))
    .select(pl.nth([0, 1, -1]))
)

# %% CREATE PIVOT TABLE
vaping_pivot = vaping_df.pivot(
    "status",
    on_columns=[
        "Daily user (%)",
        "Occasional user (%)",
        "Current e-cigarette user, or vaper (%)",
    ],
    index="Year",
    values="percentage",
)

# %% CLEAN VAPING PIVOT TABLE
# users = 'Daily user (%)' +  'Occasional user (%)' 2020 onwards
# 'Current e-cigarette user, or vaper (%)' before 2020
# convert these columns to float dtypes then
# create column that sums these columns to get vaping % by year
# keep only Year and vaping_percentage columns for merging
vaping_pivot = vaping_pivot.with_columns(
    vaping_pivot.select(pl.exclude("Year"))
    .cast(pl.Float32, strict=False)
    .sum_horizontal()
    .alias("vaping_percentage")
    .round(decimals=1)
).select(pl.nth([0, -1]))

# %% CLEAN SMOKING DATA
# rename key columns
# use All persons aged 16 and over column for smoking %
# smoking_df - remove [Note x] from Year
# ensure % is a float dtype
# keep only relevant columns
smoking_df = (
    smoking_df.rename(
        {smoking_df.columns[1]: "Year", smoking_df.columns[-1]: "smoking_percentage"}
    )
    .select(pl.nth([1, -1]))
    .with_columns(pl.col("Year").str.slice(0, 4))
    .with_columns(pl.col("smoking_percentage").cast(pl.Float32, strict=False))
)


# %% MERGE AND FORMAT DATA FOR PLOTTING
merged_df = smoking_df.join(vaping_pivot, on="Year", how="left")

# convert Year column to int
# fill null with zero
merged_df = merged_df.with_columns(
    pl.col("Year").cast(pl.Int64, strict=False)
).with_columns(pl.col("vaping_percentage").fill_null(0))

# %% PLOT BAR CHART

# prepare date for plotting
plot_df = (
    merged_df.unpivot(
        index="Year",
        on=["vaping_percentage", "smoking_percentage"],
        variable_name="nicotine_type",
        value_name="Percentage",
    )
    .filter(
        (pl.col("Year") >= 2000),
    )
    .with_columns(
        pl.when(pl.col("nicotine_type") == "vaping_percentage")
        .then(pl.lit("Vapers"))
        .otherwise(pl.lit("Smokers"))
        .alias("nicotine_type")
    )
    .with_columns(pl.col("Year").cast(pl.String))
)

# plot bar chart
bar_chart = (
    plot_df.plot.bar(x="Year", y="Percentage", color="nicotine_type")
    .properties(
        width=700,
        height=400,
        title={
            "text": ["Smoking and vaping rates in the UK"],
            "subtitle": ["As a % of all adults over 16. Data from the ONS."],
            "color": "black",
            "subtitleColor": "black",
            "offset": 20,
        },
    )
    .configure(background=off_white)
    .configure_range(category=[white, orange])
    .configure_mark(stroke="black", strokeWidth=1.2)
    .mark_bar(size=20)
    .configure_axis(
        grid=False,
        domain=True,
        domainColor="black",
        domainWidth=1.2,
        tickWidth=1.2,
        tickColor="black",
        labelColor="black",
        gridColor="black",
    )
    .configure_legend(
        orient="top-right", direction="horizontal", title=None, labelFontSize=10
    )
    .configure_view(stroke="none")
)

# save bar chart
bar_chart.save("no-smoking.png", ppi=500)
# %%
