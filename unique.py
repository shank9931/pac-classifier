import pandas as pd
import odfpy

df = pd.read_excel('canada2.ods', engine='odf', header=1)
print(df['product_type'].unique())
print(df['material_type'].unique())