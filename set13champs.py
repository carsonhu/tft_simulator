from champion import Champion, Stat, Attack
from collections import deque
import math
import numpy as np
import random
import set13buffs as buffs
import status

champ_list = ['Cassiopeia', 'Kogmaw', 'Lux', 'Maddie', 'Morgana', 'Powder', 'Silco', 
              'TwistedFate', 'Zeri', 'Ziggs', 'Gangplank', 'Heimerdinger', 'Elise',
              'Zyra', 'Vladimir', 'Malzahar', 'Zoe', 'Nami',
              'Swain', 'Twitch', 'Leblanc', 'Vex', 'Mel', 'Renata',
              'Ezreal', 'Draven', 'Tristana', 'Corki']

class Lux(Champion):
    def __init__(self, level):
        hp = 500
        atk = 35
        curMana = 15
        fullMana = 75
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Lux', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Academy', 'Sorcerer']
        self.castTime = 1.5
        self.notes = "technically her next auto is amped rather than just doing dmg"
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [360, 540, 900]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')

class Vex(Champion):
    def __init__(self, level):
        hp= 500
        atk = 35    
        curMana = 15
        fullMana = 75
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Vex', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Rebel', 'Visionary']
        self.castTime = 1
        self.num_targets = 2
        self.canFourStar = True
        self.notes = "Damage is instant"

    def abilityScaling(self, level, AD, AP):
        apScale = [240, 360, 580, 800]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [120, 180, 290, 400]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.extraAbilityScaling, 'magical')

class Nami(Champion):
    def __init__(self, level):
        hp= 700
        atk = 40
        curMana = 0
        fullMana = 60
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Nami', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['EmissaryNami', 'Sorcerer']
        self.castTime = 1

    def abilityScaling(self, level, AD, AP):
        apScale = [120, 180, 290]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 4, self.abilityScaling, 'magical')

class Swain(Champion):
    def __init__(self, level):
        hp= 650
        atk = 40
        curMana = 20
        fullMana = 70
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Swain', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Conqueror', 'FormSwapper', 'Sorcerer']
        self.castTime = 1.5

    def abilityScaling(self, level, AD, AP):
        apScale = [310, 465, 700]
        return apScale[level - 1] * AP

    def secondaryAbilityScaling(self, level, AD, AP):
        apScale = [38, 57, 90]
        return apScale[level - 1] * AP * 8

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, self.secondaryAbilityScaling, 'magical')

class Mel(Champion):
    def __init__(self, level):
        hp= 1800
        atk = 80
        curMana = 0
        fullMana = 40
        aspd = .8
        armor = 60
        mr = 60
        super().__init__('Mel', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['BanishedMage']
        self.castTime = 1.5
        self.shield_power = .5
        self.notes = "Banished Mage trait is the 10\% dmg amp. Assumes 50\% shield block. \
                      Mel cast time varies depending on dash, averaged to 1.5s."

    def abilityScaling(self, level, AD, AP):
        apScale = [200, 500, 2700]
        return apScale[level - 1] * AP

    def unleashAbilityScaling(self, level, AD, AP):
        apScale = [1600, 4000, 99999]
        shieldScaling = [300, 600, 10000]
        shield_bonus = (shieldScaling[level-1] * 3) * 2 * self.shield_power
        # 3 allies, 2 casts
        return apScale[level - 1] * AP + shield_bonus

    def performAbility(self, opponents, items, time):
        if self.numCasts % 3 != 0:
            self.castTime = 1.5
            self.multiTargetSpell(opponents, items,
                    time, 3, self.abilityScaling, 'magical')
        else:
            self.castTime = 2.5
            self.multiTargetSpell(opponents, items,
                    time, 1, self.unleashAbilityScaling, 'magical')

class Zoe(Champion):
    def __init__(self, level):
        hp= 800
        atk = 40
        curMana = 20
        fullMana = 80
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Zoe', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Rebel', 'Sorcerer']
        self.castTime = .7
        self.targets = [4, 4, 8]
        self.notes = "AFAIK Zoe spell hits 5 targets: Target -> Bounce -> target -> bounce -> target"

    def abilityScaling(self, level, AD, AP):
        apScale = [140, 210, 450]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.targets[self.level - 1] + 1, self.abilityScaling, 'magical')

