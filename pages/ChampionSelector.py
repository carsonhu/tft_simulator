import sys
sys.path.append("..")
import set13_streamlit_snipers
import streamlit as st
import set13items
import set13buffs
import set13champs
import class_utilities
import pandas as pd
import numpy as np
import copy
import itertools
import utils
import inspect

st.set_page_config(layout="wide")

t = 30
simLists = []
simDict = {}
# this is going to be individual champ tab

# Inject custom CSS to set the width of the sidebar
# st.markdown(
#     """
#     <style>
#         section[data-testid="stSidebar"] {
#             width: 500px !important; # Set the width to your desired value
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


champ_list = sorted(set13champs.champ_list)

# all_items = []
all_buffs = sorted(set13buffs.class_buffs + set13buffs.augments
            + set13buffs.no_buff + set13buffs.stat_buffs)

all_items = sorted(set13items.offensive_craftables + set13items.artifacts
            + set13items.radiants + set13items.no_item)

aug_buffs = sorted(set13buffs.augments)

anomalies = sorted(set13buffs.anomalies + set13buffs.no_buff)

# for name, obj in inspect.getmembers(set13items, inspect.isclass):
#     # st.write(dir(obj))
#     if name != 'Item':
#       all_items.append(name)

# for name, obj in inspect.getmembers(set13buffs, inspect.isclass):
#     # st.write(dir(obj))
#     if name != 'Buff':
#         all_buffs.append(name)

champ_before_sims = None

with st.sidebar:

    champ = class_utilities.champ_selector(champ_list)

    if hasattr(champ, 'num_targets') and champ.num_targets > 0:
        targets = st.slider(
        'number of targets', min_value=1, max_value=max(3, champ.num_targets+1), value=champ.num_targets)
        champ.num_targets = targets

    with st.popover("Extra options"):
        class_utilities.first_takedown("Takedown", champ)
        class_utilities.num_traits("Num traits", champ)
        class_utilities.rebel_time("Rebel", champ)
        class_utilities.bonus_stats("Bonus Stats", champ)


    st.header("Global Items")

    items = class_utilities.items_list(all_items)
    
    # we want to rework this
    # default_buffs = [this dude's]
    buffs = class_utilities.buff_bar(all_buffs, max_buffs=10, num_buffs=2,
                                     starting_buffs=champ.default_traits)

    chosen_anomaly = class_utilities.anomaly_bar(anomalies)

    if chosen_anomaly != 'NoBuff':
        class_utilities.add_anomaly(champ, chosen_anomaly)

    extra_buffs = []
    for buff in buffs:
        levels = utils.class_for_name('set13buffs', buff[0]).levels
        for level in levels:
            if level != buff[1]:
                extra_buffs.append(utils.class_for_name('set13buffs', buff[0])(level, buff[2]))

        # extraParameters = utils.class_for_name('set13buffs', buff1).extraParameters()
        # if extraParameters != 0:

    enemy = class_utilities.enemy_list("Champ selector")


    # Add items to Champion
    for item in items:
      if item != 'NoItem':
        champ.items.append(utils.class_for_name('set13items', item)())
    class_utilities.add_buffs(champ, buffs)

    champ_before_sims = copy.deepcopy(champ)

# if st.button('Run trials'):

if chosen_anomaly == 'NoBuff':
    for anomaly in anomalies:
        if anomaly != 'NoBuff':
            extra_buffs.append(utils.class_for_name('set13anomalies', anomaly)(1, []))

simLists = set13_streamlit_snipers.doExperimentOneExtra(champ, enemy,
           utils.convertStrList('set13items', all_items),
           utils.convertStrList('set13buffs', aug_buffs) + extra_buffs, t)

tab1, tab2 = st.tabs(["Items", "Radiant Refractor"])

with tab1:
    # Header
    st.header("{} {} vs {} HP, {} Armor, {} MR".format(champ_before_sims.name, champ_before_sims.level,
                                                       enemy.hp.stat,
                                                       enemy.armor.stat,
                                                       enemy.mr.stat))

    st.write("Most cast times/manalock times are guesses. Units can cast after they have completed 30\% of an autoattack. Simulator is probably not very accurate to true gameplay at high attack speeds.")

    itemSimulator = set13_streamlit_snipers.Simulator()
    itemSimulator.itemStats(champ_before_sims.items, champ_before_sims)

    class_utilities.write_champion(champ_before_sims)

    # checkboxes

    display_dps = st.checkbox("Display DPS", value=False)

    options = ["Craftable", "Artifact", "Radiant", "Trait", "Augment/Buff"]
    if len([item for item in items if item != 'NoItem']) >= 3:
        options = ["Trait", "Augment/Buff"]
    if chosen_anomaly == 'NoBuff':
        options.append("Anomaly")
    radio_value = st.radio("",
                           options, index=0, horizontal=True)

    # checkbox_cols = st.columns(10)

    # with checkbox_cols[0]:
    #     craftables = st.checkbox("Craftable", value=True)
    # with checkbox_cols[1]:
    #     artifacts = st.checkbox("Artifact", value=False)
    # with checkbox_cols[2]:
    #     radiants = st.checkbox("Radiant", value=False)
    # with checkbox_cols[3]:
    #     traits = st.checkbox("Trait", value=False)
    # with checkbox_cols[4]:
    #     augments = st.checkbox("Augment", value=False)

    df = set13_streamlit_snipers.createSelectorDPSTable(simLists)
    df_flt = df

    if radio_value == "Craftable":
        df_flt = df_flt[df_flt['Extra class name'].isin(set13items.offensive_craftables+['NoItem'])]
    if radio_value == "Artifact":
        df_flt = df_flt[df_flt['Extra class name'].isin(set13items.artifacts+['NoItem'])]
    if radio_value == "Radiant":
        df_flt = df_flt[df_flt['Extra class name'].isin(set13items.radiants+['NoItem'])]
    if radio_value == "Trait":
        df_flt = df_flt[df_flt['Extra class name'].isin([x[0] for x in buffs]+['NoItem'])]
    if radio_value == "Augment/Buff":
        df_flt = df_flt[df_flt['Extra class name'].isin(set13buffs.augments+ ['NoItem'])]
    if radio_value == "Anomaly":
        df_flt = df_flt[df_flt['Extra class name'].isin(set13buffs.anomalies + ['NoItem'])]
    # if not craftables:
    #     df_flt = df_flt[~df_flt['Extra class name'].isin(set13items.offensive_craftables)]
    # if not artifacts:
    #     df_flt = df_flt[~df_flt['Extra class name'].isin(set13items.artifacts)]
    # if not radiants:
    #     df_flt = df_flt[~df_flt['Extra class name'].isin(set13items.radiants)]
    # if not traits:
    #     df_flt = df_flt[~df_flt['Extra class name'].isin([x[0] for x in buffs])]
    # if not augments:
    #     df_flt = df_flt[~df_flt['Extra class name'].isin(set13buffs.augments)]
    new_df = df_flt.drop(['Extra class name', 'Name', 'Level'], axis=1)

    if not display_dps:
        new_df = new_df.drop(['Extra DPS ({}s)'.format(i) for i in [5, 10, 15, 20]], axis=1)
    else:
        new_df = new_df.drop(['DPS at {}'.format(i) for i in [5, 10, 15, 20, 25]], axis=1)

    class_utilities.plot_df(new_df, simLists)
    # st.write(new_df)

