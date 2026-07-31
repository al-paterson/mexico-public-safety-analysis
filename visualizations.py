import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

os.makedirs("output/charts", exist_ok=True)

conn = sqlite3.connect("data/mexico_safety.db")
QRO = "Querétaro"

# load all four datasets

yearly = pd.read_sql("""
    SELECT i.year, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ?
    GROUP BY i.year
    ORDER BY i.year
""", conn, params=[QRO])

top_crimes = pd.read_sql("""
    SELECT i.crime_type, SUM(i.incidents) AS total_incidents
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.crime_type
    ORDER BY total_incidents DESC
    LIMIT 10
""", conn, params=[QRO])

# incidents per day by month, 2015-2025 (per day because February is short)
monthly = pd.read_sql("""
    SELECT i.month,
           SUM(i.incidents) * 1.0 / CASE
               WHEN i.month = 2 THEN 311
               WHEN i.month IN (4, 6, 9, 11) THEN 330
               ELSE 341 END AS per_day
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    WHERE s.state_name = ? AND i.year <= 2025
    GROUP BY i.month
    ORDER BY i.month
""", conn, params=[QRO])

# Querétaro's rate vs the national rate, both per 100k
vs_national = pd.read_sql("""
    SELECT q.year, q.rate_per_100k AS qro_rate, n.rate_per_100k AS national_rate
    FROM (
        SELECT i.year, SUM(i.incidents) * 100000.0 / p.population AS rate_per_100k
        FROM incidents i
        INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
        WHERE i.state_code = 22 AND i.year <= 2025
        GROUP BY i.year, p.population
    ) q
    INNER JOIN (
        SELECT i.year, SUM(i.incidents) * 100000.0 / MAX(t.national_pop) AS rate_per_100k
        FROM incidents i
        INNER JOIN (
            SELECT year, SUM(population) AS national_pop FROM population GROUP BY year
        ) t ON i.year = t.year
        WHERE i.year <= 2025
        GROUP BY i.year
    ) n ON q.year = n.year
    ORDER BY q.year
""", conn)

# 2025 ranking: every state's incidents per 100k, for the ranked bar chart
state_rates = pd.read_sql("""
    SELECT s.state_name,
           ROUND(SUM(i.incidents) * 100000.0 / p.population, 1) AS rate_per_100k
    FROM incidents i
    INNER JOIN state_lookup s ON i.state_code = s.state_code
    INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
    WHERE i.year = 2025
    GROUP BY s.state_name, p.population
    ORDER BY rate_per_100k DESC
""", conn)

# each state's population growth and rate change, 2015 to 2025
growth_vs_rate = pd.read_sql("""
    SELECT s.state_name,
           ROUND((b.population - a.population) * 100.0 / a.population, 1) AS pop_growth_pct,
           ROUND((b.rate_per_100k - a.rate_per_100k) * 100.0 / a.rate_per_100k, 1) AS rate_change_pct
    FROM (
        SELECT i.state_code, p.population,
               SUM(i.incidents) * 100000.0 / p.population AS rate_per_100k
        FROM incidents i
        INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
        WHERE i.year = 2015
        GROUP BY i.state_code, p.population
    ) a
    INNER JOIN (
        SELECT i.state_code, p.population,
               SUM(i.incidents) * 100000.0 / p.population AS rate_per_100k
        FROM incidents i
        INNER JOIN population p ON i.state_code = p.state_code AND i.year = p.year
        WHERE i.year = 2025
        GROUP BY i.state_code, p.population
    ) b ON a.state_code = b.state_code
    INNER JOIN state_lookup s ON a.state_code = s.state_code
""", conn)

# 2026 is partial data (Jan–Feb only), drop from trend charts
yearly = yearly[yearly["year"] <= 2025]

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# chart 1: Incidents by year (line)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(yearly["year"], yearly["total_incidents"], marker="o",
        linewidth=2.5, color="#2563EB", markersize=6)
ax.fill_between(yearly["year"], yearly["total_incidents"], alpha=0.08, color="#2563EB")

