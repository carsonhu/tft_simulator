from set13buffs import Buff



class EagleEye(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Eagle Eye", level, params,
                         phases=["onUpdate"])
        self.scaling = 6
        self.nextBonus = 2
    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextBonus:
            champion.atk.addStat(self.scaling)
            self.nextBonus += 2
        return 0

class Bully(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Bully", level, params,
                         phases=["preCombat"])
        self.scaling = .36
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += self.scaling
        return 0

# class CosmicRhythm(Buff):
#     levels = [1]
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Cosmic Rhythm", level, params,
#                          phases=["preCombat", "onUpdate"])
#         self.baseBonus = 4
#         self.nextBonus = self.baseBonus
#     def performAbility(self, phase, time, champion, input_=0):
#         if time > self.nextBonus:
#             champion.atk.addStat(self.scaling)
#             self.nextBonus += 2
#         return 0

class AttackExpert(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Attack Expert", level, params,
                         phases=["preCombat"])
        self.scaling = .55
    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addMultiplier += self.scaling
        return 0

class MagicExpert(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Magic Expert", level, params,
                         phases=["preCombat"])
        self.scaling = .4
    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addMultiplier += self.scaling
        return 0

class AvariceIncarnate(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Avarice Incarnate (50g)", level, params,
                         phases=["preCombat"])
        self.scaling = .4
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(.4)
        return 0

class Freestyling(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Freestyling", level, params,
                         phases=["preCombat"])
        self.scaling = .045
    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling * champion.num_traits)        
        return 0

class IntoTheUnknown(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Into the Unknown", level, params,
                         phases=["preCombat"])
        self.scaling = 50
    def performAbility(self, phase, time, champion, input_=0):
        champion.atk.addStat(self.scaling)
        champion.ap.addStat(self.scaling)
        return 0

class CullTheWeak(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Cull the Weak (assume 50% hp)", level, params,
                         phases=["preCombat"])
        self.scaling = .5
    def performAbility(self, phase, time, champion, input_=0):
        champion.crit.addStat(self.scaling)
        return 0

class Hypervelocity(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Hypervelocity", level, params,
                         phases=["preCombat", "preAbility"])
        self.base_scaling = 10
        self.scaling = 15
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.addStat(self.base_scaling)
        elif phase == "preAbility":
            champion.aspd.addStat(self.scaling)
        return 0

class StrengthTraining(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("StrengthTraining", level, params,
                         phases=["preCombat", "preAttack"])
        self.base_scaling = 20
        self.scaling = 4
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.atk.addStat(self.base_scaling)
        elif phase == "preAttack":
            if champion.numAttacks % 3 == 0:
                champion.atk.addStat(self.scaling)
        return 0

class MagicTraining(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Magic Training", level, params,
                         phases=["preCombat", "preAbility"])
        self.base_scaling = 15
        self.scaling = 2
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.ap.addStat(self.base_scaling)
        elif phase == "preAbility":
            champion.ap.addStat(self.scaling * (champion.fullMana.stat / 20))
        return 0


# class OneThousandCuts(Buff):
#     levels = [1]
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("One Thousand Cuts (cap 10)", level, params,
#                          phases=["onAttack"])
#         self.base_scaling = 30
#         self.scaling = 12
#         self.stacks = 0
#         self.max_stacks = 10
#         self.current_dmg = self.base_scaling
#     def performAbility(self, phase, time, champion, input_=0):
#         champion.doDamage(champion.opponents[0], [], 0, self.current_dmg, self.current_dmg,'true', time)
#         self.current_dmg += self.scaling
#         self.stacks += 1
#         if self.stacks > self.max_stacks:
#             self.stacsk = 0
#             self.current_dmg = self.base_scaling
#         return 0

# class Knockout(Buff):
#     levels = [1]
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Knockout", level, params,
#                          phases=["preCombat", "postAbility", "preAttack"])
#         self.enhanced_active = False
#     def performAbility(self, phase, time, champion, input_=0):
#         targets = 2
#         base_dmg = self.scaling * champion.atk.stat
#         for i in range(targets):
#             champion.doDamage(champion.opponents[0], [], 0, base_dmg, base_dmg, 'physical', time)
#         return 0

class TitanicStrikes(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Titanic Strikes (2 targets)", level, params,
                         phases=["preAttack"])
        self.scaling = .40
    def performAbility(self, phase, time, champion, input_=0):
        targets = 2
        base_dmg = self.scaling * champion.atk.stat
        for i in range(targets):
            champion.doDamage(champion.opponents[0], [], 0, base_dmg, base_dmg, 'physical', time)
        return 0

# class EssenceOfNavori(Buff):
#     levels = [1]
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Essence Of Navori", level, params,
#                          phases=["preCombat", "preAbility"])
#         self.max_reductions = 3
#         self.scaling = .1
#     def performAbility(self, phase, time, champion, input_=0):
#         if phase == "preCombat":
#             champion.fullMana.mult -= .1
#         elif phase == "preAbility":
#             if self.max_reductions > 0:
#                 champion.fullMana.mult -= .1
#                 self.max_reductions -= 1
            
#         return 0