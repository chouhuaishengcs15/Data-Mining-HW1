# P3｜Model & Evaluation

本資料夾包含 P3 負責的模型、Cross Validation、Feature Ablation、Model Choice、Final Test 與統計分析。

## 主要結論

- Final model：Elastic Net
- Feature set：Raw features + `QualityArea = OverallQual × GrLivArea`
- Target：`log1p(SalePrice)`，預測後以 `expm1` 還原美元
- Hyperparameters：`alpha=0.0031622776601683794`、`l1_ratio=0.1`
- Validation：P1 固定的 5-fold split；所有 learned preprocessing 只在各 training fold 內 fit
- Training CV MAE：13,366.06 ± 809.27 USD
- Final Test：MAE 14,422.74 USD、RMSE 22,340.04 USD、R² 0.9349
- 事前 MAE threshold：15,000 USD，Final Model 通過
- 相較 Random Forest：MAE 改善 1,961.11 USD；paired permutation `p=0.0170`

模型選擇同時考慮共線性、矩陣秩、稀疏度與跨折係數穩定性，performance 僅作為支持證據。完整理由見 [`report/P3_model_choice_and_results.md`](report/P3_model_choice_and_results.md)。

## 資料夾結構

```text
model/
├── README.md
├── notebooks/
│   ├── 03_model_evaluation.ipynb
│   ├── 04_final_evaluation.ipynb
│   ├── 05_feature_ablation.ipynb
│   └── 06_model_choice.ipynb
├── report/
│   └── P3_model_choice_and_results.md
└── results/
    ├── tables/
    │   ├── model_evaluation/
    │   ├── feature_ablation/
    │   ├── model_choice/
    │   └── final_test/
    └── figures/
        ├── model_evaluation/
        ├── feature_ablation/
        ├── model_choice/
        └── final_test/
```

## Notebook 用途與執行順序

1. `03_model_evaluation.ipynb`：Pipeline、baselines、OLS/Ridge/Lasso/Elastic Net、raw/log target、CV 與 tuning。
2. `05_feature_ablation.ipynb`：P2 H1–H3、Top-k 與 engineered feature sets。
3. `06_model_choice.ipynb`：整合共線性、稀疏度、係數穩定性與 CV 證據。
4. `04_final_evaluation.ipynb`：已依 freeze 設定執行唯一一次 Final Test，並產生差異檢定、係數分析與 large-error cases。

`04_final_evaluation.ipynb` 不應再次執行；`results/tables/final_test/FINAL_TEST_EVALUATED.json` 是一次性完成標記。

## 主要結果檔

- `results/tables/model_evaluation/cv_model_comparison.csv`：CV mean/std 與 baselines。
- `results/tables/model_evaluation/tuning_results.csv`：完整 hyperparameter search。
- `results/tables/feature_ablation/hypothesis_results.csv`：H1–H3 結果。
- `results/tables/feature_ablation/ablation_results.csv`：feature set × model 主比較。
- `results/tables/model_choice/model_choice_evidence.csv`：非 performance-only 的選模證據。
- `results/tables/final_test/freeze_settings.json`：Final Test 前固定的設定。
- `results/tables/final_test/final_test_results.csv`：Final Test 正式結果。
- `results/tables/final_test/model_significance.csv`：Elastic Net 與 Random Forest 的 paired test。
- `results/tables/final_test/coefficients_ci_pvalue_vif.csv`：Coefficient、95% CI、近似 p-value 與 VIF。
- `results/tables/final_test/large_error_cases.csv`：Final Test 最大誤差案例。

## GitHub 精簡原則

GitHub 只提交主比較表、完整 tuning 表、ablation 結論、model-choice evidence 與 Final Test 正式結果。逐折分數、OOF predictions、每折係數、特徵排名、warnings 與 verification 等中間產物不提交；需要稽核時可由 03、05 重新產生。Final Test 不可重跑，正式輸出以 `results/tables/final_test/` 與 04 既有 outputs 為準。