class Viktor(Champion):
    def __init__(self, level):
        hp = 1600
        atk = 100
        curMana = 0
        fullMana = 8
        aspd = .55
        armor = 40
        mr = 40
        super().__init__('Viktor', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['']
        self.castTime = .5
        self.num_targets = 2
        self.manaPerAttack.base = 1
        self.buffs = buffs.MachineHerald()
        self.notes = "Num targets is for auto, ult hits 8 targets"

    def abilityScaling(self, level, AD, AP):
        apScale = [80, 120, 1000]
        return apScale[level - 1] * AP

    def dotScaling(self, level, AD, AP):
        apScale = [14, 21, 400]
        return apScale[level - 1] * AP * 5

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')

        opponents[0].applyStatus(status.DoTEffect("Malz {}".format(self.numCasts)),
            self, time, self.buff_duration, self.dotScaling)

class Leblanc(Champion):
    def __init__(self, level):
        hp= 500
        atk = 50    
        curMana = 45
        fullMana = 90
        aspd = .85
        armor = 15
        mr = 15
        super().__init__('Leblanc', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Sorcerer']
        self.castTime = 1
        self.ultAutos = 0
        self.ultActive = False
        self.manalockDuration = 15 # idk what it is
        self.items = [buffs.LeblancUlt()]
        self.notes = "Ult is simplified: hits 1 \
                      target and deals .2 extra true dmg. Won't exactly model her \
                      ingame behavior, but should provide good insight into item performance on her."

    def abilityScaling(self, level, AD, AP):
        apScale = [590, 888, 5000]
        return apScale[level - 1] * AP

    def autoAbilityScaling(self, level, AD, AP):
        apScale = [150, 225, 900]
        return apScale[level - 1] * AP


    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, lambda x, y, z: self.abilityScaling(x, y, z) * .2, 'true')
        self.ultActive = True
        self.ultAutos = 3



class Malzahar(Champion):
    def __init__(self, level):
        hp= 950
        atk = 45    
        curMana = 30
        fullMana = 95
        aspd = .7
        armor = 40
        mr = 40
        super().__init__('Malzahar', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Automata', 'Visionary']
        self.castTime = .5
        self.num_targets = 5
        self.buff_duration = 999
        self.notes = "No automata yet"

    def abilityScaling(self, level, AD, AP):
        apScale = [100, 150, 1000]
        return apScale[level - 1] * AP

    def dotScaling(self, level, AD, AP):
        apScale = [16, 24, 400]
        return apScale[level - 1] * AP * 5

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')

        opponents[0].applyStatus(status.DoTEffect("Malz {}".format(self.numCasts)),
            self, time, self.buff_duration, self.dotScaling)

        for opponent in opponents[0:self.num_targets]:
            opponent.applyStatus(status.MRReduction("MR Malz"), self, time, 4, .8)


class Vladimir(Champion):
    def __init__(self, level):
        hp = 800
        atk = 45
        curMana = 20
        fullMana = 80
        aspd = .65
        armor = 15
        mr = 15
        super().__init__('Vladimir', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Sorcerer']
        self.castTime = 1
        self.manaPerAttack.addStat(5)
        self.notes = "Built-in Crimson Pact"

    def abilityScaling(self, level, AD, AP):
        apScale = [140, 210, 325]
        return apScale[level - 1] * AP * 1.8

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [90, 135, 205]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.dmgMultiplier.addStat(.1)
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, self.extraAbilityScaling, 'magical')

class Zyra(Champion):
    canFourStar = True
    def __init__(self, level):
        hp= 500
        atk = 30
        curMana = 10
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Zyra', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Sorcerer']
        self.castTime = 1
        self.canFourStar = True
        self.notes = "No Zyra Experiment bonus included; it's a raw 50% multiplier if u get full 2 second burn."


    def abilityScaling(self, level, AD, AP):
        apScale = [280, 420, 630, 780]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [95, 140, 215, 290]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 2, self.extraAbilityScaling, 'magical')


