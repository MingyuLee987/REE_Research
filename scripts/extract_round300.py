"""Cached extraction of screened sources from the supplementary collection."""
import json
from pathlib import Path
from ree_research.extraction import extract

ROOT=Path(__file__).resolve().parents[1]
# Scope and target screening: the other downloaded sources contain passive-current,
# pitting-potential, refractory-corrosion or weight-loss outcomes only.
SCREENED=['springer_S2070205124702265','springer_S2070205125700261','ijes444',
          'jcscp_bce','wiley_adem.202402545']

def main():
    for name in SCREENED:
        source=ROOT/'data/raw/round300/sources'/name
        out=ROOT/'data/processed/extractions'/('r300_'+name)
        if (out/'run.json').exists():
            print(name,json.loads((out/'run.json').read_text())['rows'],'cached')
            continue
        try:print(name,extract(source,out,reuse_response=(out/'response.json').exists()))
        except (ValueError,RuntimeError) as error:print(name,str(error))

if __name__=='__main__':main()
