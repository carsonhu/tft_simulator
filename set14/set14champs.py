from champion import Champion, Stat, Attack
from collections import deque
import math
import numpy as np
import heapq
import random
import set14buffs as buffs
import status

champ_list = ['Kogmaw', 'Kindred', 'Nidalee', 'Seraphine', 'Zyra',
              'Leblanc', 'Senna', 'TwistedFate', 'Vayne', 'Veigar',
              'Draven', 'Elise', 'Jinx', 'Varus', 'Yuumi',
              'Aphelios', 'Annie', 'Brand', 'MissFortune', 'Xayah', 'Zeri', 'Ziggs']


class Kogmaw(Champion):
    def __init__(self, level):
        hp = 500
        atk = 50
        curMana = 15
        fullMana = 75
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Kogmaw', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Boombot', 'Rapidfire']
        self.buff_duration = 5
        self.manalockDuration = 5
        self.aspd_bonus = [50, 50, 50]
        self.items = [buffs.KogUlt()]
        self.castTime = 0

        self.ultActive = False
        self.notes = "Boombot not yet coded, need to figure out interaction with runaans/shiv"

    def abilityScaling(self, level, AD, AP):
        adScale = [.4, .4, .4]
        apScale = [9, 14, 20]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.applyStatus(status.ASModifier("Kogmaw"),
            self, time, self.buff_duration, self.aspd_bonus[self.level-1])
        self.applyStatus(status.UltActivator("Kog ult"),
            self, time, self.buff_duration)


class Kindred(Champion):
    def __init__(self, level):
        hp= 500
        atk = 45
        curMana = 0
        fullMana = 50
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Kindred', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Rapidfire', 'Marksman']
        self.castTime = 1.5

    def abilityScaling(self, level, AD, AP):
        adScale = [5.2, 5.2, 5.2]
        apScale = [20, 30, 45]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', 1)


class Nidalee(Champion):
    def __init__(self, level):
        hp = 650
        atk = 40
        curMana = 20
        fullMana = 60
        aspd = .75
        armor = 40
        mr = 40
        super().__init__('Nidalee', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AMP']
        self.amp_level = 0
        self.castTime = 1
        self.notes = "Melee; add scoped / rfc"
        self.ultActive = False

    def abilityScaling(self, level, AD, AP):
        apScale = [210, 315, 475]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [80, 120, 180]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')

        num_targets = 2 + self.amp_level
        self.multiTargetSpell(opponents, items,
                time, num_targets, self.extraAbilityScaling, 'magical')


class Seraphine(Champion):
    canFourStar = False
    def __init__(self, level):
        hp= 500
        atk = 35
        curMana = 0
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Seraphine', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'Techie']
        self.castTime = 1
        self.num_targets = 3
        self.canFourStar = False

    def abilityScaling(self, level, AD, AP):
        apScale = [240, 360, 550]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            self.multiTargetSpell(opponents, items, time, 1,
                                  lambda x, y, z: .65**(count) * self.abilityScaling(x, y, z), 'magical')


class Zyra(Champion):
    canFourStar = False
    def __init__(self, level):
        hp= 500
        atk = 30
        curMana = 10
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Zyra', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['StreetDemon', 'Techie']
        self.castTime = 1
        self.canFourStar = False

    def abilityScaling(self, level, AD, AP):
        apScale = [250, 375, 585]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [120, 180, 270]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, self.extraAbilityScaling, 'magical')

class Leblanc(Champion):
    # Cast times verified 12/7/24
    # Patch 14.23
    def __init__(self, level):
        hp= 550
        atk = 40
        curMana = 0
        fullMana = 50
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Leblanc', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cypher', 'Strategist']
        self.castTime = 1
        # sigil_amount = [5, 5, 7]
        self.sigils = 5
        self.notes = "Cast time set to increase by .09 with every missile."

    def abilityScaling(self, level, AD, AP):
        apScale = [65, 95, 145]
        return apScale[level - 1] * AP * self.sigils

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.sigils += 1

