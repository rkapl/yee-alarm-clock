Introduction
============

This python script is a simple alarm clock for a yeelight bulb (if you don't
like to use the Android app). The program simply waits until the wake up time
and then flashes the bulb.

Usage
=====

First, edit the main.py file and set the IP address of your yeelight bulb with
LAN control enabled. Then install the necessary requirements:

      pip3 install yeelight pendulum

To set the alarm clock, run e.g.:

      ./main.py 8:30

The program will turn off the bulb and count down until the time is reached. It
then starts to flash the bulb. To turn off the alarm, just Ctrl+C it.
