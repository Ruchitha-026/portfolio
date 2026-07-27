"""Train a small neural network from scratch on the XOR problem.

This academic demonstration shows forward propagation, activation functions,
loss calculation, backpropagation, and iterative learning without a deep-
learning framework.
"""
from __future__ import annotations

from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

SEED = 7
EPOCHS = 10_000
LEARNING_RATE = 1.0
OUTPUT_DIR = Path(__file__).resolve().parent.parent


def sigmoid(values: np.ndarray) -> np.ndarray:
    """Return the sigmoid activation for each value."""
    return 1.0 / (1.0 + np.exp(-values))


def sigmoid_derivative(activated: np.ndarray) -> np.ndarray:
    """Return the derivative using already activated values."""
    return activated * (1.0 - activated)


def binary_cross_entropy(targets: np.ndarray, predictions: np.ndarray) -> float:
    """Calculate numerically stable binary cross-entropy loss."""
    clipped = np.clip(predictions, 1e-9, 1.0 - 1e-9)
    return float(-np.mean(targets * np.log(clipped) + (1.0 - targets) * np.log(1.0 - clipped)))


def train_network() -> tuple[np.ndarray, list[tuple[int, float]]]:
    """Train a 2-4-1 feed-forward network and return predictions and history."""
    rng = np.random.default_rng(SEED)
    inputs = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
    targets = np.array([[0.0], [1.0], [1.0], [0.0]])

    weights_hidden = rng.normal(0.0, 0.8, size=(2, 4))
    bias_hidden = np.zeros((1, 4))
    weights_output = rng.normal(0.0, 0.8, size=(4, 1))
    bias_output = np.zeros((1, 1))

    history: list[tuple[int, float]] = []
    for epoch in range(EPOCHS + 1):
        hidden = sigmoid(inputs @ weights_hidden + bias_hidden)
        predictions = sigmoid(hidden @ weights_output + bias_output)

        loss = binary_cross_entropy(targets, predictions)
        if epoch % 100 == 0:
            history.append((epoch, loss))

        # Output gradient for sigmoid + binary cross entropy.
        output_error = predictions - targets
        grad_weights_output = hidden.T @ output_error / len(inputs)
        grad_bias_output = np.mean(output_error, axis=0, keepdims=True)

        hidden_error = (output_error @ weights_output.T) * sigmoid_derivative(hidden)
        grad_weights_hidden = inputs.T @ hidden_error / len(inputs)
        grad_bias_hidden = np.mean(hidden_error, axis=0, keepdims=True)

        weights_output -= LEARNING_RATE * grad_weights_output
        bias_output -= LEARNING_RATE * grad_bias_output
        weights_hidden -= LEARNING_RATE * grad_weights_hidden
        bias_hidden -= LEARNING_RATE * grad_bias_hidden

    final_hidden = sigmoid(inputs @ weights_hidden + bias_hidden)
    final_predictions = sigmoid(final_hidden @ weights_output + bias_output)
    return final_predictions, history


def save_results(predictions: np.ndarray, history: list[tuple[int, float]]) -> None:
    """Write a CSV summary and a loss chart for portfolio evidence."""
    inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
    targets = [0, 1, 1, 0]
    results_path = OUTPUT_DIR / "evidence" / "neural_network_results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["input_a", "input_b", "target", "prediction", "predicted_class"])
        for pair, target, prediction in zip(inputs, targets, predictions.flatten()):
            writer.writerow([pair[0], pair[1], target, f"{prediction:.4f}", int(prediction >= 0.5)])

    epochs, losses = zip(*history)
    plt.figure(figsize=(8, 4.6))
    plt.plot(epochs, losses, linewidth=2.2)
    plt.title("Neural Network Learning: XOR Loss by Epoch")
    plt.xlabel("Training epoch")
    plt.ylabel("Binary cross-entropy loss")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "assets" / "neural_training_loss.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    final_predictions, training_history = train_network()
    save_results(final_predictions, training_history)
    print("Final predictions:")
    for pair, prediction in zip([(0, 0), (0, 1), (1, 0), (1, 1)], final_predictions.flatten()):
        print(f"  {pair} -> {prediction:.4f} (class {int(prediction >= 0.5)})")
    print(f"Final loss: {training_history[-1][1]:.6f}")