class TwistedFate(Champion):
    def __init__(self, level):
        hp= 600
        atk = 35
        curMana = 10
        fullMana = 70
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Twisted Fate', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.is_kingpin = False
        self.default_traits = ['Syndicate', 'Rapidfire']
        self.items = [buffs.TFUlt()]
        self.castTime = 1
        self.num_targets = 2
        self.notes = "kingpin alternates red and blue; targets is for red card"
        self.red_card = True

    def abilityScaling(self, level, AD, AP):
        apScale = [160, 240, 375]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [260, 390, 610]
        mult = 1 if self.red_card else 0.5
        return apScale[level - 1] * AP * mult

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 2, self.abilityScaling, 'magical')

        if self.is_kingpin:
            if self.red_card:
                self.multiTargetSpell(opponents, items,
                                      time, self.num_targets,
                                      self.extraAbilityScaling,
                                      'magical')
                self.red_card = False
            else:    
                self.multiTargetSpell(opponents, items,
                                      time, 1,
                                      self.extraAbilityScaling,
                                      'magical')
                self.multiTargetSpell(opponents, items,
                                      time, 1,
                                      self.extraAbilityScaling,
                                      'true')
                self.red_card = True


class Vayne(Champion):
    def __init__(self, level):
        hp= 550
        atk = 50
        curMana = 0
        fullMana = 60
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Vayne', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'Slayer']
        self.items = [buffs.VayneUlt()]
        self.ultAutos = 0
        self.manalockDuration = 15
        self.castTime = 0

    def abilityScaling(self, level, AD, AP):
        adScale = [.55, .55, .55]
        return adScale[level - 1] * AD

    def thirdAbilityScaling(self, level, AD, AP):
        apScale = [10, 15, 25]
        adScale = [1.65, 1.65, 1.65]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.ultAutos = 3
        self.aspd.addStat(50)
        self.nextAttackTime = time + .01


class Veigar(Champion):
    def __init__(self, level):
        hp= 550
        atk = 35
        curMana = 0
        fullMana = 40
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Veigar', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cyberboss', 'Techie']
        self.cyberboss_upgrade = False
        self.castTime = 1
        self.num_targets = 2
        self.true_bonus = .4 if self.level == 3 else .25

    def abilityScaling(self, level, AD, AP):
        apScale = [315, 420, 605]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [125, 170, 240]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, lambda x, y, z: self.true_bonus * self.abilityScaling(x, y, z), 'true')
        if self.cyberboss_upgrade:
            self.multiTargetSpell(opponents, items,
                    time, self.num_targets, self.extraAbilityScaling, 'magical')
            self.multiTargetSpell(opponents, items,
                    time, self.num_targets, lambda x, y, z: self.true_bonus * self.extraAbilityScaling(x, y, z), 'true')


class Draven(Champion):
    # unconfirmed: is spell 1 auto or 0
    def __init__(self, level):
        hp= 700
        atk = 52
        curMana = 30
        fullMana = 120
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Draven', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cypher', 'Rapidfire']
        self.castTime = 1
        self.num_targets = 3
        self.dmg_falloff = .8
        self.notes = "Draven will hit each target twice"


    def abilityScaling(self, level, AD, AP):
        adScale = [3.7, 3.7, 3.9]
        apScale = [30, 45, 80]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets * 2):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            num_attacks = 1 if count == 0 else 0
            self.multiTargetSpell(opponents, items, time, 1,
                                  lambda x, y, z: self.dmg_falloff**(count) * self.abilityScaling(x, y, z), 'physical', num_attacks)


class Senna(Champion):
    def __init__(self, level):
        hp= 700
        atk = 85
        curMana = 0
        fullMana = 100
        aspd = .6
        armor = 25
        mr = 25
        super().__init__('Senna', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Divinicorp', 'Slayer']
        self.castTime = 1
        self.num_targets = 2
        self.items = [buffs.SennaUlt()]
        self.notes = "Passive will hit 1 other target"

    def autoScaling(self, level, AD, AP):
        adScale = [.4, .4, .4]
        return adScale[level - 1] * AD

    def abilityScaling(self, level, AD, AP):
        adScale = [2.8, 2.8, 3]
        apScale = [20, 30, 45]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, self.num_targets,
                              self.abilityScaling,
                              'physical', 1)


