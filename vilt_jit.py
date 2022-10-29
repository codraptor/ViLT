import torch
import copy
import time
import requests
import io
import numpy as np
from transformers import ViltProcessor, ViltForQuestionAnswering
from transformers.models.bert.modeling_bert import BertConfig, BertEmbeddings
from vilt.modules import heads, objectives, vilt_utils
from torchvision import transforms
import json
import urllib

from vilt.transforms import pixelbert_transform
from vilt.datamodules.datamodule_base import get_pretrained_tokenizer

import requests
import torch
import os

from PIL import Image

from vilt.config import ex
from vilt.modules import ViLTransformerSS

@ex.automain
def main(_config):
    _config = copy.deepcopy(_config)
    _config["test_only"] = True
    _config["load_path"] = "./weights/vilt_vqa.ckpt"
    assert os.path.exists(_config["load_path"]) and os.path.isfile(_config["load_path"])

    loss_names = {
        "itm": 0,
        "mlm": 0,
        "mpp": 0,
        "vqa": 1,
        "imgcls": 0,
        "nlvr2": 0,
        "irtr": 0,
        "arc": 0,
    }

    print(_config)

    with urllib.request.urlopen(
        "https://github.com/dandelin/ViLT/releases/download/200k/vqa_dict.json"
    ) as url:
        id2ans = json.loads(url.read().decode())

    url = "https://media.istockphoto.com/photos/joyful-dog-playing-with-whip-while-walking-on-green-field-picture-id1187003477?k=20&m=1187003477&s=612x612&w=0&h=fvUFuwvTZWEJjk8HUU80-zvaI4gg9szPGJ2RdASH72s="
    text = "How many dogs are there in this picture?"
    res = requests.get(url)
    image = Image.open(io.BytesIO(res.content)).convert("RGB")
    img = pixelbert_transform(size=384)(image)
    img = img.unsqueeze(0)
    tokenizer = get_pretrained_tokenizer(_config["tokenizer"])

    batch = {"text": [text], "image": img}
    encoded = tokenizer(batch["text"])
    print(encoded)
    batch["text"] = torch.tensor(encoded["input_ids"])
    batch["text_ids"] = torch.tensor(encoded["input_ids"])
    batch["text_labels"] = torch.tensor(encoded["input_ids"])
    batch["text_masks"] = torch.tensor(encoded["attention_mask"])

    bert_config = BertConfig(
            vocab_size=_config["vocab_size"],
            hidden_size=_config["hidden_size"],
            num_hidden_layers=_config["num_layers"],
            num_attention_heads=_config["num_heads"],
            intermediate_size=_config["hidden_size"] * _config["mlp_ratio"],
            max_position_embeddings=_config["max_text_len"],
            hidden_dropout_prob=_config["drop_rate"],
            attention_probs_dropout_prob=_config["drop_rate"],
    )

    text_embeddings = BertEmbeddings(bert_config)
    text_embeddings.apply(objectives.init_weights)

    # print(batch["text_ids"].shape)
    # print(batch["text"].shape)

    # print(batch["text_ids"])
    # print(text_embeddings)

    # print(text_embeddings(batch["text_ids"]))

    model = ViLTransformerSS(_config, text_embeddings, bert_config)
    model.setup("test")
    model.eval()

    logits = model(batch)
    print(logits)
    answer = id2ans[str(logits.argmax().item())]
    print(answer)
    
    trace_model = torch.jit.trace(model, batch)
    # trace_model = torch.jit.trace(model, example_inputs = (encoding['input_ids'], encoding['token_type_ids'], encoding['attention_mask'], 
    #                                   encoding['pixel_values'], encoding['pixel_mask']))

    logits = trace_model(batch)

    yes_index = [i for i in id2ans if id2ans[i]=="yes"][0]
    print(yes_index)
    print(logits.max())
    print(logits.detach().numpy()[0,int(yes_index)])
    answer = id2ans[str(logits.argmax().item())]
    print(answer)

    print("Generating bertids for texts ...")
    for t in [
        "is this pizza vegetarian?",
        "Is this pizza vegetarian?",
        "how many dogs are there in this picture ?",
        "How many Dogs are there in this picture ?",
        "what is next to the number 102"
    ]:
        ids = tokenizer([t])["input_ids"][0]
        print(t)
        print(ids)
        print()
    