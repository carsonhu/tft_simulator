import set12items as items
import matplotlib.pyplot as plt
from scipy import interpolate
import time
import copy
import csv
from collections import deque, defaultdict
from set12champs import *
import set12buffs as buffs
import numpy as np
import itertools
import xlsxwriter
class Simulator(object):
    def __init__(self):
        self.current_time = 0
        self.frameTime = 1/30
        # self.frameTime = 1/60

    def itemStats(self,items, champion):
        for item in items:
            champion.addStats(item)
        for item in items:
            item.ability("preCombat", 0, champion)
    def simulate(self, items, buffs, champion, opponents, duration):
        # there's no real distinction between items and buffs
        items = items + buffs + champion.items
        champion.items = items
        champion.opponents = opponents
        self.itemStats(items, champion)
        self.current_time = 0
        
        for opponent in opponents:
            opponent.nextAttackTime = duration * 2
        while self.current_time < duration:
            champion.update(opponents, items, self.current_time)
            for opponent in opponents:
                opponent.update(champion, [], self.current_time)
            self.current_time += self.frameTime
        return champion.dmgVector

    def simulateUlt(self, items, buffs, champion, opponents):
      items = items + buffs + champion.items
      champion.items = items
      champion.opponents = opponents
      self.itemStats(items, champion)
      champion.performAbility(opponents, items, 0)
      return champion.dmgVector


# def plotSimulation(items, t):
#     simulator = Simulator()
#     results = simulator.simulate(items, [], aphelios, [aphelios], t)
#     itemNames = ','.join([item.name for item in items])
#     plt.plot(*zip(*results), label = itemNames)


def resNoDmg(res, label):
    a,b = zip(*[(result[0], result[1][0]) for result in res])
    b = np.cumsum(b)
    plt.plot(a,b, label=label)

def plotRes(res, label):
    plt.plot(res[0], res[1], label)

def getDPS(results, time):
    dpsFunc = getDPSFunction(results)
    return dpsFunc(time) / time
    # dpsSum = 0
    # for result in results:
    #     if result[0] < time:
    #         dpsSum += result[1][0]
    # return dpsSum / time

def dpsSplit(results):
    dps = {"physical": 0, "magical": 0, "true": 0}
    for result in results:
        dps[result[1][1]] += result[1][0]
    total = sum(dps.values(), 0.0)
    if total == 0:
        return {k: 0 for k, v in dps.items()}
    else:
        return {k: v / total for k, v in dps.items()}

def getDPSFunction(results):
    # bug: doesnt work if last result is less than desired time
    # e.g u want dps at 20, but only have dps up to 18
    return interpolate.interp1d([a[0] for a in results], np.cumsum([a[1][0] for a in results]))

def createDPSChart(simList):
    for sim in simList:
        dps5s = getDPS(sim[3], 5)
        dps10s = getDPS(sim[3], 10)
        dps15s = getDPS(sim[3], 15)
        print(sim[0].name, [u.name for u in sim[1]], [u.name for u in sim[2]], dps5s, dps10s, dps15s, dpsSplit(sim[3]))
        # we want DPS at 5s, DPS at 10s, DPS at 15

