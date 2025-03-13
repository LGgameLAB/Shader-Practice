import pygame
import pytweening


class Tween:
    # Takes Duration in seconds
    # function returns value y=x
    def __init__(self, duration, var, final, interpolate = lambda x: x, end = lambda x: x):
        """
        Initializes a interpolating process/tween 

        Args:
            duration: seconds
            variable: list of (float) values to interpolate
            final: list of final values
            interpolate: function to interpolate with. Can also be name of tween
            end: function to execute when finished
        """
        self.duration = duration
        self.collect = 0
        if isinstance(interpolate, str):
            self.interpolate = pytweening.__dict__[interpolate]
        else:
            self.interpolate = interpolate
        
        self.var = var
        self.var_initial = var[:]      # Make a copy of the original var
        self.end = end
        self.finished = False
        
    def update(self, delta):
        self.collect += delta
        
        t =  self.collect/self.duration 
        for n in range(len(self.var)):
            # Lerp model
            self.var[n] = self.var_initial[n] * (1-t) + self.final[n] * t

        if self.is_finished():
            self.finished = True
            self.end()
    
    def is_finished(self):
        return collect >= self.duration


class Timer:
    def __init__(self):
        self.tweeners = []

    def update(self):
        delta = pygame.time.get_ticks() / 1000

        for tween in self.tweeners[:]:  # Copy to avoid issues when removing
            tween.update(delta)
            if tween.is_finished():
                self.tweeners.remove(tween)



# # Idea based on overriding the clock
#
# class GameClock(pygame.time.Clock):
#
#     def __init__(self, *args):
#         super().__init__(*args)
#
#         # holds the active tweens
#         self.processes = []
#
#     def tick(self, *args):
#         delta = super().tick(*args) / 1000.0  # Convert to seconds
#
#         # Update tweens
#         for tween in self.processes[:]:  # Copy to avoid issues when removing
#             tween.update(delta)
#             if tween.is_finished():
#                 self.processes.remove(tween)
#
#         return delta
#
#     def tween(self, tween):
#         self.processes.append(tween)
