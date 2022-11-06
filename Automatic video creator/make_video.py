from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
from moviepy.video.fx import  resize
import numpy as np

# helper function
rotMatrix = lambda a: np.array( [[np.cos(a),np.sin(a)], 
                                 [-np.sin(a),np.cos(a)]] )
def vortex(screenpos,i,nletters):
    d = lambda t : 1.0/(0.3+t**8) #damping
    a = i*np.pi/ nletters # angle of the movement
    v = rotMatrix(a).dot([-1,0])
    if i%2 : v[1] = -v[1]
    return lambda t: screenpos+400*d(t)*rotMatrix(0.5*d(t)*a).dot(v)
    



def generate_video(image_path, audio_path_voice, audio_path_music, text, output_path):
    """Create and save a video file to `output_path` after 
    combining a static image that is located in `image_path` 
    with an audio file in `audio_path`"""
    audio_clip_voice = AudioFileClip(audio_path_voice)
    audio_clip_music = AudioFileClip(audio_path_music)
    audio_clip_music = audio_clip_music.set_duration(audio_clip_voice.duration)
    audio_clip_music = audio_clip_music.volumex(0.2)
    audio_clip_mixed = CompositeAudioClip([audio_clip_music, audio_clip_voice])

    #Text
    text_clip = TextClip(text,color='yellow', fontsize=100)                   
    text_clip = text_clip.on_color(color=(0,0,255), pos=(6,'center'), col_opacity=0.6)
    text_clip = text_clip.set_pos('center').set_duration(10) 


    # create the image clip object
    image_clip = ImageClip(image_path)
    image_clip = image_clip.fx( vfx.resize, width = 1080)
    video_clip = image_clip.set_audio(audio_clip_mixed)

    #Compose
    final = CompositeVideoClip([video_clip,text_clip])
    final.fps = 10
    final.duration = audio_clip_mixed.duration
    
    final.write_videofile(output_path)


if __name__ == "__main__":
    generate_video("a.png", "d.mp3", "b.mp3", "La taille de Vianney ", "out.mp4")