def createUltDamageCSV(simLists):
    headers_arr = ["Champion", "Level", "Items", "Item 1", "Item 2", "Item 3",
                  "Buff 1", "Buff 2", "Damage to Squishy", "Damage to Tank", "Damage to Supertank"]
    workbook = xlsxwriter.Workbook('ult_stats.xlsx')
    dpsDict = {}
    newEntryLength = 0
    count = 0
    for simList in simLists:
      count += 1
      worksheet1 = workbook.add_worksheet(simList[0][0].name + str(simList[0][0].level) + str(count))
      worksheet1.write_row(0, 0, headers_arr)
      worksheet1.freeze_panes(1, 0)
      worksheet1.autofilter('A1:Z9999')
      for index, sim in enumerate(simList):
          new_entry = []
          # Champion
          new_entry.append(sim[0].name)
          new_entry.append(sim[0].level)

          new_entry.append(len([x for x in sim[1] if x.name != "NoItem"]))

          #Item 1
          new_entry.append(sim[1][0].name)
          new_entry.append(sim[1][1].name)
          new_entry.append(sim[1][2].name)

          # Buff 1
          new_entry.append(sim[2][0].name)
          new_entry.append(sim[2][1].name)

          # DPS at 1s      
          dpsAt1 = sim[3][0][1][0]
          dpsAt12 = sim[4][0][1][0]
          dpsAt13 = sim[5][0][1][0]
          # dpsAt1=int(getDPS(sim[3],1))
          # dpsAt12=int(getDPS(sim[4],1))
          # dpsAt13=int(getDPS(sim[5],1))
          new_entry.append(dpsAt1)
          new_entry.append(dpsAt12)
          new_entry.append(dpsAt13)

      #     # phys/magic/true
      #     dps = dpsSplit(sim[3])
      #     new_entry.append(dps['physical'])
      #     new_entry.append(dps['magical'])
      #     new_entry.append(dps['true'])

      #     dpsDict[(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name)] = dpsAt1
          worksheet1.write_row(index+1, 0, new_entry)
      # for index, sim in enumerate(simList):
      #             mainTup = (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name)
      #             tuples0 = [(sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name),
      #                       (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][1].name, sim[2][0].name, sim[2][1].name)]
      #             tuples1 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][2].name, sim[2][0].name, sim[2][1].name),
      #                       (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][0].name, sim[2][0].name, sim[2][1].name)]
      #             tuples2 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][1].name, sim[2][0].name, sim[2][1].name),
      #                       (sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][0].name, sim[2][0].name, sim[2][1].name)]
      #             tuples3 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem", sim[2][1].name),
      #                       (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][1].name, "NoItem")]
      #             # tuples4 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, "NoItem"),
      #             #            (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem", sim[2][0].name)]
      #             for tup in tuples0:
      #                 if tup in dpsDict:
      #                     worksheet1.write(index+1, len(new_entry), round(dpsDict[mainTup] / dpsDict[tup], 2))
      #             for tup in tuples1:
      #                 if tup in dpsDict:
      #                     worksheet1.write(index+1, len(new_entry)+1, round(dpsDict[mainTup] / dpsDict[tup], 2))
      #             for tup in tuples2:
      #                 if tup in dpsDict:
      #                     worksheet1.write(index+1, len(new_entry)+2, round(dpsDict[mainTup] / dpsDict[tup], 2))
      #             for tup in tuples3:
      #                 if tup in dpsDict:
      #                     worksheet1.write(index+1, len(new_entry)+3, round(dpsDict[mainTup] / dpsDict[tup], 2))
      #             # for tup in tuples4:
      #             #     if tup in dpsDict:
      #             #         worksheet1.write(index+1, len(new_entry)+4, round(dpsDict[mainTup] / dpsDict[tup], 2))    
    workbook.close()

def addSimListToDF(data_frame, simLists):
  # COLUMNS: for DF we can actually be much less noob about it
  # champion
  # level
  # items 1-3
  # buffs 1-2 (note: we eventually want support for the whole buff tree)
  # isHeadliner
  # % physical/magical/true
  # # casts
  # item 1-3 dps increase
  # headliner dps increase
  # TODO: just modify createdpscsv to use this
  for simList in simLists:
      for index, sim in enumerate(simList):
          new_entry = {}
          new_entry['Name'] = sim[0].name
          new_entry['Level'] = sim[0].level
          new_entry['Num items'] = len([x for x in sim[1] if x.name != "NoItem"])
          new_entry['Item 1'] = sim[1][0].name
          new_entry['Item 2'] = sim[1][1].name
          new_entry['Item 3'] = sim[1][2].name
          new_entry['Buff 1'] = sim[2][0].name
          new_entry['Buff 2'] = sim[2][1].name
          new_entry['DPS at 5s'] = int(getDPS(sim[3], 5))
          new_entry['DPS at 10s'] = int(getDPS(sim[3], 10))
          new_entry['DPS at 15s'] = int(getDPS(sim[3], 15))
          new_entry['DPS at 20s'] = int(getDPS(sim[3], 20))

          dps = dpsSplit(sim[3])
          new_entry['% physical'] = dps['physical']
          new_entry['% magical'] = dps['magical']
          new_entry['% true'] = dps['true']

          new_entry['# Attacks'] = sim[0].numAttacks
          new_entry['# Casts'] = sim[0].numCasts
  return 0


