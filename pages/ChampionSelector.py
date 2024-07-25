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

champ_list = sorted(set12champs.champ_list)

# all_items = []
all_buffs = []

all_items = sorted(set12items.offensive_craftables + set12items.artifacts \
            + set12items.radiants + set12items.no_item)

aug_buffs = sorted(set12buffs.augments)

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

    if hasattr(champ, 'num_targets'):
        targets = st.slider(
        'number of targets', min_value=1, max_value=max(3, champ.num_targets+1), value=champ.num_targets)
        champ.num_targets = targets

    st.header("Global Items")

    items = class_utilities.items_list(all_items)
    
    # we want to rework this
    # default_buffs = [this dude's]
    buffs = class_utilities.buff_bar(all_buffs, max_buffs=10, num_buffs=2,
                                     starting_buffs=champ.default_traits)

    extra_buffs = []
    for buff in buffs:
        levels = utils.class_for_name('set12buffs', buff[0]).levels
        for level in levels:
            if level != buff[1]:
                extra_buffs.append(utils.class_for_name('set12buffs', buff[0])(level, []))


    enemy = class_utilities.enemy_list("Champ selector")

    class_utilities.first_takedown("Takedown", champ)

    # Add items to Champion
    for item in items:
      if item != 'NoItem':
        champ.items.append(utils.class_for_name('set12items', item)())
    class_utilities.add_buffs(champ, buffs)
    

    st.write(champ.items)
    st.write([item.__class__.__name__ for item in champ.items])
    st.write(aug_buffs)
    st.write(utils.convertBuffList('set12buffs', aug_buffs))

# if st.button('Run trials'):
simLists = set12_streamlit_snipers.doExperimentOneExtra(champ, enemy,
           utils.convertStrList('set12items', all_items),
           utils.convertStrList('set12buffs', aug_buffs) + extra_buffs, t)

# Header
st.header("{} {} vs {} HP, {} Armor, {} MR".format(champ.name, champ.level,
                                                   enemy.hp.stat,
                                                   enemy.armor.stat,
                                                   enemy.mr.stat))

# checkboxes

checkbox_cols = st.columns(10)

with checkbox_cols[0]:
    craftables = st.checkbox("Craftable", value=True)
with checkbox_cols[1]:
    artifacts = st.checkbox("Artifact", value=False)
with checkbox_cols[2]:
    radiants = st.checkbox("Radiant", value=False)
with checkbox_cols[3]:
    traits = st.checkbox("Trait", value=False)
with checkbox_cols[4]:
    augments = st.checkbox("Augment", value=False)

df = set12_streamlit_snipers.createSelectorDPSTable(simLists)
df_flt = df

if not craftables:
    df_flt = df_flt[~df_flt['Extra class name'].isin(set12items.offensive_craftables)]
if not artifacts:
    df_flt = df_flt[~df_flt['Extra class name'].isin(set12items.artifacts)]
if not radiants:
    df_flt = df_flt[~df_flt['Extra class name'].isin(set12items.radiants)]
if not traits:
    df_flt = df_flt[~df_flt['Extra class name'].isin([x[0] for x in buffs])]
if not augments:
    df_flt = df_flt[~df_flt['Extra class name'].isin(set12buffs.augments)]
new_df = df_flt.drop(['Extra class name', 'Name', 'Level'], axis=1)
class_utilities.plot_df(new_df, simLists)
# st.write(new_df)

