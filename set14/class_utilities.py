# This is for commonly used functions in fated/snipers

import set14_streamlit_main
import matplotlib.pyplot as plt
import streamlit as st
import set14buffs
import set14champs
import set14items
from set14buffs import *
from set14champs import *
from set14items import *
# import plotly.graph_objects as go
import pandas as pd
import numpy as np
import itertools
import utils


def buff_bar(buff_list, num_buffs=1, max_buffs=4, starting_buffs=[], default_item='NoBuff'):
    """Buff Bar: Code for displaying the Buffs input list:
    Each Buff has a name and a level.
    
    Args:
        buff_list (TYPE): List of buffs to add in
        num_buffs (int, optional): Number of buffs in the buff bar
    
    Returns:
        tuple: (buff name, buff level, params)
    """
    st.header("Global Buffs")
    item_cols = st.columns([2, 1, 1])
    num_buffs = st.slider('Number of Buffs',
    min_value=1, max_value=max_buffs, value=max(num_buffs, len(starting_buffs)))
    buffs = []
    
    for n in range(num_buffs):
        index = 0
        if default_item in buff_list:
            index = buff_list.index(default_item)
        with item_cols[0]:
            if n < len(starting_buffs):
                if starting_buffs[n] in buff_list:
                    index = buff_list.index(starting_buffs[n])
            buff1 = st.selectbox(
            'Buff {}'.format(n+1),
             buff_list, key="Buff {}".format(n), index=index)
        with item_cols[1]:
            buff1level = st.selectbox(
            'Level',
             utils.class_for_name('set14buffs', buff1).levels, key="Buff lvl {}".format(n))
        with item_cols[2]:
            extraParams = utils.class_for_name('set14buffs', buff1).extraParameters()
            if extraParams != 0:
                buff1Extra = st.number_input(extraParams["Title"],
                                             min_value=extraParams["Min"],
                                             max_value=extraParams["Max"],
                                             value=extraParams["Default"],
                                             key=extraParams["Title"] + str(n))
            else:
                buff1Extra = st.number_input("(ignore)",
                                             min_value=0,
                                             max_value=0,
                                             value=0,
                                             key="extra buff" + buff1 + str(n))               
        buffs.append((buff1, buff1level, buff1Extra))
    return buffs


def divinicorp_selector(champion):
    st.header("Divinicorp Buffs")
    item_cols = st.columns(2)
    
    buffs = []
    
    divines = {"Morgana": False, "Senna": False, "Vex": False, "Renekton": False}
    for index, name in enumerate(list(divines.keys())):
        with item_cols[index % 2]:
            champ_divine = champion.name == name
            divines[name] = st.checkbox(name, value=champ_divine)
    champion.divines = divines

def write_champion(champ):
    st.subheader("Base stats")
    cols = st.columns(4)
    ad_text = f"AD: :blue[{round(champ.atk.stat, 2)}] = {champ.atk.base} * :green[{round(champ.atk.mult, 4)} AD]"
    ap_text = f"AP: :blue[{round(champ.ap.stat, 2)}] = {champ.ap.base} + :green[{round(champ.ap.add, 2)} AP]" \
              if champ.ap.addMultiplier == 1 else \
              f"AP: :blue[{round(champ.ap.stat, 2)}] = {champ.ap.base} + :red[{champ.ap.addMultiplier}] * :green[{round(champ.ap.add, 2)} AP]"
    dmgamp_text = f"DmgAmp: :blue[{round(champ.dmgMultiplier.stat, 2)}] = {champ.dmgMultiplier.base} + :green[{round(champ.dmgMultiplier.add, 4)} DmgAmp]"    
    mana_text = f"Mana: :blue[{round(champ.curMana, 2)}] / :blue[{round(champ.fullMana.stat, 2)}]"
    cast_text = f"Cast Time: :blue[{champ.castTime} seconds]"

    as_text = f"AS: :blue[{round(champ.aspd.stat, 3)}] = {champ.aspd.base} * (1 + :green[{round(champ.aspd.add, 4)} AS])"
    crit_chance_text = f"Crit Chance: :blue[{round(champ.crit.stat, 3)}] = {champ.crit.base} + :green[{round(champ.crit.add, 4)} Crit]"
    crit_dmg_text = f"Crit Dmg: :blue[{round(champ.critDmg.stat, 2)}] = {champ.critDmg.base} + :green[{round(champ.critDmg.add, 4)} CritDmg]"
    mana_gen_text = f"ManaGen: :blue[{round(champ.manaPerAttack.stat, 2)}] = {champ.manaPerAttack.base} + :green[{round(champ.manaPerAttack.add, 2)} Mana]"
    can_spellcrit_text = f"Can SpellCrit: :blue[{champ.canSpellCrit}]"
    with cols[0]:
        st.write(f"""
          {ad_text}
          <br>
          {ap_text}
          <br>
          {dmgamp_text}
          <br>
          {mana_text}
          <br>
          {cast_text}
          """, unsafe_allow_html=True)
    with cols[1]:
        st.write(f"""
          {as_text}
          <br>
          {crit_chance_text}
          <br>
          {crit_dmg_text}
          <br>
          {mana_gen_text}
          <br>
          {can_spellcrit_text}
          """, unsafe_allow_html=True)
    if champ.notes:
        st.write("Notes: " + champ.notes)

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
                                 damageInstance[1][1],
                                 damageInstance[2],
                                 damageInstance[3]]
                                for damageInstance in
                                simLists[index]["Results"]])
        dmgList.columns = ["Time", "Dmg", "Type", "AS", "Mana"]
        dmgList["Total Dmg"] = dmgList["Dmg"].cumsum()
        dmgList = dmgList[['Time', 'Dmg', 'Total Dmg', 'Type', 'AS', 'Mana']]

        new_entry['Dmg'] = dmgList

        rounded_list = dmgList.round(2)

        # st.write(simLists[to_plot])

        champ_name = simLists[index]["Champ"].name
        # champ_level = simLists[index]["Champ"].level
        champ_item = simLists[index]["Extra"].name

        new_entry['Name'] = champ_name
        # new_entry['Level'] = champ_level
        new_entry['Item'] = champ_item
        dmg_dict[index] = new_entry

      # label

    col1, col2 = st.columns([3, 1])

    plot_labels = {key: '{}: {}'.format(key,
                                           value['Item']) for key, value in dmg_dict.items()}

    # setting the title

    if len(dmg_dict) > 0:
        with col1:
        #     fig = go.Figure()
        #     fig.update_layout(
        #       title="{} Damage Chart".format(champ_name),
        #       xaxis_title = "Time",
        #       yaxis_title = "Damage",
        #       hovermode = "x unified")
            fig, ax = plt.subplots()
            ax.set_title('{} Damage Chart'.format(champ_name))
            ax.set_xlabel('Time')
            ax.set_ylabel('Damage')
        with col2:
            index = st.selectbox('Index Log', list(dmg_dict.keys()),
                                 format_func=lambda x: plot_labels[x])
            st.dataframe(dmg_dict[index]['Dmg'].round(2), hide_index=True, column_config={"Total Dmg": None})

    for key, value in dmg_dict.items():
        # with col1:
          # fig.add_trace(go.Line(x=value['Dmg']['Time'],
          #                       y=value['Dmg']['Total Dmg'],
          #                       name=plot_labels[key]))
          ax.plot(value['Dmg']['Time'],
                  value['Dmg']['Total Dmg'],
                  label=plot_labels[key])
          ax.legend()

    if len(dmg_dict) > 0:
        with col1:
            # st.plotly_chart(fig)
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

  #col1, col2, col3 = st.columns(3)

  item1 = st.selectbox(
  'Item 1',
   items, index=index)
  item2 = st.selectbox(
  'Item 2',
   items, index=index)
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

