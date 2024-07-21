# from collections import deque, Counter
# from items import Item
# from champion import Stat
# import status
# class Buff(Item):
#     def __init__(self, name, level, params, phases):
#         super().__init__(name, phases = phases)
#         self.level = level
#         self.params = params

#     def performAbility(self, phase, time, champion, input=0):
#         raise NotImplementedError("Please Implement this method")       

#     def ability(self, phase, time, champion, input=0):
#         if self.phases and phase in self.phases:
#             return self.performAbility(phase, time, champion, input)
#         return input

# class NoBuff(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("NoItem", level, params, phases=None)

#     def performAbility(self, phase, time, champion, input=0):
#         return 0

# class Forgotten(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Forgotten " + str(level), level, params, phases=["preCombat"])
#         self.scaling = {2: (20, 20), 4: (40, 40), 6: (70, 70)}
#         self.stacks = min(params, 4)

#     def performAbility(self, phase, time, champion, input=0):
#         champion.atk.add+= self.scaling[self.level][0]*self.stacks*1.1
#         champion.ap.add+= self.scaling[self.level][1]*self.stacks*1.1
#         return 0

# class VayneBolts(Buff):
#     def __init__(self, level=0, params=0):
#         # vayne bolts inflicts status "Silver Bolts"
#         super().__init__("Silver Bolts", level, params, phases=["onAttack"])



#     def performAbility(self, phase, time, champion, input=0):
#         # input is opponent
#         input.applyStatus(status.SilverBolts(), champion, time, 999, "")
#         return 0

# class VarusBolts(Buff):
#     def __init__(self, level=0, params=0):
#         super().__init__("Varus Arrows", level, params, phases=["onAttack"])
#     def performAbility(self, phase, time, champion, input=0):
#         # input is opponent
#         if champion.boltsActive:
#             champion.onHitSpell(input, champion.items, time, champion.getStacks, 'magical')        
#         return 0

# class LucianUlt(Buff):
#     def __init__(self, level=0, params=0):
#             super().__init__("Lucian Ult", level, params, phases=["onUpdate"])
#     def performAbility(self, phase, time, champion, input=0):
#         # input is opponent
#         if champion.ultActive:
#             if not champion.opponents:
#                 print(champion.items)
#             if champion.attackQueue[0] < time:
#                 champion.performAttack(champion.opponents, champion.items, time, Stat(0,1,0), False)
#                 champion.onHitSpell(champion.opponents[0], champion.items, time, champion.abilityScaling, 'magical')        
#                 if champion.bulletsLeft >= 2:
#                     champion.performAttack(champion.opponents, [], time, Stat(0,1,0), False)
#                     champion.onHitSpell(champion.opponents[0], champion.items, time, champion.abilityScaling, 'magical')        
#                 champion.bulletsLeft -= 2
#                 champion.attackQueue.pop(0)
#             if not champion.attackQueue:
#                 champion.ultActive = False
#         return 0
# class NidaleeBuff(Buff):
#     def __init__(self, level=0, params=0):
#         super().__init__("Aspect of the Cougar", level, params, phases=["preAttack"])
#         self.count = 0
#     def performAbility(self, phase, time, champion, input=0):
#         # input is opponent
#         if champion.ultActive:
#             self.count += 1
#         if champion.ultActive and self.count >= 4:
#             champion.onHitSpell(champion.opponents[0], champion.items, time, champion.abilityScaling, 'magical')        
#             self.count = 0
#         return 0



# class YasuoStacks(Buff):
#     def __init__(self, level=0, params=0):
#         # vayne bolts inflicts status "Silver Bolts"
#         super().__init__("Burning Blade", level, params, phases=["onAttack"])
#     def performAbility(self, phase, time, champion, input=0):
#         # input is opponent
#         champion.onHitSpell(input, champion.items, time, champion.getStacks, 'true')        
#         return 0

# class DravenAxes(Buff):
#     def __init__(self, level=0, params=0):
#         # vayne bolts inflicts status "Silver Bolts"
#         super().__init__("Spinning Axes", level, params, phases=["onUpdate"])
#     def performAbility(self, phase, time, champion, input=0):
#         # input is opponent
#         if champion.axeQueue and time > champion.axeQueue[-1]:
#             champion.axes = min(champion.axes + 1, 2)
#             champion.axeQueue.pop()
#         return 0

