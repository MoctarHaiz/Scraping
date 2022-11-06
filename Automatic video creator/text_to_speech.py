import gtts
from playsound import playsound

# make request to google to get synthesis
tts = gtts.gTTS("Bonjour. Comment allez vous ?",lang="fr")
tts.save("d.mp3")
playsound("d.mp3")