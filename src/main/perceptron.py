import numpy as np
from ..auth.models import TrainingResults, User
from .models import ModelInfo
from .. import db
import json

class Perceptron:
    def __init__(self, input_size=10, output_size=9):
        """
        Initialize a perceptron with random weights.
        
        Args:
            input_size: Number of input features (survey questions)
            output_size: Number of output classes (clubs)
        """
        # Initialize weights with small random values
        self.weights = np.random.randn(output_size, input_size + 1) * 0.1  # +1 for bias
        self.input_size = input_size
        self.output_size = output_size
        self.learning_rate = 0.01
        self.epochs = 1000
        
    def train(self, X, y):
        """
        Train the perceptron on the given data.
        
        Args:
            X: Input features (survey responses)
            y: Target outputs (one-hot encoded club indices)
        """
        # Add bias term to inputs
        X_with_bias = np.hstack((X, np.ones((X.shape[0], 1))))
        self.error_history = []
        self.loss_history = []
        for epoch in range(self.epochs):
            # Forward pass
            outputs = self.predict_raw(X_with_bias)
            # Compute error
            error = y - outputs
            # Update weights
            delta = self.learning_rate * np.dot(error.T, X_with_bias)
            self.weights += delta
            # Calculate misclassification error (number of wrong predictions)
            y_pred = np.argmax(outputs, axis=1)
            y_true = np.argmax(y, axis=1)
            misclassified = np.sum(y_pred != y_true)
            self.error_history.append(int(misclassified))
            # Calculate mean squared error (loss)
            mse = np.mean((y - outputs) ** 2)
            self.loss_history.append(float(mse))

    def predict_raw(self, X_with_bias):
        """
        Make raw predictions (before applying activation function).
        
        Args:
            X_with_bias: Input features with bias term
            
        Returns:
            Raw output values
        """
        return np.dot(X_with_bias, self.weights.T)
    
    def predict(self, X):
        """
        Predict the club index for the given input.
        
        Args:
            X: Input features (survey responses)
            
        Returns:
            Predicted club index
        """
        # Add bias term to inputs
        X_with_bias = np.hstack((X, np.ones((X.shape[0], 1))))
        
        # Get raw predictions
        outputs = self.predict_raw(X_with_bias)
        
        # Return index of highest output
        return np.argmax(outputs, axis=1)
    
    def evaluate(self, X, y_true):
        """
        Evaluate the perceptron on the given data and return accuracy.

        Args:
            X: Input features (survey responses)
            y_true: True labels (one-hot encoded)

        Returns:
            Accuracy as a float (0.0 - 1.0)
        """
        y_pred = self.predict(X)
        y_true_indices = np.argmax(y_true, axis=1)
        accuracy = np.mean(y_pred == y_true_indices)
        return accuracy

    def save_to_db(self, user_id, model_name=None, accuracy=0.0):
        """
        Save the trained model to the database.
        
        Args:
            user_id: ID of the user who trained the model
            model_name: Name of the model (ignored, always 'perceptron')
            accuracy: Model accuracy to store

        Returns:
            The saved TrainingResults object
        """

        import json
        weights_json = json.dumps(self.weights.tolist())
        parameters = {
            "input_size": self.input_size,
            "output_size": self.output_size,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs
        }
        parameters_json = json.dumps(parameters)
        error_history_json = json.dumps(getattr(self, 'error_history', []))
        loss_history_json = json.dumps(getattr(self, 'loss_history', []))
        training_result = TrainingResults(
            user_id=user_id,
            model_name="perceptron",
            weights=weights_json,
            accuracy=accuracy,
            parameters=parameters_json,
            error_history=error_history_json,
            loss_history=loss_history_json
        )

        db.session.add(training_result)
        db.session.commit()
        
        return training_result

    @classmethod
    def load_from_db(cls, model_id=None):
        """
        Load a trained model from the database.
        
        Args:
            model_id: ID of the model to load. If None, loads the latest model.
            
        Returns:
            A Perceptron object with weights loaded from the database
        """
        if model_id is None:
            # Get the latest model
            model_info = ModelInfo.query.order_by(ModelInfo.created_at.desc()).first()
        else:
            # Get the specified model
            model_info = ModelInfo.query.get(model_id)
            
        if model_info is None:
            # No model found, return a new untrained model
            return cls()
            
        # Parse parameters
        parameters = json.loads(model_info.parameters)
        
        # Create perceptron with the right dimensions
        perceptron = cls(
            input_size=parameters.get("input_size", 10),
            output_size=parameters.get("output_size", 9)
        )
        
        # Set learning parameters
        perceptron.learning_rate = parameters.get("learning_rate", 0.01)
        perceptron.epochs = parameters.get("epochs", 1000)
        
        # Load weights
        perceptron.weights = np.array(json.loads(model_info.weights))
        
        return perceptron

