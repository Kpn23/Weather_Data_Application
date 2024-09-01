import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.ticker as ticker


def extract():
    conn = sqlite3.connect(
        "/Users/superdayuanjingzhi/Documents/JDE-python/p_api_weather/weather_data.db"
    )
    your_city = pd.read_sql("SELECT DISTINCT city_name FROM weather_data", conn)[
        "city_name"
    ].tolist()
    df = pd.read_sql("SELECT * FROM weather_data", conn)
    conn.close()
    return your_city, df


def clean(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.dropna(inplace=True)
    return df


def visualize(your_city, df):
    start_time = pd.Timestamp("2024-08-27 09:00")
    end_time = pd.Timestamp("2024-08-27 17:00")
    # start_time = pd.Timestamp('2024-08-28 00:00')
    # end_time = pd.Timestamp('2024-08-28 04:00')
    df_t = df[(df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)]

    index = range(len(your_city))

    fig, axs = plt.subplots(4, 2, figsize=(20, 30))

    for city, i in zip(your_city, index):
        city_data = df_t[df_t["city_name"] == city]
        if not city_data.empty:
            ax = axs[i // 2, i % 2]  # Correctly index into the subplot grid

            # Plot the temperature lines
            ax.plot(
                city_data["timestamp"],
                city_data["temperature"],
                label="Temperature",
                color="blue",
            )
            ax.plot(
                city_data["timestamp"],
                city_data["temperature_max"],
                label="Max Temperature",
                color="red",
            )
            ax.plot(
                city_data["timestamp"],
                city_data["temperature_min"],
                label="Min Temperature",
                color="green",
            )

            # Fill the area between the max and min temperature with a gradient
            ax.fill_between(
                city_data["timestamp"],
                city_data["temperature_max"],
                city_data["temperature_min"],
                color="lightgray",
                alpha=0.5,
                label="Temperature Range",
            )

            # Limit the number of x-ticks to 5
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

            ax.set_title(f"Temperature Over Time for {city}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Temperature (°C)")
            ax.legend()

    plt.tight_layout()
    plt.savefig("temperature_over_time.png")
    plt.close()

    fig, axs = plt.subplots(4, 2, figsize=(20, 35))

    for city, i in zip(your_city, index):
        city_data = df_t[df_t["city_name"] == city]
        if not city_data.empty:
            ax = axs[i // 2, i % 2]
            correlation_matrix = city_data[
                ["temperature", "feels_like", "humidity"]
            ].corr()
            sns.heatmap(
                correlation_matrix,
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                square=True,
                ax=ax,
            )
            ax.set_title(f"Heatmap for {city}")

    plt.suptitle("Heatmap of Temperature, Feels Like, and Humidity", y=0.99)
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png")
    plt.close()

    return df_t


def output(df_t):
    df_t_t = df_t.groupby(["city_name"])[["temperature", "feels_like"]].mean()
    data_to_save = []

    for index, row in df_t_t.iterrows():
        diff = row["feels_like"] - row["temperature"]
        avg_temp = row["temperature"]
        data_to_save.append(
            {
                "City": index,
                "Avg Temp": f"{avg_temp:.2f}",
                "Difference": f"{diff:.2f}",
                "Remark": "(+) feel hotter" if diff > 0 else "(-) feel cooler",
            }
        )

    df_to_csv = pd.DataFrame(data_to_save)
    df_to_csv.to_csv("weather_report.csv", index=False)


def main():
    try:
        your_city, df = extract()
        df = clean(df)
        df_t = visualize(your_city, df)
        output(df_t)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
