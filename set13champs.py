from champion import Champion, Stat, Attack
from collections import deque
import math
import numpy as np
import random
import set13buffs as buffs
import status

champ_list = ['Cassiopeia', 'Kogmaw', 'Lux', 'Maddie', 'Morgana', 'Powder', 'Silco', 
              'TwistedFate', 'Zeri', 'Ziggs', 'Gangplank', 'Heimerdinger']

class Lux(Champion):
    def __init__(self, level):
        hp= 500
        atk = 35    
        curMana = 15
        fullMana = 75
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Lux', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Academy', 'Sorcerer']
        self.castTime = .5
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [360, 540, 900]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')

class Heimerdinger(Champion):
    def __init__(self, level):
        hp= 800
        atk = 40
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Heimerdinger', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Visionary']
        self.castTime = .75
        missile_amount = [5, 5, 7]
        self.missiles = missile_amount[level - 1]
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [54, 81, 270]
        return apScale[level - 1] * AP * self.missiles

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.missiles += 1

class Gangplank(Champion):
    def __init__(self, level):
        hp= 700
        atk = 50
        curMana = 0
        fullMana = 75
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Gangplank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['FormSwapper']
        self.castTime = 1
        self.num_targets = 2
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [30, 45, 70]
        adScale = [3.25, 3.25, 3.25]
        return apScale[level - 1] * AP + adScale[level - 1] * AD
    def adjacentAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * .2

    def performAbility(self, opponents, items, time):
        num_bombs = 3
        for n in range(num_bombs):
            self.multiTargetSpell(opponents, items,
                    time, 1, self.abilityScaling, 'physical')
            if self.num_targets > 1:
                self.multiTargetSpell(opponents, items,
                        time, self.num_targets - 1, self.adjacentAbilityScaling, 'physical')

class TwistedFate(Champion):
    def __init__(self, level):
        hp= 700
        atk = 35    
        curMana = 25
        fullMana = 75
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Twisted Fate', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Enforcer', 'Quickstriker']
        self.castTime = 1.1
        self.num_targets = 2
        self.notes = "Num targets refers solely to red card"
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [110, 165, 255]
        return apScale[level - 1] * AP
    def goldAbilityScaling(self, level, AD, AP):
        apScale = [210, 315, 505]
        return apScale[level - 1] * AP
    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, self.goldAbilityScaling, 'magical')

class Cassiopeia(Champion):
    def __init__(self, level):
        hp= 700
        atk = 40    
        curMana = 10
        fullMana = 40
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Cassiopeia', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Dominator']
        self.castTime = 1
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [230, 345, 550]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [160, 245, 385]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        if self.numCasts % 3 == 0:
            self.multiTargetSpell(opponents, items,
                time, 2, self.extraAbilityScaling, 'magical')

class Maddie(Champion):
    def __init__(self, level):
        hp= 500
        atk = 50
        curMana = 20
        fullMana = 120
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Maddie', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Enforcer', 'Sniper']
        self.castTime = 1.5
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        adScale = [1.25, 1.25, 1.4]
        apScale = [10, 15, 25]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for n in range(6):
            self.multiTargetSpell(opponents, items,
                    time, 1, self.abilityScaling, 'physical')

class Renata(Champion):
    def __init__(self, level):
        hp= 600
        atk = 35    
        curMana = 30
        fullMana = 90
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Renata', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Visionary']
        self.num_targets = 2
        self.castTime = 1
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [280, 420, 650]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [140, 210, 325]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        if self.num_targets > 1:
            self.multiTargetSpell(opponents, items,
                    time, self.num_targets - 1, self.extraAbilityScaling, 'magical')

class Kogmaw(Champion):
    def __init__(self, level):
        hp= 650
        atk = 15    
        curMana = 0
        fullMana = 40
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Kogmaw', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Sniper']
        self.castTime = 0
        self.items = [buffs.KogUlt()]
        self.notes = "Automata will be coded in later"

        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [50, 75, 120]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.aspd.addStat(25)

class Morgana(Champion):
    def __init__(self, level):
        hp= 500
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Morgana', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Visionary']
        self.castTime = 0.5
        self.notes = "Damage is instant here"

        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [500, 750, 1150]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')

