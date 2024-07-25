from collections import deque, Counter
from set12items import Item
from champion import Stat, Attack, AD
import numpy as np
import status
import random

augments = ['BlossomingLotusI', 'BlossomingLotusII',
            'ClockworkAccelerator', 'JeweledLotusII',
            'JeweledLotusIII', 'Shred30']

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

class NoBuff(Buff):
    levels = [0]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("NoItem", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class Frost(Buff):
    levels = [0, 3, 5, 7, 9]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Frost " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: 15, 5: 30, 7: 45, 9: 75}
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
        self.scaling = {0: 0, 2: 15, 4: 40, 6: 70}
        self.takedownScaling = {0: 0, 2: 15, 4: 25, 6: 40}
        # time for first takedown
        self.has_activated = False
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.atk.addStat(self.scaling[self.level])
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
    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(self.scaling[self.level])
        return 0

class Blaster(Buff):
    levels = [0, 2, 4, 6]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Blaster " + str(level), level, params,
                         phases=["preCombat", "preAbility"])
        self.scaling = {0: 0, 2: .08, 4: .15, 6: .3}
        self.burstScaling = {0: 0, 2: .17, 4: .3, 6: .6}
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
        self.scaling = {0: 0, 2: .1, 4: .18, 6: .25}
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0

class Incantor(Buff):
    levels = [0, 2, 4]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Incantor " + str(level), level, params,
                         phases=["preCombat", "preAttack", "preAbility",
                                 "onUpdate"])
        self.scaling = {0: 0, 2: 1, 4: 2}
        self.baseBuff = {0: 0, 2: 10, 4: 20}
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
                        champion.ap.addStat(1*(self.level - 1)*self.scaling[self.level])
                        self.next_faux_count += faux_as
                        self.faux_attacks += 1
                        self.stacks += 1
                    if self.faux_attacks == faux_attacks_until_cast:
                        stacks_to_add = min(3, self.maxStacks - self.stacks)
                        self.stacks += stacks_to_add
                        champion.ap.addStat(stacks_to_add*(self.level-1)*self.scaling[self.level])
                        self.faux_attacks = 0
        if self.stacks > self.maxStacks:
            self.stacks = self.maxStacks
        return 0

class ASBuff(Buff):
    levels = list(range(1, 101))
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Attack Speed " + str(level), level, params, phases=["preCombat"])
        self.scaling = {}
        for n in range(1,101):
            self.scaling[n] = n
    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.scaling[self.level])
        return 0

class SmolderUlt(Buff):
    levels = [1]
    def __init__(self, level=1, params=0):
        # params is number of stacks
        super().__init__("Learning to Fly", level, params, phases=["preAttack"])
    def performAbility(self, phase, time, champion, input_=0):
        # input is attack
        if champion.ultActive:
            input_.canOnHit = False
            input_.canCrit = champion.canSpellCrit
            input_.attackType = 'physical'
            input_.scaling = champion.abilityScaling
            print(input_)
        return 0

class CassUlt(Buff):
    levels = [1]
    def __init__(self, level=1, params=0):
        # params is number of stacks
        super().__init__("Witch Fang", level, params, phases=["preAttack"])
    def performAbility(self, phase, time, champion, input_=0):
        # input is attack
        if champion.ultActive:
            input_.canOnHit = False
            input_.canCrit = champion.canSpellCrit
            input_.attackType = 'magical'
            input_.scaling = champion.abilityScaling
            print(input_)
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
        self.scaling = {0: 0, 3: .3, 5: .5, 7: .65, 9: 1}
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
                    self.multistrikerAutoCount = 0
        return 0

class Mage(Buff):
    levels = [0, 3, 5, 7, 9]
    def __init__(self, level, params=0):
        super().__init__("Mage " + str(level), level, params, phases=["preCombat", "postAbility"])
        self.scaling = {0: 0, 3: .75, 5: .9, 7: 1.05, 9: 1.35}
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.ap.mult = self.scaling[self.level]
            # cast twice = double cast time
            champion.castTime *= 2
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
            champion.ap.addStat(8)
        return 0

class AsheUlt(Buff):
    def __init__(self, level=0, params=0):
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

class ClockworkAccelerator(Buff):
    levels=[1]
    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Clockwork Accelerator", level, params, phases=["onUpdate"])
        self.asBonus = 6
        self.nextBonus = 4

        #self.chakramQueue = deque()
        # chakram[0]: number of chakrams
        # chakram[1]: time to end
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 4
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