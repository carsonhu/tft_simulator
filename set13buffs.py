from collections import deque, Counter
from set13items import Item
from champion import Stat, Attack, AD
import numpy as np
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

# Example usage
file_path = "set13anomalies.py"
anomalies = get_classes_from_file(file_path)

class_buffs = ['Sorcerer', 'FormSwapper', 'Family', 'Visionary', 'Sniper', 
               'Quickstriker', 'Dominator', 'Ambusher']

augments = ['BlossomingLotusI', 'BlossomingLotusII',
            'ClockworkAccelerator', 'JeweledLotusII',
            'JeweledLotusIII', 'FinalAscension', 'Spellblades', 'Shred30']



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

class NoBuff(Buff):
    levels = [0]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("NoItem", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class Sorcerer(Buff):
    levels = [0, 2, 4, 6, 8]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Sorcerer " + str(level), level, params,
                         phases=["preCombat"])
        self.base_scaling = 10
        self.scaling = {2: 20, 4: 50, 6: 85, 8: 100}
    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.base_scaling)
        champion.ap.addStat(self.scaling[self.level])
        return 0

class Visionary(Buff):
    levels = [0, 2, 4, 6, 8]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Visionary " + str(level), level, params,
                         phases=["preCombat"])
        self.base_scaling = 10
        self.scaling = {2: .25, 4: .5, 6: .8, 8: 1}
    def performAbility(self, phase, time, champion, input_=0):
        champion.manaGainMultiplier.mult += self.scaling[self.level]
        return 0

class Quickstriker(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Quickstriker " + str(level), level, params,
                         phases=["preCombat"])
        # quickstriker just takes average of min and max instead
        self.scaling = {2: 40, 4: 55, 6: 70}
    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling[self.level])
        return 0

class Family(Buff):
    levels = [0, 3, 4, 5]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Family " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: .25, 4: .3, 5: .4}
        self.as_scaling = {3: 0, 4: 20, 5: 20}
    def performAbility(self, phase, time, champion, input_=0):
        champion.fullMana.mult -= self.scaling[self.level]
        champion.aspd.addStat(self.as_scaling[self.level])
        return 0

class FormSwapper(Buff):
    levels = [0, 2, 4]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Form Swapper " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: .20, 4: .40}
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0

class Sniper(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Sniper " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: .07, 4: .16, 6: .35}
        self.base_bonus = 0
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level]*self.base_bonus)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Hexes",
                "Min": 0,
                "Max": 8,
                "Default": 4}

    def extraBuff(self, hexes):
        self.base_bonus = hexes

class Dominator(Buff):
    levels=[0, 2, 4, 6]
    def __init__(self, level, params):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Dominator " + str(level), level, params,
                         phases=["preAbility"])
        self.scaling = {0: 0, 2: .25, 4: .5, 6: .75}
        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.scaling[self.level] * champion.fullMana.stat)
        return 0

class Ambusher(Buff):
    levels = [0, 2, 3, 4, 5]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Ambusher " + str(level), level, params,
                         phases=["preCombat"])
        self.crit_scaling = {0: 0, 2: 20, 3: 30, 4: 40, 5: 55}
        self.crit_dmg_scaling = {0: 0, 2: 10, 3: 20, 4: 30, 5: 35}
    def performAbility(self, phase, time, champion, input_=0):
        champion.crit.addStat(self.scaling[self.level])
        champion.critDmg.addStat(self.scaling[self.level])
        champion.canSpellCrit = True
        return 0

class Frost(Buff):
    levels = [0, 3, 5, 7, 9]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Frost " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: 16, 5: 40, 7: 55, 9: 90}
    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(self.scaling[self.level])
        champion.ap.addStat(self.scaling[self.level])
        return 0

class Hunter(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Hunter " + str(level), level, params,
                         phases=["preCombat", "onUpdate"])
        self.scaling = {0: 0, 2: 15, 4: 40, 6: 65}
        self.as_scaling = {0: 0, 2: 0, 4: 0, 6: 20}
        self.takedownScaling = {0: 0, 2: 20, 4: 30, 6: 35}
        # time for first takedown
        self.has_activated = False
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.atk.addStat(self.scaling[self.level])
            champion.aspd.addStat(self.as_scaling[self.level])
        elif phase == "onUpdate":
            if time > champion.first_takedown and not self.has_activated:
                champion.atk.addStat(self.takedownScaling[self.level])
                self.has_activated = True
        return 0

