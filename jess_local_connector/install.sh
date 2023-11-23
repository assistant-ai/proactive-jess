#!/bin/bash

cp ./com.jess.agent.plist ~/Library/LaunchAgents/
launchctl remove com.jess.agent
launchctl load ~/Library/LaunchAgents/com.jess.agent.plist
launchctl list | grep com.jess.agent
