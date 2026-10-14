# I2：Results & Figures

依專案原有的 results 目錄，整理 I2 負責的 Results Master Sheet、報告圖表與內容對照。數字沿用 P1、P2、P3 已完成的結果，沒有重新跑 EDA 或模型。

## 1. Results Master Sheet

[Results_Master.xlsx](Results_Master.xlsx) 整合資料設定、前處理、EDA、Feature Engineering、模型比較、Feature Ablation、統計與錯誤分析，讓 paper 和 slides 使用同一組數字。

- Final model：Elastic Net + Raw features + QualityArea
- Target：`log1p(SalePrice)`，預測後以 `expm1` 還原美元
- Hyperparameters：`alpha=0.0031622776601683794`、`l1_ratio=0.1`
- CV MAE：13,366.06 ± 809.27 USD
- Final Test：MAE 14,422.74 USD、RMSE 22,340.04 USD、R² 0.9349

## 2. Figures

考量正文最多六頁，我選了兩張圖：EDA 的 target–feature 圖，以及 Method 的 Pipeline。模型比較、消融與錯誤分析則整理成表格，避免重複呈現。

| 圖片 | 報告位置 | 要說明的重點 |
|---|---|---|
| [Figure 1：QualityArea](figures/Figure_1_EDA_QualityArea.png) | 4. Exploratory Feature Analysis | 品質與面積的交互作用和房價有明顯關聯，作為 H1 的動機 |
| [Figure 2：Pipeline](figures/Figure_2_Method_Pipeline_Compact.png) | 5.1 Method | 從資料切分、前處理、特徵工程到模型訓練與評估的流程 |

### Figure 1：QualityArea

- 沿用 P2 原圖，`QualityArea = OverallQual × GrLivArea`。
- 僅使用 1,166 筆 training data；與 `log1p(SalePrice)` 的 Pearson r=0.836、Spearman rho=0.850。
- 這張圖用來提出「加入品質與面積的交互作用是否改善預測」，實際效果由 Table 3 的 ablation 說明，不把相關性當成因果。
- 建議放單欄。P2 圖中的資料是 training-only EDA view，與正式 CV 每折內 fit 的前處理分開。

Caption：Training-only association between QualityArea (OverallQual × GrLivArea; rating point × sq ft) and log1p(SalePrice), with SalePrice in USD (n=1,166). Pearson r=0.836 and Spearman rho=0.850 motivate H1; predictive improvement is evaluated separately by CV ablation.

### Figure 2：Pipeline

- 依 P1、P2、P3 的既有流程重新編排，沒有新增實驗。
- 1,460 筆資料切成 training 1,168 筆、test 292 筆；只移除 training 的兩筆異常值，留下 1,166 筆。
- 主圖依序呈現 Raw data、Preprocessing、Feature engineering、Linear model、Prediction & evaluation；每一格標出 Input、Process、Output。
- 前處理輸出未縮放的欄位；加入 QualityArea 後再做數值轉換、縮放與類別編碼，輸出模型使用的數值矩陣。QualityArea 表示品質與面積的交互作用，對應 EDA 的 H1，並保留兩個原始欄位。
- 模型先預測 log1p 價格，再用 expm1 轉回美元。下方另列五折 CV 與 test 使用規則：每折只在 training fit；固定設定後重訓完整 pipeline，test 不參與選模。
- 建議跨雙欄；Experimental Setup 可引用同一張圖，不需重放。

Caption：Five-stage pipeline from raw housing records to predicted sale prices, showing each stage's input, processing and output. QualityArea retains its main effects and is added before numeric transformation and encoding. Elastic Net predicts log1p prices, which are restored to USD using expm1. Learned steps are fitted within each training fold only. After choices are frozen, the full pipeline is refitted on 1,166 training rows and applied to 292 held-out test rows without refitting.

## 3. Tables

| 表格 | 報告位置 | 要說明的重點 |
|---|---|---|
| [Table 1：資料摘要](tables/01_dataset_summary.md) | 3. Task Definition & Data | 資料規模、切分方式與主要欄位的描述統計 |
| [Table 2：模型比較](tables/02_model_comparison.md) | 7.1 Main Results | Mean、單特徵 OLS、Random Forest 與 Final EN 的 CV／Test 表現 |
| [Table 3：Feature Ablation](tables/03_feature_ablation.md) | 7.2 Feature Ablation | Raw、MI20、Raw + QualityArea 的比較，以及 H1–H3 的結果 |
| [Table 4：係數分析](tables/04_coefficients.md) | 8.1 Coefficients & Statistical Significance | 完整 214 欄係數、95% CI、p-value 與 VIF，解釋特徵與共線性 |
| [Table 5：錯誤案例](tables/05_error_cases.md) | 8.2 Error Analysis | 三筆最大誤差的實際價格、預測價格、房屋背景與共同模式 |

- Table 1 的描述統計沿用 P1 刪異常值前的 1,168 筆；正式 EDA／建模為 1,166 筆，兩者分開標示。
- Table 2 中，EN 相較 RF 的 MAE 降低 1,961.11 USD，paired permutation p=0.0170。
- Table 3 將最終 EN 的特徵組比較與固定 Ridge 的 H1–H3 分開。QualityArea 改善最明顯；最終特徵組對應 `H1_QualityArea`，不是 repo 的 `C_Engineered`。
- Table 4 保留完整數值，不只挑顯著特徵。係數是 log target 尺度，Holm 校正後沒有 p<.05 的項目，不解讀成獨立因果效果。
- Table 5 的三筆案例都是高品質住宅且被低估，呼應模型在高品質、大面積房屋上的誤差較大；原因解釋以可能方向呈現。

## 4. 資料夾結構與來源

```text
results/
├── README.md
├── Results_Master.xlsx
├── figures/                 兩張報告用圖
├── tables/                   五份表格
└── GitHub上傳位置.txt         各檔案的上傳位置
```

圖 1 來自 [P2 EDA](../EDA/README.md)；資料與統計來自 [P1](../data/README.md)；模型結果來自 [P3](../model/README.md)。各表附原始檔連結，不重複上傳來源資料。

I2 的工作是整合與核對結果、統一數字及命名、選擇主文圖表、整理說明並編排 Pipeline。過程使用 ChatGPT／Codex 協助整理檔案與文字，沒有產生新的實驗數據。
