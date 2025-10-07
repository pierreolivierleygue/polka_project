import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut

from data_prep import features, lite_features, TOP_N_GC


drop_cols = {
    "race_id","race_name","gc_winner_id","kom_winner_id","id_rider",
    "final_gc_position"
}

X_cols_full = [c for c in features.columns if c not in drop_cols.union({"label_gc", "year", "nb_stages"})]
X_cols_lite = [c for c in lite_features.columns if c not in drop_cols.union({"label_gc", "year"})]

def run_logo_cv(df, X_cols, label="label_gc"):
    df = df.sort_values("year").reset_index(drop=True)
    X = df[X_cols].fillna(0)
    y = df[label]
    groups = df["year"]

    logo = LeaveOneGroupOut()
    aucs, reports = [], []

    fold = 1
    for train_idx, test_idx in logo.split(X, y, groups=groups):
        Xtr, Xte = X.iloc[train_idx], X.iloc[test_idx]
        ytr, yte = y.iloc[train_idx], y.iloc[test_idx]

        model = CatBoostClassifier(
            iterations=300,
            learning_rate=0.05,
            depth=3,
            loss_function="Logloss",
            eval_metric="AUC",
            verbose=False,
            random_seed=42
        )
        model.fit(Xtr, ytr, eval_set=(Xte, yte))

        p = model.predict_proba(Xte)[:,1]
        pred = (p >= 0.5).astype(int)
        auc = roc_auc_score(yte, p)

        aucs.append(auc)
        reports.append(classification_report(yte, pred, digits=3, output_dict=True))

        print(f"\n=== Fold {fold} (Year {df.loc[test_idx,'year'].unique()[0]}) ===")
        print(f"AUC: {auc:.3f}")
        print(classification_report(yte, pred, digits=3))
        fold += 1

    print("Mean AUC:", round(pd.Series(aucs).mean(), 3), "| Std:", round(pd.Series(aucs).std(), 3))
    
    imp = pd.DataFrame({"feature": X_cols, "importance": model.get_feature_importance()}) 
    imp = imp.sort_values("importance", ascending=False) 
    print("\nTop 12 feature importances:\n", imp.head(12).to_string(index=False))
    return aucs, reports


print("\n>>> FULL feature set")
aucs_full, reports_full = run_logo_cv(features, X_cols_full)

"""print("\n>>> LITE feature set")
aucs_lite, reports_lite = run_logo_cv(lite_features, X_cols_lite)"""