import fedml
from ..model_args import *

# from .trainer.seq_tagging_trainer import MyModelTrainer as MySTTrainer
from .data.data_loader import load
from fedml.simulation import SimulatorMPI as Simulator
import logging
from transformers import (
    BertConfig,
    BertTokenizer,
    BertForQuestionAnswering,
    DistilBertConfig,
    DistilBertTokenizer,
    DistilBertForQuestionAnswering,
)


def create_model(args, output_dim=1):
    model_name = args.model
    logging.info(
        "create_model. model_name = %s, output_dim = %s" % (model_name, output_dim)
    )
    MODEL_CLASSES = {
        "seq_tagging": {
            "bert": (BertConfig, BertForQuestionAnswering),
            "distilbert": (DistilBertConfig, DistilBertForQuestionAnswering),
        },
    }
    try:
        config_class, model_class = MODEL_CLASSES[args.formulation][args.model_type]
    except KeyError:
        raise Exception("such model or formulation does not exist currently!")
    model_args = {}

    # model_args["num_labels"] = output_dim
    config = config_class.from_pretrained(args.model, **model_args)
    model = model_class.from_pretrained(args.model, config=config)
    trainer = MySTTrainer(model)
    return model, trainer


if __name__ == "__main__":
    # init FedML framework
    args = fedml.init()

    # init device
    device = fedml.device.get_device(args)

    # load data
    dataset, output_dim = load(args)
    (
        train_data_num,
        test_data_num,
        train_data_global,
        test_data_global,
        train_data_local_num_dict,
        train_data_local_dict,
        test_data_local_dict,
        class_num,
    ) = dataset
    args.num_labels = output_dim
    # load model and trainer
    model, trainer = create_model(args, output_dim)

    # start training
    simulator = Simulator(args, device, dataset, model, trainer)
    simulator.run()