class Silco(Champion):
    def __init__(self, level):
        hp= 800
        atk = 40
        curMana = 30
        fullMana = 80
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Silco', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Dominator']
        self.num_attacks = 5
        self.num_monstrosities = [4, 4, 8]
        self.castTime = 1.3
        self.notes = "Damage is instant here"


        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [100, 200, 1000]
        return apScale[level - 1] * AP

    def monsterAbilityScaling(self, level, AD, AP):
        apScale = [36, 55, 100]
        return apScale[level - 1] * AP * self.num_attacks

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        for m in range(self.num_monstrosities[self.level - 1]):
            self.multiTargetSpell(opponents, items,
                time, 1, self.monsterAbilityScaling, 'magical')

class Powder(Champion):
    def __init__(self, level):
        hp= 500
        atk = 35
        curMana = 40
        fullMana = 120
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Powder', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Family', 'Visionary']
        self.castTime = 2
        self.num_targets = 4
        self.damage_falloff = [.7, .7, .75]
        self.notes = "1 target at epicenter, 1 target 2 hexes away, the rest 1 hex away"

        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [320, 480, 680]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling, 'magical')
        if self.num_targets > 2:
            self.multiTargetSpell(opponents, items,
                time, self.num_targets - 2, lambda x, y, z: self.damage_falloff[x - 1]**1 * self.abilityScaling(x, y, z), 'magical')
        if self.num_targets > 1:
            self.multiTargetSpell(opponents, items,
                time, 1, lambda x, y, z: self.damage_falloff[x - 1]**2 * self.abilityScaling(x, y, z), 'magical')
        


class Zeri(Champion):
    def __init__(self, level):
        hp= 600
        atk = 45    
        curMana = 0
        fullMana = -1
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Zeri', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Sniper']
        self.castTime = 0
        self.items = [buffs.ZeriUlt()]
        self.notes = "we aint coding in firelight"
        self.manaGainMultiplier = Stat(0, 0, 0)

        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        adScale = [1.8, 1.8, 1.8]
        apScale = [10, 15, 20]
        return apScale[level - 1] * AP + adScale[level - 1] * AD


class Ziggs(Champion):
    def __init__(self, level):
        hp= 600
        atk = 35    
        curMana = 15
        fullMana = 60
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Ziggs', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Dominator']
        self.castTime = .5
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [160, 240, 375]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [80, 120, 180]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 3, self.extraAbilityScaling, 'magical')

class Hwei(Champion):
    def __init__(self, level):
        hp= 650
        atk = 35
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Hwei', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Frost', 'Blaster']
        self.num_targets = 2
        self.castTime = .5
        self.notes = "3rd cast will hit exactly 2 extra targets"
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [150, 225, 350]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
            num_targets = self.num_targets if self.numCasts % 3 != 0 else self.num_targets + 2
            self.multiTargetSpell(opponents, items,
                time, num_targets, self.abilityScaling, 'magical')

class Nomsy(Champion):
    def __init__(self, level):
        hp= 500
        atk = 48
        curMana = 10
        fullMana = 50
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Nomsy', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        # probably edit this to also include default level / params
        self.default_traits = ['Dragon', 'Hunter']
        self.castTime = .5
        self.ultAmped = False
        self.notes = "Dragon 2 not implemented yet"
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [4, 4, 4]
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

class Jinx(Champion):
    def __init__(self, level):
        hp= 650
        atk = 52
        curMana = 0
        fullMana = 50
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Jinx', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Sugarcraft', 'Hunter']

        # ultAmped: for dragon
        self.castTime = 0
        self.ultActive = False
        self.manalockDuration = 5 # idk what it is
        self.buff_duration = 5
        self.items = [buffs.JinxUlt()]
        self.notes = "Decaying AS decreases linearly across the 5 second duration. She can naturally crit when ability is active."

    def abilityScaling(self, level, AD, AP):
        adScale = [1.1, 1.1, 1.1]
        apScale = [16, 24, 36]
        return adScale[level - 1] * AD + apScale[level-1] * AP


    def performAbility(self, opponents, items, time):
        # self.ultActive = True
        self.applyStatus(status.UltActivator("JinxUlti"),
            self, time, self.buff_duration)
        self.applyStatus(status.DecayingASModifier("Jinx"),
            self, time, self.buff_duration, 125)

class Seraphine(Champion):
    def __init__(self, level):
        hp= 500
        atk = 25
        curMana = 10
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Seraphine', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Mage']
        self.num_targets = 3
        self.castTime = .5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [240, 360, 540]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            self.multiTargetSpell(opponents, items,
                time, 1, lambda x, y, z: .65**(count) * self.abilityScaling(x, y, z), 'magical')

