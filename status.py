import math

class Status(object):
    """Holds champion status effects:
    1. name
    2. wearoff time
    3. application effect
    4. wearoff effect
    """
    def __init__(self, name):
        self.wearoff_time = -1
        self.name = name
        self.active = False
        self.opponent = None 
    def application(self, champion, opponent, time, duration, params):
        # opponent applies the status
        self.opponent = opponent
        self.active = True
        self.wearoff_time = time + duration
        self.applicationEffect(champion, time, duration, params)

    def applicationEffect(self, champion, time, duration, params):
        return 0

    def reapplication(self, champion, opponent, time, duration, params):
        self.opponent = opponent
        if self.reapplicationEffect(champion, time, duration, params):
            self.wearoff_time = time + duration

    def reapplicationEffect(self, champion, time, duration, params):
        return 0

    def wearoff(self, champion, time):
        self.wearoffEffect(champion, time)
        self.active = False
        self.opponent = None


    def wearoffEffect(self, champion, time):
        return 0

    def update(self, champion, time):
        if time > self.wearoff_time and self.active:
            self.wearoff(champion, time)

        #if status not in dict, put it in
        # applyeeffect: if inactive, application
        # else, reapplication

class DoTEffect(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("DoT {}".format(name))
        self.scaling = lambda x, y, z: 0
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        self.scaling = params
        self.next_proc = math.floor(time) + 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        self.next_proc = 999
        return True

    def update(self, champion, time):
        if time > self.next_proc:
            # do damage
            self.opponent.multiTargetSpell(self.opponent.opponents, self.opponent.items,
                time, 1, self.scaling, 'magical')
            
            self.next_proc += 1
        super().update(champion, time)

class VarusBolts(Status):
    def __init__(self, wearoff_time):
        super().__init__("Varus Bolt", wearoff_time=wearoff_time)
    def applicationEffect(self, champion, time, duration, params):
        return True
    def reapplicationEffect(self, champion, time, duration, params):
        return True
    def wearoffEffect(self, champion, time):
        return True

class UltActivator(Status):
    def __init__(self, name):
        super().__init__("Ult Active {}".format(name))
    def applicationEffect(self, champion, time, duration, params):
        champion.ultActive = True
        return True
    def reapplicationEffect(self, champion, time, duration, params):
        return True
    def wearoffEffect(self, champion, time):
        champion.ultActive = False
        return True


class SilverBolts(Status):
    def __init__(self, wearoff_time=999):
        super().__init__("Silver Bolt", wearoff_time=wearoff_time)
        self.stacks = 0
    def applicationEffect(self, champion, time, duration, params):
        self.stacks += 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.stacks += 1
        if self.stacks == 3:
            self.opponent.performAbility([champion], self.opponent.items, time)
            self.stacks = 0
        return True
    def wearoffEffect(self, champion, time):
        print("shouldnt be wearing off")
        self.stacks = 0
        return True



class ADModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("AD Modifier {}".format(name))
        self.toAdd = 0

    def applicationEffect(self, champion, time, duration, params):
        self.toAdd = params
        champion.atk.addStat(self.toAdd)
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.atk.addStat(-1 * self.toAdd)
        return True

class  AsheUlt(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("Ashe Ult {}".format(name))

    def applicationEffect(self, champion, time, duration, params):
        champion.ultsActive += 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.ultsActive -= 1
        return True

class ASMultModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, wearoff_time):
        super().__init__("AS Multiplicative Modifier", wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.mult += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.aspd.mult -= self.addition
        return True

class  DmgMultiplierModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("AS Multiplicative Modifier {}".format(name))
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.dmgMultiplier.addStat(params)
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.dmgMultiplier.addStat(self.addition*-1)
        return True


class KogASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, wearoff_time):
        super().__init__("AS Modifier", wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        champion.ultActive = True
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.ultActive = False
        champion.aspd.add  -= self.addition
        return True

class KaisaBuff(Status):
    # increase AS by %
    # idea is each buff has new name
    def __init__(self, count, wearoff_time):
        super().__init__("Kaisa Buff {}".format(count), wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.aspd.add  -= self.addition
        return True

class DecayingASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("Decaying AS Modifier {}".format(name))
        self.addition = 1
        self.duration = 0

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        self.amount_to_decrease = self.addition / (duration / (1 / 30))
        self.duration = duration
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        # champion.aspd.add  -= self.addition
        return True

    def update(self, champion, time):
        # NOTE: thsi will get fucked up with frame time
        if time <= self.wearoff_time and self.active:
            champion.aspd.add -= self.amount_to_decrease
            self.addition -= self.amount_to_decrease  
        if time > self.wearoff_time and self.addition > 0:
            champion.aspd.add -= self.addition
            self.addition = 0
        super().update(champion, time)

class ASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("AS Modifier {}".format(name))
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.aspd.add  -= self.addition
        return True

class ArmorReduction(Status):
    # reduce MR by N%
    def __init__(self, name):
        super().__init__("Armor Reduction {}".format(name))
        self.reduction = 1

    def applicationEffect(self, champion, time, duration, params):
        # if it's not a bigger shred, do nothing
        champion.armor.mult = min(champion.mr.mult, params)
        self.reduction = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        if self.reduction >= params:
            champion.armor.mult = min(champion.mr.mult, self.reduction)
            return True
        else:
            # if it's weaker, doesnt work
            return False
    def wearoffEffect(self, champion, time):
        # iterate through champ statuses
        champion.armor.mult = 1
        for status_name, status in champion.statuses.items():
            if 'Armor Reduction' in status_name and status.active:
                champion.armor.mult = min(champion.armor.mult, status.reduction)
        return True

class MRReduction(Status):
    # reduce MR by N%
    def __init__(self, name):
        super().__init__("MR Reduction {}".format(name))
        self.reduction = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.mr.mult = min(champion.mr.mult, params)
        self.reduction = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        if self.reduction >= params:
            champion.mr.mult = min(champion.mr.mult, self.reduction)
            return True
        else:
            # if it's weaker, doesnt work
            return False
    def wearoffEffect(self, champion, time):
        champion.mr.mult = 1
        for status_name, status in champion.statuses.items():
            if 'MR Reduction' in status_name and status.active and status_name != self.name:
                champion.mr.mult = min(champion.armor.mult, status.reduction)
        return True
