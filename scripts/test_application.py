"""Small integration tests using real libraries, synthetic images and local CLIP weights."""

import ast
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, UnidentifiedImageError
import torch
from transformers import CLIPConfig, CLIPImageProcessor, CLIPModel, CLIPProcessor, CLIPTokenizer

import plantDisease as app


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.enterContext(contextlib.chdir(self.root))
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.enterContext(patch.object(app, 'save_dir', self.root / 'plots'))
        app.save_dir.mkdir()
        self.addCleanup(plt.close, 'all')

    def make_dataset(self):
        # Read the declared class mapping without duplicating its 15 folder names.
        tree = ast.parse(Path(app.__file__).read_text())
        loader = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'load_data')
        mapping = next(node.value for node in loader.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == 'class_folders' for target in node.targets))
        folders = ast.literal_eval(mapping)
        for name, label in folders.items():
            folder = Path('PlantVillage') / name
            folder.mkdir(parents=True)
            for index in range(2):
                Image.new('RGB', (24, 32), (180 * label + index, 20, 30)).save(folder / f'{index}.JPG')
        return folders

    def test_image_loading_cache_and_preprocessing(self):
        folders = self.make_dataset()
        pixels, targets = app.load_data()
        self.assertEqual(pixels.shape, (2 * len(folders), 128 * 128 * 3))
        self.assertEqual(pixels.dtype, np.uint8)
        self.assertEqual(set(targets), {0, 1})
        cached_pixels, cached_targets = app.load_data()
        np.testing.assert_array_equal(pixels, cached_pixels)
        np.testing.assert_array_equal(targets, cached_targets)
        paths, path_targets = app.load_data(return_array=False)
        self.assertEqual(len(paths), len(pixels))
        np.testing.assert_array_equal(targets, path_targets)
        train, test, y_train, y_test = app.preprocess(pixels, targets)
        self.assertEqual(len(train) + len(test), len(pixels))
        self.assertEqual(train.dtype, np.float32)
        self.assertGreaterEqual(train.min(), 0)
        self.assertLessEqual(train.max(), 1)
        self.assertEqual(len(y_train) + len(y_test), len(targets))

    def test_disguised_non_jpeg_is_rejected(self):
        folders = self.make_dataset()
        path = Path('PlantVillage') / next(iter(folders)) / '0.JPG'
        Image.new('RGB', (8, 8)).save(path, format='PNG')
        with self.assertRaises(UnidentifiedImageError):
            app.load_data()

    def test_training_prediction_and_plot_outputs(self):
        rng = np.random.default_rng(0)
        targets = np.tile([0, 1], 20)
        inputs = np.clip(targets[:, None] * 220 + rng.normal(0, 2, (40, 8)), 0, 255)
        train, test, y_train, y_test = app.preprocess(inputs, targets)
        model = app.train_model(train, y_train, learning_rate_init=0.03, hidden_layer_sizes=(4,))
        predictions = app.evaluate_model(model, 'Test', test, y_test)
        self.assertEqual(predictions.shape, y_test.shape)
        self.assertGreaterEqual(np.mean(predictions == y_test), 0.9)
        app.plot_all([model], train, y_train, test, y_test, 'learning_rate_init', [0.03])
        plots = list(app.save_dir.glob('*.png'))
        self.assertEqual(len(plots), 4)
        for plot in plots:
            with Image.open(plot) as image:
                image.verify()

    def test_main_runs_sweeps_and_final_fit(self):
        # Keep the real training/evaluation orchestration; substitute only a tiny pixel matrix.
        targets = np.tile([0, 1], 20)
        inputs = np.repeat((targets * 220)[:, None], 8, axis=1).astype(np.uint8)
        with patch.object(app, 'load_data', return_value=(inputs, targets)):
            app.main()
        self.assertEqual(len(list(app.save_dir.glob('*.png'))), 16)

    def test_offline_clip_pipeline_and_partial_batch(self):
        torch.manual_seed(0)
        torch.set_num_threads(1)
        model_path = self.root / 'tiny-clip'
        tokens = ['<|startoftext|>', '<|endoftext|>']
        tokens += list('abcdefghijklmnopqrstuvwxyz')
        tokens += [letter + '</w>' for letter in 'abcdefghijklmnopqrstuvwxyz']
        tokenizer = CLIPTokenizer(vocab={token: index for index, token in enumerate(tokens)},
                                  model_max_length=77)
        config = CLIPConfig(
            projection_dim=16,
            text_config={'vocab_size': len(tokenizer), 'hidden_size': 16,
                         'intermediate_size': 32, 'num_hidden_layers': 1,
                         'num_attention_heads': 2, 'max_position_embeddings': 77,
                         'bos_token_id': tokenizer.bos_token_id,
                         'eos_token_id': tokenizer.eos_token_id,
                         'pad_token_id': tokenizer.pad_token_id},
            vision_config={'hidden_size': 16, 'intermediate_size': 32,
                           'num_hidden_layers': 1, 'num_attention_heads': 2,
                           'image_size': 32, 'patch_size': 8},
        )
        CLIPModel(config).save_pretrained(model_path, safe_serialization=True)
        processor = CLIPProcessor(
            image_processor=CLIPImageProcessor(size={'shortest_edge': 32},
                                              crop_size={'height': 32, 'width': 32}),
            tokenizer=tokenizer,
        )
        processor.save_pretrained(model_path)
        paths = []
        for index, color in enumerate(['green', 'yellow', 'brown']):
            path = self.root / f'{index}.JPG'
            Image.new('RGB', (32, 32), color).save(path)
            paths.append(path)
        predictions = app.deep_model_classify(paths, [0, 1, 1], batch_size=2,
                                              model_name=str(model_path), device='cpu')
        self.assertEqual(len(predictions), 3)
        self.assertTrue(set(predictions) <= {'healthy tomato plant', 'unhealthy tomato plant'})
        app.deep_model_accuracy(predictions, [0, 1, 1])


if __name__ == '__main__':
    unittest.main()
