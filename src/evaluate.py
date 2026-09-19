# ================================================================
#  evaluate.py
#  Handles: metrics table, confusion matrix, ROC/PR curves,
#           feature importance, saving comparison CSV
#  Usage  : from evaluate import run_evaluation
# ================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score,
)

sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams["figure.dpi"] = 120


def compute_metrics(lr_model, rf_model, xgb_model,
                    X_test, X_test_scaled, y_test):
    """
    Compute Accuracy, F1, Precision, Recall, ROC-AUC
    for all 3 models and print a comparison table.
    """
    y_pred_lr  = lr_model.predict(X_test_scaled)
    y_pred_rf  = rf_model.predict(X_test)
    y_pred_xgb = xgb_model.predict(X_test)

    y_prob_lr  = lr_model.predict_proba(X_test_scaled)[:, 1]
    y_prob_rf  = rf_model.predict_proba(X_test)[:, 1]
    y_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]

    print("=" * 65)
    print(f"{'MODEL':<25} {'ACC':>7} {'F1':>7} "
          f"{'PREC':>7} {'REC':>7} {'AUC':>7}")
    print("=" * 65)

    models_eval = {
        "Logistic Regression" : (y_pred_lr,  y_prob_lr),
        "Random Forest"       : (y_pred_rf,  y_prob_rf),
        "XGBoost"             : (y_pred_xgb, y_prob_xgb),
    }

    all_metrics = {}
    for name, (y_pred, y_prob) in models_eval.items():
        acc  = accuracy_score(y_test,  y_pred)
        f1   = f1_score(y_test,        y_pred)
        prec = precision_score(y_test, y_pred)
        rec  = recall_score(y_test,    y_pred)
        auc  = roc_auc_score(y_test,   y_prob)

        all_metrics[name] = {
            "Accuracy"  : acc,  "F1"       : f1,
            "Precision" : prec, "Recall"   : rec,
            "ROC-AUC"   : auc,
        }
        print(f"{name:<25} {acc:>7.4f} {f1:>7.4f} "
              f"{prec:>7.4f} {rec:>7.4f} {auc:>7.4f}")

    print("=" * 65)

    preds  = (y_pred_lr, y_pred_rf, y_pred_xgb)
    probs  = (y_prob_lr, y_prob_rf, y_prob_xgb)

    return all_metrics, preds, probs


def plot_confusion_matrices(preds, y_test, output_dir: str):
    """Plot confusion matrices for all 3 models side by side."""
    y_pred_lr, y_pred_rf, y_pred_xgb = preds

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Confusion Matrices — All Models",
                 fontsize=14, fontweight="bold")

    model_preds = {
        "Logistic Regression" : y_pred_lr,
        "Random Forest"       : y_pred_rf,
        "XGBoost"             : y_pred_xgb,
    }

    for ax, (name, y_pred) in zip(axes, model_preds.items()):
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["Vacant","Occupied"],
                    yticklabels=["Vacant","Occupied"],
                    linewidths=1, cbar=False)
        ax.set_title(name, fontweight="bold")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")

        acc = accuracy_score(y_test, y_pred)
        ax.text(0.5, -0.12, f"Accuracy: {acc:.4f}",
                transform=ax.transAxes, ha="center",
                fontsize=11, color="#1565C0", fontweight="bold")

    plt.tight_layout()
    plt.savefig(f"{output_dir}07_confusion_matrices.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 07_confusion_matrices.png")


def plot_roc_pr_curves(probs, y_test, output_dir: str):
    """Plot ROC and Precision-Recall curves for all 3 models."""
    y_prob_lr, y_prob_rf, y_prob_xgb = probs

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("ROC & Precision-Recall Curves",
                 fontsize=14, fontweight="bold")

    colors = ["#1565C0", "#E53935", "#2E7D32"]
    models_prob = {
        "Logistic Regression" : y_prob_lr,
        "Random Forest"       : y_prob_rf,
        "XGBoost"             : y_prob_xgb,
    }

    for (name, y_prob), color in zip(models_prob.items(), colors):
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        auc = roc_auc_score(y_test, y_prob)
        axes[0].plot(fpr, tpr,
                     label=f"{name} (AUC={auc:.3f})",
                     color=color, linewidth=2)

        prec, rec, _ = precision_recall_curve(y_test, y_prob)
        ap = average_precision_score(y_test, y_prob)
        axes[1].plot(rec, prec,
                     label=f"{name} (AP={ap:.3f})",
                     color=color, linewidth=2)

    axes[0].plot([0,1],[0,1],"k--", linewidth=1, label="Random Guess")
    axes[0].set_title("ROC Curve")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].legend(loc="lower right")
    axes[0].set_xlim([0,1]); axes[0].set_ylim([0,1.02])

    baseline = y_test.mean()
    axes[1].axhline(baseline, color="k", linestyle="--",
                    linewidth=1, label=f"Baseline ({baseline:.2f})")
    axes[1].set_title("Precision-Recall Curve")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].legend(loc="upper right")
    axes[1].set_xlim([0,1]); axes[1].set_ylim([0,1.02])

    plt.tight_layout()
    plt.savefig(f"{output_dir}08_roc_pr_curves.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 08_roc_pr_curves.png")


def plot_feature_importance(rf_model, xgb_model,
                            feature_cols: list, output_dir: str):
    """Plot top 20 feature importance for RF and XGBoost side by side."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle("Feature Importance — Top 20 Features",
                 fontsize=14, fontweight="bold")

    for ax, (model, name) in zip(axes, [
        (rf_model,  "Random Forest"),
        (xgb_model, "XGBoost"),
    ]):
        importance = pd.Series(
            model.feature_importances_,
            index=feature_cols
        ).sort_values(ascending=True).tail(20)

        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(importance)))
        importance.plot(kind="barh", ax=ax,
                        color=colors, edgecolor="white")
        ax.set_title(name, fontweight="bold")
        ax.set_xlabel("Importance Score")
        ax.tick_params(axis="y", labelsize=8)

    plt.tight_layout()
    plt.savefig(f"{output_dir}09_feature_importance.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 09_feature_importance.png")


def save_metrics_csv(all_metrics: dict, output_dir: str):
    """Save model comparison metrics to CSV."""
    metrics_df = pd.DataFrame(all_metrics).T
    path = f"{output_dir}model_comparison.csv"
    metrics_df.to_csv(path)
    print(f"Metrics saved: {path}")
    return metrics_df


def run_evaluation(lr_model, rf_model, xgb_model,
                   X_test, X_test_scaled, y_test,
                   feature_cols: list, output_dir: str):
    """
    Full evaluation pipeline:
    metrics → confusion matrix → ROC/PR → feature importance → save CSV
    """
    print("\n" + "=" * 50)
    print("  MODEL EVALUATION")
    print("=" * 50)

    all_metrics, preds, probs = compute_metrics(
        lr_model, rf_model, xgb_model,
        X_test, X_test_scaled, y_test
    )
    plot_confusion_matrices(preds, y_test, output_dir)
    plot_roc_pr_curves(probs, y_test, output_dir)
    plot_feature_importance(rf_model, xgb_model,
                            feature_cols, output_dir)
    metrics_df = save_metrics_csv(all_metrics, output_dir)

    print("\nEvaluation complete!")
    print(f"   Best AUC: {max(m['ROC-AUC'] for m in all_metrics.values()):.4f}")

    return all_metrics, metrics_df
