# Disease Prediction Integration for AgriPulse

This document explains the integration of TensorFlow crop disease prediction into the Django webhook for Dialogflow.

## Overview

The integration allows Dialogflow to send crop images for disease prediction and receive natural language responses with treatment recommendations.

## Files Added/Modified

### New Files:
1. `farmbot/disease_prediction_service.py` - Main service class for disease prediction
2. `test_disease_prediction.py` - Test script for the integration
3. `requirements_disease_prediction.txt` - Additional dependencies needed

### Modified Files:
1. `farmbot/views.py` - Added crop disease prediction intent handler

## How It Works

### 1. Dialogflow Request Format
When Dialogflow sends a request to your webhook, it should include:
```json
{
  "queryResult": {
    "intent": {
      "displayName": "crop_disease_prediction"
    },
    "parameters": {
      "crop": "potato",
      "image_url": "https://example.com/potato_leaf.jpg"
    }
  }
}
```

### 2. Webhook Processing
The webhook:
1. Extracts the crop name and image URL from the request
2. Downloads the image temporarily
3. Runs the TensorFlow model prediction
4. Formats the response as natural language
5. Cleans up temporary files
6. Returns the response to Dialogflow

### 3. Response Format
The webhook returns a JSON response with natural language text:
```json
{
  "fulfillmentText": "Your Potato crop shows Early Blight (confidence: 85.2%). Recommended treatment: Chlorothalonil or Mancozeb; alternate with Azoxystrobin. Application: Every 7 to 10 days after symptoms appear. Expected control time: 2 to 3 weeks."
}
```

## Setup Instructions

### 1. Install Dependencies
Add the following to your requirements.txt:
```
tensorflow>=2.10.0
Pillow>=9.0.0
requests>=2.28.0
```

### 2. Ensure Model Files Are Present
Make sure these files exist in the `CDDM/` directory:
- `crop_disease_model_mobilenetv2.h5` - The trained model
- `class_names_mobilenetv2.txt` - Class names for predictions
- `pesticides.json` - Pesticide recommendations

### 3. Configure Dialogflow Intent
In your Dialogflow console:
1. Create a new intent called `crop_disease_prediction`
2. Add training phrases like:
   - "Check my potato crop for diseases"
   - "Analyze this tomato leaf image"
   - "What's wrong with my rice plant?"
3. Add parameters:
   - `crop` (required) - The crop type
   - `image_url` (required) - URL of the image to analyze
4. Set the webhook URL to: `https://your-domain.com/farmbot/webhook/`

## Supported Crops

The model supports the following crops:
- Cotton
- Pepper bell
- Potato
- Rice
- Tomato
- Wheat
- Groundnut
- Sugarcane
- Mango
- Maize

## Error Handling

The integration handles various error scenarios:
- Invalid image URLs
- Unsupported crop types
- Model prediction failures
- Network timeouts
- File cleanup errors

## Testing

### Manual Testing
Use the test script to verify the integration:
```bash
cd Agripulse
python test_disease_prediction.py
```

### Dialogflow Testing
1. Send a test request to your webhook endpoint
2. Use the Dialogflow simulator
3. Test with real crop images

## Example Usage

### Dialogflow Request:
```json
{
  "queryResult": {
    "intent": {
      "displayName": "crop_disease_prediction"
    },
    "parameters": {
      "crop": "potato",
      "image_url": "https://example.com/potato_early_blight.jpg"
    }
  }
}
```

### Expected Response:
```json
{
  "fulfillmentText": "Your Potato crop shows Early Blight (confidence: 92.3%). Recommended treatment: Chlorothalonil or Mancozeb; alternate with Azoxystrobin. Application: Every 7 to 10 days after symptoms appear. Expected control time: 2 to 3 weeks."
}
```

## Security Considerations

1. **Image Download**: Images are downloaded temporarily and deleted immediately after processing
2. **URL Validation**: Consider adding URL validation to prevent malicious requests
3. **File Size Limits**: The service handles large images by resizing them to 180x180 pixels
4. **Timeout Protection**: 30-second timeout for image downloads

## Performance Notes

1. **Model Loading**: The TensorFlow model is loaded once when the service initializes
2. **Memory Usage**: Images are processed in memory and temporary files are cleaned up
3. **Response Time**: Typical prediction takes 2-5 seconds depending on image size and server performance

## Troubleshooting

### Common Issues:
1. **Model not found**: Ensure the model file exists in the CDDM directory
2. **Import errors**: Install required dependencies
3. **Memory issues**: Ensure sufficient RAM for TensorFlow model
4. **Image download failures**: Check network connectivity and URL validity

### Debug Mode:
Enable Django debug mode to see detailed error messages in the webhook response.

## Future Enhancements

1. **Batch Processing**: Support multiple images in one request
2. **Confidence Thresholds**: Adjustable confidence levels for predictions
3. **Caching**: Cache model predictions for repeated requests
4. **Logging**: Add detailed logging for monitoring and debugging
