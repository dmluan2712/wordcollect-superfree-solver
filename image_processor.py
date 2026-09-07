import os
import cv2
import numpy as np
import easyocr
from snapshot import capture_direct_android_snapshot

# Initialize EasyOCR reader with GPU enabled
reader = easyocr.Reader(['en'], gpu=True)

def capture_and_process():
	os.makedirs("temp", exist_ok=True)
	os.makedirs("templates", exist_ok=True)
	
	roi_y1, roi_y2 = 1350, 2200
	roi_x, roi_w = 0, 1080
	roi_h = roi_y2 - roi_y1
	
	roi_path = os.path.join("temp", "roi_wheel.png")
	capture_direct_android_snapshot(roi_path, roi_x, roi_y1, roi_w, roi_h)
	
	wheel_roi = cv2.imread(roi_path)
	gray_wheel = cv2.cvtColor(wheel_roi, cv2.COLOR_BGR2GRAY)
	if wheel_roi is None or wheel_roi.size == 0:
		raise ValueError(f"Failed to load ROI screenshot from {roi_path}.")

	# --- STEP 1: LOCATE THE WHITE CIRCULAR TILES ON THE WHEEL ---

	##### New method: Use cv2 to find exact letter in the circular wheel
	### Find contours
	_, thresh = cv2.threshold(gray_wheel, 100, 255, cv2.THRESH_BINARY_INV) ## lower this value if the background is too dark, raise the value of too light?
	contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	
	
	roi_center_x, roi_center_y = roi_w // 2, roi_h // 2
	tile_boxes = []

	for cnt in contours:
		x, y, w, h = cv2.boundingRect(cnt)
		
		# Wheel letter tiles are roughly 200x200px to 170x170px circles
		if 5 < w < 200 and 80 < h < 200:
			aspect = w / float(h)
			if aspect < 1.3:  # Tiles are round
				cnt_cx, cnt_cy = x + (w // 2), y + (h // 2)
				dist_from_center = np.hypot(cnt_cx - roi_center_x, cnt_cy - roi_center_y)
				
				# Exclude center shuffle button (~0 to 110px from center)
				# and ignore side buttons far left/right at bottom
				if 120 < dist_from_center < 350:
					tile_boxes.append((x, y, w, h))

	# Sort tiles left-to-right
	tile_boxes = sorted(tile_boxes, key=lambda b: b[0])
	
	gray_roi = cv2.cvtColor(wheel_roi, cv2.COLOR_BGR2GRAY)
	detected_letters = []
	
	print(f"[Debug] Found {len(tile_boxes)} letter tile buttons on wheel.")

	# --- STEP 2: EXTRACT TIGHT LETTER CONTOUR FROM INSIDE EACH TILE ---
	crop_idx = 1
	for (tx, ty, tw, th) in tile_boxes:
		tile_crop_gray = gray_roi[ty:ty+th, tx:tx+tw]
		
		# Inside the white tile, dark text has low gray value -> threshold binary inv
		_, text_mask = cv2.threshold(tile_crop_gray, 120, 255, cv2.THRESH_BINARY_INV)
		
		text_contours, _ = cv2.findContours(text_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		
		# Find the main letter contour inside this tile (> 40px height)
		valid_letter_cnts = []
		for l_cnt in text_contours:
			lx, ly, lw, lh = cv2.boundingRect(l_cnt)
			if lh > 40 and lw > 10:
				valid_letter_cnts.append((lx, ly, lw, lh))
				
		if not valid_letter_cnts:
			continue
			
		# Get outer bounding rect of all letter components in this tile (fixes wide 'W')
		min_lx = min(c[0] for c in valid_letter_cnts)
		min_ly = min(c[1] for c in valid_letter_cnts)
		max_lx = max(c[0] + c[2] for c in valid_letter_cnts)
		max_ly = max(c[1] + c[3] for c in valid_letter_cnts)
		
		lw = max_lx - min_lx
		lh = max_ly - min_ly
		
		# Crop tight to the letter bounds
		letter_crop = tile_crop_gray[min_ly:max_ly, min_lx:max_lx]
		
		# Rescale to 200px height maintaining aspect ratio
		aspect = lw / float(lh)
		new_w = max(1, int(200 * aspect))
		scaled_letter_gray = cv2.resize(letter_crop, (new_w, 200), interpolation=cv2.INTER_CUBIC)

		if lw < lh: #Add white padding to width to make it 200x200
			##create new image of desired size and color (blue) for padding
			color = 255
			result = np.full((200,200), color, dtype=np.uint8)

			## compute center offset
			x_center = (200 - new_w) // 2		

			## copy img image into center of result image
			result[0 : 200, x_center: x_center+new_w] = scaled_letter_gray
		else: #for wide letters like W or M	
			result = scaled_letter_gray 	

		# Save grayscale crop
		temp_path = os.path.join("temp", f"{crop_idx}.png")
		cv2.imwrite(temp_path, result)
		print(f"  -> Saved crop #{crop_idx} ({lw}x{lh}px) to {temp_path}")
		
		# Compute screen absolute center position of the letter tile (for swiping)
		center_x = tx + (tw // 2)
		center_y = roi_y1 + ty + (th // 2)
		
		# --- TEMPLATE MATCHING ---
		matched_char = None
		best_val = 0.0
		
		template_files = [f for f in os.listdir("templates/letters") if f.lower().endswith(".png")]
		for t_file in template_files:
			char_label = os.path.splitext(t_file)[0]
			char_label = char_label[0] # In case some letters has multiple versions e.g. "I2.png", take the first letter
			template_path = os.path.join("templates/letters", t_file)
			template_gray = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
			
			if template_gray is None:
				continue
				
			res = cv2.matchTemplate(result, template_gray, cv2.TM_CCOEFF_NORMED)
			_, max_val, _, _ = cv2.minMaxLoc(res)
				
			if max_val > best_val:
				best_val = max_val
				if best_val >= 0.9:
					matched_char = char_label.upper()
 
		if matched_char:
			print(f"Matched successful to letter {matched_char} with score {best_val}")		
	
		# --- EASYOCR FALLBACK ---
		if not matched_char:
			print("Template matching fail, fall-back to OCR")
			padded_gray = cv2.copyMakeBorder(
				scaled_letter_gray, 
				15, 15, 15, 15, 
				cv2.BORDER_CONSTANT, 
				value=255
			)
			
			ocr_result = reader.readtext(padded_gray, detail=0, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
			if ocr_result:
				matched_char = ocr_result[0].strip().upper()
			else:
				matched_char = "?"
				
		detected_letters.append({
			"index": crop_idx,
			"char": matched_char,
			"center": (center_x, center_y),
			"confidence": best_val if matched_char else 0.0
		})
		
		crop_idx += 1
		
	return detected_letters

if __name__ == "__main__":
	results = capture_and_process()
	print("\nExtraction Summary:")
	for item in results:
		print(f"Letter #{item['index']}: '{item['char']}' | Center: {item['center']} | Template Score: {item['confidence']:.2f}")
