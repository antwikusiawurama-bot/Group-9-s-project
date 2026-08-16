import pandas as pd
import matplotlib.pyplot as plt  # type: ignore

utilities = pd.read_csv("utilities.csv")
substations = pd.read_csv("substations.csv")
lines = pd.read_csv("lines.csv")

print("=" * 70)
print("STEP 0: Data loaded")
print("=" * 70)
print(f"utilities: {utilities.shape[0]} rows, {utilities.shape[1]} columns")
print(f"substations: {substations.shape[0]} rows, {substations.shape[1]} columns")
print(f"lines: {lines.shape[0]} rows, {lines.shape[1]} columns")

print("\n" + "=" * 70)
print("STEP 1: Descriptive statistics (numerical columns)")
print("=" * 70)
 
print("\n--- Substations: Voltage, Capacity, Commissioning Year ---")
print(substations[["Voltage (kV)", "Capacity (MVA)", "Commissioning Year"]].describe())
 
print("\n--- Lines: Length, Capacity ---")
print(lines[["Length (km)", "Capacity (MVA)"]].describe())


print("\n" + "=" * 70)
print("STEP 2: Frequency distributions (categorical columns)")
print("=" * 70)
 
print("\n--- Substation Type ---")
print(substations["Type"].value_counts())
 
print("\n--- Substation Status (Active / Inactive) ---")
print(substations["Status"].value_counts())
 
print("\n--- Substation Voltage level ---")
print(substations["Voltage (kV)"].value_counts().sort_index())
 
print("\n--- Line Status (Active / Under Maintenance) ---")
print(lines["Status"].value_counts())
 
print("\n--- Line Type (Overhead / Underground) ---")
print(lines["Line Type"].value_counts())
 
print("\n--- Utility Type ---")
print(utilities["Type"].value_counts())

print("\n" + "=" * 70)
print("STEP 3: Top utilities by number of lines operated")
print("=" * 70)
 
lines_per_utility = lines["Utility ID"].value_counts().reset_index()
lines_per_utility.columns = ["Utility ID", "Number of Lines"]
 
lines_per_utility = lines_per_utility.merge(
    utilities[["Utility ID", "Alias", "Code"]], on="Utility ID", how="left"
)
lines_per_utility = lines_per_utility.sort_values("Number of Lines", ascending=False)
 
print(lines_per_utility.to_string(index=False))
 
plt.figure(figsize=(8, 5))
plt.bar(lines_per_utility["Alias"], lines_per_utility["Number of Lines"], color="steelblue")
plt.title("Number of Lines Operated per Utility")
plt.xlabel("Utility")
plt.ylabel("Number of Lines")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("eda_lines_per_utility.png")
plt.close()
print("Saved chart: eda_lines_per_utility.png")

print("\n" + "=" * 70)
print("STEP 4: Most-connected substations (by number of lines)")
print("=" * 70)
 
source_counts = lines["Source Substation"].value_counts()
destination_counts = lines["Destination Substation"].value_counts()

connection_counts = source_counts.add(destination_counts, fill_value=0)
connection_counts = connection_counts.sort_values(ascending=False)
 
top_10_connected = connection_counts.head(10)
print("Top 10 most-connected substations:")
print(top_10_connected)
 
plt.figure(figsize=(8, 5))
top_10_connected.plot(kind="bar", color="darkorange")
plt.title("Top 10 Most-Connected Substations")
plt.xlabel("Substation")
plt.ylabel("Number of Lines Connected")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("eda_most_connected_substations.png")
plt.close()
print("Saved chart: eda_most_connected_substations.png")

print("\n" + "=" * 70)
print("STEP 5: Geographic distribution by region")
print("=" * 70)
 
substations_per_region = substations["Region"].value_counts()
print("Substations per region:")
print(substations_per_region)
 
plt.figure(figsize=(9, 5))
substations_per_region.plot(kind="bar", color="seagreen")
plt.title("Number of Substations by Region")
plt.xlabel("Region")
plt.ylabel("Number of Substations")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("eda_substations_by_region.png")
plt.close()
print("Saved chart: eda_substations_by_region.png")
 
lines_with_region = lines.merge(
    substations[["Substation ID", "Region"]],
    left_on="Source Substation ID", right_on="Substation ID",
    how="left"
)
lines_per_region = lines_with_region["Region"].value_counts()
print("\nLines per region (by source substation's region):")
print(lines_per_region)

print("\n" + "=" * 70)
print("STEP 6: Substation status and voltage-level distribution")
print("=" * 70)
 
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
 
status_counts = substations["Status"].value_counts()
axes[0].bar(status_counts.index, status_counts.values, color=["mediumseagreen", "indianred"])
axes[0].set_title("Substation Status")
axes[0].set_ylabel("Number of Substations")
 
# Right chart: Voltage level distribution
voltage_counts = substations["Voltage (kV)"].value_counts().sort_index()
axes[1].bar(voltage_counts.index.astype(str), voltage_counts.values, color="mediumpurple")
axes[1].set_title("Substation Voltage Level Distribution")
axes[1].set_xlabel("Voltage (kV)")
axes[1].set_ylabel("Number of Substations")
 
plt.tight_layout()
plt.savefig("eda_status_and_voltage.png")
plt.close()
print("Saved chart: eda_status_and_voltage.png")
 
print("\n" + "=" * 70)
print("EDA COMPLETE - see the printed tables above and the 4 PNG charts")
print("=" * 70)