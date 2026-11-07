#!/usr/bin/env bash
# Re-download every raw input used by the pipeline (run from the repository root).
set -e
mkdir -p data/raw/{csbc,elections/pollbypoll,trade,btos,programs}
# 1. Statistics Canada tables (Web Data Service -> full-table CSV zip)
for t in 33100990 33100992 33100993 33101004 33101026 33101028 33101029 33101031 33101036 33101045 \
         33101067 33101069 33101070 33101071 33101080 33101107 33101109 33101110 33101111 33101113 33101129 \
         33101146 33101148 33101149 33101150 33101152 33101167 33101186 33101188 33101189 33101190 33101192 33101207; do
  url=$(curl -s "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/$t/en" | python -c "import sys,json;print(json.load(sys.stdin)['object'])")
  curl -s -o data/raw/csbc/$t.zip "$url" && unzip -o -q data/raw/csbc/$t.zip -d data/raw/csbc
done
url=$(curl -s "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/12100175/en" | python -c "import sys,json;print(json.load(sys.stdin)['object'])")
curl -s -o data/raw/trade/12100175.zip "$url" && unzip -o -q data/raw/trade/12100175.zip -d data/raw/trade
# 2. Elections Canada, 45th general election
for t in 8 11 12; do curl -s -A "Mozilla/5.0" -o data/raw/elections/table${t}E.html "https://www.elections.ca/res/rep/off/ovrGE45/62/table${t}E.html"; done
curl -s -A "Mozilla/5.0" -o data/raw/elections/byed_page.html "https://www.elections.ca/content.aspx?section=res&dir=rep/off/45gedata&document=byed&lang=e"
grep -o -E 'pollbypoll_bureauparbureau[0-9]+\.csv' data/raw/elections/byed_page.html | sort -u | while read f; do
  curl -s -A "Mozilla/5.0" -o data/raw/elections/pollbypoll/$f "https://www.elections.ca/res/rep/off/ovrGE45/62/data_donnees/$f"; done
# 3. US Census BTOS flat files
for f in National State Sector; do curl -s -L -A "Mozilla/5.0" -o data/raw/btos/$f.xlsx "https://www.census.gov/hfp/btos/downloads/$f.xlsx"; done
# 4. Federal grants and contributions (2.4 GB, streamed; only tariff-related rows are kept)
curl -s -L "https://open.canada.ca/data/dataset/432527ab-7aac-45b5-81d6-7597107a7013/resource/1d15a62f-5656-49ad-8c88-f40ce689d831/download/grants.csv" \
 | python code/filter_grants_stream.py > data/raw/programs/grants_tariff_filtered.csv
