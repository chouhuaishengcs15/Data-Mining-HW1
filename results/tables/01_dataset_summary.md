# Table 1：資料摘要

報告位置：3. Task Definition & Data。

## 資料設定

| 項目 | 內容 |
|---|---|
| Dataset | House Prices - Advanced Regression Techniques（Ames Housing） |
| 來源 | Kaggle；Ames, Iowa，2006–2010 年成交資料 |
| 原始資料 | 1,460 筆、81 欄（含 Id 與 SalePrice） |
| 預測目標 | 成交前估計 SalePrice，單位 USD |
| 初始切分 | Training 1,168 筆；Test 292 筆 |
| 正式 Training | 刪除 Id 524、1299 後為 1,166 筆 |
| Validation | 固定 5-fold，random seed=42；各折 233／234／234／232／233 筆 |
| 最終特徵 | Raw + QualityArea；完整 training 編碼後 214 欄 |

## 描述統計

以下是 P1 notebook 已保存的 1,168 筆初始 training 統計，尚未刪除兩筆異常值，不含 test。

| Feature | 單位 | Mean ± SD | Min | Median | Max |
|---|---|---|---|---|---|
| SalePrice | USD | 181,441.5 ± 77,263.6 | 34,900.0 | 165,000.0 | 745,000.0 |
| OverallQual | 1–10 分 | 6.1 ± 1.4 | 1.0 | 6.0 | 10.0 |
| GrLivArea | sq ft | 1,527.4 ± 524.4 | 334.0 | 1,473.0 | 5,642.0 |
| LotArea | sq ft | 10,689.6 ± 10,759.4 | 1,300.0 | 9,600.0 | 215,245.0 |
| TotalBsmtSF | sq ft | 1,061.8 ± 440.7 | 0.0 | 997.5 | 6,110.0 |

- 成交年月、交易類型與交易條件不入模；正式 CV 的補值、轉換與編碼在每個 training fold 內 fit。
- 214 欄是完整 training 的編碼結果；各 CV fold 的類別數不同，欄數不一定相同。

來源：[P1 README](../../data/README.md)、[P1 notebook 已保存的統計](../../data/P1_Preprocessing_v4.ipynb)。