class Heimerdinger(Champion):
    # Cast times verified 12/7/24
    # Patch 14.23
    def __init__(self, level):
        hp= 800
        atk = 40
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Heimerdinger', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Visionary']
        self.castTime = .6
        missile_amount = [5, 5, 7]
        self.missiles = missile_amount[level - 1]
        self.notes = "Cast time set to increase by .09 with every missile."

    def abilityScaling(self, level, AD, AP):
        apScale = [52, 78, 275]
        return apScale[level - 1] * AP * self.missiles

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.missiles += 1
        self.castTime += .09

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
        self.default_traits = ['FormSwapper', 'PitFighter']
        self.castTime = 1
        self.num_targets = 2

    def abilityScaling(self, level, AD, AP):
        apScale = [30, 45, 70]
        adScale = [2.75, 2.75, 2.9]
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
        self.default_traits = ['Enforcer', 'Quickstriker']
        self.castTime = .5
        self.num_targets = 2
        self.notes = "Num targets refers solely to red card, Quickstriker assumes 50% hp"

    def abilityScaling(self, level, AD, AP):
        apScale = [120, 180, 275]
        return apScale[level - 1] * AP
    def goldAbilityScaling(self, level, AD, AP):
        apScale = [240, 360, 560]
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
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Cassiopeia', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Dominator']
        self.castTime = 1
        # technically her next auto is amped but it's literally the same thing

    def abilityScaling(self, level, AD, AP):
        apScale = [230, 360, 580]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [220, 330, 530]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        if self.numCasts % 3 == 0:
            self.multiTargetSpell(opponents, items,
                time, 2, self.extraAbilityScaling, 'magical')

class Tristana(Champion):
    def __init__(self, level):
        hp= 500
        atk = 42
        curMana = 20
        fullMana = 60
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Tristana', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['EmissaryTrist', 'Artillerist']
        self.castTime = .75
        self.notes = "Open 'Extra options' to increase her AD from passivev"

    def abilityScaling(self, level, AD, AP):
        adScale = [5.25, 5.25, 5.25]
        apScale = [50, 75, 115]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'physical', 1)

class Corki(Champion):
    def __init__(self, level):
        hp= 850
        atk = 70
        curMana = 0
        fullMana = 60
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Corki', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Artillerist']
        self.castTime = 4
        self.notes = "Currently Artillerist isn't working properly on Corki. No armor shred"
        self.num_reg_missiles = [18, 18, 30]
        self.num_big_missiles = [3, 3, 5]

    def abilityScaling(self, level, AD, AP):
        adScale = [.35, .35, .35]
        apScale = [6, 9, 36]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.num_reg_missiles[self.level - 1]

    def bigAbilityScaling(self, level, AD, AP):
        adScale = [.35, .35, .35]
        apScale = [6, 9, 36]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.num_big_missiles[self.level - 1] * 7

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'physical', 4)
        self.multiTargetSpell(opponents, items,
                time, 1, self.bigAbilityScaling, 'physical')



class Draven(Champion):
    def __init__(self, level):
        hp= 500
        atk = 55
        curMana = 30
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Draven', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Conqueror', 'PitFighter']
        self.castTime = 0
        self.axes = 0
        self.items = [buffs.DravenUlt()]
        self.notes = "1.5 second return time."

    def abilityScaling(self, level, AD, AP):
        adScale = [1.4, 1.4, 1.5]
        apScale = [10, 15, 25]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        # he can only hold 2 axes, but this doesnt rly matter
        if self.axes < 2:
            self.axes += 1     

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
        self.default_traits = ['Enforcer', 'Sniper']
        self.castTime = 1.2

    def abilityScaling(self, level, AD, AP):
        adScale = [1.25, 1.25, 1.4]
        apScale = [10, 15, 25]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                    time, 6, self.abilityScaling, 'physical', 2)

class Ezreal(Champion):
    def __init__(self, level):
        hp= 700
        atk = 60
        curMana = 0
        fullMana = 60
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Ezreal', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Rebel', 'Artillerist']
        self.castTime = 1.5
        self.num_targets = 2

    def abilityScaling(self, level, AD, AP):
        adScale = [1.35, 1.35, 1.35]
        apScale = [20, 30, 50]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        return .7 * self.abilityScaling(level, AD, AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'physical', 1)
        self.multiTargetSpell(opponents, items,
                time, 1, self.secondaryAbilityScaling, 'physical', 1)

