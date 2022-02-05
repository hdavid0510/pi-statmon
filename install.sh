#!/bin/bash

TARGET_DIR=/usr/share/pistat
REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

STEPS_MAX=4
STEPS_NOW=1
echotitle(){
	echo -e "\n\033[96m[$STEPS_NOW/$STEPS_MAX]\033[93m ${@:1}\033[0m"
	((STEPS_NOW ++))
}


echo -e "\033[103;30m  Pi Stat Monitor service install  \033[0m"
echo -e "Visit https://github.com/hdavid0510/pi-statmon for more information."


echotitle "Updating apt packages"
sudo apt update
sudo apt upgrade -y


echotitle "Installing dependencies"
sudo apt install python3-pip python3-smbus -y
sudo -H pip3 install psutil


echotitle "Copying service files"
echo -e "\033[92mScript will be installed to:\033[0m $TARGET_DIR"
sudo cp -f $REPO_DIR/pistatmon.service /etc/systemd/system/pistatmon.service
sudo mkdir -p $TARGET_DIR
sudo cp -f $REPO_DIR/statmon_lcd1602_i2c*.py $TARGET_DIR/
sudo cp -f $REPO_DIR/RPi_I2C_driver.py $TARGET_DIR/
sudo sed -i 's|%DIR%|'"$TARGET_DIR"'|g' /etc/systemd/system/pistatmon.service


echotitle "Registering service file"
sudo systemctl daemon-reload
sudo systemctl enable pistatmon.service
sudo sh -c "grep -qF 'dtparam=spi=enabled' /boot/config.txt || echo dtparam=spi=enabled >> /boot/config.txt"
sudo sh -c "grep -qF 'dtparam=spi=enabled' /boot/config.txt || echo dtparam=i2c_arm=enabled >> /boot/config.txt"

echo -e "\n\033[91;1mDone! Reboot to finish installation.\033[0m\n"
