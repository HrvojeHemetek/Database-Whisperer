import speech_recognition as sr
import moviepy.editor as moviepy



def audio_recognition(audio_file):
    """
    Recognizes speech from an audio file using MoviePy for conversion and Google Web Speech API for recognition.

    Args:
        audio_file: The audio/video file to be processed.

    Returns:
        dict: A dictionary containing the recognized text ('content') and a 'success' flag.
    """
    # Initialize recognizer
    r = sr.Recognizer()
    print("Converting audio")
    clip = moviepy.VideoFileClip(audio_file)
    clip.audio.write_audiofile("out_audio.wav")

    # Listen for audio and recognize it
    with audio_file as source:
        print("Adjusting for ambient noise, please wait...")
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise to improve recognition
        print("Please speak now.")
        audio = r.listen(source)
    # Recognize speech using Google Web Speech API
    try:
        print("Recognizing...")
        text = r.recognize_google(audio, language = 'en-in', show_all = True )
        return {"content":text,"success":True}
    except sr.UnknownValueError:
        return {"content":"Google Web Speech API could not understand the audio","success":False}
    except sr.RequestError as e:
        return {"content":f"Could not request results from Google Web Speech API; {e}", "success":False}