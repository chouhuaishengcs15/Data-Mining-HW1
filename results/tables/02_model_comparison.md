# Table 2：模型比較

報告位置：7.1 Main Results。CV 為相同五折的 mean ± SD，Test 共 292 筆。MAE／RMSE 越低越好，R² 越高越好。

| Model | CV MAE ± SD (USD) | CV RMSE ± SD (USD) | Test MAE (USD) | Test RMSE (USD) | Test R² |
|---|---|---|---|---|---|
| Mean | 56,391.60 ± 1,243.71 | 77,190.34 ± 4,334.06 | 62,580.40 | 87,619.50 | -0.0009 |
| Single-feature OLS | 37,159.83 ± 2,294.91 | 53,091.64 ± 2,645.27 | 38,473.84 | 57,594.46 | 0.5675 |
| Random Forest | 16,554.34 ± 958.10 | 26,107.29 ± 2,431.40 | 16,383.85 | 27,017.93 | 0.9048 |
| Elastic Net + QualityArea | 13,366.06 ± 809.27 | 19,925.10 ± 2,274.15 | 14,422.74 | 22,340.04 | 0.9349 |

- Mean 使用 training mean；單特徵 OLS 使用 GrLivArea；RF 使用 Raw features 與原始 SalePrice。
- Final EN 使用 Raw + QualityArea、log1p target，alpha=0.0031622776601683794、l1_ratio=0.1；預測後還原美元。
- EN−RF 的 Test MAE 差為 -1,961.11 USD；paired-bootstrap 95% CI=[-3,846.87, -399.02] USD；paired permutation p=0.0170。結果支持 EN 在這份 test set 的誤差較低。
- EN 通過專案設定的 MAE ≤15,000 USD。門檻由 CV mean + 2 SD 向上取整，不是正式 95% CI，也不代表每一筆房屋誤差都小於 15,000 USD。
- EN 的選擇也考量共線性、係數收縮與穩定性；同 H1 的 Lasso CV MAE=13,360.81 USD，因此不宣稱 EN 優於所有候選模型。CV 同時用於調參，並非 nested CV。

來源：[CV](../../model/results/tables/model_evaluation/cv_model_comparison.csv)、[最終特徵組 CV](../../model/results/tables/feature_ablation/ablation_results.csv)、[Final Test](../../model/results/tables/final_test/final_test_results.csv)、[配對檢定](../../model/results/tables/final_test/model_significance.csv)、[選模證據](../../model/results/tables/model_choice/model_choice_evidence.csv)。
