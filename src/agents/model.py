import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'  # kill warning about tensorflow
import numpy as np
import sys

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import load_model


class TrainModel:
    def __init__(self, num_layers, width, batch_size, learning_rate, input_dim, output_dim):
        self._input_dim = input_dim
        self._output_dim = output_dim
        self._batch_size = batch_size
        self._learning_rate = learning_rate
        self.model = self._build_model(num_layers, width) #main network
        self.model_target = self._build_model(num_layers, width)  # target network
        self._training_loss = 0


    def _build_model(self, num_layers, width):
        """
        Build and compile a fully connected deep neural network
        """
        inputs = keras.Input(shape=(self._input_dim,))
        x = layers.Dense(width, activation='relu')(inputs)
        for _ in range(num_layers):
            x = layers.Dense(width, activation='relu')(x)
        outputs = layers.Dense(self._output_dim, activation='linear')(x)
        model = keras.Model(inputs=inputs, outputs=outputs, name='my_model')
        model.compile(loss=losses.Huber(reduction=losses.Reduction.SUM_OVER_BATCH_SIZE), optimizer=Adam(learning_rate=self._learning_rate))
        return model

    #custom loss function that can be added to compile the model
    # def custom_mean_squared_error(self, y_true, y_pred):
    #     return tf.math.reduce_mean(tf.square(y_true - y_pred), axis=-1)

    def predict_one(self, state):
        """
        Predict the action values from a single state
        """
        state = np.reshape(state, [1, self._input_dim])
        return self.model.predict(state, verbose=0)


    def copy_weights(self):
        self.model_target.set_weights(self.model.get_weights())  #copy the weights of the main network to the target network


    def predict_batch(self, states):
        """
        Predict the action values from a batch of states
        """
        return self.model.predict(states, verbose=0)

    def predict_batch_target(self, states):
        """
        Predict the action values from a batch of states
        """
        return self.model_target.predict(states, verbose=0)


    def train_batch(self, states, q_sa):
        """
        Train the nn using the updated q-values
        """
        loss = self.model.train_on_batch(states, q_sa)
        self._training_loss = loss


    def save_model(self, path, filename):
        """
        Save the current model in the folder as h5 file and a model architecture summary as png
        """
        if not filename.endswith(".h5"):
            filename += ".h5"
        self.model.save(os.path.join(path, filename))
        #plot_model(self._model, to_file=os.path.join(path, 'model_structure.png'), show_shapes=True, show_layer_names=True)


    @property
    def training_loss(self):
        return self._training_loss

    @property
    def input_dim(self):
        return self._input_dim


    @property
    def output_dim(self):
        return self._output_dim


    @property
    def batch_size(self):
        return self._batch_size


class TestModel:
    def __init__(self, input_dim, model_path, name):
        self._input_dim = input_dim
        self.model = self._load_my_model(model_path, name)


    def _load_my_model(self, model_folder_path, name):
        """
        Load the model stored in the folder specified by the model number, if it exists
        """
        model_file_path = os.path.join(model_folder_path, name)

        if os.path.isfile(model_file_path):
            loaded_model = load_model(model_file_path)
            return loaded_model
        else:
            sys.exit("Model number not found")


    def predict_one(self, state):
        """
        Predict the action values from a single state
        """
        state = np.reshape(state, [1, self._input_dim])
        #print(state,"reshape model")
        #print(self._input_dim,"inputdim")
        return self.model.predict(state, verbose = 0)


    @property
    def input_dim(self):
        return self._input_dim
