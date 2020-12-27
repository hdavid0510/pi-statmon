#!/usr/bin/python3

import RPi_I2C_driver
from time import *
import netifaces as ni
import psutil
import os

REFRESH_DELAY = 0.7
CYCLE_CLOCK = 4
CYCLE_IP = 7
CYCLE_END = 7

l = RPi_I2C_driver.lcd(0x27,16,2)
l.lcd_clear()

fontdata1 = [
	# 0: Clock
	[0x00,0x0E,0x1B,0x1B,0x19,0x1F,0x0E,0x00],
	# 1: LAN
	[0x00,0x1F,0x11,0x11,0x11,0x1B,0x0E,0x00],
	# 2: WiFi
	[0x00,0x0E,0x11,0x04,0x0A,0x00,0x04,0x00],
	# 3: WiFi(external)
	[0x1F,0x11,0x0E,0x1B,0x15,0x1F,0x1B,0x1F],
	# 4: Up (kbps)
	[0x04,0x0E,0x1F,0x00,0x08,0x0A,0x0C,0x0A],
	# 5: Down (kbps)
	[0x08,0x0A,0x0C,0x0A,0x00,0x1F,0x0E,0x04],
	# 6: Up (mbps)
	[0x04,0x0E,0x1F,0x00,0x00,0x1B,0x15,0x15],
	# 7: Down (mbps)
	[0x1B,0x15,0x15,0x00,0x00,0x1F,0x0E,0x04],
]
l.lcd_load_custom_chars(fontdata1)
ID_CLOCK	= 0
ID_LAN		= 1
ID_WIFI		= 2
ID_WUSB		= 3
ID_UP_K		= 4
ID_DOWN_K	= 5
ID_UP_M		= 6
ID_DOWN_M	= 7
LCD_LINE	= [0x80+0x00, 0x80+0x40]


tx_old = 0
rx_old = 0


def get_network_avail(netinterface):
	try:
		return ni.ifaddresses(netinterface)[ni.AF_INET][0]['addr']
	except:
		return None


def get_network_usage(netinterface='wlan0'):
	global tx_old
	global rx_old
	tx_bytes = open('/sys/class/net/'+netinterface+'/statistics/tx_bytes','r')
	rx_bytes = open('/sys/class/net/'+netinterface+'/statistics/rx_bytes','r')
	tx_now, rx_now = float(tx_bytes.read().rstrip()), float(rx_bytes.read().rstrip())
	tx, rx = (tx_now-tx_old), (rx_now-rx_old)
	tx_old, rx_old = tx_now, rx_now
	return (tx, rx)

def print_network_ip(netinterface, ip):
	l.lcd_write(LCD_LINE[0]+0); l.lcd_write_char(netinterface)
	l.lcd_display_string_pos(ip+"        ",1,1)


def print_network_usage(tx, rx):
	l.lcd_write(LCD_LINE[1]+4); 
	if tx > 10000:
		l.lcd_write_char(ID_UP_M)
		l.lcd_display_string_pos(f'{(tx/1024**2)/REFRESH_DELAY:.4f}',2, 5)
	else:
		l.lcd_write_char(ID_UP_K)
		l.lcd_display_string_pos(f'{(tx/1024)/REFRESH_DELAY:.4f}',2, 5)
	l.lcd_write(LCD_LINE[1]+10);
	if rx > 10000:
		l.lcd_write_char(ID_DOWN_M)
		l.lcd_display_string_pos(f'{(rx/1024**2)/REFRESH_DELAY:.4f}',2,11)
	else:
		l.lcd_write_char(ID_DOWN_K)
		l.lcd_display_string_pos(f'{(rx/1024)/REFRESH_DELAY:.4f}',2,11)


def print_clock(line=0, pos=0):
	l.lcd_write(LCD_LINE[line]+pos); l.lcd_write_char(ID_CLOCK)
	l.lcd_display_string_pos(strftime("%m-%d %H:%M:%S", localtime()),line+1,pos+1)


def print_thermal():
	with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ft:
		temp = round(int(ft.read())/1000);
	l.lcd_display_string_pos(f'{temp:2d}c',2,0)

def main():
	cycle = 0
	netinterface = None

	while True:
		wifi0 = get_network_avail('wlan0')
		wifi1 = get_network_avail('wlan1')
		lan = get_network_avail('eth0')

		if lan == None and wifi1 == None and wifi0 == None:
			l.lcd_write(LCD_LINE[1]+4); l.lcd_write_char(ID_WIFI)
			l.lcd_write(LCD_LINE[1]+5); l.lcd_write_char(ID_LAN)
			l.lcd_display_string_pos("Disconnected",2,4)
			print_clock()
		else:
			if lan != None:
				netinterface, ip = ID_LAN, lan
				tx, rx = get_network_usage('eth0')
			elif wifi1 != None:
				netinterface, ip = ID_WUSB, wifi1
				tx, rx = get_network_usage('wlan1')
			elif wifi0 != None:
				netinterface, ip = ID_WIFI, wifi0
				tx, rx = get_network_usage('wlan0')
			
			print_network_usage(tx, rx)
			if cycle < CYCLE_CLOCK:
				# print clock
				print_clock()
			elif cycle < CYCLE_IP:
				# print IP
				print_network_ip(netinterface, ip)
			cycle += 1
			if cycle >= CYCLE_END:
				cycle = 0
			
		print_thermal()
		sleep(REFRESH_DELAY)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		l.lcd_clear()
		l.lcd_display_string_pos("! Update script",1,0)
		l.lcd_display_string_pos("  terminated",2,0)
		for i in range(2):
			l.backlight(0)
			sleep(0.5)
			l.backlight(1)
			sleep(0.5)
		l.backlight(0)
		l.lcd_clear()
