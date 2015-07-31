import pygame
from math import pi

from obdiface import ObdIface
from gauge import HilgaGauge
from misc import FPS, load_font

ASTART = -pi/4
ASTOP = pi + pi/4

SPEED_MIN = 0
SPEED_MAX = 160

SG_WIDTH = 250
class SpeedWidget(HilgaGauge):
    def __init__(self, obdiface, (x, y), **opts):
        HilgaGauge.__init__(self, (x, y, SG_WIDTH, SG_WIDTH*2),
                            ("0", "", "20", "", "40", "", "60", "", "80", "", "100", "", "120", "", "140", "", "160"),
                            (SPEED_MIN, SPEED_MAX),
                            (ASTART, ASTOP), **opts)

        self.obd = obdiface
        self.speed = -100

        self.avg_n = 0
        self.avg_speed = 0

        self.fnt = load_font("Anton.ttf", 64)
        self.dfnt = load_font("default.ttf", 24)

        # precalculate position for 1,2,3-symbol speed label
        def gen_ssxoff(lbl):
            ss = self.fnt.render(lbl, True, (255,255,255))
            ssr = ss.get_rect()
            ssr.centerx = SG_WIDTH/2
            return ssr.x

        self.ssxoffs = map(gen_ssxoff, ["0", "00", "120"])

    def calc_moving_avg(self, speed):
        # See wikipedia for `Cumulative moving average'
        if speed < 0:
            return
        
        self.avg_n += 1
        self.avg_speed += (speed-self.avg_speed)/self.avg_n

    def draw(self, tick, surf):
        # Sample every third tick
        if tick % 3 != 0:
            return

        speed = self.obd.sensor(ObdIface.SPEED_IDX)
        pavg = self.avg_speed
        self.calc_moving_avg(speed)

        # redraw if changed
        if round(speed) != round(self.speed) \
               or round(pavg) != round(self.avg_speed):
            # Redraw gauge pointer
            self.redraw_pointer(speed)

            speedlbl = "%d"%int(round(speed))
            ssxoff = self.ssxoffs[len(speedlbl)-1]
            self.surf.blit(self.fnt.render(speedlbl, True, (255,255,255)),
                           (ssxoff, 120))
            self.surf.blit(self.dfnt.render("avg: %d"%int(round(self.avg_speed)),
                                            True, (100,100,100)), (80,220))
            self.redraw_into(surf)

        self.speed = speed