# Function to convert survey responses to feature vector
def survey_to_features(survey_data):
    """
    Convert survey responses to a feature vector.
    
    Args:
        survey_data: Dictionary of survey responses
        
    Returns:
        Numpy array of features
    """
    # Define the order of features
    feature_keys = [
        'enjoy_activities',
        'enjoy_sports',
        'enjoy_art',
        'enjoy_science',
        'enjoy_clubs',
        'enjoy_fieldtrips',
        'overall_satisfied',
        'more_resources',
        'recommend',
        'enjoy_math'
    ]
    
    # Convert to binary features (1 for true, 0 for false)
    features = []
    for key in feature_keys:
        value = survey_data.get(key, 'false')
        features.append(1 if value.lower() == 'true' else 0)
    
    return np.array([features])

# Function to get club name from index
def get_club_from_index(index):
    """
    Get the club name from the predicted index.
    
    Args:
        index: Index of the predicted club
        
    Returns:
        Dictionary with club information
    """
    # Define mapping from index to club slug
    index_to_slug = {
        0: 'chess-club',
        1: 'robotics',
        2: 'art-club',
        3: 'music-band',
        4: 'mathletes',
        5: 'drama-club',
        6: 'debate-team',
        7: 'coding-club',
        8: 'sports-club'
    }
    
    # Get the club slug
    slug = index_to_slug.get(index, 'chess-club')  # Default to chess club if index is invalid
    
    # Import the function to get club details
    from .routes import get_clubs_dict
    
    # Get all clubs
    clubs = get_clubs_dict()
    
    # Get the club details
    club = clubs.get(slug, {})
    club['slug'] = slug
    
    return club

# Function to train the perceptron with sample data
def train_perceptron():
    """
    Train the perceptron with sample data.
    
    Returns:
        Trained Perceptron object
    """
    # Create sample training data
    # Each row represents a set of survey responses
    # 1 for true, 0 for false
    X = np.array([
        # Chess club - enjoys thinking activities
        [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],  # Enjoys math, science, clubs
        [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],  # Enjoys math, science, clubs
        
        # Robotics - enjoys science and tech
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],  # Enjoys science, clubs, field trips
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],  # Enjoys science, clubs, field trips
        
        # Art club - enjoys creative activities
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],  # Enjoys art, clubs, field trips
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],  # Enjoys art, clubs, field trips
        
        # Music band - enjoys performing arts
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],  # Enjoys art, clubs, field trips
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],  # Enjoys art, clubs, field trips
        
        # Mathletes - enjoys math and competition
        [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],  # Enjoys math, science, clubs
        [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],  # Enjoys math, science, clubs
        
        # Drama club - enjoys performing
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],  # Enjoys art, clubs, field trips
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],  # Enjoys art, clubs, field trips
        
        # Debate team - enjoys public speaking
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 0],  # Enjoys science, clubs, field trips
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 0],  # Enjoys science, clubs, field trips
        
        # Coding club - enjoys tech
        [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],  # Enjoys math, science, clubs
        [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],  # Enjoys math, science, clubs
        
        # Sports club - enjoys physical activities
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 0],  # Enjoys sports, clubs, field trips
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 0]   # Enjoys sports, clubs, field trips
    ])
    
    # Create target outputs (one-hot encoded)
    y = np.zeros((X.shape[0], 9))
    for i in range(9):
        y[i*2:(i+1)*2, i] = 1
    
    # Create and train perceptron
    perceptron = Perceptron()
    perceptron.train(X, y)
    
    return perceptron