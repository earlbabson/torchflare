# flake8: noqa
from torchflare.callbacks.callback import CallbackRunner
from torchflare.callbacks.states import ExperimentStates
from torchflare.callbacks.early_stopping import  EarlyStopping
from fastprogress.fastprogress import master_bar


class DummyPipeline:
    def __init__(self, cbs):

        self.stop_training = False
        self._model_state = None
        self.cb = CallbackRunner(cbs)

        self.cb.set_experiment(self)
        self._model_logs = {}
        self.master_bar = master_bar(range(10))

    @property
    def set_model_state(self):

        return self._model_state

    @set_model_state.setter
    def set_model_state(self, state):

        self._model_state = state
        epoch = self._model_logs.pop("Epoch") if "Epoch" in self._model_logs.keys() else None
        if self.cb is not None:
            self.cb(current_state=self._model_state, epoch = epoch ,logs=self._model_logs)

    def fit(self):

        train_loss = 0.01
        val_loss = 0.02
        train_acc = 10
        val_acc = 10

        self.set_model_state = ExperimentStates.EXP_START

        for epoch in range(10):

            train_loss += 0.01
            val_loss += 0.02
            train_acc += 0.2
            val_acc -= 0.2

            # print(epoch)
            logs = {
                "Epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "train_acc": train_acc,
            }

            self._model_logs.update(logs)
            self.set_model_state = ExperimentStates.EPOCH_END

            if self.stop_training:
                break
        self.set_model_state = ExperimentStates.EXP_END


def test_on_val_loss():

    es = EarlyStopping()
    trainer = DummyPipeline(cbs=[es])

    trainer.fit()

    assert es.monitor == "val_loss"
    assert trainer.stop_training is True


def test_on_metric():
    es = EarlyStopping(monitor="acc", mode="max")
    trainer = DummyPipeline(cbs=[es])

    trainer.fit()
    assert es.monitor == "val_acc"
    assert trainer.stop_training is True
