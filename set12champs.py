from champion import Champion, Stat, Attack
from collections import deque
import math
import numpy as np
import random
import set12buffs as buffs
import status

champ_list = ['Ezreal', 'Nomsy', 'Twitch', 'Ashe', 'Tristana', 'Galio', 'Zoe', 'Veigar']

class Ezreal(Champion):
    def __init__(self, level):
        hp= 700
        atk = 60
        curMana = 15
        fullMana = 75
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Ezreal', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Portal', 'Blaster']
        self.total_targets = 4
        self.castTime = 1.5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [2.6, 2.65, 2.75]
        abilityScale = [50, 60, 75]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.total_targets):
            self.multiTargetSpell(opponents, items,
                time, 1, lambda x, y, z: .8**(count) * self.abilityScaling(x, y, z), 'physical')

class Nomsy(Champion):
    def __init__(self, level):
        hp= 500
        atk = 50
        curMana = 15
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Nomsy', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Dragon', 'Hunter']
        self.castTime = .5
        self.ultAmped = False
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [3.45, 3.5, 3.55]
        abilityScale = [40, 60, 100]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def ampedAbilityScaling(self, level, AD, AP):
        adScale = [5, 5, 5]
        abilityScale = [40, 60, 100]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD


    def performAbility(self, opponents, items, time):
        if not self.ultAmped:
            self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, 'physical')
        else:
            self.multiTargetSpell(opponents, items, time, 3, self.abilityScaling, 'physical')

class Twitch(Champion):
    def __init__(self, level):
        hp= 450
        atk = 50
        curMana = 0
        fullMana = 40
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Twitch', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Frost', 'Hunter']
        self.num_targets = 3
        self.status_duration = 5
        self.castTime = .5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [1.6, 1.6, 1.6]
        abilityScale = [20, 30, 45]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            self.multiTargetSpell(opponents, items,
                time, 1, lambda x, y, z: .8**(count) * self.abilityScaling(x, y, z), 'physical')
            for opponent in opponents[0:self.num_targets]:
                opponent.applyStatus(status.ArmorReduction("Twitch"), self, time, self.status_duration, .8)

class Ashe(Champion):
    def __init__(self, level):
        hp= 450
        atk = 50
        curMana = 30
        fullMana = 80
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Ashe', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Eldritch', 'Multistriker']
        self.buff_duration = 5
        self.castTime = 0
        self.manalockDuration = 0.5 # idk what it is
        self.ultsActive = 0
        self.ultCount = 0
        self.items = [buffs.AsheUlt()]
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [.45, .45, .45]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.applyStatus(status.AsheUlt("Ashe {}".format(self.ultCount)),
            self, time, math.floor(self.buff_duration * self.ap.stat), 0)
        self.ultCount += 1

class Tristana(Champion):
    def __init__(self, level):
        hp= 550
        atk = 55
        curMana = 0
        fullMana = 60
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Tristana', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Faerie', 'Blaster']
        self.castTime = 1.5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [3.35, 3.4, 3.5]
        abilityScale = [40, 55, 90]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling, 'physical')

class Galio(Champion):
    # Daeja
    def __init__(self, level):
        hp= 750
        atk = 55
        curMana = 30
        fullMana = 90
        aspd = .65
        armor = 45
        mr = 45
        super().__init__('Galio', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Mage']
        self.castTime = .5
        self.manalockDuration = .75
        self.items = [buffs.DejaVu()]
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        daeja_amplifier = 2.3
        abilityScale = [50, 75, 115]
        return abilityScale[level - 1] * (AP) * daeja_amplifier

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)

class Zoe(Champion):
    # ignoring shred for now
    def __init__(self, level):
        hp= 450
        atk = 40
        curMana = 0
        fullMana = 30
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Zoe', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Scholar']
        self.castTime = .5
        self.manalockDuration = .75
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [130, 195, 295]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)

class Veigar(Champion):
    def __init__(self, level):
        hp= 550
        atk = 45
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Veigar', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Honeymancy', 'Mage']
        self.castTime = .5
        self.manalockDuration = .75
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [215, 320, 515]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)


