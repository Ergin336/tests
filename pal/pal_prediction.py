import numpy as np
import serialcom as sc
import tensorflow as tf
def prediction():
    matrix = sc.compute_matrix()
    model = tf.keras.models.load_model('palwatch_modelwatch.hdf5')
    activity = np.array(matrix)
    activity = activity[0][:240]
    activity = activity[:240].reshape(1, 240) / activity.max()
    keras_prediction = np.argmax(model.predict(activity), axis=1)
    return keras_prediction[0]