import pandas as pd
import configparser
from configparser import ConfigParser, ExtendedInterpolation

config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
config.read('../../init.config')

METADATA_PATH = config['DEFAULT']['metadata_file']
CORDUID_PATH = config['DEFAULT']['cord_uid_file']
PMCID_PATH = config['DEFAULT']['pmcid_file']

metadata = pd.read_csv(METADATA_PATH, low_memory=False)
corduids = pd.read_csv(CORDUID_PATH, low_memory=False)

#Get those in CORD_UID, that have match in metadata
pmcids = metadata[metadata.cord_uid.isin(corduids.iloc[:,0])]['pmcid']

#Get those in MetaData, that are in the CORD_UID
#pmcids = metadata[~ metadata.cord_uid.isin(corduids.iloc[:,0])]['pmcid']

#Filter those with pmcid
pmcids = pmcids[~pmcids.isna()]

pmcids.to_csv (PMCID_PATH, index = False, header=['pmcid'])