def createDPScsv(simLists):
    """Creates the DPS csv dps_stats.xlsx: This keeps a record of all the different dps combos for a champion.
    
    Args:
        simLists (List): list of simulation results
    """
    headers_arr = ["Champion", "Level", "Items", "Item 1", "Item 2", "Item 3", "Buff 1", "Buff 2", "DPS at 5s", "DPS at 10s", "DPS at 15s", "DPS at 20s",
                   "% physical", "% magical", "% true", "# Attacks", "# Casts", "Item 1 DPS Increase", "Item 2 DPS Increase", "Item 3 DPS Increase",
                   "Buff DPS Increase"]
    workbook = xlsxwriter.Workbook('dps_stats.xlsx')
    dpsDict = {}
    newEntryLength = 0
    count = 0
    for simList in simLists:
        worksheet1 = workbook.add_worksheet(simList[0][0].name + str(simList[0][0].level))
        worksheet1.write_row(0, 0, headers_arr)
        worksheet1.freeze_panes(1, 0)
        worksheet1.autofilter('A1:Z9999')
        for index, sim in enumerate(simList):
            new_entry = []
            # Champion
            new_entry.append(sim[0].name)
            new_entry.append(sim[0].level)

            new_entry.append(len([x for x in sim[1] if x.name != "NoItem"]))

            #Item 1
            new_entry.append(sim[1][0].name)
            new_entry.append(sim[1][1].name)
            new_entry.append(sim[1][2].name)

            # Buff 1
            new_entry.append(sim[2][0].name)
            new_entry.append(sim[2][1].name)

            # DPS at 5s
            dpsAt5=int(getDPS(sim[3],5))
            dpsAt10=int(getDPS(sim[3],10))
            dpsAt15=int(getDPS(sim[3],15))
            dpsAt20=int(getDPS(sim[3],20))
            new_entry.append(dpsAt5)
            new_entry.append(dpsAt10)
            new_entry.append(dpsAt15)
            new_entry.append(dpsAt20)

            # % Physical
            dps = dpsSplit(sim[3])
            # print(dps)
            new_entry.append(dps['physical'])
            new_entry.append(dps['magical'])
            new_entry.append(dps['true'])

            # # Attacks
            new_entry.append(sim[0].numAttacks)
            new_entry.append(sim[0].numCasts)
            newEntryLength= len(new_entry)
            # item1 formula
            # formula = '=J{0} / INDEX(J:J,MATCH(1,(A{0}=A:A)*("NoItem"=D:D)*(G{0}=G:G)*((E{0}=E:E)*(F{0}=F:F)+(E{0}=F:F)*(F{0}=E:E)),0))'.format(index+2)
            # print(formula)
                
            dpsDict[(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name)] = dpsAt20
            #if sim[2][0].name == "NoItem":
            #    continue
            worksheet1.write_row(index+1, 0, new_entry)
            

        for index, sim in enumerate(simList):
            mainTup = (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name)
            tuples0 = [(sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name),
                      (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][1].name, sim[2][0].name, sim[2][1].name)]
            tuples1 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][2].name, sim[2][0].name, sim[2][1].name),
                      (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][0].name, sim[2][0].name, sim[2][1].name)]
            tuples2 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][1].name, sim[2][0].name, sim[2][1].name),
                      (sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][0].name, sim[2][0].name, sim[2][1].name)]
            tuples3 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem", sim[2][1].name),
                      (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][1].name, "NoItem")]
            tuples4 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, "NoItem"),
                       (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem", sim[2][0].name)]
            for tup in tuples0:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry), round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples1:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+1, round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples2:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+2, round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples3:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+3, round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples4:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+4, round(dpsDict[mainTup] / dpsDict[tup], 2))    
    workbook.close()

def doExperiment(champion, opponent, itemList, buffList, t):
    simulator = Simulator()
    simList = []
    # buffList.append(buffs.NoBuff(0,[]))
    for itemCombo in itemList:
        for buffCombo in buffList:
            champ = copy.deepcopy(champion)
            items = copy.deepcopy(itemCombo)
            buffs = copy.deepcopy(buffCombo)
            results1 = simulator.simulate(items, buffs, champ,
                [copy.deepcopy(opponent), copy.deepcopy(opponent), copy.deepcopy(opponent), copy.deepcopy(opponent)], t)    
            simList.append((champ, items, buffs, results1))
        #resNoDmg(results1, label=item.name)
    print("Finished simulation on {}".format(champion.name))
    return simList

def doExperimentGivenItems(champion, opponent, itemList, buffs, t):
    simulator = Simulator()
    simList = []
    for itemCombo in itemList:
        champ = copy.deepcopy(champion)
        results1 = simulator.simulate(itemCombo, copy.deepcopy(buffs), champ,
            [copy.deepcopy(opponent) for i in range(8)], t)    
        simList.append((champ, itemCombo, [buffs], results1))
    return simList  

