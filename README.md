# Crossword-Go (PlaySimple) Solver

Another Python-based CLI automation tool to solve the Android game [**Word Collect** by **Superfree**](https://play.google.com/store/apps/details?id=com.platinumplayer.word.addict&hl=en-US). 

---

## How It Works & Architecture

The idea is similar to other game solvers such as [Cryptogram solver](https://github.com/dmluan2712/cryptogram-playsimple-solver) and [Crossword-Go](https://github.com/dmluan2712/crossword-go-solver) and [WordSearch](https://github.com/dmluan2712/wordsearch-playsimple-solver):

1. **`image_processor.py`**: I manually calibrate my phone screen of resolution 1080x2340, using OpenCV to detect the letter box that contains the letters to be swiped  
2. **`solver.py`**: Extracts words from an English dictionary (I use [this dictionary](https://github.com/ryanjosephkamp/english-openlist) but manually add a few words the game has and the dict doesn't); the code sees what words it can make from the letters in the letter box, and form a list of adb commands to swipe these letters in sequence.
3. **`next_action.py'**: Again using OpenCV and image comparison to detect ``Next level`` buttons or ``Close`` button for ads and automatically click on them   
4. **`play.py`**: The main CLI program that integrates all components above and execute adb commands to complete the level.

---

## Prerequisites & Setup
* **Android phone screen resolution 1080x2340 
* **Android Device** with USB Debugging enabled
* **ADB (Android Debug Bridge)** installed and added to your system PATH
* **Python 3.x**
* Required Python libraries:
  ```bash
  pip install opencv-python numpy requests beautifulsoup4 easyocr
  ```
* If you have a GPU, you should install `torch` and `torch-vision` to speed up EasyOCR. If not, change 'gpu=True' to 'gpu=False' in `image_processor.py`when calling EasyOCR
