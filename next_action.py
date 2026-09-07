from snapshot import capture_direct_android_snapshot, detect_logo
import time, sys
import subprocess

ADB_PATH = "adb" 

def send_tap(x, y):
	"""Sends an ADB tap command to the connected Android device."""
	cmd = [ADB_PATH, "shell", "input", "tap", str(x), str(y)]
	try:
		subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		print(f"Executed Tap: ({x}, {y})")

	except subprocess.CalledProcessError:
		print("Error: Failed to execute ADB command. Is your device connected?")

def start_level():	
	capture_direct_android_snapshot("temp/test-fireflies.png", 180, 510, 720, 90) # catch if out of fireflies banner is there, close it
	capture_direct_android_snapshot("temp/test-piggy.png", 180, 375, 720, 90) # catch if piggy bank banner is there, close it
	capture_direct_android_snapshot("temp/test-next-level.png", 244, 345, 592, 130) # catch if main logo is there to click the play/ continue button		
	capture_direct_android_snapshot("temp/test-promo.png", 980, 445, 56, 56) # catch if close button X of Sand Castle promo is there to click on it to close		
	
	if detect_logo("temp/test-fireflies.png", "templates/buttons/out-of-fireflies.png"):
		send_tap(970,595)
		print("Sent tap to close out-of-fireflies banner") ## uncomment to debug
		
	
	if detect_logo("temp/test-piggy.png", "templates/buttons/piggy.png"):
		send_tap(970,460)
		print("Sent tap to close piggy banner") ## uncomment to debug
		

	if detect_logo("temp/test-promo.png", "templates/buttons/close.png"): 
		send_tap(1007,472)
		print("Sent tap to close promotion") ## uncomment to debug
		

	if detect_logo("temp/test-next-level.png", "templates/buttons/complete.png"): 
		send_tap(540,1850) # next-level button
		print("Sent tap to next level") ## uncomment to debug
		
		send_tap(540,1940) # collect coin button
		print("Sent tap to collect coins") ## uncomment to debug
			
	time.sleep(3)

			
