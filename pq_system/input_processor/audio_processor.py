import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

def process_audio(file_path):
    """
    Process an audio file and convert speech to text
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text from the audio
    """
    try:
        # Initialize the recognizer
        recognizer = sr.Recognizer()
        
        # Convert audio file to WAV if it's not already
        file_ext = os.path.splitext(file_path)[1].lower()
        temp_wav_path = None
        
        if file_ext != '.wav':
            # Convert to WAV using pydub
            temp_wav_path = file_path + ".wav"
            audio = AudioSegment.from_file(file_path)
            audio.export(temp_wav_path, format="wav")
            audio_path = temp_wav_path
        else:
            audio_path = file_path
        
        # Load the audio file
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            
            # For longer files, we'll chunk the audio to process it better
            audio_data = recognizer.record(source)
        
        # Use Google's speech recognition
        text = recognizer.recognize_google(audio_data)
        
        # Clean up temporary file if created
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
            
        return text
    except Exception as e:
        # Clean up temporary file if an error occurred
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
            
        raise Exception(f"Error processing audio file: {str(e)}")

def large_audio_processing(file_path):
    """
    Process a large audio file by splitting it into chunks
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text from the audio
    """
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Convert to WAV if needed
    file_ext = os.path.splitext(file_path)[1].lower()
    temp_wav_path = None
    
    if file_ext != '.wav':
        # Convert to WAV using pydub
        temp_wav_path = file_path + ".wav"
        audio = AudioSegment.from_file(file_path)
        audio.export(temp_wav_path, format="wav")
        audio_path = temp_wav_path
    else:
        audio_path = file_path
        audio = AudioSegment.from_wav(audio_path)
    
    # Split audio into chunks based on silence
    chunks = split_on_silence(
        audio,
        min_silence_len=500,  # minimum length of silence in ms
        silence_thresh=audio.dBFS-14,  # silence threshold
        keep_silence=500  # keep 500ms of silence at the beginning and end
    )
    
    # Process each chunk
    transcript = ""
    for i, chunk in enumerate(chunks):
        # Export chunk to a temporary file
        chunk_path = f"temp_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        
        try:
            # Process the chunk
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                transcript += text + " "
        except Exception as e:
            # Skip chunks that can't be recognized
            pass
        finally:
            # Remove temporary chunk file
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
    
    # Clean up temporary WAV file if created
    if temp_wav_path and os.path.exists(temp_wav_path):
        os.remove(temp_wav_path)
        
    return transcript 