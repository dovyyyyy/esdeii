# Background music for esdeii

Three original tracks made for these themes:

| Track | Feel |
|---|---|
| 01 - Plaza Stroll | mellow bossa, electric piano |
| 02 - Channel Lounge | calm piano lounge |
| 03 - Pocket Breeze | cheerful chiptune |

ES-DE can't play background music from a theme yet (it's on their roadmap).
On Android the usual way is the **Tasker** app (paid), which plays a music
folder while ES-DE is open and stops it when you launch a game or leave.

## Setup

1. Copy this `music` folder somewhere on your device, e.g.
   `Internal storage/ES-DE/music`.
2. Install Tasker and follow the ES-DE community guide:
   https://github.com/RobZombie9043/bgmusic-android-es-de
   It has a ready-made project file you can import. When it asks for the
   music folder, pick the folder from step 1.

## Turning it on and off

In Tasker, the music is a **profile** (for example "ES-DE Music"):

- Quick way: open Tasker and flip the switch next to the profile.
- One-tap toggle: make a Tasker task with the action
  **Tasker → Profile Status**, name = your music profile, set = **Toggle**.
  Add that task as a home-screen widget or a Quick Settings tile
  (Tasker → Preferences → Action → Quick Setting Tasks) and you can switch
  the music on or off from the notification shade.

Add your own `.ogg` or `.mp3` files to the same folder to mix them in.
