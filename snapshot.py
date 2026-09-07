import subprocess
import io
import cv2
from PIL import Image
	
def capture_direct_android_snapshot(output_path, x, y, width, height):
	"""
	Takes a snapshot of an Android device via ADB, pipes it directly into 
	Linux memory (skipping device storage), crops, and saves it.
	
	:param output_path: Path where the final image will be saved
	:param x: Top-left X coordinate for cropping
	:param y: Top-left Y coordinate for cropping
	:param width: Width of the cropped area
	:param height: Height of the cropped area
	"""
	try:
		# print("📸 Streaming screenshot directly from device...")
		
		# Run screencap and pipe the output directly to stdout
		# Note: 'exec-out' is used instead of 'shell' because 'shell' can 
		# occasionally corrupt binary data on older ADB versions by mangling line endings.
		result = subprocess.run(
			["adb", "exec-out", "screencap", "-p"], 
			stdout=subprocess.PIPE, 
			stderr=subprocess.PIPE,
			check=True
		)
		
		# Convert the raw bytes from stdout into a file-like stream
		image_stream = io.BytesIO(result.stdout)
		
		# print("✂️ Cropping and saving image...")
		# Open the image directly from memory
		with Image.open(image_stream) as img:
			# Define the box to crop: (left, upper, right, lower)
			crop_box = (x, y, x + width, y + height)
			cropped_img = img.crop(crop_box)
			
			# Save the final processed image to your Linux machine
			cropped_img.save(output_path)
			#print(f"✅ Success! Image saved to: {output_path}")
			
	except subprocess.CalledProcessError as e:
		#print(f"❌ ADB Command failed. Error: {e.stderr.decode().strip()}")
		print(f"ADB Command failed. Error: {e.stderr.decode().strip()}")

	except Exception as e:
		print(f"An error occurred: {e}")


def detect_logo(image_file, button_path, confidence_threshold = 0.85):
	# This function check if the next level button is ready
	
	# STEP 1: Load your template library
	template_img = cv2.imread(button_path, cv2.IMREAD_GRAYSCALE)	

	# Read snapshot in grayscale for template verification
	img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
	template_height, template_width = template_img.shape 
	img_test = cv2.resize(img, (template_width, template_height))
		
	result = cv2.matchTemplate(img_test, template_img, cv2.TM_CCOEFF_NORMED)
	_, max_val, _, _ = cv2.minMaxLoc(result)
	
	highest_score = -1	
				
	if max_val > highest_score:
		highest_score = max_val
				
	# STEP 2: see if the two image matches
	if highest_score >= confidence_threshold:
		print(f"{button_path} score check: {highest_score}") ## uncomment for debugging
		return True		

	else:
		#print(f"{button_path} score check: {highest_score}") ## uncomment for debugging
		return False

# --- Example Usage ---
if __name__ == "__main__":
	save_files = capture_snapshots()
