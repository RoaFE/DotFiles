#!/bin/bash
if pgrep hypridle > /dev/null; then
	pkill hypridle
	notify-send "Idle lock disabled" --icon=system-lock-screen
else
	hypridle &
	notify-send "Idle lock enabled" --icon=system-lock-screen
fi