class Dragon(Buff):
    levels =[0, 3]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Dragon " + str(level), level, params,
                         phases=["preCombat"])
    def performAbility(self, phase, time, champion, input_=0):
        if self.level == 3:
            champion.ultAmped = True
        return 0

class Scholar(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Scholar " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: 3, 4: 5, 6: 10}
        self.ap_scaling = {0: 0, 2: 10, 4: 15, 6: 20}
    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(self.scaling[self.level])
        champion.ap.addStat(self.ap_scaling[self.level])
        return 0

class Blaster(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Blaster " + str(level), level, params,
                         phases=["preCombat", "preAbility"])
        self.scaling = {0: 0, 2: .15, 4: .35, 6: .6}
        self.burstScaling = {0: 0, 2: .15, 4: .3, 6: .4}
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.dmgMultiplier.addStat(self.scaling[self.level])
        elif phase == "preAbility":
            champion.applyStatus(status.DmgMultiplierModifier("Blaster"),
                     champion, time, 3,
                     self.burstScaling[self.level])
        return 0

class Warrior(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Warrior " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: .1, 4: .2, 6: .25}
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0

class Faerie(Buff):
    levels = [0, 3, 5, 7]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Faerie " + str(level), level, params,
                         phases=["onDealDamage"])
        self.scaling = {0: 0, 3: .3, 5: .45, 7: .55}
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        # weird hack, but total stacks is doubled since 'onDoDamage' is called twice on any damage strike,
        # since it checks for crit and noncrit. Rather than create a special exception, might as well just do this
        if "FaerieQueen's Crown" in [item.name for item in champion.items]:
            if self.stacks < 12:
                self.stacks += 1
            elif self.stacks == 12:
                self.stacks += 1
                champion.dmgMultiplier.add += self.scaling[self.level]

        return input_

class Pyro(Buff):
    levels = [0, 2, 3, 4, 5]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Pyro " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: 10, 3: 25, 4: 50, 5: 65}
        self.base_bonus = 3
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling[self.level] + self.base_bonus)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Cinders",
                "Min": 0,
                "Max": 100,
                "Default": 0}

    def extraBuff(self, cinders):
        self.base_bonus += cinders // 5 * 2

class ArcanaAhri(Buff):
    levels = [0, 2, 3, 4, 5]
    def __init__(self, level, params):
        # params is number of three-stars
        super().__init__("Arcana(Ahri) " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: 10, 3: 15, 4: 20, 5: 25}
        self.bonus_scaling = {0: 0, 2: 5, 3: 8, 4: 12, 5: 18}
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.scaling[self.level] + self.bonus_scaling[self.level])
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# 3-stars",
                "Min": 0,
                "Max": 8,
                "Default": 0}

    def extraBuff(self, three_stars):
        for k, v in self.bonus_scaling.items():
            self.bonus_scaling[k] *= three_stars

class ArcanaXerath(Buff):
    levels = [0, 2, 3, 4, 5]
    def __init__(self, level, params):
        # params is number of three-stars
        super().__init__("Arcana(Xerath) " + str(level), level, params,
                         phases=["onDealSpellDamage"])
        self.scaling = {0: 0, 2: .02, 3: .03, 4: .045, 5: .07}
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        true_dmg = self.scaling[self.level] * input_
        champion.doDamage(champion.opponents[0], [], 0, true_dmg, true_dmg, 'true', time)
        return input_

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# Charms",
                "Min": 0,
                "Max": 20,
                "Default": 12}

    def extraBuff(self, charms):
        for k, v in self.scaling.items():
            self.scaling[k] *= (charms // 3)

class ArcanaEmblem(Buff):
    levels = [0, 2, 3, 4, 5]
    def __init__(self, level, params):
        # params is number of three-stars
        super().__init__("Arcana(Emblem) " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: .08, 3: .12, 4: .18, 5: .25}
        self.bonus_scaling = {0: 0, 2: .02, 3: .03, 4: .04, 5: .06}
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level] + self.bonus_scaling[self.level])
        return input_

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# Emblems",
                "Min": 0,
                "Max": 10,
                "Default": 0}

    def extraBuff(self, emblems):
        for k, v in self.scaling.items():
            self.bonus_scaling[k] *= emblems

