from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Ground truth (teacher evaluation)
y_true = [1, 0, 1, 1, 1]

# Model predictions
y_pred = [1, 0.9, 1, 1, 0.89]

# Create confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Display
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Incorrect", "Correct"]
)

disp.plot(cmap="Blues")
plt.title("Confusion Matrix for Answer Script Evaluation")
plt.show()
