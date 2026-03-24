#!/usr/bin/env bash

dir="$HOME/.config/rofi/"
theme='style'

#CMDs
uptime="`uptime -p | sed -e 's/up //g'`"
host=`hostname`

# Options
shutdown=' Shutdown'
shutdownTimer='󱎫 Shutdown 1hr'
reboot='󰜉 Reboot'
lock='󰌾 Lock'
suspend='󰤄 Suspend'
logout='󰍃 Logout'
yes='󰸞 Yes'
no='󱎘 No'

# Rofi CMD

rofi_cmd() {
    rofi -dmenu \
        -p "$host" \
        -mesg "Uptime : $uptime" \
        -theme ${dir}/${theme}.rasi
}

# COnfirmation CMD
confirm_cmd() {
    rofi -theme-str 'window {location: center; anchor: center; fullscreen: false; width: 250px;}' \
    -theme-str 'mainbox {children: [ "message", "listview" ];}' \
    -theme-str 'listview {columns:2; lines: 1;}' \
    -theme-str 'element-text {horizontal-align: 0.5;}' \
    -theme-str 'textbox {horiontal-align: 0.5;}' \
    -dmenu \
    -p 'Confirmation' \
    -mesg 'Are you Sure?' \
    -theme ${dir}/${theme}.rasi
}

#Ask for confirmation
confirm_exit() {
    echo -e "$yes\n$no" | confirm_cmd
}
run_rofi()
{
    echo -e "$logout\n$lock\n$suspend\n$reboot\n$shutdown\n$shutdownTimer" | rofi_cmd
}
#pass variables to rofi dmenu
run_cmd() {
    selected="$(confirm_exit)"
    if [[ "$selected" == "$yes" ]]; then
        if [[ $1 == '--shutdown' ]]; then
            systemctl poweroff
        elif [[ $1 == '--reboot' ]]; then
            systemctl reboot
        elif [[ $1 == '--shutdown 60' ]]; then
            shutdown 60
        elif [[ $1 == '--suspend' ]]; then
            systemctl suspend
        elif [[ $1 == '--lock' ]]; then
            hyprlock
        elif [[ $1 == '--logout' ]]; then
            hyprctl dispatch exit
        fi
        
    else
        exit 0
    fi     
}


# Actions
chosen="$(run_rofi)"
case ${chosen} in
    $shutdown)
		run_cmd --shutdown
        ;;
    $reboot)
		run_cmd --reboot
        ;;
    $shutdownTimer)
        run_cmd --shutdown 60
        ;;
    $suspend)
		run_cmd --suspend
        ;;
    $lock)
        run_cmd --lock
        ;;
    $logout)
		run_cmd --logout
        ;;
esac