class Sugarcraft(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of three-stars
        super().__init__("Sugarcraft " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: 20, 4: 30, 6: 35}
        self.layers = 0
        self.extraBuff(params)
    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(self.scaling[self.level] * (1 + self.layers/10))
        champion.ap.addStat(self.scaling[self.level] * (1 + self.layers/10))
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Layers",
                "Min": 0,
                "Max": 7,
                "Default": 0}

    def extraBuff(self, layers):
        self.layers = layers

class Chrono(Buff):
    levels=[0, 2, 4, 6]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Chrono " + str(level), level, params, phases=["preCombat", "onUpdate"])
        self.ap_scaling = {0: 0, 2: 20, 4: 55, 6: 35}
        self.as_scaling = {0: 0, 2: 0, 4: 0, 6: 60}
        self.baseBuff = 15
        self.proc_time = 10

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.ap.addStat(self.ap_scaling[self.level])
        elif phase == "onUpdate":
            if time >= self.proc_time:
                self.proc_time = 999
                champion.ap.addStat(self.ap_scaling[self.level])
                champion.aspd.addStat(self.as_scaling[self.level])


class Preserver(Buff):
    levels=[0, 2, 3, 4, 5]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Preserver " + str(level), level, params, phases=["onUpdate"])
        self.scaling = {0: 0, 2: .03, 3: .05, 4: .07, 5: .11}
        self.nextBonus = 3

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if time >= self.nextBonus:
            self.nextBonus += 3
            champion.curMana += champion.fullMana.stat * self.scaling[self.level] * 2

# class KogTeammate(Buff):
#     levels = [0, 1, 2, 3]
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Kog Teammate " + str(level), level, params,
#                          phases=["onUpdate"])
#         self.scaling = {0: 0, 1: 20, 2: 25, 3: 30}
#         self.extraBuff(params)
#         self.base_as = 0.8

#         self.next_faux_count = 0
#         self.faux_attacks_until_cast = 6
#         self.faux_attacks = 0

#     def extraParameters():
#         # defining the parameters for the extra shit
#         return {"Title": "AP",
#                 "Min": 0,
#                 "Max": 999,
#                 "Default": 0}

#     def extraBuff(self, ap):
#         for k, v in self.scaling.items():
#             self.scaling[k] *= (1 + ap / 100)


#     def performAbility(self, phase, time, champion, input_=0):
#         if self.level == 0:
#             return
#         # pretend you have an extra syndra. if 4 incantor,
#         # u have 3 syndras.
#         faux_as = 1 / self.base_as
#         faux_attacks_until_cast = 6
#         if time > self.next_faux_count:
#             self.next_faux_count += faux_as
#             self.faux_attacks += 1
#         if self.faux_attacks == self.faux_attacks_until_cast:
#             self.faux_attacks = 0
#             champion.applyStatus(status.ASModifier("Kogmaw"), champion, time,
#                                  self.buff_duration,
#                                  asBuff[self.level - 1] * self.ap.stat)
#             self.next_faux_count = 8
#         return 0

