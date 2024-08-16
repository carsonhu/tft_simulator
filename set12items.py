# from collections import deque
import status
# from champion import Stat

offensive_craftables = ['Rabadons', 'Bloodthirster', 'HextechGunblade', 'GuinsoosRageblade',
                        'Archangels', 'HoJ', 'Guardbreaker', 'GuardbreakerNoGuard', 'InfinityEdge', 'LastWhisper',
                        'Shojin', 'Titans', 'GS', 'GSNoGiant', 'Nashors',
                        'Adaptive', 'RunaansHurricane', 'Deathblade', 'QSS', 'JeweledGauntlet', 'Red', 'Shiv',
                        'Blue', 'Morellos', 'FaerieQueensCrown']

artifacts = ['InfinityForce', 'Fishbones', 'RFC', 'Mittens', 'GamblersBlade',
             'WitsEndStage2', 'WitsEndStage3', 'WitsEndStage4',
             'WitsEndStage5', 'WitsEndStage6', 'LichBaneStage2',
             'LichBaneStage3', 'LichBaneStage4', 'LichBaneStage5',
             'LichBaneStage6'
             ]

radiants = ['RadiantGuardbreaker', 'RadiantShiv', 'RadiantBlue',
            'RadiantArchangels', 'RadiantRunaansHurricane', 'RadiantGuinsoosRageblade',
            'RadiantLastWhisper', 'RadiantGS', 'RadiantRabadons', 'RadiantJeweledGauntlet',
            'RadiantNashors', 'RadiantShojin', 'RadiantInfinityEdge',
            'RadiantDeathblade', 'RadiantAdaptive', 'RadiantTitans',
            'RadiantHoJ', 'RadiantRed', 'RadiantMorellos']

no_item = ['NoItem']


