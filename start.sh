#!/bin/bash

# Install dependencies
echo "\nInstalling dependencies...\n"
pip install -r requirements.txt


# Install dependencies of NTLFlowLyzer
NTLFlowLyzer_PATH="./libs/NTLFlowLyzer"
CAMEBACK_PATH=$(pwd)

echo "\nInstalling dependencies of NTLFlowLyzer...\n"
cd $NTLFlowLyzer_PATH

pip install -r requirements.txt
python3 setup.py install

cd $CAMEBACK_PATH

