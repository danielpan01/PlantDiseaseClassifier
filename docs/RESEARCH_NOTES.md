# Methods & evaluation notes

This document describes the implementation preserved in [plantDisease.py](../plantDisease.py), originally committed in 2024. It accompanies the [research preprint](https://doi.org/10.58445/rars.1772) and distinguishes reported findings from what the current script implements.

## Experiment design

| Component | Implementation |
| :--- | :--- |
| Target | Healthy = 0; diseased = 1 |
| Input | RGB images resized to 128 × 128, flattened to 49,152 features |
| Scaling | Pixel values divided by 255 after splitting |
| Split | 80% training / 20% testing; `random_state=0`; no stratification or grouping |
| Model | scikit-learn `MLPClassifier`; `random_state=0`; `max_iter=1000` |
| Architecture sweep | `(50,)`, `(100,)`, `(100, 50, 25)` |
| Learning-rate sweep | `0.001`, `0.01`, `0.1` |
| Selection | Lowest `best_loss_` within each sweep, then a final fit combining the selected values |
| Diagnostics | Accuracy, training-loss curves, and train/test confusion matrices |

These are **two separate sweeps**, not a joint grid search. Architecture experiments use learning rate `0.001`; learning-rate experiments use architecture `(100, 50, 25)`. Selection is based on training loss rather than validation performance.

Unspecified MLP settings use scikit-learn defaults, including ReLU and Adam. The script does not enable validation-based early stopping; normal training-loss convergence criteria still apply.

## Evaluation scope

The preprint reports **88.06% MLP classification accuracy**. That result is attributed to the paper, not presented as a new execution or a benchmark reproduced during the documentation update.

The optional CLIP experiment is exploratory:

- It evaluates all loaded images, while the MLP is evaluated on an 80/20 partition.
- It uses the prompts `healthy tomato plant` and `unhealthy tomato plant` for pepper, potato, and tomato images alike.
- It uses pretrained CLIP weights without task-specific fine-tuning.

These differences prevent a controlled, like-for-like comparison between the reported model scores. A stronger comparison would use the same untouched test set, crop-appropriate prompts, and consistent metrics.

Additional limits of this implementation:

- An image-level random split does not establish performance on unseen farms, growing conditions, or independently collected field images.
- Hyperparameters are selected by training loss, without a separate validation set.
- The script computes accuracy and confusion matrices; it does not compute F1 scores.
- There are no committed run logs, dataset checksums, saved model checkpoints, or generated figures with which to audit the original result.

### Reading the paper alongside the code

The preprint discusses methods beyond those implemented here. In particular, this script does not implement dropout, batch normalization, or a joint grid search, and it does not set `early_stopping=True`. Refer to the source for executable behavior and the preprint for the original research narrative.

The [scikit-learn 1.5.1 implementation](https://github.com/scikit-learn/scikit-learn/blob/1.5.1/sklearn/neural_network/_multilayer_perceptron.py) documents the defaults used by the original dependency series.

## Dataset layout

Download the [dataset referenced by the preprint](https://www.kaggle.com/datasets/emmarex/plantdisease), then place the following folders directly under `PlantVillage/` at the repository root. Preserve their spelling.

| Folder | Binary label |
| :--- | :--- |
| `Pepper__bell___Bacterial_spot` | Diseased |
| `Pepper__bell___healthy` | Healthy |
| `Potato___Early_blight` | Diseased |
| `Potato___healthy` | Healthy |
| `Potato___Late_blight` | Diseased |
| `Tomato__Target_Spot` | Diseased |
| `Tomato__Tomato_mosaic_virus` | Diseased |
| `Tomato__Tomato_YellowLeaf__Curl_Virus` | Diseased |
| `Tomato_Bacterial_spot` | Diseased |
| `Tomato_Early_blight` | Diseased |
| `Tomato_healthy` | Healthy |
| `Tomato_Late_blight` | Diseased |
| `Tomato_Leaf_Mold` | Diseased |
| `Tomato_Septoria_leaf_spot` | Diseased |
| `Tomato_Spider_mites_Two_spotted_spider_mite` | Diseased |

The loader scans only files with the exact suffix `.JPG`. Missing directories cause loading to fail. Images using other extensions must be prepared consistently before running the experiment.

### Cache behavior

The `saved_imgs_*.npz` cache name hashes the folder-to-label mapping, not the underlying image contents or preprocessing settings. Remove the generated cache before rerunning after any dataset or preprocessing change. Dataset images, arrays, and plot outputs are excluded by [.gitignore](../.gitignore).

### Outputs

For each sweep, the script saves loss curves, best-loss plots, and train/test confusion matrices to `DataPlotting/`. It prints the final model's test accuracy and constructs a final confusion-matrix figure, but does not explicitly save or display that final figure. Models are retained in memory only.

## Useful next experiments

1. Define a stratified train/validation/test split and select hyperparameters using validation performance.
2. Evaluate MLP and CLIP on the same held-out test images with crop-appropriate prompts.
3. Report precision, recall, F1, class counts, and per-crop results alongside accuracy.
4. Preserve split manifests, dependency locks, model checkpoints, and run metadata.
5. Test generalization on a separately collected field-image dataset.

These are proposed extensions, not completed capabilities.

[Back to the project overview](../README.md)