class Syndra(Champion):
    def __init__(self, level):
        hp= 700
        atk = 45
        curMana = 0
        fullMana = 30
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Syndra', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Fated', 'Arcanist']
        self.butterflies = 6

        self.castTime = 1.5
        self.manalockDuration = 1.5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [45, 70, 180]
        return abilityScale[level - 1] * (AP) * self.butterflies


    def performAbility(self, opponents, items, time):
        # not sure if its before or aftter cast
        self.butterflies += 1
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)


class Kindred(Champion):
    def __init__(self, level):
        hp= 550
        atk = 40
        curMana = 0
        fullMana = 30
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Kindred', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Fated', 'Dryad', 'Reaper']
        self.castTime = .5
        self.manalockDuration = .75
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [135, 200, 300]
        return abilityScale[level - 1] * (AP)
    def extraAbilityScaling(self, level, AD, AP):
        abilityScale = [70, 105, 165]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)
        self.multiTargetSpell(opponents, items,
            time, 1, self.extraAbilityScaling)

class EtherealShen(Champion):
    def __init__(self, level):
        hp= 800
        atk = 55    
        curMana = 25
        fullMana = 75
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Shen', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.castTime = 1
        self.manalockDuration = 4
        self.etherealStacks = 3
        self.ultActive = False
        self.items = [buffs.EtherealShen()]
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [1, 1.5, 2.35]
        return abilityScale[level - 1] * self.armor.stat

    def performAbility(self, opponents, items, time):
        self.ultActive = True
        self.etherealStacks = 3

class Kogmaw(Champion):
    def __init__(self, level):
        hp= 500
        atk = 55
        curMana = 15
        fullMana = 75
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Kogmaw', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Honeymancy', 'Hunter']
        self.castTime = .5
        self.num_targets = 2
        self.manalockDuration = 1
        self.buff_duration = 4
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [2.9, 3, 3.25]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        # does not count as an attack
        self.multiTargetSpell(opponents, items,
            time, self.num_targets, self.abilityScaling, 'physical')
        asBuff = [20, 25, 35]
        self.applyStatus(status.ASModifier("Kogmaw"),
            self, time, self.buff_duration, asBuff[self.level - 1] * self.ap.stat)
        # add ad scaling

class Aphelios(Champion):
    def __init__(self, level):
        hp= 650
        atk = 60
        curMana = 40
        fullMana = 100
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Aphelios', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Fated', 'Sniper']
        self.castTime = .5
        self.num_targets = 3
        self.manalockDuration = 1
        self.status_duration = 7
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [1.85, 1.85, 1.95]
        abilityScale = [30, 45, 70]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        # doesn't count as an autoattack
        for opponent in opponents[0:self.num_targets]:
            opponent.applyStatus(status.ArmorReduction("Aphelios"), self, time, self.status_duration, .8)
        self.multiTargetSpell(opponents, items,
            time, self.num_targets, self.abilityScaling, 'physical')
        
        # add ad scaling

class Tristana(Champion):
    def __init__(self, level):
        hp= 700
        atk = 55
        curMana = 40
        fullMana = 100
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Tristana', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Duelist']
        self.castTime = 1.5
        self.manalockDuration = 1.5
        self.buff_duration = 6
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [2.65, 2.65, 2.7]
        abilityScale = [75, 115, 185]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 2, self.abilityScaling, 'physical')
        adBuff = [50, 50, 55]
        self.applyStatus(status.ADModifier("Senna"),
            self, time, self.buff_duration, adBuff[self.level - 1])
        # add ad scaling

class Irelia(Champion):
    def __init__(self, level):
        hp= 900
        atk = 80
        curMana = 0
        fullMana = 80
        aspd = .9
        armor = 40  
        mr = 40
        super().__init__('Irelia', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 1
        # self.items = [buffs.IreliaUlt()]

    def abilityScaling(self, level, AD, AP):
        adScale = [3,3,3]
        apScale = [100, 100, 100]
        return adScale[level - 1] * AD + apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetAttack(opponents, items,
            time, 3, self.abilityScaling, 'physical', numAttacks=1)

class ZeroResistance(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 0
        mr = 0
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5
    def performAbility(self, opponents, items, time):
        return 0

class DummyTank(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 100
        mr = 100
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5
    def performAbility(self, opponents, items, time):
        return 0

class SuperDummyTank(Champion):
    def __init__(self, level):
        hp = 2000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 200
        mr = 200
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5
    def performAbility(self, opponents, items, time):
        return 0

