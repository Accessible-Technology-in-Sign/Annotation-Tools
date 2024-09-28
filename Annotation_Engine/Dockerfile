#Use a "headless VNC" container based off of this repository here: 
# https://github.com/ConSol/docker-headless-vnc-container
FROM consol/debian-xfce-vnc
ENV REFRESHED_AT 2024-09-28

# Switch to root user to install additional software
USER 0


## TODO

# Set environment variables for VLC
ENV VLC_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/vlc/plugins

## switch back to default user
USER 1000