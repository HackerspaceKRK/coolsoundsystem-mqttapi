#!/bin/bash

socat tcp-l:10001,reuseaddr,fork FILE:/dev/ttyUSB0,b38400,raw