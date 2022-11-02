# Mobile ViLT

*This repo is a work-in-progress!*

# Introduction

This repo attempts to port the **ViLT** model -- described in the ICML 2021 (long talk) paper: "[ViLT: Vision-and-Language Transformer Without Convolution or Region Supervision](https://arxiv.org/abs/2102.03334)" -- for mobile devices (modern Android systems). It forks and builds over the original repository, found [here](https://github.com/dandelin/ViLT). There is a [Huggingface module for ViLT (with a QA head)](https://huggingface.co/docs/transformers/model_doc/vilt#transformers.ViltForQuestionAnswering), but the interface and APIs are bloated, due to cross-compatibility reasons.

This effort was inspired by the [2022 MobiVQA paper](https://awk.ai/assets/mobivqa.pdf) which reportedly deploys a modified LXMERT model for VQA on mobile hardware (Nvidia Jetson and Google Pixel). Unfortunately, the [MobiVQA repository](https://github.com/SBUNetSys/MobiVQA/issues/1) contains no instructions on running (or replicating) the results. Important parts of the code (like configs, data setup scripts, etc) are missing, including perhaps the most crucial part of modifying the model and pre-processors for [Torchscript](https://pytorch.org/tutorials/recipes/torchscript_inference.html) compatibility. 

Our goal is to implement the optimizations discussed in MobiVQA on top of the ViLT architecture, while also ensuring that the model and pre-processors are Torchscript compatible.

# Resources on Torch JIT

* Working example of scripting a Huggingface model *that is designed to be scriptable* -- <https://huggingface.co/docs/transformers/main/en/torchscript>
* A short introduction to `script` vs `trace` functionality, and handling some edge cases -- <https://ppwwyyxx.com/blog/2022/TorchScript-Tracing-vs-Scripting/>
* Scripting a "complex" PyTorch chatbot model -- <https://pytorch.org/tutorials/beginner/deploy_seq2seq_hybrid_frontend_tutorial.html>
* Some utilities in `detectron2` which can help in scripting -- <https://github.com/facebookresearch/detectron2/blob/e091a07ef573915056f8c2191b774aad0e38d09c/detectron2/export/flatten.py#L186-L208>
* Another example of scripting a "complex" PyTorch translation model -- <https://colab.research.google.com/drive/1HiICg6jRkBnr5hvK2-VnMi88Vi9pUzEJ>
* (and finally) PyTorch documentation on torchscript -- <https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html#introduction-to-torchscript>

# Android app

The `HelloWorld` directory links to android app submodule -- <https://github.com/priyamtejaswin/HelloWorld>. This app can be built and tested on Android Studio independently. So far, it implements the Question Preprocessor (which needed to be implemented in pure Java).

# Setup and eval

Ensure you have the [ViLT VQA2 checkpoint](https://github.com/dandelin/ViLT/releases/download/200k/vilt_vqa.ckpt) downloaded to the `./weights` directory.

Also ensure that the model is in `test` mode.

Check that the Android App source (`HelloWorld`) is at the latest commit.

* `git submodule update --init`
* `git submodule update --remote --merge`

If you have the latest changes, the last command should not show any updates in `git status`.

To check functionality and correctness, run `python vilt_jit.py`

To prepare Torchscript files for the app, run `generate_assets.py`. This will save all Torchscript assets to `HelloWorld/app/src/main/assets/`.

ViLT is fine-tuned on VQA2 as a classification problem. Download the dict to assets -- <https://github.com/dandelin/ViLT/releases/download/200k/vqa_dict.json>

-- Priyam, Rishubh, Bi