class Soraka(Champion):
    def __init__(self, level):
        hp= 500
        atk = 30
        curMana = 10
        fullMana = 50
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Soraka', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Sugarcraft', 'Mage']
        self.num_targets = 2
        self.castTime = .5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [200, 300, 450]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
            self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')

class Twitch(Champion):
    def __init__(self, level):
        hp= 450
        atk = 50
        curMana = 0
        fullMana = 35
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Twitch', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Frost', 'Hunter']
        self.num_targets = 3
        self.status_duration = 5
        self.castTime = .5
        self.ability_falloff = .2
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [1.8, 1.8, 1.9]
        abilityScale = [20, 30, 45]
        return abilityScale[level - 1] * (AP) + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            self.multiTargetSpell(opponents, items, time, 1,
                                  lambda x, y, z: (1-self.ability_falloff)**(count)*self.abilityScaling(x, y, z),
                                  'physical', numAttacks=0)
            for opponent in opponents[0:self.num_targets]:
                opponent.applyStatus(status.ArmorReduction("Twitch"), self, time, self.status_duration, .8)

class Olaf(Champion):
    def __init__(self, level):
        hp= 1150
        atk = 75
        curMana = 30
        fullMana = 80
        aspd = .85
        armor = 60
        mr = 60
        super().__init__('Olaf', hp, atk, curMana, fullMana,
                         aspd, armor, mr, level)
        self.default_traits = ['Frost', 'Hunter']
        self.num_targets = 2
        self.buff_duration = 5
        self.aspd_bonus = [90, 100, 300]
        self.castTime = 0
        self.manalockDuration = self.buff_duration
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [3.6, 3.6, 3.6]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.applyStatus(status.ASModifier("Olaf"),
            self, time, self.buff_duration, self.aspd_bonus[self.level-1])

class Nilah(Champion):
    def __init__(self, level):
        hp= 700
        atk = 55
        curMana = 0
        fullMana = 60
        aspd = .8
        armor = 35
        mr = 35
        super().__init__('Nilah', hp, atk, curMana, fullMana,
                         aspd, armor, mr, level)
        self.default_traits = ['Warrior']
        self.num_targets = 2
        self.buff_duration = 3
        self.aspd_bonus = 60
        self.castTime = 1
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [3.6, 3.6, 3.8]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, self.num_targets, self.abilityScaling, 'physical', numAttacks = 1)
        self.applyStatus(status.ASModifier("Nilah"),
            self, time, self.buff_duration, self.aspd_bonus)

class Ashe(Champion):
    def __init__(self, level):
        hp= 450
        atk = 50
        curMana = 30
        fullMana = 100
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Ashe (14.18)', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Multistriker']
        # self.buff_duration = [5, 8, 12]
        self.castTime = 0
        # self.manalockDuration = 0.5 # idk what it is
        self.ultCount = 0
        self.items = [buffs.AsheUltNew()]
        # we instead just say that every other cast is amped
        self.notes = "Multistriker proc is 4x multiplier to AS for 2 autos."

    def abilityScaling(self, level, AD, AP):
        adScale = .3  
        apScale = [5, 8, 12]
        return adScale * AD + apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        print(self.items)
        self.ultCount += 1

class Smolder(Champion):
    def __init__(self, level):
        hp= 1000
        atk = 80
        curMana = 30
        fullMana = 80
        aspd = .85
        armor = 50
        mr = 50
        super().__init__('Smolder', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Dragon', 'Blaster']

        # ultAmped: for dragon
        self.ultAutos = 0
        self.ultAmped = False
        self.aspd_bonus = 50
        self.castTime = 0
        self.ultActive = False
        self.manalockDuration = 10 # idk what it is
        self.items = [buffs.SmolderUlt()]
        self.notes = "Dragon 2 not implemented yet"
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        adScale = [1.85, 1.9, 888]
        apScale = [25, 40, 888]
        dragonAmp = 1 if not self.ultAmped else 1.3
        return (adScale[level - 1] * AD + apScale[level-1] * AP) * dragonAmp


    def performAbility(self, opponents, items, time):
        self.ultActive = True
        self.aspd.addStat(50)
        self.ultAutos = 4 if not self.ultAmped else 6

        # self.applyStatus(status.UltActivator("SmolderUlti"),
        #     self, time, self.buff_duration)
        # self.applyStatus(status.ASModifier("SmolderAS"),
        #     self, time, self.buff_duration, self.aspd_bonus)
        

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
        self.castTime = .7

    def abilityScaling(self, level, AD, AP):
        adScale = [3.6, 3.6, 3.6]
        abilityScale = [50, 70, 110]
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
        self.default_traits = ['Mage', 'DejaVu']
        self.castTime = .5
        # self.manalockDuration = .75
        self.items = [buffs.DejaVu()]
        self.notes = "This is assuming Deja Vu."
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        daeja_amplifier = 2.25
        abilityScale = [50, 75, 115]
        return abilityScale[level - 1] * (AP) * daeja_amplifier

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)