class Incantor(Buff):
    levels = [0, 2, 4]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Incantor " + str(level), level, params,
                         phases=["preCombat", "preAttack", "preAbility",
                                 "onUpdate"])
        self.scaling = {0: 0, 2: 1, 4: 2}
        self.baseBuff = {0: 0, 2: 10, 4: 30}
        self.stacks = 0
        self.maxStacks = 40

        self.next_faux_count = 0
        self.faux_attacks = 0
    def performAbility(self, phase, time, champion, input_=0):
        if self.level == 0:
            return
        if phase == "preCombat":
            champion.ap.addStat(self.baseBuff[self.level])
        if self.stacks < self.maxStacks:
            if phase == "preAttack":
                    self.stacks += 1
                    champion.ap.addStat(1 * self.scaling[self.level])
            elif phase == "preAbility": 
                    stacks_to_add = min(3, self.maxStacks - self.stacks)
                    self.stacks += stacks_to_add
                    champion.ap.addStat(stacks_to_add * self.scaling[self.level])
            elif phase == "onUpdate":
                # pretend you have an extra syndra. if 4 incantor,
                # u have 3 syndras.
                faux_as = 1 / .75
                faux_attacks_until_cast = 6
                if self.stacks < self.maxStacks:
                    if time > self.next_faux_count:
                        stacks_to_add = min(1*(self.level - 1)*self.scaling[self.level],
                                        self.maxStacks - self.stacks)
                        champion.ap.addStat(stacks_to_add)
                        self.next_faux_count += faux_as
                        self.faux_attacks += 1
                        self.stacks += 1
                    if self.faux_attacks == faux_attacks_until_cast:
                        stacks_to_add = min(3*(self.level - 1), self.maxStacks - self.stacks)
                        self.stacks += stacks_to_add
                        champion.ap.addStat(stacks_to_add*self.scaling[self.level])
                        self.faux_attacks = 0
        if self.stacks > self.maxStacks:
            self.stacks = self.maxStacks
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

class KogUlt(Buff):
    levels = [1]
    def __init__(self, level=1, params=0):
        # params is number of stacks
        super().__init__("Upgrading Barrage Module", level, params, phases=["preAttack"])
    def performAbility(self, phase, time, champion, input_=0):
        champion.multiTargetSpell(champion.opponents,
              champion.items, time,
              1, champion.abilityScaling,
              'magical')        
        return 0

class ZeriUlt(Buff):
    levels = [1]
    def __init__(self, level=1, params=0):
        # params is number of stacks
        super().__init__("Living Battery", level, params, phases=["preAttack"])
        self.stacks = 0
    def performAbility(self, phase, time, champion, input_=0):
        self.stacks += 1
        if self.stacks == 3:
            input_.canOnHit = True # does it?
            input_.canCrit = champion.canSpellCrit
            input_.attackType = 'physical'
            input_.scaling = champion.abilityScaling
            input_.numTargets = 3  
            self.stacks = 0
        return 0

class SmolderUlt(Buff):
    levels = [1]
    def __init__(self, level=1, params=0):
        # params is number of stacks
        super().__init__("Learning to Fly", level, params, phases=["preAttack"])
    def performAbility(self, phase, time, champion, input_=0):
        # BUG: currently does not work with Xerath Arcana

        # input is attack
        if champion.ultActive and champion.ultAutos > 0:
            input_.canOnHit = True
            input_.canCrit = champion.canSpellCrit
            input_.attackType = 'physical'
            input_.scaling = champion.abilityScaling
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.aspd.addStat(-50)
                champion.manalockTime = time + .01
        return 0

class CassUlt(Buff):
    levels = [1]
    def __init__(self, level=1, params=0):
        # params is number of stacks
        super().__init__("Witch Fang", level, params, phases=["preAttack"])
    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultAutos > 0:
            # champion.multiTargetSpell(champion.opponents,
            #                           champion.items, time,
            #                           1, champion.abilityScaling,
            #                           'magical')
            input_.canOnHit = True
            input_.canCrit = champion.canSpellCrit
            input_.attackType = 'magical'
            input_.scaling = champion.abilityScaling
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.manalockTime = time + .01
        return 0


