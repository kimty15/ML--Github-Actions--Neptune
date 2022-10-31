
import neptune.new as neptune
from tensorflow import keras

run= neptune.init(
    project="kimty15/MLops",
    api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiIwZWU0ODU1OC1jZjdiLTRhZTItOWJmMy01MjViMjllMDQ3ZDUifQ==",
)

params = {
    "epoch_nr": 15,
    "batch_size": 128,
    "lr": 0.003,
    "momentum": 0.4,
    "use_nesterov": True,
    "unit_nr": 256,
    "dropout": 0.03,
}

mnist = keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = keras.models.Sequential(
    [
        keras.layers.Flatten(),
        keras.layers.Dense(params["unit_nr"], activation=keras.activations.relu),
        keras.layers.Dropout(params["dropout"]),
        keras.layers.Dense(10, activation=keras.activations.softmax),
    ]
)

optimizer = keras.optimizers.SGD(
    lr=params["lr"],
    momentum=params["momentum"],
    nesterov=params["use_nesterov"],
)

model.compile(
    optimizer=optimizer, loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)


# log metrics during training
class NeptuneLogger(keras.callbacks.Callback):
    def on_batch_end(self, batch, logs=None):
        if logs is None:
            logs = {}
        for log_name, log_value in logs.items():
            run["batch/{}".format(log_name)].log(log_value)

    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        for log_name, log_value in logs.items():
            run["epoch/{}".format(log_name)].log(log_value)


model.fit(
    x_train,
    y_train,
    epochs=params["epoch_nr"],
    batch_size=params["batch_size"],
    callbacks=[NeptuneLogger()],
)



