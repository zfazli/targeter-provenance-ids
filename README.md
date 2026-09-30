# Targeter

This repository contains the implementation of **Targeter**, a behavior-driven approach for improving alert quality in provenance-based intrusion detection systems. Information about the datasets used for training, validation, and testing is provided in util/config.py.

## Acknowledgment

Parts of the preprocessing pipeline used in this project are based on the preprocessing utilities provided by [threaTrace](https://github.com/threaTrace-detector/threaTrace/). We thank the authors of threaTrace for making their implementation publicly available.
The ground-truth annotations used in this study are available through the [ORTHRUS](https://zenodo.org/records/14641606).

## Requirements

Install the required Python packages before running the experiments:

```bash
pip install -r requirements.txt
```

## Execution Pipeline

The experiments should be executed in the following order:

1. **Parse the dataset**
2. **Train the model**
3. **Test the trained model**

### 1. Parse

The `parse.py` script preprocesses the raw dataset and generates the required intermediate files.

For example:

```bash
python parse.py --dataset theia-e3
```

Replace `theia-e3` with the desired dataset.

### 2. Train

After parsing the dataset, train the Targeter model using:

```bash
python train.py --dataset theia-e3
```

The training procedure generates the model files required for evaluation.

### 3. Test

After training, evaluate the trained model using:

```bash
python test.py --dataset theia-e3
```

The test stage generates the detection results reported in the paper.

## Reproducibility

To reproduce the experiments, run the three stages sequentially:

```bash
python parse.py --dataset theia-e3
python train.py --dataset theia-e3
python test.py --dataset theia-e3
```

The same procedure can be applied to the other datasets by changing the value of `--dataset`.

## Citation

If you use this repository or Targeter in your research, please cite the associated paper.
