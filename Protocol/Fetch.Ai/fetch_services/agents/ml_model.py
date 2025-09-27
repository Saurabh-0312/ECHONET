import numpy as np

# In a real-world application, this file would load a pre-trained
# TensorFlow Lite or ONNX model to perform inference. For our simulation,
# we use a simple heuristic to mimic the behavior of a real AI model.

def run_inference(sound_features: np.array) -> tuple[str, float]:
    """
    a dummy ml for future enhancement 
    Args:
        sound_features: A numpy array of numbers representing sound characteristics.

    Returns:
        A tuple containing the predicted class name (str) and the confidence (float).
    """
    if not isinstance(sound_features, np.ndarray) or sound_features.size == 0:
        return "error", 0.0

    # This is a simple heuristic-based rule to simulate a real model.
    # A real model would perform complex calculations on these features.
    mean_feature_value = np.mean(sound_features)

    if mean_feature_value > 0.75:
        # High average feature value could correspond to a loud, distinct event.
        return "car_horn", 0.92
    elif mean_feature_value > 0.5:
        # Medium value could be general ambient noise.
        return "ambient_noise", 0.85
    else:
        # Low value corresponds to a quiet environment.
        return "quiet", 0.95
