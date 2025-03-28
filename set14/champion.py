import random
import status

class Stat(object):

    """Object for each stat, (AD, HP, Armor, etc.)
    
    Attributes:
        add (double): Additive modifier
        base (double): Base modifier
        mult (double): Multiplier
    """
    
    def __init__(self, base, multModifier, addModifier):
        self.base = base
        self.mult = multModifier
        self.add = addModifier

    @property
    def stat(self):
        # ad: (base + add)* mult
        # i.e 15% AS is base AS * .15
        return self.mult * (self.base + self.add)

    def addStat(self, add):
        self.add += add

class AD(Stat):
    # AD has different behavior for adding stat
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)
        self.addMultiplier = 1 # used for Attack Expert

    def addStat(self, add):
        # if u get 6 AD, mult is +6
        self.mult += add/100

    @property
    def stat(self):
        return (1 + (self.mult - 1) * self.addMultiplier) * (self.base + self.add)

class Aspd(Stat):
    # AS needs a slightly different calc and a cap
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)
        self.as_cap = 5

    @property
    def stat(self):
        return min(self.mult * self.base * (1 + self.add/100), self.as_cap)

class AP(Stat):
    # AP needs a slightly different calcualtion
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)
        # temporary
        self.base = 100
        self.addMultiplier = 1 # only for ahri

    @property
    def stat(self):
        return self.mult * (self.base + self.add * self.addMultiplier) / 100



class Attack(object):
    # stores details on an attack
    def __init__(self, opponents=None, scaling=lambda level, AD, AP=0: AD, canCrit=True,
                 canOnHit=True, multiplier=Stat(0, 1, 0),
                 attackType='physical', numTargets=1, regularAuto=True):
        self.opponents = opponents
        self.scaling = scaling
        self.canCrit = canCrit
        self.canOnHit = canOnHit
        self.multiplier = multiplier
        self.attackType = attackType
        self.numTargets = numTargets
        self.regularAuto = regularAuto