class Jinx(Champion):
    def __init__(self, level):
        hp= 650
        atk = 55
        curMana = 0
        fullMana = 50
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Jinx', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['StreetDemon', 'Marksman']
        self.castTime = 2
        self.rockets = 5

    def abilityScaling(self, level, AD, AP):
        adScale = [1.4, 1.4, 1.5]
        apScale = [15, 25, 40]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.rockets

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', self.rockets // 2)
        self.rockets += 1


class Elise(Champion):
    def __init__(self, level):
        hp= 700
        atk = 40
        curMana = 0
        fullMana = 55
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Elise', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Dynamo']
        self.castTime = 1
        self.notes = "Does not include the flat MR reduction!"

    def abilityScaling(self, level, AD, AP):
        apScale = [54, 81, 125]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        # 8 lasers
        self.multiTargetSpell(opponents, items,
                              time, 4,
                              self.abilityScaling,
                              'magical', 1)
        self.multiTargetSpell(opponents, items,
                              time, 4,
                              self.abilityScaling,
                              'magical', 1)
        


class Varus(Champion):
    def __init__(self, level):
        hp= 700
        atk = 35
        curMana = 15
        fullMana = 75
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Varus', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Executioner']
        self.castTime = 1


    def abilityScaling(self, level, AD, AP):
        apScale = [200, 300, 480]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [100, 150, 240]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'magical', 1)
        self.multiTargetSpell(opponents, items,
                              time, 3,
                              self.abilityScaling,
                              'magical', 1)


class Aphelios(Champion):
    def __init__(self, level):
        hp= 800
        atk = 63
        curMana = 0
        fullMana = 60
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Aphelios', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['GoldenOx', 'Marksman']
        self.items = [buffs.ApheliosUlt()]
        self.num_targets = 4
        self.ultAutos = 0
        self.base_chakrams = 4
        self.chakrams = 0
        self.manalockDuration = 999
        self.castTime = 1

    def abilityScaling(self, level, AD, AP):
        apScale = [20, 30, 100]
        adScale = [2.2, 2.2, 5]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def chakramAbilityScaling(self, level, AD, AP):
        adScale = [.07, .07, .2]
        return adScale[level - 1] * AD * self.chakrams

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, self.num_targets,
                              self.abilityScaling,
                              'physical', 1)
        self.chakrams = self.base_chakrams + self.num_targets
        self.ultAutos = 6


class Xayah(Champion):
    # TODO: How many autos is her ult?
    def __init__(self, level):
        hp= 800
        atk = 63
        curMana = 25
        fullMana = 75
        aspd = .8
        armor = 30
        mr = 30
        super().__init__('Xayah', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'Marksman']
        self.castTime = 2
        self.num_feathers = 6
        self.notes = "Feathers are instant, will apply on same target"

    def abilityScaling(self, level, AD, AP):
        apScale = [20, 30, 200]
        adScale = [1.5, 1.5, 4]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.num_feathers

    def extraAbilityScaling(self, level, AD, AP):
        adScale = [.35, .35, 1]
        return adScale[level - 1] * AD * self.num_feathers

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', 1)
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.extraAbilityScaling,
                              'physical', 1)


class Zeri(Champion):
    def __init__(self, level):
        hp= 800
        atk = 65
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Zeri', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Rapidfire']
        self.castTime = .2
        self.items = [buffs.ZeriUlt()]
        self.queued_autos = []
        self.duration = [5, 5, 10]

    def abilityScaling(self, level, AD, AP):
        adScale = [.5, .5, 2]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        heapq.heappush(self.queued_autos,
                       (time, (self.atk.stat, self.aspd.stat,
                       time + self.duration[self.level - 1] * self.ap.stat,
                       time)))
        return 0


