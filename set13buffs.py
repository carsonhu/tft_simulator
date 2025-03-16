from collections import deque, Counter
from set13items import Item
from champion import Stat, Attack, AD

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

# Example usage
file_path = "set13anomalies.py"
anomalies = get_classes_from_file(file_path)

class_buffs = ['Sorcerer', 'FormSwapper', 'Family', 'Visionary', 'Sniper', 
               'Quickstriker', 'Dominator', 'Ambusher', 'Rebel',
               'Conqueror', 'EmissaryNami', 'EmissaryTrist',
               'PitFighter', 'ExperimentTwitch', 'Enforcer',
               'BanishedMage', 'Artillerist', 'Automata']

augments = ['ClockworkAccelerator', 'ManaflowI', 'ManaflowII', 'Shred30',
            'BlazingSoulI', 'BlazingSoulII', 'BadLuckProtection',
            'CalculatedEnhancement', 'GlassCannonI',
            'GlassCannonII', 'FlurryOfBlows', 'MacesWill', 'Backup',
            'CategoryFive', 'Moonlight', 'PiercingLotusI',
            'PiercingLotusII']



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


class Sorcerer(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__("Sorcerer " + str(level), level, params,
                         phases=["preCombat"])
        self.base_scaling = 10
        self.scaling = {2: 20, 4: 50, 6: 85}

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.base_scaling)
        champion.ap.addStat(self.scaling[self.level])
        return 0


class PitFighter(Buff):
    levels = [0, 2, 4, 6, 8]

    def __init__(self, level, params):
        super().__init__("Pit Fighter " + str(level), level, params,
                         phases=["onDealDamage"])
        self.scaling = {2: .06, 4: .12, 6: .22, 8: .45}

    def performAbility(self, phase, time, champion, input_=0):
        true_dmg = self.scaling[self.level] * input_
        champion.doDamage(champion.opponents[0], [], 0,
                          true_dmg, true_dmg, 'true', time)
        return input_


class ExperimentTwitch(Buff):
    levels = [0, 3, 5, 7]

    def __init__(self, level, params):
        super().__init__("ExperimentTwitch " + str(level), level, params,
                         phases=["postAttack"])
        self.scaling = {3: .15, 5: .15, 7: .3}

    def performAbility(self, phase, time, champion, input_=0):
        if len(champion.opponents) > 0:
            if champion.numAttacks % 5 == 0:
                opponent = champion.opponents[0]
                dmg = opponent.hp.stat * self.scaling[self.level]
                champion.doDamage(champion.opponents[0], [], 0,
                    dmg, dmg, 'physical', time)
        return 0


class Visionary(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__("Visionary " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: .25, 4: .5, 6: .75}

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaGainMultiplier.mult += self.scaling[self.level]
        return 0


class Quickstriker(Buff):
    levels = [0, 2, 3, 4]

    def __init__(self, level, params):
        super().__init__("Quickstriker " + str(level), level, params,
                         phases=["preCombat"])
        # quickstriker just takes average of min and max instead
        self.scaling = {2: 40, 3: 55, 4: 70}

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling[self.level])
        return 0