class Renata(Champion):
    def __init__(self, level):
        hp= 600
        atk = 35    
        curMana = 20
        fullMana = 80   
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Renata', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Visionary']
        self.num_targets = 2
        self.castTime = 1

    def abilityScaling(self, level, AD, AP):
        apScale = [310, 465, 700]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [130, 195, 290]
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
        self.default_traits = ['Automata', 'Sniper']
        self.castTime = 0
        self.items = [buffs.KogUlt()]

    def abilityScaling(self, level, AD, AP):
        apScale = [48, 72, 120]
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
        self.default_traits = ['Visionary']
        self.castTime = 1
        self.notes = "Damage is instant here; sims on morg will be \
                      misleading since her targets will die before \
                      she gets full DoT value anyways."

    def abilityScaling(self, level, AD, AP):
        apScale = [530, 800, 1500]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')

class Elise(Champion):
    def __init__(self, level):
        hp= 750
        atk = 45
        curMana = 20
        fullMana = 80
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Elise', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['FormSwapper']
        self.castTime = 1.75
        self.num_spiderlings = 4
        self.num_targets = 2

    def abilityScaling(self, level, AD, AP):
        apScale = [250, 375, 1200]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [90, 135, 400]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        for n in range(self.num_spiderlings):
            self.multiTargetSpell(opponents, items,
                    time, 1, self.abilityScaling, 'magical')
            if self.num_targets > 1:
                self.multiTargetSpell(opponents, items,
                    time, 1, self.extraAbilityScaling, 'magical')

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
        self.default_traits = ['Dominator']
        self.num_attacks = 5
        self.num_monstrosities = [4, 4, 8]
        self.castTime = 1.3
        self.notes = "Damage is instant here"

    def abilityScaling(self, level, AD, AP):
        apScale = [140, 200, 1000]
        return apScale[level - 1] * AP

    def monsterAbilityScaling(self, level, AD, AP):
        apScale = [38, 58, 100]
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
        atk = 30
        curMana = 40
        fullMana = 120
        aspd = .75
        armor = 15
        mr = 15
        super().__init__('Powder', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Family', 'Visionary']
        self.castTime = 2
        self.num_targets = 4
        self.damage_falloff = [.75, .75, .75]
        self.notes = "1 target at epicenter, 1 target 2 hexes away, the rest 1 hex away"

    def abilityScaling(self, level, AD, AP):
        apScale = [420, 550, 735]
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
        
class Twitch(Champion):
    def __init__(self, level):
        hp= 800
        atk = 70
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Twitch', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['ExperimentTwitch', 'Sniper']

        # ultAmped: for dragon
        self.ultAutos = 0
        self.aspd_bonus = 75
        self.castTime = 0
        self.ultActive = False
        self.manalockDuration = 15 # idk what it is
        self.items = [buffs.TwitchUlt()]
        self.notes = ""
        self.num_targets = 2

    def abilityScaling(self, level, AD, AP):
        adScale = [1.4, 1.4, 3]
        apScale = [18, 25, 120]
        return adScale[level - 1] * AD + apScale[level-1] * AP

    def performAbility(self, opponents, items, time):
        self.ultActive = True
        self.aspd.addStat(self.aspd_bonus)
        self.ultAutos = 8


class Zeri(Champion):
    def __init__(self, level):
        hp= 600
        atk = 51
        curMana = 0
        fullMana = -1
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Zeri', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Sniper']
        self.castTime = 0
        self.items = [buffs.ZeriUlt()]
        self.notes = "we aint coding in firelight"
        self.manaGainMultiplier = Stat(0, 0, 0)

    def abilityScaling(self, level, AD, AP):
        adScale = [2, 2, 2]
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
        self.default_traits = ['Dominator']
        self.castTime = .5

    def abilityScaling(self, level, AD, AP):
        apScale = [180, 270, 480]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [80, 120, 180]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 3, self.extraAbilityScaling, 'magical')

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

