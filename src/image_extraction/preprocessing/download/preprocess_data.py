import pandas as pd
METADATA_PATH = "/workspace/allen/dataset/2020-10-15/metadata.csv"
CORDUID_PATH = "/workspace/allen/Allen-Collection-Curation/input/cord_uid.csv"

metadata = pd.read_csv(METADATA_PATH, low_memory=False)
corduids = pd.read_csv(CORDUID_PATH, low_memory=False)

#Get document not in the file provided
pmcids = metadata[~ metadata.cord_uid.isin(corduids.iloc[:,0])]['pmcid']
#Filter those with pmcid
pmcids = pmcids[~pmcids.isna()]

pmcids.to_csv (r'../../PMCIDS.csv', index = False, header=False)