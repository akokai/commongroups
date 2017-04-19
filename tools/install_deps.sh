#!/bin/bash
# Install dependencies for Common Groups with conda and initialize PostgreSQL.
# Usage:
#   install_deps.sh -n name -d datadir [-f] [-s]
# Options:
#   name:     Name of conda environment to use
#   datadir:  Path to PostgreSQL data directory
#   -f:       Install full dependencies for development environment
#   -s:       Skip PostgreSQL setup
# Based on install guide: http://www.rdkit.org/docs/Install.html

usage="Usage: install_deps.sh -n name -d datadir [-f] [-s]"
# Name of database to create:
rdkitdb="cmgdata"

while getopts ":n:d:fs" opt; do
  case $opt in
    n ) name=$OPTARG ;;
    d ) datadir=$OPTARG ;;
    f ) fulldeps=1 ;;
    s ) rdkitdb="" ;;
    \?) echo $usage; exit 1
  esac
done
shift $(($OPTIND - 1))

if [ -z $name ]; then
  echo $usage
  exit 1
elif [ $rdkitdb ] && [ -z $datadir ]; then
  echo $usage
  exit 1
fi

# Test to see if conda is accessible.
condaver=$(conda -V)
if ! [ $? -eq 0 ]; then
  echo "Unable to run conda. Exiting."
  exit 1
fi

# Determine currently active conda environment
active=$(conda info --envs | grep "*" | awk -F ' ' '{print $1}')
if [ $active != "root" ]; then
  echo "Switching to root conda environment before proceeding"
  source deactivate
fi

# Determine conda environments directory
envsdir=$(conda info | grep envs | awk -F ' : ' '{print $2}')
if [ -d $envsdir ]; then
  echo "Conda environments directory found: $envsdir"
else
  echo "Unable to verify conda environments directory: $envsdir"
  echo "Exiting."
  exit 1
fi

# Install software using conda
##############################
# Packages available in anaconda/rdkit channel: https://anaconda.org/rdkit/repo

# Install minimal environment
conda create -c rdkit -n $name rdkit-postgresql cairocffi cairo
conda install -n $name pandas pillow psycopg2 pytest requests sqlalchemy xlrd xlsxwriter
# For oauth2client, pip will install dependencies (pyasn1, pyasn1-modules, rsa)
$envsdir/$name/bin/pip install ashes boltons commongroups oauth2client
# Prevent pip/gspread from trying to update requests (already installed)
$envsdir/$name/bin/pip install --no-deps gspread

# Optionally install full development environment
if [ $fulldeps ]; then
  conda install -n $name ipython jupyter sphinx
fi

# Set up PostgreSQL
###################
echo

if [ -z $rdkitdb ]; then
  echo "Skipping PostgreSQL database setup."
  echo "Done."
  echo "====="
  exit 0
fi

echo "Continue setting up PostgreSQL database? (y/[n])"
read ans
if ! [[ "${ans:=n}" =~ [Yy].* ]]; then
  echo "Exiting."
  exit 0
fi

if [ ${PGDATA:+1} ]; then
  echo "Warning: \$PGDATA environment variable exists. Attempting to unset."
  unset PGDATA
fi

echo "Creating directory $datadir with permissions 0700"
mkdir -p $datadir
chmod 0700 $datadir

echo "Setting up PostgreSQL..."
$envsdir/$name/bin/initdb -D $datadir
$envsdir/$name/bin/pg_ctl -D $datadir start
wait
# This is not a good way of waiting for the database to start, but...
echo "... waiting for PostgreSQL server to start..."
sleep 10
echo
echo "Creating database $rdkitdb and adding RDKit extension..."
$envsdir/$name/bin/createdb $rdkitdb
$envsdir/$name/bin/psql $rdkitdb -c 'create extension rdkit;'
$envsdir/$name/bin/pg_ctl -D $datadir stop
wait

echo
echo "Done."
echo "====="
echo
echo "Notes:"
echo "------"
echo "Your database URL is: postgresql://$USER@localhost/$rdkitdb"
echo "==> Add this to your Common Groups home environment configuration."
echo "To start the PostgreSQL database server, run"
echo "  $envsdir/$name/bin/pg_ctl -D $datadir start"
echo "To shut down the server, run:"
echo "  $envsdir/$name/bin/pg_ctl -D $datadir stop"
echo "You may want to edit $datadir/postgresql.conf to institute these settings:"
echo "  shared_buffers = 2048MB"
echo "  work_mem = 128MB"
exit 0
