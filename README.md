# Sauce-Engine
A wrapper for Pygame and Pymunk that makes it much quicker to make multi-scene projects with animations and physics and the like.

# How To Use
Drop the Sauce folder in your python project folder, making sure its adjacent to your main python file. Then, drop the assets directory in the same place (this is so Sauce can use this assets directory using its built in functions, technically its optional). Then, you can go `from sauce import sauce` to import the main engine. Extensions can be found in the same place (e.g `from sauce import splash` for the built in splash screen scene)

# Requirements
Main engine - pygame, pymunk
File browser extension - pywebview
