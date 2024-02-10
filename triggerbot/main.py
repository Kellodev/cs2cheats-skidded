import pymem
import keyboard
import time
import os
import random
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
from offsets import *

mouse = Controller()
client = Client()

dwEntityList = client.offset('dwEntityList')
dwLocalPlayerPawn = client.offset('dwLocalPlayerPawn')
m_iIDEntIndex = client.get('C_CSPlayerPawnBase', 'm_iIDEntIndex')
m_iTeamNum = client.get('C_BaseEntity', 'm_iTeamNum')
m_iHealth = client.get('C_BaseEntity', 'm_iHealth')
version = "v0.2"

print("Welcome to CS2 TriggerBot by KelloDev - " + version)
print("ALL VALUES ARE IN MS")


file_name = "config.txt"

if not os.path.exists(file_name):
    with open(file_name, 'w') as file:
        file.write("This is the config file.\n")
        file.write("holdDown: false\n")
        file.write("minDelayMS: 5\n")
        file.write("maxDelayMS: 10\n")
        file.write("minPressLenght: 5\n")
        file.write("maxPressLenght: 10\n")
        file.write("maxShots: 7\n")
        file.write("shotResetSleepTime: 1000\n")
        file.write("minMissShots: 0\n")
        file.write("maxMissShots: 2\n")
        file.write("missShotChance: 25\n")
        
    print(f"Config has been created, to edit config edit the config.txt in the directory you launched the program.\n")
else:
    print(f"Config already exists, to edit config edit the config.txt in the directory you launched the program.\n")

def load_config():
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()

        config_values = {}
        for line in lines:
            # Check if the line contains the separator ": "
            if ": " in line:
                key, value = line.strip().split(": ", 1)
                config_values[key] = value

        return config_values
    else:
        print(f"The file '{file_name}' does not exist.")
        return None

# Check if the file exists and load configuration values
config_values = load_config()

# If the file exists, update the variables
if config_values:
    holdDown = config_values.get("holdDown", "True").lower() == "true"
    minDelayMS = int(config_values.get("minDelayMS", "0"))
    maxDelayMS = int(config_values.get("maxDelayMS", "0"))
    minPressDelay = int(config_values.get("minPressDelay", "0"))
    maxPressDelay = int(config_values.get("maxPressDelay", "0"))
    maxShots = int(config_values.get("maxShots", "7"))
    shotResetSleepTime = int(config_values.get("shotResetSleepTime", "1500"))
    minMissShots = int(config_values.get("minMissShots", "0"))
    maxMissShots = int(config_values.get("maxMissShots", "0"))
    missShotChance = int(config_values.get("missShotChance", "0"))
else:
    print("Using default values because the config file does not exist.")

shots = 0
missedShots = 0
on = True
pm = pymem.Pymem("cs2.exe")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_status():
    print("Welcome to CS2 TriggerBot by KelloDev - " + version)

def reset_config():
    clear_console()
    print("Welcome to CS2 TriggerBot by KelloDev - " + version)
    print("ALL VALUES ARE IN MS")
    global minDelayMS, maxDelayMS, minPressDelay, maxPressDelay, maxShots, shotResetSleepTime, minMissShots, maxMissShots, missShotChance, holdDown
    holdDown = str(input("Make TriggerBot just hold down mouse button while on target? (Y/N): "))
    holdDownBool = holdDown == "y"
    minDelayMS = int(input("Min Delay: "))
    maxDelayMS = int(input("Max Delay: "))
    minPressDelay = int(input("Min Press Length: "))
    maxPressDelay = int(input("Max Press Length: "))
    maxShots = int(input("Max amount of shots before reset (Normal = 7): "))
    shotResetSleepTime = int(input("Reset sleep time (Normal = 1500MS): "))
    minMissShots = int(input("Min missed shots after shooting: "))
    maxMissShots = int(input("Max missed shots after shooting: "))
    missShotChance = int(input("Miss shot chance: "))
    print("NOTE: Hold delay will be the same as normal shots.")
    missShotMinDelay = int(input("Miss shot min delay: "))
    missShotMaxDelay = int(input("Miss shot max delay: "))

def reset_shots():
    global shotResetSleepTime, shots
    time.sleep(shotResetSleepTime / 1000)
    shots = 0

def main():
    global on, shots

    while True:

        try:
            if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                continue

            if on:
                client = pymem.process.module_from_name(pm.process_handle, "client.dll")
                client_base = client.lpBaseOfDll

                player = pm.read_longlong(client_base + dwLocalPlayerPawn)
                entityId = pm.read_int(player + m_iIDEntIndex)

                if entityId > 0 and shots < int(maxShots):
                    entList = pm.read_longlong(client_base + dwEntityList)

                    entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                    entityTeam = pm.read_int(entity + m_iTeamNum)
                    playerTeam = pm.read_int(player + m_iTeamNum)

                    if entityTeam != playerTeam:
                        entityHp = pm.read_int(entity + m_iHealth)
                        if entityHp > 0:
                            if holdDown:
                                time.sleep(random.uniform(float(minDelayMS) / 1000, float(maxDelayMS) / 1000))
                                mouse.press(Button.left)
                                missedShots = 0
                            else:
                                time.sleep(random.uniform(float(minDelayMS) / 1000, float(maxDelayMS) / 1000))
                                mouse.press(Button.left)
                                time.sleep(random.uniform(float(minPressDelay) / 1000, float(maxPressDelay) / 1000))
                                mouse.release(Button.left)
                                shots += 1
                                missedShots = 0
                else:
                    reset_shots()
                    if holdDown:
                        time.sleep(random.uniform(float(minPressDelay) / 1000, float(maxPressDelay) / 1000))
                        mouse.release(Button.left)

                    if not missShotChance == 0 and missShotChance > random.randint(0, 100):
                        f32rf2f = missedShots

                        while random.randint(minMissShots, maxMissShots) > f32rf2f:
                            time.sleep(random.uniform(minDelayMS / 1000, maxDelayMS / 1000))
                            mouse.press(Button.left)
                            time.sleep(random.uniform(float(minPressDelay) / 1000, float(maxPressDelay) / 1000))
                            mouse.release(Button.left)
                            f32rf2f = f32rf2f + 1


            time.sleep(0.03)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    clear_console()
    print_status()
    main()
