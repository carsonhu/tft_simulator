from collections import deque, Counter
from set14items import Item
from champion import Stat, Attack, AD

import heapq
import numpy as np
import copy
import status
import random
import ast

def get_classes_from_file(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    # Parse the file content into an AST
    tree = ast.parse(file_content)

    # Extract all class definitions
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return classes

class_buffs = ['Rapidfire', 'Techie', 'StreetDemon', 'Marksman',
               'Strategist', 'Cypher', 'Slayer', 'Syndicate',
               'Executioner', 'AMP', 'Dynamo', 'AnimaSquad',
               'Cyberboss', 'Divinicorp']

augments = ['ClockworkAccelerator', 'ManaflowI', 'ManaflowII', 'Shred30',
            'BlazingSoulI', 'BlazingSoulII', 'BadLuckProtection',
            'CalculatedEnhancement', 'GlassCannonI',
            'GlassCannonII', 'FlurryOfBlows', 'MacesWill', 'Backup',
            'CategoryFive', 'Moonlight', 'PiercingLotusI',
            'PiercingLotusII', 'BlueBatteryIII']

stat_buffs =['ASBuff']

no_buff = ['NoBuff']


class Buff(Item):
    levels = [0]

    def __init__(self, name, level, params, phases):
        super().__init__(name, phases=phases)
        self.level = level
        self.params = params

    def performAbility(self, phase, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method")    

    def ability(self, phase, time, champion, input_=0):
        # if it's level 0 of an ability
        if self.level == 0:
            return input_
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def extraParameters():
        return 0

    def hashFunction(self):
        # Hash function used for caching;
        # (name, level, params)
        init_tuple = (self.name, str(self.level))
        if isinstance(self.params, int):
            param_tuple = (self.params,)
        else:
            param_tuple = tuple(self.params)
        return (init_tuple + param_tuple)

    def __hash__(self):
        return hash(self.hashFunction())


class NoBuff(Buff):
    levels = [0]

    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("NoItem", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class Rapidfire(Buff):
    levels = [0, 2, 4, 6]
    
    def __init__(self, level, params):
        super().__init__("Rapidfire " + str(level), level, params,
                         phases=["preCombat", "preAttack"])
        self.scaling = {0: 0, 2: 4, 4: 10, 6: 22}
        self.base_scaling = 10
        self.stacks = 0
        self.maxStacks = 10

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.addStat(self.base_scaling)
        elif phase == "preAttack":
            if self.stacks < self.maxStacks:
                self.stacks += 1
                champion.aspd.addStat(self.scaling[self.level])
        return 0

class Syndicate(Buff):
    levels = [0, 3, 5, 7]

    def __init__(self, level, params):
        super().__init__("Syndicate " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: .05, 5: .2, 7: .3}
        self.is_kingpin = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        champion.is_kingpin = self.is_kingpin
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Kingpin",
                "Min": 0,
                "Max": 1,
                "Default": 1}

    def extraBuff(self, is_kingpin):
        self.is_kingpin = is_kingpin

class StreetDemon(Buff):
    levels = [0, 3, 5, 7, 10]

    def __init__(self, level, params):
        super().__init__("Street Demon " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: 6, 5: 10, 7: 15, 10: 40}
        self.is_streetdemon = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        mult = 2 if self.is_streetdemon else 1
        champion.atk.addStat(self.scaling[self.level] * 1.5 * mult)
        champion.ap.addStat(self.scaling[self.level] * 1.5 * mult)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Demon",
                "Min": 0,
                "Max": 1,
                "Default": 1}

    def extraBuff(self, is_streetdemon):
        self.is_streetdemon = is_streetdemon

class Strategist(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Strategist " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: .06, 3: .1, 4: .14, 5: .18}
        self.is_strategist = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        mult = 3 if self.is_strategist else 1
        champion.dmgMultiplier.addStat(self.scaling[self.level] * mult)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Strat",
                "Min": 0,
                "Max": 1,
                "Default": 1}

    def extraBuff(self, is_strategist):
        self.is_strategist = is_strategist

class AMP(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("AMP " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: 1, 3: 2, 4: 3, 5: 4}

    def performAbility(self, phase, time, champion, input_=0):
        champion.amp_level = self.scaling[self.level]
        return 0

class Cypher(Buff):
    levels = [0, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Cypher " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: 25, 4: 35, 5: 45}

    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(self.scaling[self.level])
        champion.ap.addStat(self.scaling[self.level])
        return 0


class AnimaSquad(Buff):
    levels = [0, 3, 5, 7]

    def __init__(self, level, params):
        super().__init__("Anima Squad " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: .05, 5: .1, 7: .15}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


class Divinicorp(Buff):
    levels = [0, 1, 2, 3, 4, 5, 6, 7]

    def __init__(self, level, params):
        super().__init__("Divinicorp " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {1: 1, 2: 1.1, 3: 1.2, 4: 1.5, 5: 1.75, 6: 2, 7: 2.25}

        # divincorp base
        self.ad_base = 8
        self.ap_base = 9
        self.crit_base = .07
        self.as_base = 5

        self.is_divin = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        mult = 2 if self.is_divin else 1
        if champion.divines["Morgana"]:
            champion.ap.addStat(self.ap_base * self.scaling[self.level] * mult)
        if champion.divines["Senna"]:
            champion.atk.addStat(self.ad_base * self.scaling[self.level] * mult)
        if champion.divines["Vex"]:
            champion.crit.addStat(self.crit_base * self.scaling[self.level] * mult)
        if champion.divines["Renekton"]:
            champion.aspd.addStat(self.as_base * self.scaling[self.level] * mult)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Divin",
                "Min": 0,
                "Max": 1,
                "Default": 1}

    def extraBuff(self, is_divin):
        self.is_divin = is_divin


class Cyberboss(Buff):
    levels = [0, 2, 3, 4]

    def __init__(self, level, params):
        super().__init__("Cyberboss " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: 15, 3: 25, 4: 30}

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.scaling[self.level])
        champion.cyberboss_upgrade = True
        return 0


class Dynamo(Buff):
    levels = [0, 2, 3, 4]

    def __init__(self, level, params):
        super().__init__("Dynamo " + str(level), level, params,
                         phases=["onUpdate"])
        self.scaling = {2: 5, 3: 7, 4: 10}
        self.is_dynamo = 0
        self.extraBuff(params)
        self.next_mana = 3

    def performAbility(self, phase, time, champion, input_=0):
        mult = 2 if self.is_dynamo else 1
        if time > self.next_mana:
            champion.addMana(self.scaling[self.level] * mult)
            self.next_mana += 3
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Dynamo",
                "Min": 0,
                "Max": 1,
                "Default": 1}

    def extraBuff(self, is_dynamo):
        self.is_dynamo = is_dynamo

class Slayer(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__("Slayer " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: 15, 4: 40, 6: 70}

    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(self.scaling[self.level])
        return 0


class Executioner(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Executioner " + str(level), level, params, phases=["preCombat"])
        self.critChanceScaling = {2: .25, 3: .35, 4: .45, 5: .55}
        self.critDmgScaling = {2: .08, 3: .15, 4: .2, 5: .25}

    def performAbility(self, phase, time, champion, input=0):
        champion.canSpellCrit = True
        champion.critDmg.addStat(self.critDmgScaling[self.level])
        champion.crit.addStat(self.critChanceScaling[self.level] * .5)
        return 0

class Techie(Buff):
    levels = [0, 2, 4, 6, 8]

    def __init__(self, level, params):
        super().__init__("Techie " + str(level), level, params,
                         phases=["preCombat"])
        self.base_scaling = 0
        self.scaling = {2: 15, 4: 45, 6: 80, 8: 110}

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.base_scaling)
        champion.ap.addStat(self.scaling[self.level])
        return 0

class Marksman(Buff):
    levels = [0, 2, 4]

    def __init__(self, level, params):
        super().__init__("Marksman " + str(level), level, params,
                         phases=["preCombat", "onUpdate"])
        self.base_scaling = {2: 18, 4: 35}
        self.bonus_scaling = {2: 0, 4: 20}
        self.first_bonus = 8
        self.bonus_interval = 6
        self.second_bonus = self.first_bonus + self.bonus_interval

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.atk.addStat(self.base_scaling[self.level])
        elif phase == "onUpdate":
            if time > self.first_bonus:
                champion.atk.addStat(self.base_scaling[self.level])
                self.first_bonus = 999
            if time > self.second_bonus:
                champion.atk.addStat(self.bonus_scaling[self.level])
                self.second_bonus += self.bonus_interval
        return 0


class VayneUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Bat Bolts", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultAutos > 0:
            if champion.ultAutos == 2 or champion.ultAutos == 3:
                champion.multiTargetSpell(champion.opponents,
                                          champion.items, time,
                                          1, champion.abilityScaling,
                                          'physical')                                                
            elif champion.ultAutos == 1:
                champion.multiTargetSpell(champion.opponents,
                                          champion.items, time,
                                          1, champion.thirdAbilityScaling,
                                          'physical')       
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.aspd.addStat(-50)     
                champion.manalockTime = time + .01                                                                            
        return 0


class ApheliosUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Moonlight Vigil", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultAutos > 0:
            champion.multiTargetSpell(champion.opponents,
                                      champion.items, time,
                                      1, champion.chakramAbilityScaling,
                                      'physical')
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.manalockTime = time + .01
        return 0


class KogUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Fire at Will", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultActive:
            champion.multiTargetSpell(champion.opponents,
                                      champion.items, time,
                                      1, champion.abilityScaling,
                                      'physical')     
        return 0

class SennaUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Ion Beam", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.multiTargetSpell(champion.opponents,
                                  champion.items, time,
                                  1, champion.autoScaling,
                                  'physical')
        return 0

class TFUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Ace High", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(2)
        return 0


class ZeriUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Hyperthread Rush", level, params, phases=["onUpdate"])

    def performAbility(self, phase, time, champion, input_=0):
        # this needs serious test cases written out
        # queued autos: priority queue with tuple
        # (AD, AS, wearoff time, next_auto)
        if len(champion.queued_autos) > 0:
            bottom = champion.queued_autos[0][1]  
            if time > bottom[2]:
                heapq.heappop(champion.queued_autos)
            elif time > bottom[3]:
                next_auto = time + 1 / bottom[1]
                heapq.heappop(champion.queued_autos)

                champion.multiTargetSpell(champion.opponents,
                                          champion.items, time,
                                          1, lambda x, y, z: champion.abilityScaling(x, bottom[0], z),
                                          'physical')      

                heapq.heappush(champion.queued_autos,
                               (next_auto, (bottom[0], bottom[1], bottom[2], next_auto)))

        return 0


class YuumiUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Yuum.AI", level, params, phases=["onUpdate"])
        self.interval = 1
        self.nextBonus = 1
        self.manaToAdd = 3

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextBonus:
            champion.addMana(self.manaToAdd * champion.amp_level)
            self.nextBonus += self.interval
        return 0


class ASBuff(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Attack Speed " + str(level), level, params, phases=["preCombat"])
        self.as_buff = 0
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.as_buff)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "AS",
                "Min": 0,
                "Max": 100,
                "Default": 0}
    def extraBuff(self, as_buff):
        self.as_buff = as_buff

