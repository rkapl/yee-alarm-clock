#!/usr/bin/env python3
import yeelight
import pendulum
import re
import argparse
import time
import random

ip = '192.168.169.157'

time_re = re.compile('([0-9]+):([0-9]+)')

def wait_until(until):
    while True:
        status()
        diff = (until - pendulum.now()).total_seconds()
        if diff <= 0:
            return
        elif diff <= 60:
            time.sleep(diff)
        else:
            time.sleep(60)

def parse_time(v):
    if v == 'test':
        return v

    match = time_re.fullmatch(v)
    if match is None:
        raise argparse.ArgumentTypeError('Expects time in 24 hr format, eg. 7:30')
    hours = int(match.group(1))
    minutes = int(match.group(2))
    if hours < 0 or hours >= 24:
        raise argparse.ArgumentTypeError('Hours must be between 0 and 23')
    if minutes < 0 or minutes >= 60:
        raise argparse.ArgumentTypeError('Minutes must be between 0 and 60')
    return (hours, minutes)

def status():
    print('Alarm will set off in {}, at {} {}'.format(
        diff_time(alarm), alarm.to_datetime_string(), alarm.timezone_name))


def get_next_time(time):
    if time == 'test':
        return pendulum.now()
    hours, minutes = time
    now = pendulum.now('local')
    alarm = now.start_of('day').replace(hour=hours, minute=minutes)
    if alarm < now:
        alarm = alarm.add(days=1)
    return alarm

def diff_time(time):
    period = time - pendulum.now()
    return '{} h {} m'.format(period.in_hours(), period.minutes)

def blink():
    #bulb.set_scene(yeelight.SceneClass.CT, 6500, 100)
    bulb.set_brightness(100)
    time.sleep(1)
    # Turning the bulb off completely will disconnect music mode
    bulb.set_brightness(1)
    #bulb.set_scene(yeelight.SceneClass.CT, 6500, 1)
    time.sleep(1)

blink_transitions = [
    yeelight.TemperatureTransition(duration=50, brightness=100, degrees=6700),
    yeelight.SleepTransition(duration=1000),
    yeelight.TemperatureTransition(duration=50, brightness=0, degrees=6700),
    yeelight.SleepTransition(duration=1000),
]
blink_flow = yeelight.Flow(2, yeelight.Flow.actions.off, blink_transitions)

alarm_transitions = [
    yeelight.TemperatureTransition(duration=50, brightness=100, degrees=6700),
    yeelight.SleepTransition(duration=8000),
    yeelight.TemperatureTransition(duration=50, brightness=0, degrees=1700),
    yeelight.SleepTransition(duration=1000),

    yeelight.TemperatureTransition(duration=50, brightness=100, degrees=6700),
    yeelight.SleepTransition(duration=3000),
    yeelight.TemperatureTransition(duration=50, brightness=0, degrees=1700),
    yeelight.SleepTransition(duration=700),
]
alarm_flow = yeelight.Flow(0, yeelight.Flow.actions.off, alarm_transitions)

def disconnect_bulb(bulb):
    if bulb._Bulb__socket:
        bulb._Bulb__socket.close()
        bulb._Bulb__socket = None

def main():
    global bulb, alarm
    cparse = argparse.ArgumentParser(
        prog = 'yeelight-alarm-clock',
        description = 'Turn on yeelight at certain time, like an alarm clock')
    cparse.add_argument('time', help = 'time to turn on the clock', type = parse_time)
    cargs = cparse.parse_args()

    alarm = get_next_time(cargs.time)

    bulb = yeelight.Bulb(ip)
    bulb.turn_on()
    #print(bulb.get_properties())
    bulb.start_flow(blink_flow)
    time.sleep(5)

    # Bulb will reconnect on next command, we do not want to maintain the socket the whole night
    disconnect_bulb(bulb)

    wait_until(alarm)
    print('Alarm on')
    try:
        d = 5
        bulb.effect = 'sudden'
        bulb.turn_on()
        bulb.start_flow(alarm_flow)
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        bulb.turn_off()
        print('Alarm off')

main()