"""
AI Module: Face Matching
Compares face in ID card photo with selfie using DeepFace (FaceNet model).
Runs 100% locally — no external API calls, no data leaves your server.
"""


def match_faces(id_card_path: str, selfie_path: str) -> dict:
    """
    Compare face in ID card with selfie.
    Uses FaceNet model — accurate and runs locally.
    Returns match result with confidence score.
    """
    try:
        from deepface import DeepFace
    except ImportError as e:
        return {
            'matched':    False,
            'confidence': 0,
            'message':    (
                'Face matching dependency missing. Install tensorflow and tf_keras, or '
                'remove the face-match feature if not needed.'
            )
        }

    try:
        result = DeepFace.verify(
            img1_path         = id_card_path,
            img2_path         = selfie_path,
            model_name        = 'Facenet',
            enforce_detection = False     # don't crash if face not detected perfectly
        )
        confidence = round((1 - result['distance']) * 100, 1)
        return {
            'matched':    result['verified'],
            'confidence': confidence,
            'distance':   round(result['distance'], 4),
            'threshold':  result['threshold'],
            'message':    'Face matched with ID card' if result['verified']
                          else 'Face does not match ID card photo'
        }
    except Exception as e:
        return {
            'matched':    False,
            'confidence': 0,
            'message':    f'Face matching failed: {str(e)}'
        }