ax.set_title("Reported Crime Incidents in Querétaro (2015–2025)", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Year")
ax.set_ylabel("Total Incidents")
ax.set_xticks(yearly["year"])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("output/charts/chart1_yearly_trend.png", dpi=150)
plt.close()
print("Saved chart1_yearly_trend.png")

# chart 2: Top 10 crime types (horizontal bar)

fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#2563EB"] + ["#93C5FD"] * 9
ax.barh(top_crimes["crime_type"][::-1], top_crimes["total_incidents"][::-1], color=colors[::-1])

ax.set_title("Top 10 Crime Types in Querétaro (2015–2025)", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Total Incidents")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("output/charts/chart2_top_crimes.png", dpi=150)
plt.close()
print("Saved chart2_top_crimes.png")

# chart 3: Incidents by month (bar)

fig, ax = plt.subplots(figsize=(10, 5))
bar_colors = ["#DC2626" if v == monthly["per_day"].max()
              else "#93C5FD" if v == monthly["per_day"].min()
              else "#2563EB"
              for v in monthly["per_day"]]

ax.bar(MONTH_LABELS, monthly["per_day"], color=bar_colors)

ax.set_title("Incidents per Day by Month in Querétaro (2015–2025)", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Month")
ax.set_ylabel("Incidents per day")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", linestyle="--", alpha=0.4)

ax.annotate("Peak: Oct", xy=(9, monthly["per_day"].iloc[9]),
            xytext=(9, monthly["per_day"].iloc[9] + 1.5),
            ha="center", fontsize=9, color="#DC2626")

plt.tight_layout()
plt.savefig("output/charts/chart3_seasonal.png", dpi=150)
plt.close()
print("Saved chart3_seasonal.png")

# chart 4: Querétaro vs national rate per 100k (line)
# per capita, Querétaro is above the national rate every year

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(vs_national["year"], vs_national["qro_rate"], marker="o",
        linewidth=2.5, color="#2563EB", markersize=6, label="Querétaro")
ax.plot(vs_national["year"], vs_national["national_rate"], marker="s",
        linewidth=2.5, color="#DC2626", linestyle="--", markersize=6, label="National rate")

ax.set_title("Reported Incidents per 100,000 Inhabitants: Querétaro vs National (2015–2025)",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Year")
ax.set_ylabel("Incidents per 100k")
ax.set_xticks(vs_national["year"])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.legend(frameon=False)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("output/charts/chart4_vs_national_rate.png", dpi=150)
plt.close()
print("Saved chart4_vs_national_rate.png")

# chart 5: Fastest rising crime types 2015 vs 2024 (horizontal bar)

rising = pd.read_sql("""
    SELECT
        a.crime_type,
        COALESCE(b.incidents_2015, 0) AS incidents_2015,
        a.incidents_2024,
        ROUND(
            (a.incidents_2024 - COALESCE(b.incidents_2015, 0)) * 100.0
            / NULLIF(COALESCE(b.incidents_2015, 0), 0),
            1
        ) AS pct_change
    FROM (
        SELECT i.crime_type, SUM(i.incidents) AS incidents_2024
        FROM incidents i
        INNER JOIN state_lookup s ON i.state_code = s.state_code
        WHERE s.state_name = ? AND i.year = 2024
        GROUP BY i.crime_type
    ) a
    LEFT JOIN (
        SELECT i.crime_type, SUM(i.incidents) AS incidents_2015
        FROM incidents i
        INNER JOIN state_lookup s ON i.state_code = s.state_code
        WHERE s.state_name = ? AND i.year = 2015
        GROUP BY i.crime_type
    ) b ON a.crime_type = b.crime_type
    WHERE b.incidents_2015 > 0
    ORDER BY pct_change DESC
    LIMIT 8
""", conn, params=[QRO, QRO])

labels = [t[:35] + "…" if len(t) > 35 else t for t in rising["crime_type"]]

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(labels[::-1], rising["pct_change"][::-1], color="#2563EB")

ax.set_title("Fastest Rising Crime Types in Querétaro (2015 vs 2024)", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("% Change")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}%"))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("output/charts/chart5_rising_crimes.png", dpi=150)
plt.close()
print("Saved chart5_rising_crimes.png")

# chart 6: All 32 states ranked by rate per 100k, 2025 (horizontal bar)
# Querétaro highlighted

# highlight Querétaro in dark blue, all other states in light blue
bar_colors6 = ["#2563EB" if name == QRO else "#BFDBFE"
               for name in state_rates["state_name"]]

fig, ax = plt.subplots(figsize=(10, 10))  # tall figure so 32 labels stay readable
ax.barh(state_rates["state_name"][::-1], state_rates["rate_per_100k"][::-1],
        color=bar_colors6[::-1])

ax.set_title("Reported Incidents per 100,000 Inhabitants by State (2025)",
             fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Incidents per 100k")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.4)

# label Querétaro's bar with its rank and rate so the takeaway is instant
qro_rank = state_rates.reset_index(drop=True).query("state_name == @QRO").index[0] + 1
qro_rate = float(state_rates.loc[state_rates["state_name"] == QRO, "rate_per_100k"].iloc[0])
ax.annotate(f"#{qro_rank} of 32: {qro_rate:,.0f}",
            xy=(qro_rate, 32 - qro_rank),  # bar positions are bottom-up
            xytext=(qro_rate + 80, 32 - qro_rank),
            va="center", fontsize=9, fontweight="bold", color="#2563EB")

plt.tight_layout()
plt.savefig("output/charts/chart6_state_ranking.png", dpi=150)
plt.close()
print("Saved chart6_state_ranking.png")

# chart 7: Population growth vs change in crime rate, 2015→2025 (scatter)

fig, ax = plt.subplots(figsize=(10, 7))

# all states as light dots, Querétaro as a big dark one
is_qro = growth_vs_rate["state_name"] == QRO
ax.scatter(growth_vs_rate.loc[~is_qro, "pop_growth_pct"],
           growth_vs_rate.loc[~is_qro, "rate_change_pct"],
           s=45, color="#93C5FD", edgecolor="#2563EB", linewidth=0.5, zorder=3)
ax.scatter(growth_vs_rate.loc[is_qro, "pop_growth_pct"],
           growth_vs_rate.loc[is_qro, "rate_change_pct"],
           s=140, color="#2563EB", zorder=4)

# zero line: states below it got safer per capita even as they grew
ax.axhline(0, color="#9CA3AF", linewidth=1, linestyle="--")

# label a handful of notable states so the chart reads without a legend
to_label = ["Querétaro", "Quintana Roo", "Baja California Sur",
            "Nuevo León", "Yucatán", "Baja California"]
for _, row in growth_vs_rate[growth_vs_rate["state_name"].isin(to_label)].iterrows():
    ax.annotate(row["state_name"],
                xy=(row["pop_growth_pct"], row["rate_change_pct"]),
                xytext=(6, 5), textcoords="offset points", fontsize=9,
                fontweight="bold" if row["state_name"] == QRO else "normal",
                color="#1E3A8A" if row["state_name"] == QRO else "#374151")

ax.set_title("Population Growth vs Change in Crime Rate by State (2015–2025)",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Population growth 2015–2025 (%)")
ax.set_ylabel("Change in incidents per 100k (%)")
ax.grid(linestyle="--", alpha=0.4)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("output/charts/chart7_growth_vs_crime.png", dpi=150)
plt.close()
print("Saved chart7_growth_vs_crime.png")

conn.close()
