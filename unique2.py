import pandas as pd
df = pd.read_excel('canada2.ods', engine='odf', header=1, na_filter=False)
print(df['dosage_form'].unique())
print(df['release_mechanism'].unique())