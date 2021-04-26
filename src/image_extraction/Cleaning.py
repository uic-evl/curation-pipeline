import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('init.config')

metadata_file = config['DEFAULT']['metadata_file']
pmcid_file = config['DEFAULT']['pmcid_file']

print("Loading only PMCID column from metadata")
df = pd.read_csv(metadata_file, usecols=['pmcid'])

print("Clean NaN")
df = df[df.pmcid.notna()]

print("Exported a new csv file")
df.to_csv (pmcid_file, index = False)