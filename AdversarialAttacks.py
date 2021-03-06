import numpy as np
import os
import pickle
import tensorflow as tf
from keras import regularizers
from keras import layers
from keras.models import Model
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import class_weight
from keras.optimizers import RMSprop, SGD, Adam
from keras.callbacks import ReduceLROnPlateau
from sklearn.metrics import accuracy_score
from keras.metrics import categorical_accuracy
from os import listdir

# gpus = tf.config.list_physical_devices('GPU')
# print("GPU DISPO : ",gpus)
#
# tf.config.experimental.set_virtual_device_configuration(
#         gpus[0],
#         [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=3000)])
# logical_gpus = tf.config.experimental.list_logical_devices('GPU')
# print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")

os.chdir("/home/ubuntu/Implementation_Mael")
dataset = "/mnt/data/Dataset/ModifiedLabelsV3/05 nv-bkl/"

training_dataset = dataset + "Training/"
validation_dataset = dataset + "Validation/"
test_dataset = dataset + "Test/"
# different parameters for the model
batch_size = 64
nb_epochs = 35


# **************** Dataset Creation ********************

train_datagen = ImageDataGenerator(
    rescale=1. / 255.,
    featurewise_center=False,  # set input mean to 0 over the dataset
    samplewise_center=False,  # set each sample mean to 0
    featurewise_std_normalization=False,  # divide inputs by std of the dataset
    samplewise_std_normalization=False,  # divide each input by its std
    zca_whitening=False,  # apply ZCA whitening
    rotation_range=180,  # randomly rotate images in the range (degrees, 0 to 180)
    zoom_range=0.1,  # Randomly zoom image
    width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
    height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
    horizontal_flip=False,  # randomly flip images
    vertical_flip=False,
)

val_datagen = ImageDataGenerator(
    rescale=1. / 255.,
    featurewise_center=False,  # set input mean to 0 over the dataset
    samplewise_center=False,  # set each sample mean to 0
    featurewise_std_normalization=False,  # divide inputs by std of the dataset
    samplewise_std_normalization=False,  # divide each input by its std
    zca_whitening=False,  # apply ZCA whitening
)

train_ds = train_datagen.flow_from_directory(
    training_dataset,
    target_size=(224, 224),
    color_mode="rgb",
    classes=None,
    class_mode="categorical",
    batch_size=batch_size,
    shuffle=True,
    seed=False,
    interpolation="bilinear",
    follow_links=False)

val_ds = val_datagen.flow_from_directory(
    validation_dataset,
    target_size=(224, 224),
    color_mode="rgb",
    classes=None,
    class_mode="categorical",
    batch_size=batch_size,
    shuffle=True,
    seed=False,
    interpolation="bilinear",
    follow_links=False)

test_datagen = ImageDataGenerator(
    rescale=1. / 255.,
    featurewise_center=False,  # set input mean to 0 over the dataset
    samplewise_center=False,  # set each sample mean to 0
    featurewise_std_normalization=False,  # divide inputs by std of the dataset
    samplewise_std_normalization=False,  # divide each input by its std
    zca_whitening=False,  # apply ZCA whitening
)

test_ds = test_datagen.flow_from_directory(
    test_dataset,
    target_size=(224, 224),
    color_mode="rgb",
    classes=None,
    class_mode="categorical",
    batch_size=1,
    shuffle=False,
    seed=False,
    interpolation="bilinear",
    follow_links=False)


class_names = train_ds.class_indices
print(class_names)

class_weights = class_weight.compute_class_weight("balanced",
                                                 np.unique(train_ds.classes),
                                                 train_ds.classes)


print("training class weights :", class_weights)
class_weights = {i: class_weights[i] for i in range(7)}

# **************** Model Creation (import the Inception V3 and perform transfer learning) ********************


pre_trained_model = InceptionV3(input_shape=(224, 224, 3), include_top=False, weights="imagenet")

#for layer in pre_trained_model.layers:
 #   layer.trainable = False

# add a global spatial average pooling layer
x = pre_trained_model.output
x = layers.GlobalAveragePooling2D()(x)
# add a fully-connected layer
x = layers.Dropout(0.4)(x)
x = layers.Dense(units=512,kernel_regularizer=regularizers.l1(1e-3), activation='relu')(x)
x = layers.Dropout(0.4)(x)
# and a fully connected output/classification layer
x = layers.Dense(7, kernel_regularizer=regularizers.l1(1e-3))(x)
x = layers.Activation(activation='softmax')(x)
# create the full network so we can train on it
model = Model(pre_trained_model.input, x)


learning_rate_reduction = ReduceLROnPlateau(monitor='val_categorical_accuracy',
                                            patience=5,
                                            verbose=1,
                                            factor=0.2,
                                            min_lr=0.00001)


model.compile(optimizer=Adam(lr=1e-4), loss="categorical_crossentropy", metrics=[categorical_accuracy])

history = model.fit_generator(
    train_ds,
    steps_per_epoch=train_ds.samples // batch_size,
    validation_data=val_ds,
    validation_steps=val_ds.samples // batch_size,
    epochs=nb_epochs,
    initial_epoch=0,
    verbose=2,
    class_weight=class_weights,
    workers=8,
    callbacks=[learning_rate_reduction]
)


# ******************* Printing Confusion Matrix ***************
model.evaluate_generator(val_ds,val_ds.samples // batch_size, verbose = 2)

Y_pred = model.predict_generator(test_ds, steps = test_ds.samples)
y_pred = np.argmax(Y_pred, axis=1)

cm = confusion_matrix(test_ds.classes, y_pred)

with open("./pythonProject1/Saves/ConfusionMatrixes/ConfusionMatrix_inceptionV3_AttackedModel_05.pkl", 'wb') as f:
    pickle.dump(cm, f)

accuracy_scr = accuracy_score(test_ds.classes, y_pred)

print("ACCURACY SCORE = ",accuracy_scr)



