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

class Repulsor(Buff):
    levels = [1]
    def __init__(self, level, params):
        super().__init__("Repulsor", level, params,
                         phases=["preCombat"])
        self.scaling = 40
    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
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

class MiniMees(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Mini Mees (no armor shred)", level, params,
                         phases=["preAttack"])
        self.scaling = .3 * 3
    def performAbility(self, phase, time, champion, input_=0):
        if champion.numAttacks % 2 == 0:
            dmg = self.scaling * champion.atk.stat
            champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, 'physical', time)
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
        if input_.regularAuto:
            # shouldn't proc on spells
            targets = 2
            base_dmg = self.scaling * champion.atk.stat
            for i in range(targets):
                champion.doDamage(champion.opponents[0], [], 0, base_dmg, base_dmg, 'physical', time)
            return 0

class WolfFamiliars(Buff):
    levels = [1]
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Wolf Familiars", level, params,
                         phases=["postPreCombat", "onUpdate"])
        self.wolf_ad = .65
        self.wolf_as = .9
        self.wolf_crit = .25
        self.wolf_crit_dmg = 1.4
        self.next_wolf_auto = 0
    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            self.wolf_ad = self.wolf_ad * champion.atk.stat
        elif phase == "onUpdate":
            if time > self.next_wolf_auto:
                crit_dmg = self.wolf_ad * self.wolf_crit_dmg
                champion.doDamage(champion.opponents[0], [],
                                  self.wolf_crit, crit_dmg * 2,
                                  self.wolf_ad * 2, 'physical', time)
                self.next_wolf_auto += 1 / self.wolf_as
        return 0