def doUltExperiment(champion, opponents, itemList, buffList):
    simulator = Simulator()
    simList = []
    # buffList.append(buffs.NoBuff(0,[]))
    for itemCombo in itemList:
        for buffCombo in buffList:
            results = ()
            for opponent in opponents:
              champ = copy.deepcopy(champion)
              items = copy.deepcopy(itemCombo)
              buffs = copy.deepcopy(buffCombo)
              results1 = simulator.simulateUlt(items, buffs, champ,
                  [copy.deepcopy(opponent)])    
              results += (results1,)
            simList.append((champ, items, buffs)+results)
        #resNoDmg(results1, label=item.name)
    return simList


def getComboList(items, comboSize, replace=True):
    if replace:
      itemComboList = itertools.combinations_with_replacement(items, comboSize)
    else:
      itemComboList = itertools.combinations(items, comboSize)
      itemComboList = itertools.chain(itemComboList, iter([[buffs.NoBuff(0, []), buffs.NoBuff(0, [])]]))
    return [list(a) for a in itemComboList]

def constructGraph():
    t = 22
    # want to construct graph for karma  
    oneItemList = [items.NoItem(), items.Blue(), items.Archangels(), items.Shojin(), items.JG(),
                   items.HoJ(), items.Rab(), items.Shiv()]
    oneItemList = [[a] for a in oneItemList]
    twoItemList = [[items.Blue(), items.Archangels()],
        #           [items.Shojin(), items.Archangels()],
        #           [items.Archangels(), items.Archangels()],
                   [items.Blue(), items.Rab()],
        #           [items.Shojin(), items.Rab()],
                   [items.JG(), items.IE()],  
                   [items.Blue(), items.Shojin()],
        #           [items.JG(), items.Archangels()],
        #           [items.Archangels(), items.Rab()]
                   ]
    itemList = twoItemList
    karmaSimList = doExperimentGivenItems(Karma(2), Viktor(2), itemList, [buffs.Invoker(2,[])], t)
    printSims(karmaSimList)
    karmaSimList = [np.array([[damageInstance[0], damageInstance[1][0]] for damageInstance in k[3]]) for k in karmaSimList]
    for i in enumerate(karmaSimList):
      karmaSimList[i[0]][:,1] = np.cumsum(karmaSimList[i[0]][:,1], axis=0)
  
    
    # newList = np.cumsum(karmaSimList[0], axis=1)

#   # print(np.cumsum(karmaSimList[0], axis=1))
    for index, value in enumerate(karmaSimList):
      itemNames = ','.join([item.name for item in itemList[index]])
      # itemNames = oneItemList[index][0].name
      plt.plot(*zip(*value), label = itemNames)
    plt.legend()
    plt.show()
    

def printSims(simList):
  f = open("karmaSims.txt", "w")
  for sim in simList:    
    f.write("Champion: {0} {1} \n Items: {2} \n Buffs: {3}\n".format(sim[0].name, sim[0].level,
                                                                   ','.join([item.name for item in sim[1]]),
                                                                   ','.join([buff[0].name for buff in sim[2]])))
    for dmg in sim[3]:
      f.write("t {0:.2f}, dmg {1:.2f}, type {2} \n".format(dmg[0], dmg[1][0], dmg[1][1]))
    f.write("\n")
  f.close()


def ultCSV():
  itemComboList = getComboList([
                   items.NoItem(),
                   items.IE(),
                   items.JG(),
                   items.HoJ(),
                   items.GS(),
                   items.DB(),
                   items.LW()], 3)

  apComboList = getComboList([
                   items.NoItem(),
                   items.IE(),
                   items.JG(),
                   items.HoJ(),
                   items.Rab(),
                   items.GS()], 3)

  noneBuffList = getComboList([buffs.NoBuff(0, []), buffs.NoBuff(0, [])], 2, False) 
  simLists = []
  opponents = [ZeroResistance(1), DummyTank(2), SuperDummyTank(2)]
  simLists.append(doUltExperiment(Zippy(1), opponents, itemComboList, zippyBuffList))
  simLists.append(doUltExperiment(Zippy(2), opponents, itemComboList, zippyBuffList))
  simLists.append(doUltExperiment(Zippy(3), opponents, itemComboList, zippyBuffList))

  simLists.append(doUltExperiment(Karma(2), opponents, apComboList, sejBuffList))
  simLists.append(doUltExperiment(Karma(3), opponents, apComboList, sejBuffList))


  print(simLists)
  createUltDamageCSV(simLists)


