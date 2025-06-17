import unittest
import numpy as np
from src.main.perceptron import Perceptron, survey_to_features

class TestPerceptron(unittest.TestCase):
    def setUp(self):
        self.model = Perceptron()

    def test_prediction_shape(self):
        x = np.ones((1, 10))
        y = self.model.predict(x)
        self.assertEqual(y.shape, (1,))

    def test_survey_to_features(self):
        data = {key: 'true' for key in [
            'enjoy_activities', 'enjoy_sports', 'enjoy_art', 'enjoy_science',
            'enjoy_clubs', 'enjoy_fieldtrips', 'overall_satisfied',
            'more_resources', 'recommend', 'enjoy_math'
        ]}
        features = survey_to_features(data)
        self.assertTrue((features == 1).all())