# AUGMENTS

class BlueBatteryIII(Buff):
    # crazy bug that i gotta fix: naming it 'blue' fucks things up with blue
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("BlueBattery III", level, params, phases=["preCombat", "postAbility"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.ap.addStat(15)
        elif phase == "postAbility":
            champion.addMana(5)
        return 0

class JeweledLotusII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Jeweled Lotus II", level, params, phases=["preCombat"])
        self.critBonus = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
            champion.crit.addStat(self.critBonus)
        return 0


class JeweledLotusIII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Jeweled Lotus III", level, params, phases=["preCombat"])
        self.critBonus = 0.45

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
            champion.crit.addStat(.45)
        return 0


class BlossomingLotusI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Blossoming Lotus I", level, params, phases=["preCombat", "onUpdate"])
        self.critBonus = 0.05
        self.nextBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.crit.addStat(self.critBonus)
        return 0


class BlossomingLotusII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Blossoming Lotus II", level, params, phases=["preCombat", "onUpdate"])
        self.critBonus = 0.1
        self.nextBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.crit.addStat(self.critBonus)
        return 0


class FlurryOfBlows(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Flurry of Blows", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(30)
        champion.crit.addStat(.45)
        return 0


class GlassCannonI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Glass Cannon I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(.15)
        return 0


class GlassCannonII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Glass Cannon II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(.25)
        return 0


class ManaflowI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Manaflow I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(2)
        return 0


class ManaflowII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Manaflow II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(3)
        return 0


class PiercingLotusI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Piercing Lotus I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.crit.addStat(.05)
        champion.canSpellCrit = True
        for opponent in champion.opponents:
            opponent.applyStatus(status.MRReduction("MR Piercing"), self, time, 30, .8)
        return 0


class PiercingLotusII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Piercing Lotus II", level, params, phases=["preCombat"])
    
    def performAbility(self, phase, time, champion, input_=0):
        champion.crit.addStat(.2)
        champion.canSpellCrit = True
        for opponent in champion.opponents:
            opponent.applyStatus(status.MRReduction("MR Piercing 2"), self, time, 30, .8)
        return 0


class CalculatedEnhancement(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Calculated Enhancement", level, params, phases=["preCombat"])
    
    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(40)
        champion.ap.addStat(50)
        return 0


class Moonlight(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Moonlight (for 3* champs)", level, params, phases=["preCombat"])
    
    def performAbility(self, phase, time, champion, input_=0):
        if champion.level == 3:
            champion.atk.addStat(45)
            champion.ap.addStat(45)
        return 0


class CategoryFive(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Category Five", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.categoryFive = True
        return 0


class MacesWill(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Maces Will", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(6)
        champion.crit.addStat(.2)
        return 0


class Backup(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Backup", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(12)
        return 0


class BlazingSoulI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Blazing Soul I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(20)
        champion.ap.addStat(20)
        return 0


class BlazingSoulII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Blazing Soul II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(35)
        champion.ap.addStat(35)
        return 0


class BadLuckProtection(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Bad Luck Protection", level, params, phases=["onUpdate"])
  
    def performAbility(self, phase, time, champion, input_=0):
        if champion.canCrit or champion.canSpellCrit or champion.crit.base > 0:
            champion.canCrit = False
            champion.canSpellCrit = False
            champion.atk.addStat(champion.crit.stat * 80)
            champion.crit.base = 0
            champion.crit.add = 0

        return 0


class FinalAscension(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Final Ascension", level, params, phases=["preCombat", "onUpdate"])
        self.initialDmgBonus = 0.15
        self.dmgBonus = 0.3
        self.nextBonus = 15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.dmgMultiplier.addStat(self.initialDmgBonus)
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 99999
                champion.dmgMultiplier.addStat(self.dmgBonus)
        return 0


class ClockworkAccelerator(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Clockwork Accelerator", level, params, phases=["onUpdate"])
        self.asBonus = 10
        self.nextBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.aspd.addStat(self.asBonus)
        return 0


class Shred30(Buff):
    levels = [1]
    
    def __init__(self, level=1, params=0):
        super().__init__("30% Armor/MR Shred", level, params, phases=["onUpdate"])

    def performAbility(self, phase, time, champion, input_=0):
        # expensive af but w/e
        for opponent in champion.opponents:
            opponent.armor.mult = .7
            opponent.mr.mult = .7
        return 0