def first_takedown(key, champ):
    """Enemy list: Configure the base stats of the enemy: HP, Armor, and MR
    
    Args:
        key (string): unique key for streamlit
    
    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """

    # st.subheader("First takedown")
    first_takedown = st.number_input('Time of first takedown',
                                     min_value=1, max_value=30,
                                     value=5, key=key)
    champ.first_takedown = first_takedown

def bonus_stats(key, champ):
    """Enemy list: Configure the base stats of the enemy: HP, Armor, and MR
    
    Args:
        key (string): unique key for streamlit
    
    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """

    # st.subheader("First takedown")
    cols = st.columns(3)
    with cols[0]:
      ad_bonus = st.number_input('Bonus AD',
                                       min_value=0, max_value=2000,
                                       value=0, key=key + "ad")
    with cols[1]:
      ap_bonus = st.number_input('Bonus AP',
                                       min_value=0, max_value=2000,
                                       value=0, key=key + "ap")
    with cols[2]:
      as_bonus = st.number_input('Bonus AS',
                                       min_value=0, max_value=200,
                                       value=0, key=key + "AS")
    # with col2:
    #   crit_bonus = st.number_input('Bonus Crit',
    #                                    min_value=0, max_value=200,
    #                                    value=0, key=key + "crit")
    #   crit_dmg_bonus = st.number_input('Bonus Crit Dmg',
    #                                    min_value=0, max_value=200,
    #                                    value=0, key=key + "critdmg")
    champ.atk.addStat(ad_bonus)
    champ.ap.addStat(ap_bonus)
    champ.aspd.addStat(as_bonus)
    # champ.crit.addStat(crit_bonus)
    # champ.critDmg.addStat(crit_dmg_bonus)


def num_traits(key, champ):
    """num traits
    
    Args:
        key (string): unique key for streamlit
    
    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """

    # st.subheader("Number of traits")
    traits = st.number_input('Number of active traits',
                                     min_value=0, max_value=12,
                                     value=6, key=key)
    champ.num_traits = traits
    

def add_items(champ, buffs, add_noitem=False):
  if item != 'NoItem' or add_noitem:
    champ.items.append(utils.class_for_name('set14items', item)())

def add_buffs(champ, buffs, add_noitem=False):
  for buff, level, extraParams, in buffs:
    if buff != 'NoBuff' or add_noitem:
      champ.items.append(utils.class_for_name('set14buffs', buff)(level, extraParams))



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
    levels = [1, 2, 3]
    if utils.class_for_name('set14champs', champ).canFourStar:
      levels.append(4)
    champlevel = st.selectbox(
    'Level',
     levels, index=1)

    

  new_champ = utils.class_for_name('set14champs', champ)(champlevel)
  return new_champ

