import app
from app_components import TextDialog, clear_background
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import *
from machine import RTC
import ntptime
import math

def zfl(s, width):
    # Zero pad the provided string with leading 0
    return '{:0>{w}}'.format(s, w=width)

class ClockyApp(app.App):
    #   Define the colours
    red   = (255,   0,   0)
    black = (  0,   0,   0)
    white = (255, 255, 255)

    #   Set the clock
    ntptime.settime()

    def __init__(self):
        self.button_states = Buttons(self)
        # This disables the patterndisplay system module, which does the default colour spinny thing
        eventbus.emit(PatternDisable())

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

    def draw(self, ctx):
        #   Get the time
        rtc = RTC()
        datetime = rtc.datetime()
        year    =      str( datetime[0] )
        month   = zfl( str( datetime[1] ), 2)
        day     = zfl( str( datetime[2] ), 2)
        hours   = zfl( str( datetime[4] +1 ), 2) # UTC adjustment
        minutes = zfl( str( datetime[5] ), 2)
        seconds = zfl( str( datetime[6] ), 2)
        ctx.save()

        clear_background(ctx)

        #   Draw background
        ctx.rgb(*self.black).rectangle(-120, -120, 240, 240).fill()
        #   Draw text 
        # ctx.font = "Arimo Bold Italic"
        ctx.font_size = 50
        ctx.text_align = ctx.CENTER
        ctx.rgb(*self.red).move_to(0,  0).text( year  + "-" + month   + "-" + day)
        ctx.rgb(*self.white).move_to(0, 60).text( hours + ":" + minutes + ":" + seconds)

        #   Turn off all LEDs
        ##  LEDs are numbered 1-12
        for i in range(0,12):
            tildagonos.leds[i+1] = (0, 0, 0)
        
        #   Which second is it?
        seconds_int = datetime[6]
        
        #   Illuminate the LED relevant to the seconds
        led_number = int( seconds_int / 5 ) + 1 #   Which LED to light
        brightness =    ( seconds_int % 5 ) + 1 #   How bright to make it
        tildagonos.leds[led_number] = (10*brightness, 10*brightness, 2*brightness)

        #   Calculate hands 
        # x​=r⋅cos(θ)
        # y=r⋅sin(θ)
        minutes_int = datetime[5]
        minutes_degrees = minutes_int * 6
        minutes_radians = minutes_degrees * ( math.pi / 180 )
        minutes_x =  120 * math.sin( minutes_radians )  #   Long hand
        minutes_y = -120 * math.cos( minutes_radians )

        hours_int = datetime[4] +1 #    UTC adjustment
        if (hours_int > 12):    #   24 hour adjustment
            hours_int = hours_int - 12
        hours_degrees = ( hours_int * 30 ) + ( minutes_int / 2)
        hours_radians = hours_degrees * ( math.pi / 180 )
        hours_x =  90 * math.sin( hours_radians )   #   Short hand
        hours_y = -90 * math.cos( hours_radians )

        #   Draw Hands
        #   Hand thickness
        ctx.line_width = 10
        #   Semi transparent
        ctx.rgba(0, 255, 0, 0.5).begin_path()
        ctx.move_to(0,0)
        ctx.line_to( minutes_x, minutes_y )
        ctx.stroke()
        #   Hour hand
        ctx.rgba(0, 0, 255, 0.5).begin_path()
        ctx.move_to(0,0)
        ctx.line_to( hours_x, hours_y )
        ctx.stroke()

        ctx.restore()

__app_export__ = ClockyApp
