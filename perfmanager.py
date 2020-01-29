import keyboard, time
import numpy as np


current_milli_time = lambda: int(round(time.time() * 1000))
class AnimationPerformanceManager(): #because a person pushing a button every minute isn't really a timer

    def __init__(self, adapter):
        self.current_anim = None
        self.animations = []
        self.adapter = adapter
        self.named_animations = {}
        self.keybinds = {}
        self.timeline_keybinds = {}
        self.timelines = {}
        #{"timeline1": [[anim1,anim2],[10000,15000],]}
        self.timeline_playing = None
        self.time_started = None
        self.timer_started = False
        keyboard.on_press(self.on_key)

    def start_timer(self):
        self.time_started = current_milli_time()
        self.timer_started = True

    def change_animation(self, animid):
        self.current_anim = animid
        self.timeline_playing = None
        adapter.play(animid)
        
    def get_timeline_animind(self, timeline):
        ind = self.timelines[timeline]['cur_ind']
        anim_name = self.timelines[timeline]['anims'][ind]
        anim_ind = self.named_animations[anim_name]
        return anim_ind
    
    def play_timeline(self, name):
        anim_ind = self.get_timeline_animind(name)
        adapter.play(anim_ind)
        print("now playing", anim_ind)
        self.current_anim = anim_ind
        self.timeline_playing = name

    def add_animation(self, anim, name, **kwargs):
        key = kwargs.pop("key", None)
        self.animations.append(anim)
        index = len(self.animations) - 1 
        print(name, index)
        self.named_animations[name] = index #
        if key:
            self.keybinds[key] = index

    def add_timeline(self, anims, times, name, **kwargs):
        key = kwargs.pop("key", None)
        times = list(np.cumsum(times))
        self.timelines[name] = {"anims": anims, "times": times, "cur_ind": 0, "done": False}
        if key:
            self.timeline_keybinds[key] = name

    def on_key(self, key):
        key = key.name
        if key == "y": self.start_timer()
        try:
            if key in self.keybinds:
                self.change_animation(self.keybinds[key]) 
            elif key in self.timeline_keybinds:
                self.play_timeline(self.timeline_keybinds[key])
        except Exception as e:
            print("ERROR:",e)

    def run_program(self):
        while True:
            if not self.timer_started: continue
            for name, timeline in self.timelines.items():
                if timeline['done'] == True: continue
                cur_ind = timeline['cur_ind']
                if current_milli_time() > timeline['times'][cur_ind] + self.time_started:
                    cur_ind += 1
                    if cur_ind >= len(timeline['times']):
                        self.timelines[name]['done'] = True
                        continue
                    self.timelines[name]['cur_ind'] = cur_ind
                    if self.timeline_playing == name:
                        anim_ind = self.get_timeline_animind(name)
                        adapter.play(anim_ind)
                        self.current_anim = anim_ind

if __name__ == "__main__":

    a1 = Animation().read_anim_file("animations/sign.doom")
    a2 = Animation().read_anim_file("animations/faceevil.doom")
    a3 = Animation().read_anim_file("animations/woopidle.doom")

    man = AnimationPerformanceManager()
    man.add_animation(a1, "sign", key="0")
    man.add_animation(a2, "faceevil", key="1")
    man.add_animation(a3, "woopidle", key="2")
    try:
        man.run_program()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        display.stop()
        v.stop()
        exit()

    """man = AnimationPerformanceManager()
    man.add_animation("1", "test1", key="a")
    man.add_animation("2", "test2", key="s")
    man.add_animation("3", "test3", key="d")
    man.add_animation("4", "test4")
    man.add_timeline(["test1","test2","test3","test4"], [5000,5000,1000,4000], "testtl", key="b")
    man.add_timeline(["test4","test3","test2","test1"], [10000,5000,6000,4000], "testtl2", key="n")
    print(np.cumsum([1,2,3,4,5]))
    man.run_program()"""

