import sys
sys.path.append("..")
import set12_streamlit_snipers
import streamlit as st
import set12items
import set12buffs
import set12champs
import class_utilities
import pandas as pd
import numpy as np
import itertools
import utils
import inspect

st.set_page_config(layout="wide")

t = 30
simLists = []
simDict = {}
# this is going to be individual champ tab

champ_list = set12champs.champ_list

all_items = []
all_buffs = []

all_items = set12items.offensive_craftables + set12items.artifacts \
            + set12items.radiants + set12items.no_item

# for name, obj in inspect.getmembers(set12items, inspect.isclass):
#     # st.write(dir(obj))
#     if name != 'Item':
#       all_items.append(name)


for name, obj in inspect.getmembers(set12buffs, inspect.isclass):
    # st.write(dir(obj))
    if name != 'Buff':
      all_buffs.append(name)


with st.sidebar:

    champ = class_utilities.champ_selector(champ_list)

    st.header("Global Items")

    items = class_utilities.items_list(all_items)
    
    # we want to rework this
    # default_buffs = [this dude's]
    buffs = class_utilities.buff_bar(all_buffs, max_buffs=10, num_buffs=2)

    enemy = class_utilities.enemy_list("Champ selector")


    # Add items to Champion
    for item in items:
      if item != 'NoItem':
        champ.items.append(utils.class_for_name('set12items', item)())
    class_utilities.add_buffs(champ, buffs)
    

    st.write(champ.items)
    st.write([item.__class__.__name__ for item in champ.items])

# if st.button('Run trials'):
simLists = set12_streamlit_snipers.doExperimentOneExtra(champ, enemy,
           utils.convertStrList('set12items', all_items), [], t)

# Header
st.header("{} {}".format(champ.name, champ.level))


# checkboxes

checkbox_cols = st.columns(11)

with checkbox_cols[0]:
  craftables = st.checkbox("Craftable", value=True)
with checkbox_cols[1]:
  artifacts = st.checkbox("Artifact", value=False)
with checkbox_cols[2]:
  radiants = st.checkbox("Radiant", value=False)

df = set12_streamlit_snipers.createSelectorDPSTable(simLists)
df_flt = df

if not craftables:
  df_flt = df_flt[~df_flt['Extra class name'].isin(set12items.offensive_craftables)]

if not artifacts:
  df_flt = df_flt[~df_flt['Extra class name'].isin(set12items.artifacts)]

if not radiants:
  df_flt = df_flt[~df_flt['Extra class name'].isin(set12items.radiants)]

new_df = df_flt.drop('Extra class name', axis=1)
class_utilities.plot_df(new_df, simLists)
# st.write(new_df)

