import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit

from data_prep import features, TOP_N_GC
START_TEST_YEAR = 2018    

# --- 4) TRAIN / EVAL (time-based) ---
# Keep only numeric features for route-only modeling
drop_cols = {
    "race_id","race_name","gc_winner_id","kom_winner_id","id_rider",
    "final_gc_position"
}
X_cols = [c for c in features.columns if c not in drop_cols.union({"label_gc"})]

# Simple time split
train_mask = features["year"] < START_TEST_YEAR
X_train, y_train = features.loc[train_mask, X_cols], features.loc[train_mask, "label_gc"]
X_test,  y_test  = features.loc[~train_mask, X_cols], features.loc[~train_mask, "label_gc"]

X_train = X_train.fillna(0)
X_test  = X_test.fillna(0)

# Train CatBoost (route-only)
model = CatBoostClassifier(
    iterations=1000,
    learning_rate=0.03,
    depth=6,
    loss_function="Logloss",
    eval_metric="AUC",
    random_seed=42,
    verbose=100
)
model.fit(X_train, y_train, eval_set=(X_test, y_test))

# Evaluate
proba = model.predict_proba(X_test)[:,1]
pred  = (proba >= 0.5).astype(int)

print("\n=== Test Metrics (>= {} as GC) ===".format(TOP_N_GC))
print(classification_report(y_test, pred, digits=3))
try:
    print("Test ROC-AUC:", round(roc_auc_score(y_test, proba), 3))
except Exception:
    pass

# Feature importance
imp = pd.DataFrame({"feature": X_cols, "importance": model.get_feature_importance()})
imp = imp.sort_values("importance", ascending=False)
print("\nTop 20 feature importances:\n", imp.head(20).to_string(index=False))

# --- 5) (Optional) TimeSeriesSplit CV ---
# Gives you robustness across years without leaking future data
print("\n=== TimeSeriesSplit CV (optional quick view) ===")
tscv = TimeSeriesSplit(n_splits=3)
F = features.sort_values("year").reset_index(drop=True)
Xs = F[X_cols].fillna(0).values
y = F["label_gc"].values

fold = 1
for train_idx, test_idx in tscv.split(Xs):
    Xtr, Xte = Xs[train_idx], Xs[test_idx]
    ytr, yte = y[train_idx], y[test_idx]
    m = CatBoostClassifier(iterations=600, learning_rate=0.05, depth=6, loss_function="Logloss", eval_metric="AUC", verbose=False, random_seed=42)
    m.fit(Xtr, ytr, eval_set=(Xte, yte))
    p = m.predict_proba(Xte)[:,1]
    auc = roc_auc_score(yte, p)
    print(f"Fold {fold} AUC: {auc:.3f}")
    fold += 1

print("\nDone. This pipeline uses only route/climb info and avoids data leakage.")
