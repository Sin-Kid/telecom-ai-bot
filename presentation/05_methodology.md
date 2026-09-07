# Slide 5: Methodology

## Implementation Workflow
1.  **Intent Processing**: User input is sent to the local Ollama instance where Llama 3.2 processes the intent and generates a response.
2.  **Linguistic Filtering**: The response is analyzed to determine the language and character set.
3.  **Local Synthesis**:
    *   **FastPitch**: Generates a mel-spectrogram from the text.
    *   **HiFi-GAN**: Converts the spectrogram into high-quality raw audio.
4.  **Audio Streaming**: The generated WAV audio is base64-encoded and sent to the local frontend for immediate playback.
5.  **Multi-Speaker Selection**: Users can toggle between various male/female local voices for a personalized experience.
