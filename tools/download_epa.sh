#!/bin/bash
# Download some datasets from the US EPA CompTox Dashboard.

if ! [ $1 ]; then
  echo "Usage: download_epa.sh dest_dir" ; exit 1
fi

if ! [ -d $1 ]; then
  echo "Creating directory: $1"
  mkdir -p $1
fi

wget --version > /dev/null 2>&1
if ! [ $? -eq 0 ]; then
  echo "Install wget before running this script."
  exit 1
fi

unzip -h > /dev/null 2>&1
if ! [ $? -eq 0 ]; then
  echo "Install zip/unzip before running this script."
  exit 1
fi

echo "Downloading files to $1"

wget -P $1 "ftp://newftp.epa.gov/COMPTOX/Sustainable_Chemistry_Data/Chemistry_Dashboard/DSSTox_Mapping_20160701.zip"
wget -P $1 "ftp://newftp.epa.gov/COMPTOX/Sustainable_Chemistry_Data/Chemistry_Dashboard/Dsstox_CAS_number_name.xlsx"
wget -P $1 "ftp://newftp.epa.gov/COMPTOX/Sustainable_Chemistry_Data/Chemistry_Dashboard/PubChem_DTXSID_mapping_file.txt"

echo "Unzipping and deleting DSSTox Mapping file."
unzip -d $1 $1/DSSTox_Mapping_20160701.zip
rm $1/DSSTox_Mapping_20160701.zip

if [ $? -eq 0 ]; then
  echo "Done."
fi