def constructCSV():
    t = 30
    simLists = []
    simDict = {}
    itemComboList = getComboList([items.NoItem(),
                items.Archangels(),
                items.Rageblade(),
                items.HoJ(),
                items.Rab(),
                items.Shojin(),
                items.JG(),
                items.Shiv(),
                items.IE()], 3)

    ADComboList = getComboList([items.NoItem(),
               items.IE(),
               items.HoJ(),
               items.GS(),
               items.RH(),
               items.LW(),
               items.Shojin(),
               items.Blue(),
               items.Rageblade(),
               items.Red(),
               items.DB(),
               items.Nashors(),
               items.Guardbreaker()], 3)

    APComboList = getComboList([items.NoItem(),
                   items.IE(),
                   items.HoJ(),
                   items.GS(),
                   items.Rageblade(),
                   items.Rab(),
                   items.Shojin(),
                   items.Shiv(),
                   items.Red(),
                   items.Guardbreaker(),
                   items.Nashors(),
                   items.Adaptive(),
                   items.JG(),
                   items.Archangels(),
                   items.Blue()], 3)
    shenComboList = getComboList([items.NoItem(),
                items.Rageblade(),
                items.GS(),
                items.Bramble(),
                items.Titans()], 3)

    noneBuffList = getComboList([buffs.NoBuff(0, []), buffs.NoBuff(0, [])], 2, False) 

    blasterBuffList = getComboList([buffs.NoBuff(0, []),
                                buffs.Blaster(2, [])], 2, False)

    hunterBuffList = getComboList([buffs.NoBuff(0, []),
                                buffs.Hunter(2, [])], 2, False)

    mageBuffList = getComboList([buffs.NoBuff(0, []),
                                buffs.Mage(3, [])], 2, False)

    scholarBuffList = getComboList([buffs.NoBuff(0, []),
                                buffs.Scholar(2, []),
                                buffs.Scholar(4, [])], 2, False)


  # galio
    simLists.append(doExperiment(Galio(2), DummyTank(2), APComboList, mageBuffList, t))      
  # galio
    simLists.append(doExperiment(Galio(3), DummyTank(2), APComboList, mageBuffList, t))      



  # # galio
  #   simLists.append(doExperiment(Zoe(2), DummyTank(2), APComboList, scholarBuffList, t))      
  # # galio
  #   simLists.append(doExperiment(Zoe(3), DummyTank(2), APComboList, scholarBuffList, t))  

  # # # Syndra
  # #   simLists.append(doExperiment(Syndra(1), DummyTank(2), APComboList, AhriBuffList, t))      
  # # # Syndra
  # #   simLists.append(doExperiment(Syndra(2), DummyTank(2), APComboList, AhriBuffList, t))      

  # # Shen
  #   simLists.append(doExperiment(Ezreal(2), DummyTank(2), ADComboList, blasterBuffList, t))      
  # # Shen
  #   simLists.append(doExperiment(Ezreal(3), DummyTank(2), ADComboList, blasterBuffList, t))      


  # # Shen
  #   simLists.append(doExperiment(Nomsy(2), DummyTank(2), ADComboList, hunterBuffList, t))      
  # # Shen
  #   simLists.append(doExperiment(Nomsy(3), DummyTank(2), ADComboList, hunterBuffList, t))      

  # # Shen
  #   simLists.append(doExperiment(Twitch(2), DummyTank(2), ADComboList, hunterBuffList, t))      
  # # Shen
  #   simLists.append(doExperiment(Twitch(3), DummyTank(2), ADComboList, hunterBuffList, t))      

  # # Senna
  #   simLists.append(doExperiment(Senna(2), DummyTank(2), ADComboList, sniperBuffList, t))      
  # # Senna
  #   simLists.append(doExperiment(Senna(3), DummyTank(2), ADComboList, sniperBuffList, t))      

  # # Aphelios
  #   simLists.append(doExperiment(Aphelios(1), DummyTank(2), ADComboList, sniperBuffList, t))      
  # # Aphelios
  #   simLists.append(doExperiment(Aphelios(2), DummyTank(2), ADComboList, sniperBuffList, t))      

  # # Ashe
  #   simLists.append(doExperiment(Ashe(1), DummyTank(2), ADComboList, asheBuffList, t))      
  # # Ashe
  #   simLists.append(doExperiment(Ashe(2), DummyTank(2), ADComboList, asheBuffList, t))      


  # # Tristana
  #   simLists.append(doExperiment(Tristana(2), DummyTank(2), ADComboList, DuelistBuffList, t))      
  # # Tristana
  #   simLists.append(doExperiment(Tristana(3), DummyTank(2), ADComboList, DuelistBuffList, t))      

    merged = list([itertools.chain.from_iterable(simList) for simList in simLists])
    createDPScsv(simLists)
    #createDPSChart(simList)


if __name__ == "__main__":
    constructCSV()
    # constructGraph()
    # ultCSV()