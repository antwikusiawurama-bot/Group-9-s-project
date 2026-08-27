import pandas as pd


utilities = pd.read_csv('utilities.csv')
substations = pd.read_csv('substations.csv')
lines = pd.read_csv('lines.csv')

# Join Substations with Utilities on 'utility_id'
substations_util = pd.merge(
    substations,
    utilities,
    on='utility_id',
    how='left'
)

# Join Lines with Substations+Utilities on 'substation_id'
master_df = pd.merge(
    lines,
    substations_util,
    on='substation_id',
    how='left',
    indicator='join_status'
)

# Identify orphaned lines
orphaned_lines = master_df[master_df['join_status'] == 'left_only']


total_lines = len(lines)
orphan_count = len(orphaned_lines)
data_loss_pct = (orphan_count / total_lines) * 100

print(f"Total Lines Processed: {total_lines}")
print(f"Orphaned Records Identified: {orphan_count}")
print(f"Data Loss Percentage: {data_loss_pct:.2f}%")


clean_master_df = master_df[master_df['join_status'] == 'both'].copy()
clean_master_df.drop(columns=['join_status'], inplace=True)


clean_master_df.to_csv('integrated_master_dataset.csv', index=False)