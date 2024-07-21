import sys
sys.path.append("..")
import set12_streamlit_snipers
import streamlit as st
from set12buffs import *
from set12champs import *
from set12items import *
import pandas as pd
import numpy as np
import itertools

st.set_page_config(layout="wide")

t = 30
simLists = []
simDict = {}
# this is going to be individual champ tab
st.header("Ashe")

# for now, just copy over the functionality

# items
ADComboList = set12_streamlit_snipers.getComboList([NoItem(),
           IE(),
           HoJ(),
           GS(),
           RH(),
           LW(),
           Shojin(),
           Blue(),
           Rageblade(),
           Red(),
           DB(),
           Nashors(),
           Guardbreaker()], 3)

# buffs
asheBuffList = set12_streamlit_snipers.getComboList([NoBuff(0, []),
                            Multistriker(3, [])], 2, False)

if st.button('Run trials'):
  simLists = set12_streamlit_snipers.doExperiment(Ashe(2), DummyTank(2), ADComboList, asheBuffList, t)

  df = set12_streamlit_snipers.createUnitDPSTable(simLists)
  st.write(df)