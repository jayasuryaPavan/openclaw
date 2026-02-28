import numpy as np
import json
from brain_core import SimpleBrain

class ValidatorBrain(SimpleBrain):
    def __init__(self):
        super().__init__(input_size=512, hidden_size=64, output_size=1)
        
    def validate(self, skill_data):
        # Simulate validation logic as a probability output
        score = self.forward(np.random.randn(1, 512))
        return score > 0.5

if __name__ == "__main__":
    val_brain = ValidatorBrain()
    val_brain.save('brain/validator_weights.json')
    print("Validator ANN file created.")
