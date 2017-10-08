#!/bin/bash

# raspi na all
mosquitto_pub -t /mixer/0/source -m 0 -h 10.12.4.11
mosquitto_pub -t /mixer/1/source -m 1 -h 10.12.4.11

mosquitto_pub -t /mixer/2/source -m 0 -h 10.12.4.11
mosquitto_pub -t /mixer/3/source -m 1 -h 10.12.4.11

mosquitto_pub -t /mixer/0/mute -m 0 -h 10.12.4.11
mosquitto_pub -t /mixer/1/mute -m 0 -h 10.12.4.11
mosquitto_pub -t /mixer/2/mute -m 0 -h 10.12.4.11
mosquitto_pub -t /mixer/3/mute -m 0 -h 10.12.4.11

mosquitto_pub -t /mixer/0/volume -m 0 -h  10.12.4.11
mosquitto_pub -t /mixer/1/volume -m 0 -h  10.12.4.11
mosquitto_pub -t /mixer/2/volume -m 0 -h  10.12.4.11
mosquitto_pub -t /mixer/3/volume -m 0 -h  10.12.4.11