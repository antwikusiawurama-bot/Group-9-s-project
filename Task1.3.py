import pandas as pd  # type: ignore

# 1. Load Datasets
utilities = pd.read_csv('utilities_cleaned.csv')
substations = pd.read_csv('substations_cleaned.csv')
lines = pd.read_csv('lines_cleaned.csv')

# Handle column naming flexibility 
src_col = 'source_substation_id' if 'source_substation_id' in lines.columns else 'Source Substation ID'
dst_col = 'destination_substation_id' if 'destination_substation_id' in lines.columns else 'Destination Substation ID'
sub_id_col = 'substation_id' if 'substation_id' in substations.columns else 'Substation ID'
util_id_col = 'utility_id' if 'utility_id' in utilities.columns else 'Utility ID'

# 2.Join Source Substation attributes
master_df = pd.merge(
    lines,
    substations.add_suffix('_source'),
    left_on=src_col,
    right_on=f"{sub_id_col}_source",
    how='left',
    indicator='source_join'
)

# 3.Join Destination Substation attributes
master_df = pd.merge(
    master_df,
    substations.add_suffix('_dest'),
    left_on=dst_col,
    right_on=f"{sub_id_col}_dest",
    how='left',
    indicator='dest_join'
)

# 4.Join Utility metadata
master_df = pd.merge(
    master_df,
    utilities.add_suffix('_utility'),
    left_on=util_id_col,
    right_on=f"{util_id_col}_utility",
    how='left',
    indicator='utility_join'
)

# 5. Identify Orphaned Records (missing source sub, dest sub, or utility)
orphaned_lines = master_df[
    (master_df['source_join'] == 'left_only') |
    (master_df['dest_join'] == 'left_only') |
    (master_df['utility_join'] == 'left_only')
]

# Calculate Metrics
total_lines = len(lines)
orphan_count = len(orphaned_lines)
data_loss_pct = (orphan_count / total_lines) * 100 if total_lines > 0 else 0.0

print(f"Total Lines Processed: {total_lines}")
print(f"Orphaned Records Identified: {orphan_count}")
print(f"Data Loss Percentage: {data_loss_pct:.2f}%")

# 6. Filter Clean Records and Save
clean_master_df = master_df[
    (master_df['source_join'] == 'both') &
    (master_df['dest_join'] == 'both') &
    (master_df['utility_join'] == 'both')
].copy()

# Drop merge indicator helper columns
clean_master_df.drop(columns=['source_join', 'dest_join', 'utility_join'], inplace=True)

# Save integrated master dataset
clean_master_df.to_csv('integrated_master_dataset.csv', index=False)
print("Successfully saved 'integrated_master_dataset.csv'!")


# Fast dictionary lookup for substation metadata by ID
substation_lookup = substations.set_index(sub_id_col).to_dict(orient='index')

# Network Adjacency List (Source Substation ID -> List of Destination Substation IDs)
adjacency_list = clean_master_df.groupby(src_col)[dst_col].apply(list).to_dict()

print(f"Built adjacency lookup for {len(adjacency_list)} active source substations.")