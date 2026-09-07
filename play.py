import os
import time
import sys
import subprocess
from pynput import keyboard
from solver import solve_current_level

import multiprocessing
from snapshot import capture_direct_android_snapshot
from next_action import send_tap, start_level

ADB_PATH = "adb"
#file_path = "temp/test-next-level-2.png"
		
def generate_continuous_swipe_command(path):
	"""
	Generates a continuous motion event across all points in `path`
	using Android's native `cmd input motionevent`.
	"""
	if len(path) < 3:
		return None

	start_x, start_y = path[0]
	
	shell_lines = [
		f"cmd input motionevent DOWN {start_x} {start_y}", "sleep 0.02",
		#f"cmd input motionevent DOWN {start_x+1} {start_y+1}", "sleep 0.1" # Fix touch problem fo the game, usually at the first letter
	]
	
	# Generate intermediate MOVE events along the path
	for x, y in path[1:]:
		shell_lines.append(f"cmd input motionevent MOVE {x} {y}")
		shell_lines.append("sleep 0.02")
		
	shell_lines.append(f"cmd input motionevent UP {path[-1][0]} {path[-1][1]}")
	#shell_lines.append("sleep 0.05")
	
	# Combine into a single ADB shell command executed as one batch
	single_shell_cmd = " && ".join(shell_lines)
	return f"{ADB_PATH} shell \"{single_shell_cmd}\""

def execute_level():
	"""Runs a single iteration: solves the current level and swipes valid words."""
	solutions = solve_current_level()
	if not solutions:
		print("[Play] No solutions found for current level screen.")
		start_level()
		return

	os.makedirs("temp", exist_ok=True)
	debug_commands = []
	
	print(f"[Play] Found {len(solutions)} target words. Executing swipes...")
	
	for item in solutions:
		word = item['word']
		path = item['path']
		
		if len(path) < 3:
			continue
			
		print(f"[Play] Swiping: '{word}'")
		debug_commands.append(f"# Word: {word}")
		
		cmd = generate_continuous_swipe_command(path)
		if cmd:
			debug_commands.append(cmd)
			try:
				subprocess.run(cmd, shell=True, check=False)
				time.sleep(0.5)
			except Exception as e:
				print(f"[Error] Execution failed for '{word}': {e}")
				
		time.sleep(0.1)

	with open("temp/commands.txt", "w") as f:
		for line in debug_commands:
			f.write(f"{line}\n")
	
	print("[Play] Commands logged to temp/commands.txt. Level execution finished!")
	time.sleep(0.5)
	start_level()


def main():
		print("=" * 60)
		print(" WORD SEARCH AUTOMATION BOT READY ")
		
		while True:
			print("-" * 60)
			print("Controls: Press [Ctrl+C] any time to quit program.")
			print("-" * 60)	
		
			try:
				print("\n" + "=" * 40)
				print("[Play] Starting level processing...")
				print("=" * 40)
				execute_level()		
				#send_tap(540,1850) # tap continue if possible
			
				print("Next level starts in 3 seconds...")
				time.sleep(3)
				
			except KeyboardInterrupt:
				print("\n[Play] Program interrupted by user.")
				sys.exit(0)

if __name__ == "__main__":	
	main()

