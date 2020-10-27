#!/usr/bin/env bash

mkdir -p media/PIX2PIX/checkpoints/43kGoldDigger/
mkdir -p media/PIX2PIX/checkpoints/87kGoldDigger/

wget https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EYAW60h1luRGmW-Qqu2lXCIBX2TAxxMuLrrowH2vpyMIuA?download=1 -O media/PIX2PIX/checkpoints/43kGoldDigger/latest_net_G.pth
wget https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EcTS95eKY9JOsBXFnqlUj70Btlyrm3cbPlMXaRCqzPt0Ng?download=1 -O media/PIX2PIX/checkpoints/87kGoldDigger/latest_net_G.pth

