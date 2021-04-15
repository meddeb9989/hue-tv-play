Hue play TV Project *for Philips Hue* 
============================
[![Maintenance](https://img.shields.io/maintenance/no/2021)](https://GitHub.com/meddeb9989/hue-play-tv/graphs/commit-activity) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)<!--[![Trust](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fastronomer.ullaakut.eu%2Fshields%3Fowner%3DMCPCapital%26name%3DHarmonizeProject)](#)--> [![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](#)
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](#)

Hue play TV Project is a low latency video analysis and pass-through application built in Python which alters Philips Hue lights based on their location relative to a screen; creating an ambient lighting effect and expanding content past the boundaries of a screen.

# Features:
* Light color and intensity changes based on pixels in its relative set location
* Video -> Light latency of 80ms via Streaming to Hue Lights via Entertainment API
* Sending 50-75 color updates per second

# Requirements 
Hardware Option A (Tested on Raspberry Pi 4B):
* RAM: 256MB Free Minimum (512MB recommended)
* CPU: 1.5GHz+, 4 Cores strongly recommended due to running three simultaneous threads.
* HDMI Splitter (Must be able to output 4k & 1080/720p simultaneously) [Here is a good one for $25](https://www.amazon.com/gp/product/B07YTWV8PR/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1), though it breaks HDR when downscaling output 2. The goal here is one output of 4K and another output of 1080/720p.
* USB3.0 HDMI Capture Card (Capable of capturing 720/1080p; delay should be 50ms or under.) [I got this when it was $45.](https://www.amazon.com/gp/product/B07Z7RNDBZ/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) A similar one should be fine. These are untested: [Panoraxy](https://www.amazon.com/Panoraxy-Capture-1080PFHD-Broadcast-Camcorder/dp/B088PYDJ22/ref=sr_1_21?dchild=1&keywords=hdmi+to+usb+3.0+capture&qid=1596386201&refinements=p_36%3A1253504011%2Cp_85%3A2470955011&rnid=2470954011&rps=1&s=electronics&sr=1-21) | [Aliexpress (This shape/style tends to perform well.)](https://www.aliexpress.com/item/4000834496145.html?spm=a2g0o.productlist.0.0.27a14df5Wc5Qoc&algo_pvid=e745d484-c811-4d2e-aebd-1403e862f148&algo_expid=e745d484-c811-4d2e-aebd-1403e862f148-15&btsid=0ab50f4415963867142714634e7e8e&ws_ab_test=searchweb0_0,searchweb201602_,searchweb201603_)

Hardware Option B (for A/V receivers with 2 or more HDMI outputs):
* Raspberry Pi 4B kit running with recommended power supply (tested on 8GB model running on Ubuntu 20.04 64-bit OS)
* HDMI Splitter (tested on U9 ViewHD Latest 4K 1x2 HDMI Splitter 1 in 2 Out, Model U9-Pluto v1.4)
* USB3.0 HDMI Capture Card (tested on Elgato Cam Link 4k)

# Setup

**Software Setup Option A:**

Download the latest scripts and install all dependencies via the following commands. **Be sure to watch for errors!** You will need about 1GB of free space. The script can run for up to an hour.

```
git clone https://github.com/meddeb9989/hue-tv-play.git
cd hue-tv-play
./compose up hue-play
```

**Software Setup Option B (tested with Ubuntu 20.04.2 and Python v3.8.5):**

Install all dependencies via the following commands. **Be sure to watch for errors!** 

* Install pip:
```
sudo apt-get install python3-pip
```
* Install HTTP Parser and NumPy dependencies via pip:
```
pip3 install http-parser numpy
```
* Compile and install OpenCV from source - [Follow this guide...] (https://docs.opencv.org/master/d2/de6/tutorial_py_setup_in_ubuntu.html) Compiling may take a couple of hours.
```
sudo apt-get install cmake
sudo apt-get install gcc g++
sudo apt-get install python3-dev python3-numpy
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev
sudo apt-get install libgtk-3-dev
sudo apt-get install git
git clone https://github.com/opencv/opencv.git
mkdir opencv/build
cd opencv/build
cmake ../
make
sudo make install
cd ../..
git clone https://github.com/MCPCapital/HarmonizeProject.git
```

**Hardware Setup Option A:**

* Connect Video Device (PS4, FireStick, etc.) to the splitter input. 
* Connect an HDMI cable from the 4k output to the TV; and from Output 2 (downscaled) to the video capture card connected to your device.
* Ensure your splitter's switches are set to downscale Output 2 to 1080 or 720p!

**Hardware Setup Option B (for A/V receivers with 2 or more HDMI outputs):**

* Connect your video device (PS4, FireStick, etc.) to an available HDMI input on your A/V receiver. 
* Connect an HDMI cable from the HDMI output 1 from A/V receiver to the TV.
* Connect an HDMI cable from HDMI output 2 from the receiver to the HDMI input on the splitter.
* Connect an HDMI cable from the HDMI output 1 of the splitter to the HDMI input on the video capture device.
* Connect the video capture device USB 3.0 output to a USB 3.0 port (not a USB 2.0 port) on the Raspberry Pi. 
* Ensure that the DIP switches on the splitter are set to downscale HDMI Output 1 to 1080 or 720p.

**Entertainment Area Configuration:**

* Hue App -> Settings -> Entertainment Areas
* Harmonize will use the **height** and the **horizontal position** of lights in relation to the TV. **The depth/vertical position are currently ignored.**
* In the example below, the light on the left is to the left of the TV at the bottom of it. The light on the right is on the right side of the TV at the top of it.

**First-Time Run Instructions:**

* If you have not set up a bridge before, the program will attempt to register you on the bridge. You will have 45 second to push the button on the bridge. *Current Bug* - After registering, the script will store the clientdata but fail & exit. *Workaround* - Simply run the script again since the data was saved.
* If multiple bridges are found, you will be given the option to select one. You will have to do this every time if you have multiple bridges (for now).
* If multiple entertainment areas are found, you will be given the option to select one. You can also enter this as a command line argument.

# Usage

**To start the program:**

* `screen`
* `cd hue-tv-play`
* `./compose up hue-play`
* Type Ctrl+A and Ctrl-D to continue running the script in the background.
* To resume the terminal session use `screen -r`
* Press *ENTER* to safely stop the program.

**Command line arguments:**

* `-v `           Display verbose output
* `-g # `         Use specific entertainment group number (#)

**Configurable values within the script:** (Advanced users only)

* Line 237 - `breadth` - determines the % from the edges of the screen to use in calculations. Default is 15%. Lower values can result in less lag time, but less color accuracy.
* Line 315 - `time.sleep(0.01)` - Determines how frequently messages are sent to the bridge. Keep in mind the rest of the function takes some time to run in addition to this sleep command. Bridge requests are capped by Philips at a rate of 60/s (1 per ~16.6ms) and the excess are dropped.
* Run with `sudo` to give Harmonize higher priority over other CPU tasks.

# Troubleshooting

* "Import Error" - Ensure you have all the dependencies installed. Run through the manual dependency install instructions above.
* No video input // lights are all dim gray - Run `python3 ./videotest.py` to see if your device (via OpenCV) can properly read the video input.
* w, h, or rgbframe not defined - Increase the waiting time from 0.75 seconds - Line 330 {time.sleep(.75)} *This is a known bug (race condition).
* python3-opencv installation fails - Compile from source - [Follow this guide.](https://pimylifeup.com/raspberry-pi-opencv/)
