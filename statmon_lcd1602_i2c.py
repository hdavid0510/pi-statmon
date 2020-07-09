#!/usr/bin/python3

import RPi_I2C_driver
from time import *
import netifaces as ni
import psutil
import os

REFRESH_DELAY = 2.0

l = RPi_I2C_driver.lcd(0x27,16,2)
l.lcd_clear()

fontdata1 = [
	# 0: ROS
	[0x0,0x15,0x0,0x15,0x0,0x15,0x0,0x0],
	# 1: LAN
	[0x0,0x1F,0x11,0x11,0x1B,0xE,0x0,0x0],
	# 2: WiFi
	[0x0,0xE,0x11,0x4,0xA,0x0,0x4,0x0],
	# 3: Temp
	[0x4,0x6,0x4,0xD,0x16,0x4,0xE,0xE],
	# 4: Up
	[0x4,0xE,0x1F,0x0,0x0,0x0,0x0,0x0],
	# 5: Down
	[0x0,0x0,0x0,0x0,0x0,0x1F,0xE,0x4],
	# 6: degc
	[0x0,0x12,0x5,0x4,0x4,0x5,0x2,0x0],
	# 7: pers
	[0x4,0x4,0x8,0xB,0x14,0x12,0x1,0x6]
]
l.lcd_load_custom_chars(fontdata1)
ICN_ROS		= 0
ICN_LAN		= 1
ICN_WIFI	= 2
ICN_TEMP	= 3
ICN_UP		= 4
ICN_DOWN	= 5
ICN_DEGC	= 6
ICN_PERSEC	= 7


def get_network_usage(netinterface='wlan0'):
	rx_bytes = open('/sys/class/net/'+netinterface+'/statistics/rx_bytes','r')
	tx_bytes = open('/sys/class/net/'+netinterface+'/statistics/tx_bytes','r')
	rx = float(rx_bytes.read().rstrip())
	tx = float(tx_bytes.read().rstrip())
	return (rx, tx)


def print_info(netup,netdown):
	with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ft:
		temp = round(int(ft.read())/1000);
	l.lcd_display_string_pos('{:2d}'.format(temp),2,0)
	l.lcd_write(0x80+0x40+0x2); l.lcd_write_char(ICN_DEGC)
	l.lcd_write(0x80+0x40+0x4); l.lcd_write_char(ICN_UP)
	l.lcd_display_string_pos('{:4f}'.format((  netup/1024)/REFRESH_DELAY),2, 5)
	l.lcd_write(0x80+0x40+0x9); l.lcd_write_char(ICN_DOWN)
	l.lcd_display_string_pos('{:4f}'.format((netdown/1024)/REFRESH_DELAY),2,10)
	l.lcd_write(0x80+0x40+0xf); l.lcd_write_char(ICN_PERSEC)
	l.lcd_display_string_pos("K",2,14)


def main():
	netusage_old_down, netusage_old_up = 0,0;
	while True:
		avail_wifi = False
		try:
			ip_wifi = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
			avail_wifi = True
		except:
			pass
		avail_lan = False
		try:
			ip_lan = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
			avail_lan = True
		except:
			pass
		if avail_lan:
			l.lcd_write(0x80+0x00+0x0);	l.lcd_write_char(ICN_LAN)
			l.lcd_display_string_pos(ip_lan+"        ",1,1)
			netusage_now_down, netusage_now_up = get_network_usage('eth0')
			print_info(netusage_now_up - netusage_old_up, netusage_now_down - netusage_old_down)
			netusage_old_down, netusage_old_up = netusage_now_down, netusage_now_up
		elif avail_wifi:
			l.lcd_write(0x80+0x00+0x0); l.lcd_write_char(ICN_WIFI)
			l.lcd_display_string_pos(ip_wifi+"        ",1,1)
			netusage_now_down, netusage_now_up = get_network_usage('wlan0')
			print_info(netusage_now_up - netusage_old_up, netusage_now_down - netusage_old_down)
			netusage_old_down, netusage_old_up = netusage_now_down, netusage_now_up
		else:
			l.lcd_display_string_pos("No network available",1,1)
		sleep(REFRESH_DELAY)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		l.lcd_clear()
		l.lcd_display_string_pos("! Updater script",1,0)
		l.lcd_display_string_pos("  terminated",2,0)
		sleep(1)
		l.lcd_clear()
		l.backlight(0)