class Family(Buff):
    levels = [0, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Family " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {3: .25, 4: .3, 5: .4}
        self.as_scaling = {3: 0, 4: 20, 5: 20}

    def performAbility(self, phase, time, champion, input_=0):
        champion.fullMana.mult -= self.scaling[self.level]
        champion.aspd.addStat(self.as_scaling[self.level])
        return 0


class Enforcer(Buff):
    levels = [0, 2, 4, 6, 8]

    def __init__(self, level, params):
        super().__init__("Enforcer (No Wanted) " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: .12, 4: .2, 6: .33, 8: .44}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


class FormSwapper(Buff):
    levels = [0, 2, 4]

    def __init__(self, level, params):
        super().__init__("Form Swapper " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {2: .20, 4: .44}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


class LeblancUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("The Chains of Fate", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        # input is attack
        if champion.ultActive and champion.ultAutos > 0:
            champion.multiTargetSpell(champion.opponents,
                                      champion.items, time,
                                      1, champion.autoAbilityScaling,
                                      'magical')    
            champion.multiTargetSpell(champion.opponents,
                                      champion.items, time,
                                      1, lambda x, y, z: champion.autoAbilityScaling(x, y, z) * .25,
                                      'true')    
            champion.ultAutos -= 1
            # just call doattack
            if champion.ultAutos == 0:
                champion.manalockTime = time + .01
                champion.ultActive = False
                # so u dont gain mana on last auto
        return 0


class DravenUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Spinning Axes", level, params, phases=["preAttack", "onUpdate"])
        self.attack_queue = deque()

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack":
            if champion.axes > 0:
                input_.canOnHit = True
                input_.canCrit = champion.canCrit
                input_.attackType = 'physical'
                input_.scaling = champion.abilityScaling
                champion.axes -= 1
                self.attack_queue.append(time + 1.5)
        if phase == "onUpdate":
            if self.attack_queue and self.attack_queue[0] < time:
                if champion.axes < 2:
                    champion.axes += 1
                self.attack_queue.popleft()
        return 0


class TwitchUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Spray and Pray", level, params, phases=["preCombat", "preAttack"])
        self.newAttack = Attack()

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.newAttack.opponents = champion.opponents
            self.newAttack.canCrit = champion.canSpellCrit
            self.newAttack.canOnHit = True
            self.newAttack.numTargets = 1
        else:
            # input is attack
            if champion.ultActive and champion.ultAutos > 0:
                input_.canOnHit = True
                input_.canCrit = champion.canSpellCrit
                input_.attackType = 'physical'
                input_.scaling = champion.abilityScaling
                champion.ultAutos -= 1
                # just call doattack

                # 
                #
                # newAttack = Attack(opponents=champion.opponents,
                #                    canCrit=champion.canSpellCrit,
                #                    canOnHit=True,
                #                    numTargets=1)
                self.newAttack.canCrit = champion.canSpellCrit
                # self.newAttack.opponents = champion.opponents
                # self.newAttack.canCrit = champion.canSpellCrit
                # self.newAttack.canOnHit = True
                # self.newAttack.numTargets = 1
                for index in range(champion.num_targets - 1):                
                    self.newAttack.scaling = lambda x, y, z: .6**(index+1) * champion.abilityScaling(x, y, z)
                    champion.doAttack(self.newAttack, champion.items, time)

                    # necessary to be able to pickle the object
                    self.newAttack.scaling = None

                if champion.ultAutos == 0:
                    champion.aspd.addStat(-85)
                    champion.manalockTime = time + .01
                    champion.ultActive = False
                    # so u dont gain mana on last auto
        return 0


class BanishedMage(Buff):
    levels = [0, 1]

    def __init__(self, level, params):
        # just sets whether Mel has 10% dmg amp
        super().__init__("Banished Mage " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 1: .1}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


class Sniper(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        # params is number of hexes
        super().__init__("Sniper " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: .05, 4: .1, 6: .2}
        self.base_scaling = {0: 0, 2: .05, 4: .35, 6: .75}
        self.base_bonus = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.base_scaling[self.level] + self.scaling[self.level]*self.base_bonus)
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
    levels = [0, 2, 4, 6]
    
    def __init__(self, level, params):
        super().__init__("Dominator " + str(level), level, params,
                         phases=["preAbility"])
        self.scaling = {0: 0, 2: .25, 4: .5, 6: .75}

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.scaling[self.level] * champion.fullMana.stat)
        return 0


class Automata(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__("Automata " + str(level), level, params,
                         phases=["PostOnDealDamage"])
        self.scaling = {0: 0, 2: 150, 4: 400, 6: 1200}
        self.current_crystals = 0
        self.stored_damage = 0
        self.max_crystals = 20
        self.base_pct = .25

    def performAbility(self, phase, time, champion, input_=0):
        # input_: (dmg, dtype)
        if self.current_crystals < 20:
            self.current_crystals += 1
            self.stored_damage += input_[0]
        if self.current_crystals >= 20:
            baseDmg = self.stored_damage * self.base_pct + self.scaling[self.level]
            champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
            self.current_crystals = 0
            self.stored_damage = 0
        return 0


class Ambusher(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Ambusher " + str(level), level, params,
                         phases=["preCombat"])
        self.crit_scaling = {0: 0, 2: 25, 3: 35, 4: 45, 5: 55}
        self.crit_dmg_scaling = {0: 0, 2: 10, 3: 20, 4: 25, 5: 25}

    def performAbility(self, phase, time, champion, input_=0):
        champion.crit.addStat(self.scaling[self.level])
        champion.critDmg.addStat(self.scaling[self.level])
        champion.canSpellCrit = True
        return 0


class Artillerist(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        # params is number of targets
        super().__init__("Artillerist " + str(level), level, params,
                         phases=["preCombat", "preAttack"])
        self.attacks_until_rocket = {0: 0, 2: 5, 4: 5, 6: 3}
        self.rocket_scaling = {0: 0, 2: 1.25, 4: 1.25, 6: 1.25}
        self.ad_scaling = {0:0, 2: 10, 4: 45, 6: 70}
        self.num_targets = 0
        self.next_rocket = self.attacks_until_rocket[self.level]
        self.extraBuff(params)

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# Targets",
                "Min": 1,
                "Max": 3,
                "Default": 2}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.atk.addStat(self.ad_scaling[self.level])
        elif phase == "preAttack":
            # if attack is a spell, this is queued up until first real auto
            if self.next_rocket <= 1 and input_.regularAuto:
                input_.canOnHit = True # does it?
                input_.canCrit = champion.canCrit
                input_.attackType = 'physical'
                input_.scaling = lambda level, AD, AP: AD * self.rocket_scaling[self.level]
                input_.numTargets = self.num_targets
                self.next_rocket = self.attacks_until_rocket[self.level]
            else:
                self.next_rocket -= 1
        return 0

    def extraBuff(self, num_targets):
        self.num_targets = num_targets


class Emissary(Buff):
    levels = [0, 1, 4]

    def __init__(self, level, params, emissary_name):
        # params: Whether champ is emissary
        super().__init__("Emissary " + str(level), level, params,
                         phases=["preCombat"])
        self.emissary_name = emissary_name
        self.is_emissary = 0
        self.extraBuff(params)

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Emissary",
                "Min": 0,
                "Max": 1,
                "Default": 1}

    def performAbility(self, phase, time, champion, input_=0):
        if self.emissary_name == "Nami" or self.level == 4:
            champion.manaPerAttack.addStat(2)
        if self.emissary_name == "Tristana" or self.level == 4:
            champion.aspd.addStat(6 * champion.level)
        if self.level == 4 and self.is_emissary:
            champion.dmgMultiplier.addStat(.2)
        return 0

    def extraBuff(self, is_emissary):
        self.is_emissary = is_emissary


class EmissaryNami(Emissary):
    def __init__(self, level, params):
        super().__init__(level, params, "Nami")


class EmissaryTrist(Emissary):
    def __init__(self, level, params):
        super().__init__(level, params, "Tristana")


class Rebel(Buff):
    levels = [0, 3, 5, 7]

    def __init__(self, level, params):
        super().__init__("Rebel " + str(level), level, params,
                         phases=["onUpdate"])
        self.atk_scaling = {0: 0, 3: 15, 5: 30, 7: 45}
        self.ap_scaling = {0: 0, 3: 15, 5: 30, 7: 45}
        self.buff_duration = 5
        self.aspd_bonus = 60

    def performAbility(self, phase, time, champion, input_=0):
        if time > champion.rebel_time:
            champion.atk.addStat(self.atk_scaling[self.level])
            champion.ap.addStat(self.ap_scaling[self.level])
            champion.applyStatus(status.ASModifier("Rebel"),
            champion, time, self.buff_duration, self.aspd_bonus)
            champion.rebel_time = 999
        return 0


class Conqueror(Buff):
    levels = [0, 2, 4, 6, 9]

    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Conqueror " + str(level), level, params,
                         phases=["preCombat"])
        self.scaling = {0: 0, 2: 22, 4: 25, 6: 40, 9: 100}
        self.chests = 0
        self.chest_scaling = 0.08
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(self.scaling[self.level] * (1 + self.chest_scaling * self.chests))
        champion.ap.addStat(self.scaling[self.level] * (1 + self.chest_scaling * self.chests))
        return 0

    def extraParameters():
        return {"Title": "War Chests",
                "Min": 0,
                "Max": 15,
                "Default": 3}

    def extraBuff(self, chests):
        self.chests = chests


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

# AUGMENTS


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
        champion.manaPerAttack.addStat(4)
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
        champion.aspd.addStat(8)
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
        champion.aspd.addStat(30)
        champion.ap.addStat(45)
        return 0


class BadLuckProtection(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Bad Luck Protection", level, params, phases=["onUpdate"])
  
    def performAbility(self, phase, time, champion, input_=0):
        if champion.canCrit or champion.canSpellCrit or champion.crit.base > 0:
            champion.canCrit = False
            champion.canSpellCrit = False
            champion.atk.addStat(champion.crit.stat * 100)
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