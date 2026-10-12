# P2：EDA & Feature Engineering

依分工表回報 P2 的六項交付。分析僅使用 P1 [train_readable.csv](../data/outputs/p1/train_readable.csv) 的 **1,166 筆 Training Data**，未使用 Test Set。Target 為 **log 房屋總價**（沿用 P1 `log1p(SalePrice)`）。

## 1. EDA Figures

| 圖表 | 主要觀察 |
|---|---|
| [MI Top-15 Ranking](figures/01_feature_ranking.png) | OverallQual、Neighborhood、GrLivArea 位於 MI 排名前列，品質、區位與面積值得關注。 |
| [Feature–Feature Correlation](figures/02_feature_correlation.png) | 32 個 numeric features 中，有 3 組配對達到探索門檻 `abs(r) > 0.8`。 |
| [QualityArea Scatter Plot](figures/03_quality_area.png) | Pearson r = 0.836，高於單獨品質或居住面積，據此提出 H1。 |
| [LotArea／LogLotArea 對照](figures/04_log_lot_area.png) | Pearson r 從 0.261 提高至 0.415，據此提出 H2。 |
| [TotalSF Scatter Plot](figures/05_total_sf.png) | Pearson r = 0.822，據此提出 H3。 |

[HouseAge](figures/supplementary/house_age.png) 為補充探索，Pearson r = −0.578；因公式使用 P1 判定預測時不可用的 YrSold，**不納入正式 Feature Sets**。

## 2. Correlation / Redundancy Analysis

[完整 Feature Ranking](tables/feature_ranking.csv) 包含 Pearson、Spearman 與 MI。Pearson／Spearman 計算 32 個 numeric features，依絕對值排名；MI 計算全部 73 個原始可用 features。文字類別的 Pearson／Spearman 留空，不代表 0。

| 高相關配對 | Pearson r |
|---|---:|
| GarageCars / GarageArea | 0.889 |
| GrLivArea / TotRmsAbvGrd | 0.826 |
| TotalBsmtSF / 1stFlrSF | 0.808 |

這些配對可能提供重複資訊，但高相關不代表必須刪除；保留、替換或合併的效果仍需 Ablation 驗證。完整數值見 [Correlation Matrix](tables/feature_feature_pearson_matrix.csv) 與 [高相關配對表](tables/high_correlation_feature_pairs.csv)。

## 3. Hypothesis List

**H1–H3 均為 Proposed / Not Validated。**

| ID | Hypothesis | 驗證方式 |
|---|---|---|
| H1 | 品質 × 面積的 Interaction 可改善線性模型預測。 | Raw vs Raw + QualityArea，保留 main effects。 |
| H2 | 土地面積的 Log Transformation 可改善線性模型預測。 | Raw vs 以 LogLotArea 替換 LotArea。 |
| H3 | 整合面積可減少特徵數，並維持相近準確率。 | Raw vs 以 TotalSF 替換三個面積分項。 |

Correlation 提高不等於模型一定更準。詳細驗證計畫見 [hypothesis_table.csv](tables/hypothesis_table.csv)。

## 4. Feature Definition Table

| Feature | Formula | Unit | 設計理由 |
|---|---|---|---|
| QualityArea | OverallQual × GrLivArea | rating point × sq ft | 探索品質與面積的 Interaction。 |
| LogLotArea | log1p(LotArea) | log-transformed sq-ft value | 探索土地面積的非線性關係。 |
| TotalSF | TotalBsmtSF + 1stFlrSF + 2ndFlrSF | sq ft | 整合空間規模，測試能否取代分項。 |
| HouseAge | YrSold − YearBuilt | years | 探索屋齡；因 YrSold 可用性限制，不入模。 |

完整定義與限制見 [feature_definition.csv](tables/feature_definition.csv)；數值見 [候選 Correlations](tables/candidate_feature_correlations.csv) 與 [候選／原始特徵對照](tables/candidate_vs_original.csv)。

## 5. Feature Engineering Code 與 Feature Sets

[run_eda.py](codes/run_eda.py) 包含候選特徵計算，統一產生 6 張圖及 8 份 CSV。`hypothesis_table.csv` 為人工整理，程式不覆寫。模型用的 fold-local transformation pipeline 尚待與 P3 整合。

| Feature Set | 定義 |
|---|---|
| A_Raw | 73 個可用原始 features。 |
| B_MI20 | 每折 Training Data 內的 MI Top-20。 |
| B_Pearson20 | 補充比較：每折 numeric features 的 absolute Pearson Top-20。 |
| C_Engineered | **同折 B_MI20 + QualityArea + LogLotArea + TotalSF**，預期 23 個 encoding 前特徵。 |

C 的 Control 為 B_MI20；H1–H3 的 Control 仍為 A_Raw。Top-k 必須在每折 training 內重算，不能直接使用全 training 的 EDA 排名。C 固定沿用同折 B_MI20 的名單再新增三項；若包含總面積及全部分項，需處理 exact linear dependence。詳細保留／移除規則見 [Feature Sets 摘要](tables/feature_sets_summary.csv) 與 [逐欄定義](tables/feature_sets.csv)。

## 6. Feature Ablation Results

**Pending，尚無正式 CV RMSE 結果。** 後續沿用 P1 的 5-fold CV，比較上述 Feature Sets 與 H1–H3。執行前需與 P3 固定主要指標（RMSE_log 或 RMSE_USD）、共同模型／preprocessing，以及 H3「誤差相近」的 tolerance。

限制：P1 readable 已使用整份 training 補值；fold-local selection 不能消除此項既有資訊混入，正式結果需揭露。

## 執行方式

從 repository 根目錄執行（已驗證環境：Python 3.9）：

```bash
python -m pip install "numpy==1.26.4" "pandas==2.3.3" "scipy==1.13.1" "scikit-learn==1.6.1" "matplotlib==3.9.4"
python EDA/codes/run_eda.py
```

輸出位於 `figures/` 與 `tables/`；程式不執行模型訓練或 CV。若系統找不到中文字型，設定 `EDA_FONT` 為中文字型檔路徑。