class Baboom(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Baboom " + str(level), level, params, phases=["preAbility"])
        self.scaling = {1: .90}
        self.castCounter = 0
    def performAbility(self, phase, time, champion, input_=0):
        self.castCounter += 1
        if self.castCounter % 2 == 0:
            champion.applyStatus(status.DmgMultiplierModifier("Baboom"),
                                 champion, time, 2,
                                 self.scaling[self.level])
        return 0

class Multistriker(Buff):
    levels = [0, 3, 5, 7, 9]
    def __init__(self, level=0, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Multistriker " + str(level), level, params, phases=["postAttack"])
        self.scaling = {0: 0, 3: .25, 5: .65, 7: .8, 9: 1}
        self.multistrikerActive = False
        self.multistrikerAutoCount = 0
        self.auto_counter = 0

    def performAbility(self, phase, time, champion, input_=0):

        # if multistrike not active:
        # option 1: edit attackTime() function for the next 2 attacks


        if phase == "postAttack":
            if not self.multistrikerActive:
                self.auto_counter += self.scaling[self.level]
                if self.auto_counter >= 1:
                    # champion.aspd.addStat(300)
                    champion.aspd.mult = 4
                    champion.aspd.as_cap = 100
                    self.multistrikerAutoCount = 0
                    self.multistrikerActive = True
                    self.auto_counter -= 1
            elif self.multistrikerActive:
                self.multistrikerAutoCount += 1
                if self.multistrikerAutoCount == 2:
                    self.multistrikerActive = False
                    champion.aspd.mult = 1
                    champion.aspd.as_cap = 5
                    self.multistrikerAutoCount = 0
        return 0

class Mage(Buff):
    levels = [0, 3, 5, 7, 10]
    def __init__(self, level, params=0):
        super().__init__("Mage " + str(level), level, params, phases=["preCombat", "postAbility"])
        self.scaling = {0: 0, 3: .85, 5: .95, 7: 1.1, 10: 2}
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.ap.mult = self.scaling[self.level]
            # cast twice = not quite double cast time but close to it
            champion.castTime *= 1.8
        elif phase =="postAbility":
            champion.performAbility(champion.opponents, champion.items, time)

class DejaVu(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Deja Vu", level, params, phases=["preCombat", "preAttack"])
        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.manaPerAttack.addStat(15)
        if phase == "preAttack":
            champion.ap.addStat(5)
        return 0

class AsheUlt(Buff):
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Ashe Ult", level, params, phases=["preAttack"])
        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack":
            for ult in range(champion.ultsActive):
                champion.multiTargetSpell(champion.opponents,
                      champion.items, time,
                      1, champion.abilityScaling,
                      'physical')
        return 0

class AsheUltNew(Buff):
    def __init__(self, level=1, params=0):
        super().__init__("Ashe Ult New", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        print("ult count: {}".format(champion.ultCount))
        for ult in range(champion.ultCount):
            champion.multiTargetSpell(champion.opponents,
                  champion.items, time,
                  1, champion.abilityScaling,
                  'physical')
        return 0

# AUGMENTS

class JeweledLotusII(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        super().__init__("Jeweled Lotus II", level, params, phases=["preCombat"])
        self.critBonus = 0.15

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
            champion.crit.addStat(self.critBonus)
        return 0

class JeweledLotusIII(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        super().__init__("Jeweled Lotus III", level, params, phases=["preCombat"])
        self.critBonus = 0.45

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
            champion.crit.addStat(.45)
        return 0

class BlossomingLotusI(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Blossoming Lotus I", level, params, phases=["preCombat", "onUpdate"])
        self.critBonus = 0.05
        self.nextBonus = 3

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.crit.addStat(self.critBonus)
        return 0

class BlossomingLotusII(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Blossoming Lotus II", level, params, phases=["preCombat", "onUpdate"])
        self.critBonus = 0.1
        self.nextBonus = 3

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.crit.addStat(self.critBonus)
        return 0

class Spellblades(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Spellblades", level, params, phases=["preAbility", "preAttack"])
        self.enhancedAuto = False
        self.dmgRatio = 120
        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                champion.doDamage(champion.opponents[0], [], 0, champion.ap.stat * self.dmgRatio,
                                  champion.ap.stat * self.dmgRatio, 'magical', time)

        return 0

class FinalAscension(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Final Ascension", level, params, phases=["preCombat", "onUpdate"])
        self.initialDmgBonus = 0.15
        self.dmgBonus = 0.3
        self.nextBonus = 15

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.dmgMultiplier.addStat(self.initialDmgBonus)
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 99999
                champion.dmgMultiplier.addStat(self.dmgBonus)
        return 0

class ClockworkAccelerator(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Clockwork Accelerator", level, params, phases=["onUpdate"])
        self.asBonus = 9
        self.nextBonus = 3

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.aspd.addStat(self.asBonus)
        return 0

class Shred30(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("30% Armor/MR Shred", level, params, phases=["onUpdate"])

    def performAbility(self, phase, time, champion, input_=0):
        # expensive af but w/e
        for opponent in champion.opponents:
            opponent.armor.mult = .7
            opponent.mr.mult = .7
        return 0