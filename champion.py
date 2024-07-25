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

    def addStat(self, add):
        # if u get 6 AD, mult is +6
        self.mult += add/100

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

    @property
    def stat(self):
        return self.mult * (self.base + self.add) / 100



class Attack(object):
    # stores details on an attack
    def __init__(self, opponents, scaling=lambda level, AD, AP=0: AD, canCrit=True,
                 canOnHit=True, multiplier=Stat(0, 1, 0),
                 attackType='physical', numTargets=1):
        self.opponents = opponents
        self.scaling = scaling
        self.canCrit = canCrit
        self.canOnHit = canOnHit
        self.multiplier = multiplier
        self.attackType = attackType
        self.numTargets = numTargets

class Champion(object):
    def __init__(self, name, hp, atk, curMana, fullMana, aspd, armor, mr, level):
        self.name = name
        levels = [1, 1.5, 1.5**2, 1.5**3]
        hp_levels = [1, 1.8, 1.8**2, 1.8**3]
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
        self.level = level
        self.dmgMultiplier = Stat(1, 1, 0)
        self.crit = Stat(.25, 1, 0)
        self.critDmg = Stat(1.4, 1, 0)

        # currently unused
        self.armorPierce = Stat(0, 1, 0)

        self.canCrit = True
        self.canSpellCrit = False
        self.manalockTime = -1  # time until unmanalocked
        self.manalockDuration = 1  # how long manalock lasts
        self.castTime = 0
        self.items = []
        self.statuses = {}  # current statuses
        self.nextAttackTime = 0
        self.opponents = []
        self.dmgVector = []
        self.alive = True
        # self.ie = False # calculations for IE

        self.first_takedown = 5 # time of first takedown

        self.numAttacks = 0
        self.numCasts = 0

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
    def addStats(self,item):
        self.hp.addStat(item.hp)
        self.atk.addStat(item.ad) # now we have multipicative AD only
        self.ap.addStat(item.ap)
        self.aspd.addStat(item.aspd)
        self.curMana = min(self.curMana + item.mana, self.fullMana.stat)
        self.armor.addStat(item.armor)
        self.mr.addStat(item.mr)
        self.crit.addStat(item.crit / 100)

    def canCast(self, time):
        # check whether we can currently cast
        return self.curMana >= self.fullMana.stat and self.fullMana.stat > -1 \
            and self.manalockTime <= time

    def canAttack(self, time):
        return time >= self.nextAttackTime

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

        # some wiggle room for managen since you get mana while it's in air
        if self.manalockTime <= time + 0.1 and generateMana == True:
            self.curMana += self.manaPerAttack.stat
        for item in items:
            item.ability("postAttack", time, self)
    
    def performAbility(self, opponents, items, time):
        # abstract method
        return 0

    def update(self, opponents, items, time):
        self.opponents = opponents
        # Update each status
        for status in self.statuses.values():
            status.update(self, time)

        # Call any items which activate on each update
        for item in items:
            item.ability("onUpdate", time, self)
        if self.canAttack(time):
            if opponents:
                self.numAttacks += 1
                self.performAttack(opponents, items, time, Stat(0, 1, 0))
                self.nextAttackTime += self.attackTime()
        if self.canCast(time):
            self.numCasts += 1
            for item in items:
                item.ability("preAbility", time, self)
            self.performAbility(opponents, items, time)
            # set manalock
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
        if attack.canOnHit:
            for item in items:
                item.ability("onAttack", time, self, attack.opponents)
        if attack.canCrit:
            for item in items:
                item.ability("onCrit", time, self, attack.opponents)
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
                 dtype, time):
        # actually doing damage: consider average of damage if crit and damage
        # if not crit
        critChance = min(1, critChance)
        preDmg = damage
        preCritDmg = damageIfCrit
        for item in items:
            preDmg = item.ability("onDoDamage", time, self, preDmg)
            preCritDmg = item.ability("onDoDamage", time, self, preCritDmg)
        dmg = self.damage(preDmg, dtype, opponent)
        critDmg = self.damage(preCritDmg, dtype, opponent)
        avgDmg = (dmg[0] * (1 - critChance) + critDmg[0] * critChance, dmg[1])
        if avgDmg:
            # record (Time, Damage Dealt, current AS, current Mana)
            self.dmgVector.append((time, avgDmg, self.aspd.stat, self.curMana))

    def multiTargetAttack(self, opponents, items, time, targets, scaling, type='physical', numAttacks=1):        
        # for item in items:
        #     item.ability("preAbility", time, self)
        newAttack = Attack(opponents, Stat(0,1,0), 'physical', 1)
        for a in range(numAttacks):
            for item in items:
                item.ability("preAttack", time, self, newAttack)            
        # Activating onhits
        # TODO: change this to just call doAttack

        # it shouldn't active 'onattack'
        # for item in items:
        #     item.ability("onAttack", time, self, opponents[0])
        baseDmg = scaling(self.level, self.atk.stat, self.ap.stat)
        baseCritDmg = baseDmg
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat
        for opponent in opponents[0:targets]:
            self.doDamage(opponent, items, self.crit.stat, baseCritDmg, baseDmg, type, time)
        for a in range(numAttacks):
            for item in items:
                item.ability("postAttack", time, self)
                
    def activateOnHits(self, opponents, items, time, onhits=True):
        newAttack = Attack(opponents=opponents,
                   canCrit=True,
                   canOnHit=True,
                   attackType='physical',
                   numTargets=1)
        for item in items:
            # here, the new attack is not used
            item.ability("preAttack", time, self, newAttack)
        if onhits:
            for item in items:
                item.ability("onAttack", time, self, opponents[0])
        for item in items: # shiv, guinsoos
            item.ability("postAttack", time, self, opponents[0])


    def onHitSpell(self, opponents, items, time, targets, scaling, type='magical'):
        # So I can actually calculate archangels on yasuo
        tempMana = self.fullMana
        self.fullMana = Stat(-1, 1, 0)
        self.multiTargetSpell(opponents, items, time, targets, scaling, type)
        self.fullMana = tempMana

    def multiTargetSpell(self, opponents, items, time, targets, scaling, type='magical', numAttacks=0):
        baseDmg = scaling(self.level, self.atk.stat, self.ap.stat)
        baseCritDmg = baseDmg
        for attacks in range(numAttacks):
            # activate onhits, currently unused
            for item in items:
                item.ability("onAttack", time, self, opponents[0])
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat
        for opponent in opponents[0:targets]:
            self.doDamage(opponent, items, self.crit.stat, baseCritDmg, baseDmg, type, time)    

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
        