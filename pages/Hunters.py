import sys
sys.path.append("..")
import set12_streamlit_snipers
import matplotlib.pyplot as plt
import class_utilities
import streamlit as st
import set12buffs
import set12champs
import set12items
from set12buffs import *
from set12champs import *
from set12items import *
import pandas as pd
import numpy as np
import itertools
import utils

st.set_page_config(page_title="Hunters",
                   page_icon="📈",
                   layout="wide")

st.markdown("# Hunter Demo")
st.sidebar.header("Hunter Demo")
st.write(
    """we sniping"""
)

sniper_items = ['NoItem',
              'Rageblade',
              'IE',
              'HoJ',
              'GS',
              'RH',
              'LW',
              'Shojin',
              'DB',
              'Nashors',
              'Guardbreaker']
hunter_buffs = ['Hunter', 'ASBuff', 'NoBuff']

twitch_buffs = ['Frost', 'NoBuff']

with st.sidebar:

    st.header("Global Items")

    item1, item2, item3 = class_utilities.items_list(sniper_items)

    # Global Buffs
    st.header("Global Buffs")
    item_cols = st.columns([3, 1])
    num_buffs = st.slider('Number of Buffs',
    min_value=1, max_value=4)


    buffs = []
    for n in range(num_buffs):
        with item_cols[0]:
          buff1 = st.selectbox(
          'Buff {}'.format(n+1),
           hunter_buffs, key="Buff {}".format(n))
        with item_cols[1]:
          buff1level = st.selectbox(
          'Level',
           utils.class_for_name('set12buffs', buff1).levels, key="Buff lvl {}".format(n))
        buffs.append((buff1, buff1level))

    st.header("Twitch")

    twitch_targets = st.slider(
    'number of targets', min_value=1, max_value=3, value=2)
    # given a set of items and buffs
    # do it on these champions

    with item_cols[0]:      
      twitch_buff = st.selectbox(
            'Buff {}'.format(1),
             twitch_buffs, key="twitch Buff {}".format(1))
    with item_cols[1]:
      buff1level = st.selectbox(
      'Level',
       utils.class_for_name('set12buffs', twitch_buff).levels, key="twitch Buff lvl {}".format(n))      

    twitches = [Twitch(i) for i in range(1, 3)]
    for twitch in twitches:
      twitch.num_targets = twitch_targets
      twitch.items.append(utils.class_for_name('set12buffs', twitch_buff)(buff1level, []))

    st.header("Enemy")

    enemy = class_utilities.enemy_list("Hunters")


    nomsys = [Nomsy(i) for i in range(1, 4)]
    kogs =  [Kogmaw(i) for i in range(1, 4)]
    champs = twitches + nomsys + kogs

    # Add in global buffs
    for champ in champs:
        for buff, level in buffs:
          champ.items.append(utils.class_for_name('set12buffs', buff)(level, []))

simLists = set12_streamlit_snipers.doExperimentGivenItems(champs, enemy,
        [utils.class_for_name('set12items', item1)(),
        utils.class_for_name('set12items', item2)(),
        utils.class_for_name('set12items', item3)()],
        [utils.class_for_name('set12buffs', buff)(level, []) for buff, level in buffs], 30)
# df.write(simLists)
df = set12_streamlit_snipers.createDPSTable(simLists)
df["To Plot"] = False
df_test = st.data_editor(
    df,
    column_config={
        "To Plot": st.column_config.CheckboxColumn(
            "To Plot",
            help="Which trials to plot",
            default=False,
        )
    },
    hide_index=False,
)
indices_to_plot = df_test.index[df_test["To Plot"]].tolist()
# st.write(df.index[df["To Plot"] == True])

# we want this to be comma separated input

dmg_dict = {}

for index in indices_to_plot:
    new_entry = {}
    dmgList = pd.DataFrame([[damageInstance[0],
                             damageInstance[1][0],
                             damageInstance[1][1]] \
                             for damageInstance in simLists[index][3]])
    dmgList.columns = ["Time", "Damage", "Type"]
    dmgList["Total Dmg"] = dmgList["Damage"].cumsum()
    dmgList = dmgList[['Time', 'Damage', 'Total Dmg', 'Type']   ]

    new_entry['Damage'] = dmgList

    rounded_list = dmgList.round(2)

    # st.write(simLists[to_plot])

    champ_name = simLists[index][0].name
    champ_level = simLists[index][0].level

    new_entry['Name'] = champ_name
    new_entry['Level'] = champ_level
    dmg_dict[index] = new_entry

# label

col1, col2 = st.columns([2, 1])

plot_labels = {key: '{}: {} {}'.format(key, value['Name'],
                value['Level']) for key, value in dmg_dict.items()}

if len(dmg_dict) > 0:
    with col1:
        fig, ax = plt.subplots()
        ax.set_title('Damage Chart')
        ax.set_xlabel('Time')
        ax.set_ylabel('Damage')
    with col2:
        index = st.selectbox('Index Log', list(dmg_dict.keys()), format_func = lambda x : plot_labels[x])
        st.dataframe(dmg_dict[index]['Damage'].round(2))

for key, value in dmg_dict.items():
    with col1:
        ax.plot(value['Damage']['Time'],
                value['Damage']['Total Dmg'],
                label=plot_labels[key])
        ax.legend()

if len(dmg_dict) > 0:
    with col1:
        st.pyplot(fig)

    



# display chart