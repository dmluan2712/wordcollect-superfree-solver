import os
from collections import Counter
import nltk

# load dictionary
def load_two_tier_dictionaries(path_to_fast_dictionary = "templates/top_english.txt", path_to_slow_dictionary = "templates/english_words.txt"):
	"""
	Loads a fast, clean core vocabulary list and a comprehensive 
	backup dictionary for deep semantic bridging.
	"""
	# 1. Fast-Pass List: Top 10k common, actual words (No abbreviations)
	with open(path_to_fast_dictionary, "r", encoding="utf-8") as f:
		fast_dict = {line.strip().upper() for line in f if len(line.strip()) >= 3}
		
	# 2. Deep-Search List: The massive backup dictionary
	with open(path_to_slow_dictionary, "r", encoding="utf-8") as f:
		deep_dict = {line.strip().upper() for line in f if line.strip()}
		
	return fast_dict, deep_dict


# Ensure the NLTK dictionary dataset is present locally
try:
	from nltk.corpus import words
	_ = words.words()
except LookupError:
	nltk.download('words')
	from nltk.corpus import words

from image_processor import capture_and_process

def load_dictionary():
	"""Loads and returns a set of unique uppercase English dictionary words."""
	word_list = set(w.upper() for w in words.words())
	return word_list

def find_valid_words(letter_data):
	"""
	Given detected letters and their screen coordinates from image_processor,
	returns a list of valid words with their continuous coordinate path.
	"""
	
	#dictionary	= load_dictionary()
	_, dictionary = load_two_tier_dictionaries()
	
	# Extract letters and character-to-positions map
	# Handling duplicates on the wheel if present
	available_chars = [item['char'] for item in letter_data if item['char'] != '?']
	num_letters = len(available_chars)
	
	if not available_chars:
		print("[Solver] No valid letters recognized.")
		return []

	letters_count = Counter(available_chars)
	valid_results = []
	
	# Filter dictionary to candidate words matching length criteria (3 to N)
	# and anagram feasibility
	for word in dictionary:
		word_len = len(word)
		if 3 <= word_len <= num_letters:
			word_count = Counter(word)
			# Check if word can be formed with available letter frequency
			if all(word_count[char] <= letters_count[char] for char in word_count):
				
				# Resolve screen coordinate path for the word sequence
				path = []
				used_indices = set()
				possible_match = True
				
				for char in word:
					match_found = False
					for item in letter_data:
						if item['char'] == char and item['index'] not in used_indices:
							used_indices.add(item['index'])
							path.append(item['center'])
							match_found = True
							break
					if not match_found:
						possible_match = False
						break
						
				if possible_match:
					valid_results.append({
						"word": word,
						"length": word_len,
						"path": path  # [(x1, y1), (x2, y2), ...]
					})
					
	# Sort results first by word length (ascending), then alphabetically
	valid_results = sorted(valid_results, key=lambda x: (x['length'], x['word']))
	return valid_results

def solve_current_level():
	print("[1/2] Processing game image...")
	detected_letters = capture_and_process()
	
	print(f"\n[2/2] Solving dictionary words for: {[item['char'] for item in detected_letters]}")
	found_words = find_valid_words(detected_letters)
	
	return found_words

if __name__ == "__main__":
	solutions = solve_current_level()
	
	print(f"\nFound {len(solutions)} valid words:")
	for item in solutions:
		print(f"Word: {item['word']:<10} | Length: {item['length']} | Swipe Path: {item['path']}")