class Champion(object):
    canFourStar = False
    def __init__(self, name, hp, atk, curMana, fullMana, aspd, armor, mr, level):
        self.name = name
        levels = [1, 1.5, 1.5**2, 1.5**3, 1.5**4]
        hp_levels = [1, 1.8, 1.8**2, 1.8**3, 1.8**4]
        self.hp = Stat(hp * hp_levels[level - 1], 1, 0)
        self.atk = AD(atk * levels[level - 1], 1, 0)
        self.curMana = curMana
        self.fullMana = Stat(fullMana, 1, 0)
        self.startingMana = 0
        self.aspd = Aspd(aspd, 1, 0)
        self.ap = AP(0, 1, 0)
        self.armor = Stat(armor, 1, 0)
        self.mr = Stat(mr, 1, 0)
        self.manaPerAttack = Stat(10, 1, 0)
        self.manaGainMultiplier = Stat(1, 1, 0)
        self.level = level
        self.dmgMultiplier = Stat(1, 1, 0)
        self.crit = Stat(.25, 1, 0)
        self.critDmg = Stat(1.4, 1, 0)

        # currently unused
        self.armorPierce = Stat(0, 1, 0)

        self.canCrit = True
        self.canSpellCrit = False
        self.manalockTime = -1  # time until unmanalocked
        self.manalockDuration = 0  # how long manalock lasts
        self.castTime = 0
        self.attackWindupLockout = -1  # attack windup: can only cast after attack windup is finished
        self.items = []
        self.statuses = {}  # current statuses
        self.nextAttackTime = 0
        self.opponents = []
        self.dmgVector = []
        self.alive = True

        # notes for user
        self.notes = ""

        self.first_takedown = 5  # time of first takedown
        self.num_traits = 0

        # Divinicorp buffs
        self.divines = {"Morgana": False,
                        "Senna": False,
                        "Vex": False,
                        "Renekton": False}

        self.categoryFive = False
        
        self.num_targets = 0
        self.num_extra_targets = 0

        self.numAttacks = 0
        self.numCasts = 0

    def hashFunction(self):
        # Hash to cache champion data
        items_tuple = tuple(item.hashFunction() for item in self.items)
        stat_tuple = (self.name,
                     self.hp.stat,
                     self.atk.stat,
                     self.aspd.stat,
                     self.ap.stat,
                     self.armor.stat,
                     self.mr.stat,
                     self.manaPerAttack.stat,
                     self.manaGainMultiplier.stat,
                     self.level,
                     self.dmgMultiplier.stat,
                     self.crit.stat,
                     self.critDmg.stat,
                     self.canCrit,
                     self.canSpellCrit,
                     self.castTime,
                     self.first_takedown,
                     self.num_traits,
                     self.categoryFive,
                     self.num_targets,
                     self.num_extra_targets)
        divine_tuple = tuple(value for value in list(self.divines.values()))
        return (items_tuple + stat_tuple + divine_tuple)
        
    def __hash__(self):
        # used for caching
        return hash(self.hashFunction())

    def applyStatus(self, status, champion, time, duration, params=0):
        """ Apply status to self.
        
        Args:
            status (Status): Status to apply
            champion (Champion): Opponent who applied the status
            time (int): time of application
            duration (int): How long to apply for
            params (??): any extra params
        """
        if status.name not in self.statuses:
            self.statuses[status.name] = status
            self.statuses[status.name].application(self, champion, time, duration, params)
        else:
            if not self.statuses[status.name].active:
                self.statuses[status.name].application(self, champion, time, duration, params)
            else:
                self.statuses[status.name].reapplication(self, champion,  time, duration, params)

    # get basic stats from items
    def addStats(self,item) -> None:
        self.hp.addStat(item.hp)
        self.atk.addStat(item.ad) # now we have multipicative AD only
        self.ap.addStat(item.ap)
        self.aspd.addStat(item.aspd)
        self.curMana = min(self.curMana + item.mana, self.fullMana.stat)
        self.armor.addStat(item.armor)
        self.mr.addStat(item.mr)
        self.crit.addStat(item.crit / 100)

    def canCast(self, time):
        # 4 conditions:
        # Current mana >= full mana
        # champ can cast
        # champ not manalocked
        # champ not in auto animation
        return self.curMana >= self.fullMana.stat and self.fullMana.stat > -1 \
            and self.manalockTime <= time and self.attackWindupLockout < time

    def canAttack(self, time):
        return time >= self.nextAttackTime

    def addMana(self, amount) -> None:
        # if time > self.manalockTime:
        #     # may need to adjust this
        self.curMana += amount * self.manaGainMultiplier.stat

    def abilityScaling(self, level):
        # Abstract method
        return 0

    def __str__(self):
        return ','.join((str(p) for p in (self.hp.stat, self.atk.stat,
                        self.aspd.stat, self.ap.stat)))

    def attackTime(self):
        return 1 / self.aspd.stat

    def performAttack(self, opponents, items, time,
                      multiplier=Stat(0, 1, 0),
                      generateMana=True):
        """Perform Attack: Activate 'before attack' and
           'after attack' effects.
        
        Args:
            opponents (list[champion]): list of opps
            items (list[Item]): list of active items
            time (float): current time
            multiplier (Stat, optional): dmg multiplier on attack
            generateMana (bool, optional): whether to gen mana
        """
        newAttack = Attack(opponents=opponents,
                           multiplier=multiplier,
                           canCrit=True,
                           canOnHit=True,
                           attackType='physical',
                           numTargets=1)
        for item in items:
            item.ability("preAttack", time, self, newAttack)
        
        self.doAttack(newAttack, items, time)

        if self.manalockTime <= time and generateMana == True:
            self.addMana(self.manaPerAttack.stat)
        for item in items:
            item.ability("postAttack", time, self)
    
    def performAbility(self, opponents, items, time):
        # abstract method
        return 0


    def startAttack(self, opponents, items, time):
        # increment attack and set next attack time
        # needs to be a separate function b/c of vayne
        self.numAttacks += 1
        self.performAttack(opponents, items, time, Stat(0, 1, 0))

        # in case it's accelerated by vayne
        self.nextAttackTime = min(self.nextAttackTime, time) + self.attackTime()
        self.attackWindupLockout = time + self.attackTime() * .3

    def update(self, opponents, items, time):
        self.opponents = opponents
        # Update each status
        for status in self.statuses.values():
            status.update(self, time)

        # Call any items which activate on each update
        for item in items:
            item.ability("onUpdate", time, self)
        if self.canAttack(time) and not self.canCast(time):
            # if they can cast it overrides the 1st auto
            if opponents:
                self.startAttack(opponents, items, time)
        if self.canCast(time):
            self.numCasts += 1
            for item in items:
                item.ability("preAbility", time, self)
            self.performAbility(opponents, items, time)
            # set manalock
            if time < -1: # this line doesn't do what it should
                # if they instant cast they shouldn't be manalocked
                self.manalockTime = 0
            else:
                # manalock duration is deprecated
                self.manalockTime = max(time + self.manalockDuration,
                                    time + self.castTime)
            self.curMana = self.curMana - self.fullMana.stat + self.startingMana
            # basically, can't attack before cast time up.
            # this logic might be slightly incorrect
            self.nextAttackTime = max(self.nextAttackTime,
                                      time + self.castTime)
            for item in items:
                item.ability("postAbility", time, self)
        
    def baseAtkDamage(self, attack, multiplier):
        # just an extra method for abilities which attack for a % of your AD,
        # like Runaans
        # Probably does result in some niche buggy interactions

        return (attack + multiplier.add) * multiplier.mult

    def doAttack(self, attack, items, time):
        # Activating onhits
        # onAttack is currently unused
        if attack.canOnHit:
            for item in items:
                item.ability("onAttack", time, self, attack.opponents)
                
        baseDmg = self.baseAtkDamage(attack.scaling(self.level, self.atk.stat,
                                     self.ap.stat), attack.multiplier)
        baseCritDmg = baseDmg
        if attack.canCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat
        for target in range(attack.numTargets):
            self.doDamage(attack.opponents[target], items, self.crit.stat,
                          baseCritDmg, baseDmg, attack.attackType, time)

    def critDamage(self):
        return self.critDmg.stat + max(0, 0 + (self.crit.stat - 1) / 2)

    def doDamage(self, opponent, items, critChance, damageIfCrit, damage,
                 dtype, time, is_spell=False):
        """ Actually doing damage: consider
            average of damage if crit and damage
        
        Args:
            opponent (Champion): opp to do dmg to
            items (List[item]): List of active items/buffs
            critChance (float)
            damageIfCrit (float)
            damage (float): dmg if not crit
            dtype (str): "physical", "magical", "true"
            time (int)
            is_spell (bool, optional): is it spell damage?
        """
        # 
        # if not crit
        critChance = min(1, critChance)
        preDmg = damage
        preCritDmg = damageIfCrit
        
        avgDmg = (preDmg * (1 - critChance) + preCritDmg * critChance)
        # if anything needs to modify the damage dealt
        for item in items:
            avgDmg = item.ability("onDealDamage", time, self, avgDmg)
        # if only spell dmg needs to be modified (Arcana Xerath)    
        if is_spell:
            for item in items:
                avgDmg = item.ability("onDealSpellDamage", time, self, avgDmg)

        avgDmg = self.damage(avgDmg, dtype, opponent)
        
        for item in items:
            # if you need to track how much dmg was actually dealt
            item.ability("PostOnDealDamage", time, self, avgDmg)

        if avgDmg:
            # record (Time, Damage Dealt, current AS, current Mana)
            self.dmgVector.append((time, avgDmg, self.aspd.stat, self.curMana))

    def multiTargetSpell(self, opponents, items, time, targets, scaling, type='magical', numAttacks=0):
        """Cast a damage-dealing spell
        
        Args:
            opponents (List[Champion]): List of opponents
            items (List[item]): active items & buffs
            time (float): current float
            targets (int): # targets
            scaling (func): damage func(level, AD, AP)
            type (str, optional): physical, magical, true
            numAttacks (int, optional): # of attacks to apply for guinsoo/runaans
        """
        baseDmg = scaling(self.level, self.atk.stat, self.ap.stat)
        baseCritDmg = baseDmg
        newAttack = Attack(opponents, Stat(0,1,0), 'physical', 1, regularAuto=False)
        for attacks in range(numAttacks):
            # activate onhits, currently unused
            for item in items:
                item.ability("preAttack", time, self, newAttack)
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat

        for opponent in opponents[0:targets]:
            self.doDamage(opponent, items, self.crit.stat, baseCritDmg, baseDmg, type, time, is_spell=True)    

    def damage(self, dmg, dtype, defender):
        """deal dmg, dmg is premitigated
        
        Args:
            dmg (FLOAT): for basic attacks, it's just atk. sometimes 
            dtype (STRING): physical/magical/true
            defender (Champion): recipient
        """
        if dtype == "physical":
            defense = defender.armor.stat * (1 - self.armorPierce.stat)
        elif dtype == "magical":
            defense = defender.mr.stat
        elif dtype == "true":
            defense = 0

        # also add in 'damageTaken' modifier
        dModifier = 100 / (100 + defense)
        return (dmg * dModifier, dtype)
        