class Ryze(Champion):
    def __init__(self, level):
        hp= 450
        atk = 45
        curMana = 15
        fullMana = 90
        aspd = .8
        armor = 30
        mr = 30
        super().__init__('Ryze', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Scholar']
        self.castTime = 1.5
        self.notes = "Currently 3 autos per cast. Not accurate to live behavior, as \
                      # autos increases as Ryze AS increases."  
        # self.manalockDuration = 1
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        portals = 10 + math.ceil(self.aspd.stat / .4)

        abilityScale = [85, 130, 300]
        return abilityScale[level - 1] * (AP) * portals


    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling, numAttacks=3)


class Karma(Champion):
    # ignoring shred for now
    def __init__(self, level):
        hp= 850
        atk = 45
        curMana = 0
        fullMana = 30
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Karma', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Chrono', 'Incantor']
        self.castTime = .5
        # self.manalockDuration = .5
        self.notes = "Dmg is instant instead of DoT for clarity. \
                      Incantor always assumes syndra. \
                      Chrono is flat 10 second proc time currently."
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [190, 285, 1600]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 2, self.abilityScaling)

class Zilean(Champion):
    # ignoring shred for now
    def __init__(self, level):
        hp= 550
        atk = 35
        curMana = 20
        fullMana = 70
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Zilean', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Frost', 'Preserver']
        self.num_targets = 2
        self.castTime = .5
        # self.manalockDuration = .75
        self.notes = "For simplicity, bomb detonates instantly instead of after 1.25s"
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [180, 270, 405]
        return abilityScale[level - 1] * (AP)

    def secondaryAbilityScaling(self, level, AD, AP):
        abilityScale = [150, 225, 340]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)
        # we don't delay the dmg because not much point
        self.multiTargetSpell(opponents, items,
            time, 1, self.abilityScaling)
        if self.num_targets > 1:
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets - 1,
                                  self.secondaryAbilityScaling)

class Bard(Champion):
    # ignoring shred for now
    def __init__(self, level):
        hp= 700
        atk = 40
        curMana = 30
        fullMana = 80
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Bard', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.default_traits = ['Sugarcraft', 'Preserver', 'Scholar']
        self.castTime = .5
        # self.manalockDuration = .75
        self.notes = "Dmg Amp portion not included."
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [105, 160, 245]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
            time, 4, self.abilityScaling)

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
        # self.manalockDuration = .75
        self.notes = "Currently does not reduce MR"
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
        # recorded as about .8s with mage
        # self.manalockDuration = .75
        self.notes = "Honeymancy will not be implemented. Mage is coded to increase cast time by 1.8x."
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [240, 300, 475]
        return abilityScale[level - 1] * (AP)

    def extraParameter(self, input_):
        # input is number of charms
        charm_ap = 3
        self.ap.addStat(charm_ap * input_)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1, self.abilityScaling)

class Ahri(Champion):
    def __init__(self, level):
        hp= 550
        atk = 45
        curMana = 0
        fullMana = 35
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Ahri', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        # default traits: would be used in ui
        self.foxfires = 3
        self.default_traits = ['ArcanaAhri', 'Scholar', 'ArcanaXerath', 'ArcanaEmblem']

        # seems to be 1.5s cast time, might get faster with higher AS?
        self.castTime = .5
        # self.manalockDuration = 1.5
        # we instead just say that every other cast is amped

    def abilityScaling(self, level, AD, AP):
        abilityScale = [230, 345, 520]
        return abilityScale[level - 1] * (AP)

    def trueDmgAbilityScaling(self, level, AD, AP):
        abilityScale = [15, 25, 35]
        return abilityScale[level - 1] * (AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1, self.abilityScaling)
        for foxfire in range(self.foxfires):
            self.multiTargetSpell(opponents, items,
                                  time, 1, self.trueDmgAbilityScaling, 'true')
        self.foxfires += 1


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
