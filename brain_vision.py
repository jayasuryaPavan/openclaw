import numpy as np
import json
from brain_core import SimpleBrain

class VisionBrain(SimpleBrain):
    def __init__(self):
        super().__init__(input_size=1024, hidden_size=128, output_size=10)
        
    def analyze(self, image_features):
        # In a real ANN, image_features would be a flattened array of pixels
        # Here we simulate with random data if none provided
        if image_features is None:
            image_features = np.random.randn(1, 1024)
        return self.forward(image_features)

if __name__ == "__main__":
    v_brain = VisionBrain()
    v_brain.save('brain/vision_weights.json')
    print("Vision ANN file created.")
