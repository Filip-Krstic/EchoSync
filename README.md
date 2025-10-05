# Real-Time Slovenian Speech Translator
This project provides a real-time speech translation system designed to support multilingual communication in academic settings. It captures spoken Slovenian, transcribes it using Google’s speech recognition, and translates it instantly into English or Serbian. A built-in graphical interface allows users to monitor translations live and export transcripts for later use.
# Purpose
This tool was developed to assist newly arriving Serbian students and other international students attending Slovenian universities. It enables them to follow lectures delivered in Slovenian by providing real-time translation into English or Serbian. The goal is to reduce language barriers in the classroom and promote inclusive, accessible learning environments.
# Features
- Real-time speech recognition using Google Speech API
- Instant translation into English or Serbian via Deep Translator
- Graphical user interface with side-by-side source and translated text
- Language switching during runtime
- Transcript export to .txt format
- Adjustable window transparency for unobtrusive overlay
- Console fallback if GUI is unavailable
# System Requirements
- Python 3.7 or higher
- Internet connection (required for speech recognition and translation)
- Microphone input
- Optional: tkinter for GUI (pre-installed on most systems)
# Installation
- Clone the repository:
- ```bash
  git clone https://github.com/yourusername/slovenian-translator.git cd slovenian-translator
  '''
- Install dependencies:
- ```bash
  pip install -r requirements.txt
  '''
- Run the translator:
- ``` bash
  python translator.py --source sl --target en
  '''
- ```bash
  --source sl
  ''' sets Slovenian as the input language.
- ```bash
  --target en
  ''' sets English as the output language.
- You can also use ```bash
- --target sr
  ''' for Serbian.
# GUI Overview- Start/Stop button to control live listening
- Language dropdown to switch between English (en) and Serbian (sr)
- Save button to export the full transcript
- Transparency slider to adjust window opacity
# Limitations- Only supports Slovenian as the input language
- Translation accuracy depends on Google Translate
- GUI requires tkinter; falls back to console mode if unavailable
# License
This project is licensed under the MIT License. See the LICENSE file for details.
# Acknowledgments
- Google Speech Recognition
- Deep Translator
- Tkinter (Python standard library)