class MissFortune(Champion):
    def __init__(self, level):
        hp= 700
        atk = 50
        curMana = 50
        fullMana = 150
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Miss Fortune', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Syndicate', 'Dynamo']
        self.is_kingpin = False

        self.castTime = 2.2 # this is probably lower without syndicate
        self.num_targets_fixed = 4 # no need for customization
        # self.num_bullets = 8
        self.dmg_falloff = .75
        self.notes = "8 bullets in each wave, assume every bullet hits. \
                      fixed at 4 targets, each getting hit by 2 bullets."

    def abilityScaling(self, level, AD, AP):
        adScale = [.5, .5, 1.35]
        apScale = [8, 12, 100]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        num_waves = 12 if self.is_kingpin else 8
        for wave in range(num_waves):
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets_fixed,
                                  self.abilityScaling,
                                  'physical', 1)
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets_fixed,
                                  lambda x, y, z: self.dmg_falloff * self.abilityScaling(x, y, z),
                                  'physical', 1)


class Annie(Champion):
    def __init__(self, level):
        hp= 850
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Annie', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Golden Ox', 'AMP']
        self.amp_level = 0  # amp_level gets modified by AMP
        self.castTime = 1
        self.num_targets = 2
        self.notes = "# targets is for tibbers"

    def abilityScaling(self, level, AD, AP):
        apScale = [175, 265, 790]
        return apScale[level - 1] * AP

    def fireballAbilityScaling(self, level, AD, AP):
        apScale = [40, 60, 180]
        return apScale[level - 1] * AP

    def tibbersAbilityScaling(self, level, AD, AP):
        apScale = [270, 405, 1215]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        if self.numCasts % 4 == 0:
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets,
                                  self.tibbersAbilityScaling, 'magical')
        else:
            self.multiTargetSpell(opponents, items,
                                  time, 1, self.abilityScaling,
                                  'magical')
            self.multiTargetSpell(opponents, items,
                                  time, self.amp_level + 2,
                                  self.fireballAbilityScaling, 'magical')

class Brand(Champion):
    def __init__(self, level):
        hp= 800
        atk = 35
        curMana = 25
        fullMana = 75
        aspd = .7
        armor = 30
        mr = 30
        super().__init__('Brand', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['StreetDemon', 'Techie']
        self.castTime = 2
        self.num_targets = 3

    def abilityScaling(self, level, AD, AP):
        apScale = [260, 390, 1500]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [80, 120, 600]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 4, self.abilityScaling, 'magical')

class Yuumi(Champion):
    def __init__(self, level):
        hp= 650
        atk = 35
        curMana = 0
        fullMana = 30
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Yuumi', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'AMP', 'Strategist']
        self.items.append(buffs.YuumiUlt())
        self.amp_level = 0
        self.castTime = 1
        self.marked = False
        self.notes = "Every other cast will be marked"

    def abilityScaling(self, level, AD, AP):
        mult = 1.7 if self.marked else 1
        apScale = [95, 145, 220]
        return apScale[level - 1] * AP * mult

    def secondaryAbilityScaling(self, level, AD, AP):
        mult = 1.7 if self.marked else 1
        apScale = [55, 85, 125]
        return apScale[level - 1] * AP * mult

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, self.secondaryAbilityScaling, 'magical')
        self.marked = not self.marked


class Ziggs(Champion):
    def __init__(self, level):
        hp= 850
        atk = 40
        curMana = 20
        fullMana = 70
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Ziggs', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cyberboss', 'Strategist']
        self.cyberboss_upgrade = False
        self.castTime = 1
        self.num_targets = 2
        self.num_extra_targets = 5
        self.notes = "Num targets is for center, extra targets is for further away"

    def abilityScaling(self, level, AD, AP):
        apScale = [240, 360, 1500]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [100, 150, 750]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')
        if self.cyberboss_upgrade:
            self.multiTargetSpell(opponents, items,
                time, self.num_extra_targets, self.extraAbilityScaling, 'magical')


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

