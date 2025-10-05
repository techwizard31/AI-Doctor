import os
import base64
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Annotated

# Make sure to install python-dotenv and load environment variables
# You can run: pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()

# Import functions from your existing modules
from brain_of_the_doctor import analyze_image_with_query, encode_image
from voice_of_the_patient import transcribe_with_groq
# We will create this new function in 'voice_of_the_doctor.py'
from voice_of_the_doctor import text_to_speech_with_elevenlabs_api

# Define the FastAPI app
app = FastAPI(title="AI Doctor API")

# Define the data structure for our API response
class DoctorResponse(BaseModel):
    transcribed_text: str
    doctor_response: str
    doctor_audio_base64: str

# System prompt for the doctor model, moved from gradio_app.py
SYSTEM_PROMPT = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

@app.post("/process-consultation/", response_model=DoctorResponse)
async def process_consultation(image: Annotated[UploadFile, File(description="An image file of the patient's ailment.")], 
                             audio: Annotated[UploadFile, File(description="An audio file of the patient's query.")]):
    """
    Processes a patient's consultation by analyzing an image and an audio query.
    Returns the transcription, the doctor's text analysis, and the doctor's audio response.
    """
    # Create temporary file paths to store uploaded files
    temp_image_path = f"temp_{image.filename}"
    temp_audio_path = f"temp_{audio.filename}"

    try:
        # Save uploaded files to the temporary paths
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # 1. Transcribe the patient's audio query using Groq API
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set.")
        
        transcribed_text = transcribe_with_groq(
            stt_model="whisper-large-v3",
            audio_filepath=temp_audio_path,
            GROQ_API_KEY=groq_api_key
        )

        # 2. Analyze the image along with the transcribed query
        encoded_image_data = encode_image(temp_image_path)
        full_query = f"{SYSTEM_PROMPT}\n\nPatient asks: {transcribed_text}"
        
        doctor_text_response = analyze_image_with_query(
            query=full_query,
            encoded_image=encoded_image_data,
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )

        # 3. Convert the doctor's text response to speech using our new API-friendly function
        elevenlabs_api_key = os.environ.get("ELEVEN_API_KEY")
        if not elevenlabs_api_key:
            raise HTTPException(status_code=500, detail="ELEVEN_API_KEY environment variable not set.")

        audio_bytes = text_to_speech_with_elevenlabs_api(
            input_text=doctor_text_response,
            api_key=elevenlabs_api_key
        )

        # 4. Encode the audio bytes to a Base64 string for the JSON response
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        # 5. Return the final structured response
        return DoctorResponse(
            transcribed_text=transcribed_text,
            doctor_response=doctor_text_response,
            doctor_audio_base64=audio_base64
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up by removing the temporary files
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.get("/", summary="Health Check")
def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "AI Doctor API is running"}