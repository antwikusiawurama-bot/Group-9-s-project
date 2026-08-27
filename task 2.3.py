import pandas as pd
import matplotlib.pyplot as plt
 

utilities = pd.read_csv("utilities.csv")
substations = pd.read_csv("substations.csv")
lines = pd.read_csv("lines.csv")
 
print("=" * 70)
print("STEP 0: Data loaded")
print("=" * 70)
print(f"utilities: {len(utilities)} rows | substations: {len(substations)} rows | lines: {len(lines)} rows")

print("\n" + "=" * 70)
print("STEP 1: Utility footprint by region (based on lines operated)")
print("=" * 70)

lines_with_region = lines.merge(
    substations[["Substation ID", "Region"]],
    left_on="Source Substation ID", right_on="Substation ID",
    how="left"
)

lines_with_region = lines_with_region.merge(
    utilities[["Utility ID", "Alias"]], on="Utility ID", how="left"
)
 
footprint = (
    lines_with_region
    .groupby(["Alias", "Region"])
    .size()
    .reset_index(name="Number of Lines")
    .sort_values(["Alias", "Number of Lines"], ascending=[True, False])
)
print(footprint.to_string(index=False))

print("STEP 2: Upgrade candidates (lowest capacity within their voltage tier)")
print("=" * 70)
print("NOTE: this is a proxy based on rated capacity only - we do not have")
print("real load data, so this flags candidates for investigation, not a")
print("certified upgrade list.\n")
 
substations["Capacity Rank Within Voltage Tier"] = (
    substations.groupby("Voltage (kV)")["Capacity (MVA)"].rank(method="min")
)
upgrade_candidates = substations.sort_values(
    ["Voltage (kV)", "Capacity (MVA)"]
)[["Name", "Region", "Voltage (kV)", "Capacity (MVA)"]].groupby("Voltage (kV)").head(3)
 
print("Bottom 3 substations by capacity, within each voltage tier:")
print(upgrade_candidates.to_string(index=False))

print("\n" + "=" * 70)
print("STEP 3: Underserved regions (fewest substations / lowest total capacity)")
print("=" * 70)
 
region_summary = substations.groupby("Region").agg(
    Number_of_Substations=("Substation ID", "count"),
    Total_Capacity_MVA=("Capacity (MVA)", "sum"),
).reset_index()
 

ghana_only = region_summary[~region_summary["Region"].str.contains("border|Togo$|Benin|Guinea|Ivoire$|Faso$", regex=True)]
underserved = ghana_only.sort_values("Total_Capacity_MVA").head(5)
 
print("5 most underserved Ghanaian regions (lowest total substation capacity):")
print(underserved.to_string(index=False))
 
plt.figure(figsize=(8, 5))
plt.bar(underserved["Region"], underserved["Total_Capacity_MVA"], color="tomato")
plt.title("Most Underserved Regions (Lowest Total Substation Capacity)")
plt.xlabel("Region")
plt.ylabel("Total Capacity (MVA)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("bi_underserved_regions.png")
plt.close()
print("Saved chart: bi_underserved_regions.png")

print("\n" + "=" * 70)
print("STEP 4: Technical-loss proxy (Length / Voltage)")
print("=" * 70)
print("NOTE: this is an educational proxy, not a real loss calculation,")
print("which would need current, resistance, and load data.\n")
 
lines["Loss Proxy (Length/Voltage)"] = lines["Length (km)"] / lines["Voltage (kV)"]
highest_loss_risk = lines.sort_values("Loss Proxy (Length/Voltage)", ascending=False).head(10)
 
print("Top 10 lines by loss-risk proxy (long + low voltage = higher risk):")
print(highest_loss_risk[["Source Substation", "Destination Substation",
                          "Length (km)", "Voltage (kV)", "Loss Proxy (Length/Voltage)"]].to_string(index=False))


print("\n" + "=" * 70)
print("STEP 5: Utility asset age (average commissioning year of substations they connect to)")
print("=" * 70)
 
lines_with_year = lines.merge(
    substations[["Substation ID", "Commissioning Year"]],
    left_on="Source Substation ID", right_on="Substation ID", how="left"
).merge(
    utilities[["Utility ID", "Alias"]], on="Utility ID", how="left"
)
 
utility_age = (
    lines_with_year.groupby("Alias")["Commissioning Year"]
    .mean()
    .round(1)
    .sort_values()
    .reset_index(name="Average Commissioning Year")
)
print(utility_age.to_string(index=False))
print("(Lower average year = older infrastructure on average)")

print("\n" + "=" * 70)
print("STEP 6: Proportion of lines Under Maintenance")
print("=" * 70)
 
# By region (using source substation's region)
maintenance_by_region = (
    lines_with_region.groupby("Region")["Status"]
    .apply(lambda s: (s == "Under Maintenance").mean() * 100)
    .round(1)
    .sort_values(ascending=False)
    .reset_index(name="Percent Under Maintenance")
)
print("By region:")
print(maintenance_by_region.to_string(index=False))
 
# By utility
maintenance_by_utility = (
    lines_with_region.groupby("Alias")["Status"]
    .apply(lambda s: (s == "Under Maintenance").mean() * 100)
    .round(1)
    .sort_values(ascending=False)
    .reset_index(name="Percent Under Maintenance")
)
print("\nBy utility:")
print(maintenance_by_utility.to_string(index=False))

print("\n" + "=" * 70)
print("STEP 7: Substation age distribution")
print("=" * 70)
 
bins = [1960, 1980, 2000, 2010, 2024]
labels = ["1960s-70s (oldest)", "1980s-90s", "2000s", "2010s-20s (newest)"]
substations["Age Band"] = pd.cut(substations["Commissioning Year"], bins=bins, labels=labels)
 
age_distribution = substations["Age Band"].value_counts().reindex(labels)
print(age_distribution)
 
plt.figure(figsize=(8, 5))
age_distribution.plot(kind="bar", color="slateblue")
plt.title("Substation Age Distribution (Fault-Risk Proxy)")
plt.xlabel("Commissioning Era")
plt.ylabel("Number of Substations")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("bi_age_distribution.png")
plt.close()
print("Saved chart: bi_age_distribution.png")

print("\n" + "=" * 70)
print("STEP 8: Capacity concentration (risk indicator)")
print("=" * 70)
 
total_capacity = substations["Capacity (MVA)"].sum()
top_5_capacity = substations.sort_values("Capacity (MVA)", ascending=False).head(5)
top_5_share = top_5_capacity["Capacity (MVA)"].sum() / total_capacity * 100
 
print(f"Total national capacity: {total_capacity:.1f} MVA")
print(f"Capacity held by the top 5 substations: {top_5_capacity['Capacity (MVA)'].sum():.1f} MVA")
print(f"That's {top_5_share:.1f}% of all capacity sitting in just 5 substations.")
print("\nTop 5 substations by capacity:")
print(top_5_capacity[["Name", "Region", "Capacity (MVA)"]].to_string(index=False))
 
print("\n" + "=" * 70)
print("BUSINESS INTELLIGENCE & RELIABILITY ANALYSIS COMPLETE")
print("See the printed tables above and 3 PNG charts")
print("=" * 70)