# class Cannoneer(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Cannoneer " + str(level), level, params, phases=["preAttack"])
#         self.scaling = {2: 2.25, 4: 4.5, 6: 12}
#         self.counter = 0

#     def performAbility(self, phase, time, champion, input=0):
#         self.counter += 1
#         if self.counter == 5:
#             # do (scaling-1) dmg to primary target
#             champion.doAttack(champion.opponents[0], champion.items, time, multiplier=Stat(0, self.scaling[self.level]-1, 0))
#             champion.doAttack(champion.opponents[1], champion.items, time, multiplier=Stat(0, self.scaling[self.level], 0))
#             champion.doAttack(champion.opponents[2], champion.items, time, multiplier=Stat(0, self.scaling[self.level], 0))
#             self.counter = 0
#             # do scaling dmg to nearby targets
#         return 0



# class Legionnaire(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Legionnaire " + str(level), level, params, phases=["preCombat"])
#         self.scaling = {2: 25, 4: 60, 6: 135, 8: 250}

#     def performAbility(self, phase, time, champion, input=0):
#         champion.aspd.add += self.scaling[self.level]
#         return 0

# class Sentinel(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Sentinel " + str(level), level, params, phases=["preCombat"])
#         self.scaling = {3: 25, 6: 90, 9: 500}

#     def performAbility(self, phase, time, champion, input=0):
#         champion.aspd.add += self.scaling[self.level]
#         return 0

# class Assassin(Buff):
#     def __init__(self, level, params):
#             # params is number of stacks
#         super().__init__("Assassin " + str(level), level, params, phases=["preCombat"])
#         self.scaling = {2: (.1, .25), 4: (.3, .5), 6: (.5, .75)}
#     def performAbility(self, phase, time, champion, input=0):
#         champion.crit.add += self.scaling[self.level][0]
#         champion.critDmg.add += self.scaling[self.level][0]
#         champion.canSpellCrit = True
#         return 0


# class Ranger(Buff):
#     def __init__(self, level, params):
#         # params is the time you get the stacks
#         super().__init__("Ranger" + str(level), level, params, phases=["onUpdate"])
#         self.baseBuff = {2: .8, 4: 1.8}
#         # self.baseBuff = {2: 80, 4: 180}
#         self.lastSecond = 4

#     def performAbility(self, phase, time, champion, input=0):
#         if phase == "onUpdate":
#             if time > self.lastSecond:
#                 self.lastSecond += 8
#                 champion.applyStatus(status.ASMultModifier(4), champion, time, 4, self.baseBuff[self.level])
#         return 0

# class Redeemed(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Redeemed " + str(level), level, params, phases=["preCombat"])
#         self.scaling = {3: 30, 6: 30, 9: 30}

#     def performAbility(self, phase, time, champion, input=0):
#         champion.ap.add+= self.scaling[self.level]
#         return 0

# class Invoker(Buff):
#     def __init__(self, level, params):
#         # params is number of stacks
#         super().__init__("Invoker " + str(level), level, params, phases=["preCombat"])
#         self.scaling = {2: 3, 4: 6}

#     def performAbility(self, phase, time, champion, input=0):
#         champion.manaPerAttack.add += self.scaling[self.level]
#         return 0


# class Spellweaver(Buff):
#     def __init__(self, level, params):
#         # params is the time you get the stacks
#         super().__init__("Spellweaver" + str(level), level, params, phases=["preCombat", "onUpdate"])
#         self.baseBuff = {2: 20, 4: 50}
#         self.stackingBuff = {2: 2, 4: 5}
#         self.nextProc = 0

#     def performAbility(self, phase, time, champion, input=0):
#         if phase == "preCombat":
#             champion.ap.add+= self.baseBuff[self.level]
#         elif phase == "onUpdate":
#             if time > self.nextProc:
#                 self.nextProc = time + 1
#                 champion.ap.add += self.stackingBuff[self.level]
#         return 0

# class Skirmisher(Buff):
#     def __init__(self, level, params):
#         # params is the time you get the stacks
#         super().__init__("Skirmisher" + str(level), level, params, phases=["onUpdate"])
#         self.baseBuff = {3: 3, 6: 6}
#         self.lastSecond = 0

#     def performAbility(self, phase, time, champion, input=0):
#         if phase == "onUpdate":
#             if time > self.lastSecond:
#                 self.lastSecond += 1
#                 champion.atk.add += self.baseBuff[self.level]
#         return 0