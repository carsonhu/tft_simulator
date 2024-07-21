# This is for commonly used functions in fated/snipers

import set12_streamlit_snipers
import matplotlib.pyplot as plt
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

def buff_bar(buff_list, num_buffs=1,max_buffs=4, default_item='NoBuff'):
    """Buff Bar: Code for displaying the Buffs input list:
    Each Buff has a name and a level.
    
    Args:
        buff_list (TYPE): List of buffs to add in
        num_buffs (int, optional): Number of buffs in the buff bar
    
    Returns:
        TYPE: Description
    """
    st.header("Global Buffs")
    item_cols = st.columns([3, 1])
    num_buffs = st.slider('Number of Buffs',
    min_value=1, max_value=max_buffs, value=num_buffs)

    index = 0
    if default_item in buff_list:
      index = buff_list.index(default_item)

    buffs = []
    for n in range(num_buffs):
        with item_cols[0]:
          buff1 = st.selectbox(
          'Buff {}'.format(n+1),
           buff_list, key="Buff {}".format(n), index=index)
        with item_cols[1]:
          buff1level = st.selectbox(
          'Level',
           utils.class_for_name('set12buffs', buff1).levels, key="Buff lvl {}".format(n))
        buffs.append((buff1, buff1level))
    return buffs

def plot_df(df, simLists):
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

    # we want this to be comma separated input

    dmg_dict = {}

    for index in indices_to_plot:
        new_entry = {}
        dmgList = pd.DataFrame([[damageInstance[0],
                                 damageInstance[1][0],
                                 damageInstance[1][1]]
                                for damageInstance in
                                simLists[index]["Results"]])
        dmgList.columns = ["Time", "Damage", "Type"]
        dmgList["Total Dmg"] = dmgList["Damage"].cumsum()
        dmgList = dmgList[['Time', 'Damage', 'Total Dmg', 'Type']]

        new_entry['Damage'] = dmgList

        rounded_list = dmgList.round(2)

        # st.write(simLists[to_plot])

        champ_name = simLists[index]["Champ"].name
        champ_level = simLists[index]["Champ"].level

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
            index = st.selectbox('Index Log', list(dmg_dict.keys()),
                                 format_func=lambda x: plot_labels[x])
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

def items_list(items, default_item='NoItem'):
  """Items list: Display 3 select boxes for the 3 items to be calculated.
  
  Args:
      items (list[str]): list of strings for item names
  
  Returns:
      (string, string, string): the 3 items
  """
  index = 0
  if default_item in items:
    index = items.index(default_item)

  col1, col2, col3 = st.columns(3)
  with col1:
    item1 = st.selectbox(
    'Item 1',
     items, index=index)
  with col2:
    item2 = st.selectbox(
    'Item 2',
     items, index=index)
  with col3:
    item3 = st.selectbox(
    'Item 3',
     items, index=index)
  return item1, item2, item3

def enemy_list(key):
  """Enemy list: Configure the base stats of the enemy: HP, Armor, and MR
  
  Args:
      key (string): unique key for streamlit
  
  Returns:
      Champion: a champion with the requested hp, armor, and mr
  """
  st.header("Enemy")

  col1, col2, col3 = st.columns(3)
  with col1:
    hp = st.number_input('Enemy HP',
    min_value=1, max_value=99999, value=1800, key=key + "1")
  with col2:
    armor = st.number_input('Enemy Armor',
    min_value=0, max_value=99999, value=100, key=key + "2")
  with col3:
    mr = st.number_input('Enemy MR',
    min_value=0, max_value=99999, value=100, key=key + "3")
  enemy = DummyTank(1)
  enemy.hp.base = hp
  enemy.armor.base = armor
  enemy.mr.base = mr
  return enemy

def add_items(champ, buffs, add_noitem=False):
  if item != 'NoItem' or add_noitem:
    champ.items.append(utils.class_for_name('set12items', item)())

def add_buffs(champ, buffs, add_noitem=False):
  for buff, level in buffs:
    if buff != 'NoBuff' or add_noitem:
      champ.items.append(utils.class_for_name('set12buffs', buff)(level, []))




def champ_selector(champ_list):
  """champ list: select da champion
  
  Args:
      key (string): unique key for streamlit
  
  Returns:
      Champion: a champion with the requested hp, armor, and mr
  """
  st.header("Champion")
  item_cols = st.columns([3, 1])
  
  with item_cols[0]:
    champ = st.selectbox(
    'Champion',
     champ_list)
  with item_cols[1]:
    champlevel = st.selectbox(
    'Level',
     [1, 2, 3])
  return utils.class_for_name('set12champs', champ)(champlevel)