class Item(object):
    def __init__(self, name, hp=0, ad=0, ap=0, 
                 aspd=0, armor=0, mr=0, crit=0,
                 dodge=0, mana=0, has_radiant=False, item_type='Craftable', phases=None):
        self.name = name
        self.hp = hp
        self.ad = ad
        self.ap = ap
        self.aspd = aspd
        self.armor = armor
        self.mr = mr
        self.crit = crit
        self.dodge = dodge
        self.mana = mana
        self.has_radiant = has_radiant
        self.phases = phases


    def performAbility(self, phases, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method for {}".format(self.name))       

    def ability(self, phase, time, champion, input_=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

class NoItem(Item):
    def __init__(self):
        super().__init__("NoItem", phases=None)

class Rabadons(Item):
    def __init__(self):
        super().__init__("Rabadon's Deathcap", ap=50, has_radiant=True, phases="preCombat")
    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        champion.dmgMultiplier.add += .20
        return 0

class Bloodthirster(Item):
    def __init__(self):
        super().__init__("Bloodthirster", ad=20, ap=20, phases=None)

class HextechGunblade(Item):
    def __init__(self):
        super().__init__("Gunblade", ad=15, ap=15, phases=None)

class GuinsoosRageblade(Item):
    def __init__(self):
        super().__init__("Guinsoo's Rageblade", aspd=15, ap=10, has_radiant=True, phases=["postAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.aspd.stat <= 5:
            champion.aspd.add += 5
        return 0

class Archangels(Item):
    def __init__(self):
        super().__init__("Archangels", mana=15, ap=20, has_radiant=True, phases=["onUpdate"])
        self.nextAP = 5

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextAP:
            champion.ap.add += 30
            self.nextAP += 5
        return 0

class Warmogs(Item):
    def __init__(self):
        super().__init__("Warmogs", hp=1000, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class HoJ(Item):
    def __init__(self):
        super().__init__("Hand of Justice", mana=10, crit=20, ad=30, ap=30, has_radiant=True, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class Guardbreaker(Item):
    def __init__(self):
        super().__init__("Guardbreaker", crit=20, ap=10, aspd=20, has_radiant=True, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += .25
        return 0

class GuardbreakerNoGuard(Item):
    def __init__(self):
        super().__init__("Guardbreaker (no shield)", crit=20, ap=10, aspd=20, has_radiant=True, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class InfinityEdge(Item):
    def __init__(self):
        super().__init__("Infinity Edge", ad=35, crit=35, has_radiant=True, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0

class LastWhisper(Item):
    def __init__(self):
        super().__init__("Last Whisper", aspd=25, crit=20, ad=15, has_radiant=True, phases=["preAttack"])

    def performAbility(self, phase, time, champion, opponents):
        # NOTE: LW usually applies AFTER attack but we want to calculate w/ reduced armor
        for opponent in champion.opponents:
            opponent.armor.mult = .7
        return 0

class Shojin(Item):
    def __init__(self):
        super().__init__("Spear of Shojin", ad=20, mana=15, ap=20, has_radiant=True, phases=["preCombat"])
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.add += 5
        return 0

class Titans(Item):
    def __init__(self):
        super().__init__("Titan's Resolve", aspd=10, armor=20, has_radiant=True, phases="preAttack")
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 25:
            champion.atk.addStat(2)
            champion.ap.addStat(1)
        self.stacks += 1
        if self.stacks == 25:
            champion.armor.addStat(20)
            champion.mr.addStat(20)
        return 0

class Nashors(Item):
    def __init__(self):
        super().__init__("Nashor's Tooth", aspd=10, ap=30, has_radiant=True, phases=["preAbility", "onUpdate"])
        self.active = False
        self.wearoffTime = 9999
        self.base_duration = 4
        self.aspdBoost = 40
        # we just dont treat it as a sttus

    def performAbility(self, phase, time, champion, input_=0):
        duration = champion.castTime + self.base_duration # add cast time
        if phase == "preAbility":
            if not self.active:
                # if not active, give the AS bonus
                champion.aspd.addStat(self.aspdBoost)
            self.active = True
            self.wearoffTime = time + duration
        elif phase == "onUpdate":
            if time > self.wearoffTime and self.active:
                # wearing off
                self.active = False
                champion.aspd.addStat(self.aspdBoost * -1)
        return 0

class Adaptive(Item):
    def __init__(self):
        super().__init__("Adaptive Helm", mana=15, ap=35, has_radiant=True, phases="onUpdate")
        self.nextMana = 3

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextMana:
            champion.curMana += 10
            # champion.addMana(time, 10)
            self.nextMana += 3
        return 0

class RunaansHurricane(Item):
    def __init__(self):
        super().__init__("Runaan's Hurricane", aspd=10, ad=25, has_radiant=True, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = champion.atk.stat * .55
        if len(champion.opponents) > 1:
            champion.doDamage(champion.opponents[1], [], 0, baseDmg, baseDmg,'physical', time)
        return 0

class Deathblade(Item):
    def __init__(self):
        super().__init__("Deathblade", ad=55, has_radiant=True, phases="preCombat")

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += .08
        return 0

class QSS(Item):
    def __init__(self):
        super().__init__("Quicksilver", aspd=30, crit=20, phases="onUpdate")
        self.nextAS = 2
        self.asGain = 4

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextAS and time <= 14:
            champion.aspd.addStat(self.asGain)
            self.nextAS += 2
        return 0

class JeweledGauntlet(Item):
    def __init__(self):
        super().__init__("Jeweled Gauntlet", crit=35, ap=35, has_radiant=True, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0

class Red(Item):
    def __init__(self):
        super().__init__("Red (no burn yet)", aspd=40, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += .06
        # champion.critDmg.add += 0.1
        return 0

class Morellos(Item):
    def __init__(self):
        super().__init__("Morellos (no burn yet)", aspd=10, ap=25, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class Shiv(Item):
    def __init__(self):
        super().__init__("Statikk Shiv", ap=15, aspd=20, mana=15, has_radiant=True, phases=["preAttack"])
        self.shivDmg = 30
        self.shivTargets = 4
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
            baseDmg = self.shivDmg
            # only consider dmg to primary target
            # champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
            for opponent in champion.opponents[0:self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg,'magical', time)
                opponent.applyStatus(status.MRReduction("MR"), champion, time, 5, .7)
        return 0

class GS(Item):
    # needs reworking
    def __init__(self):
        super().__init__("Giant Slayer", aspd=10, ad=30, ap=20, has_radiant=True, phases="preCombat")

    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        if len(champion.opponents) > 0:
            vsGiants = champion.opponents[0].hp.stat >= 1750
            if vsGiants:
                champion.dmgMultiplier.add += .25
        return 0

class GSNoGiant(Item):
    # needs reworking
    def __init__(self):
        super().__init__("Giant Slayer (no Giant)", aspd=10, ad=30, ap=20, has_radiant=True, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0

class Bramble(Item):
    def __init__(self):
        super().__init__("Bramble Vest", armor=55, phases=None)

class Blue(Item):
    def __init__(self):
        super().__init__("Blue Buff", mana=20, ap=20, ad=20, has_radiant=True, phases=["preCombat", "onUpdate"])
        self.has_activated = False

    def performAbility(self, phase, time, champion, input_=0):
        # blue buff is the only multiplier so we just to flat -10
        if phase == "preCombat":
            champion.fullMana.add = -10
            champion.curMana = min(champion.curMana, champion.fullMana.stat)

        if phase == "onUpdate":
            if time > champion.first_takedown and not self.has_activated:
                champion.dmgMultiplier.add += .08 # we actually want this only after 5s or so
                self.has_activated = True
        return 0

### FAERIE CROWN

class FaerieQueensCrown(Item):
    def __init__(self):
        super().__init__("FaerieQueen's Crown", ad=30, ap=30, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

### ARTIFACTS

class InfinityForce(Item):
    def __init__(self):
        super().__init__("Infinity Force", ad=25, ap=25, aspd=25, mana=25, item_type='Artifact', phases=None)

class Fishbones(Item):
    def __init__(self):
        super().__init__("Fishbones", aspd=35, ad=35, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0

class RFC(Item):
    def __init__(self):
        super().__init__("Rapid Firecannon", aspd=75, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0

class Mittens(Item):
    def __init__(self):
        super().__init__("Mittens", aspd=60, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0

class GamblersBlade(Item):
    def __init__(self):
        super().__init__("Gambler's Blade (30g)", aspd=70, ap=10, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0

class LichBaneStage2(Item):
    def __init__(self):
        super().__init__("Lich Bane (Stage 2)", ap=30, mana=15, phases=["preAbility", "preAttack"])
        self.enhancedAuto = False


    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                champion.doDamage(champion.opponents[0], [], 0, 200,
                                  200, 'magical', time)
        return 0    

class LichBaneStage3(Item):
    def __init__(self):
        super().__init__("Lich Bane (Stage 3)", ap=30, mana=15, phases=["preAbility", "preAttack"])
        self.enhancedAuto = False


    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                champion.doDamage(champion.opponents[0], [], 0, 270,
                                  270, 'magical', time)
        return 0    

class LichBaneStage4(Item):
    def __init__(self):
        super().__init__("Lich Bane (Stage 4)", ap=30, mana=15, phases=["preAbility", "preAttack"])
        self.enhancedAuto = False


    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                champion.doDamage(champion.opponents[0], [], 0, 340,
                                  340, 'magical', time)
        return 0    

class LichBaneStage5(Item):
    def __init__(self):
        super().__init__("Lich Bane (Stage 5)", ap=30, mana=15, phases=["preAbility", "preAttack"])
        self.enhancedAuto = False


    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                champion.doDamage(champion.opponents[0], [], 0, 410,
                                  410, 'magical', time)
        return 0    

class LichBaneStage6(Item):
    def __init__(self):
        super().__init__("Lich Bane (Stage 6)", ap=30, mana=15, phases=["preAbility", "preAttack"])
        self.enhancedAuto = False


    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                champion.doDamage(champion.opponents[0], [], 0, 480,
                                  480, 'magical', time)
        return 0    

class WitsEndStage2(Item):
    def __init__(self):
        super().__init__("Wit's End (Stage 2)", aspd=30, mr=30, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = 42
        champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
        return 0        

class WitsEndStage3(Item):
    def __init__(self):
        super().__init__("Wit's End (Stage 3)", aspd=30, mr=30, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = 60
        champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
        return 0    

class WitsEndStage4(Item):
    def __init__(self):
        super().__init__("Wit's End (Stage 4)", aspd=30, mr=30, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = 75
        champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
        return 0            

class WitsEndStage5(Item):
    def __init__(self):
        super().__init__("Wit's End (Stage 5)", aspd=30, mr=30, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = 90
        champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
        return 0            

class WitsEndStage6(Item):
    def __init__(self):
        super().__init__("Wit's End (Stage 6+)", aspd=30, mr=30, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = 100
        champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
        return 0            


### RADIANTS
class RadiantGuardbreaker(Item):
    def __init__(self):
        super().__init__("Radiant Guardbreaker", crit=20, ap=30, aspd=40, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += .5
        return 0

class RadiantShiv(Item):
    def __init__(self):
        super().__init__("Radiant Shiv", ap=50, aspd=20, mana=15, phases=["preAttack"])
        self.shivDmg = 80
        self.shivTargets = 8
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
            baseDmg = self.shivDmg
            # only consider dmg to primary target
            # champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
            for opponent in champion.opponents[0:self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg,'magical', time)
                opponent.applyStatus(status.MRReduction("MR"), champion, time, 5, .7)
        return 0

class RadiantBlue(Item):
    def __init__(self):
        super().__init__("Radiant Blue", mana=60, ap=60, ad=60, phases=["preCombat", "onUpdate"])
        self.has_activated = False
        

    def performAbility(self, phase, time, champion, input_=0):
        # blue buff is the only multiplier so we just to flat -10
        if phase == "preCombat":
            champion.fullMana.add = -10

        if phase == "onUpdate":
            if time > champion.first_takedown and not self.has_activated:
                champion.dmgMultiplier.add += .2 # we actually want this only after 5s or so
                self.has_activated = True
        return 0

class RadiantArchangels(Item):
    def __init__(self):
        super().__init__("Radiant Archangels", mana=15, ap=50, phases=["onUpdate"])
        self.nextAP = 4

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextAP:
            champion.ap.add += 40
            self.nextAP += 4
        return 0

class RadiantRunaansHurricane(Item):
    def __init__(self):
        super().__init__("Radiant Runaan's", aspd=20, ad=35, phases="preAttack")

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = champion.atk.stat * 1.1
        if len(champion.opponents) > 1:
            champion.doDamage(champion.opponents[1], [], 0, baseDmg, baseDmg,'physical', time)
        return 0

class RadiantGuinsoosRageblade(Item):
    def __init__(self):
        super().__init__("Radiant Rageblade", aspd=20, ap=10, phases=["postAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.aspd.stat <= 5:
            champion.aspd.addStat(10)
        return 0

class RadiantHoJ(Item):
    def __init__(self):
        super().__init__("Radiant HoJ", mana=10, crit=40, ad=60, ap=60, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class RadiantLastWhisper(Item):
    def __init__(self):
        super().__init__("Radiant LW", aspd=25, crit=55, ad=45, phases=["preAttack"])

    def performAbility(self, phase, time, champion, opponents):
        # NOTE: LW usually applies AFTER attack but we want to calculate w/ reduced armor
        for opponent in champion.opponents:
            opponent.armor.mult = .7
        return 0

class RadiantGS(Item):
    # needs reworking
    def __init__(self):
        super().__init__("Radiant GS", aspd=10, ad=50, ap=40, phases="preCombat")

    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        vsGiants = champion.opponents[0].hp.stat >= 1750
        if vsGiants:
            champion.dmgMultiplier.add += .6
        return 0

class RadiantRabadons(Item):
    def __init__(self):
        super().__init__("Radiant Rab", ap=70, phases="preCombat")
    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        champion.dmgMultiplier.add += .5
        return 0

class RadiantJeweledGauntlet(Item):
    def __init__(self):
        super().__init__("Radiant JG", crit=75, ap=65, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0

class RadiantNashors(Item):
    def __init__(self):
        super().__init__("Radiant Nashor's", aspd=20, ap=55, phases=["preAbility", "onUpdate"])
        self.active = False
        self.wearoffTime = 9999
        self.duration = 8
        self.aspdBoost = 80
        # we just dont treat it as a sttus

    def performAbility(self, phase, time, champion, input_=0):
        self.duration = champion.castTime + self.duration # add cast time
        if phase == "preAbility":
            if not self.active:
                # if not active, give the AS bonus
                champion.aspd.addStat(self.aspdBoost)
            self.active = True
            self.wearoffTime = time + self.duration
        elif phase == "onUpdate":
            if time > self.wearoffTime and self.active:
                # wearing off
                self.active = False
                champion.aspd.addStat(self.aspdBoost * -1)
        return 0

class RadiantShojin(Item):
    def __init__(self):
        super().__init__("Radiant Spear of Shojin", ad=50, mana=20, ap=50, phases=["preCombat"])
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.add += 10
        return 0

class RadiantInfinityEdge(Item):
    def __init__(self):
        super().__init__("Radiant InfinityEdge", ad=65, crit=75, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0

class RadiantDeathblade(Item):
    def __init__(self):
        super().__init__("Radiant DB", ad=105, phases="preCombat")

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += .12
        return 0

class RadiantRed(Item):
    def __init__(self):
        super().__init__("Radiant Red (no burn yet)", aspd=60, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += .1
        # champion.critDmg.add += 0.1
        return 0

class RadiantMorellos(Item):
    def __init__(self):
        super().__init__("RadiantMorellos (no burn yet)", aspd=25, ap=50, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0

class RadiantAdaptive(Item):
    def __init__(self):
        super().__init__("Radiant Adaptive", mana=15, ap=80, phases="onUpdate")
        self.nextMana = 3

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextMana:
            champion.curMana += 10
            # champion.addMana(time, 20)
            self.nextMana += 3
        return 0

class RadiantTitans(Item):
    def __init__(self):
        super().__init__("Radiant Titans", aspd=30, armor=35, phases="preAttack")
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 25:
            champion.atk.addStat(3)
            champion.ap.addStat(2)
        self.stacks += 1
        if self.stacks == 25:
            champion.armor.addStat(50)
            champion.mr.addStat(50)
        return 0