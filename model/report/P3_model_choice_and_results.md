# P3 模型選擇與實驗結果

模型候選、validation protocol、hyperparameter tuning、baselines、model comparison、feature ablation，以及模型選擇理由。

## 最終模型與固定設定

推薦使用 **Elastic Net + QualityArea interaction + log1p target**：

- `alpha = 0.0031622776601683794`
- `l1_ratio = 0.1`
- QualityArea = OverallQual × GrLivArea，並保留兩個 main effects
- 預測後以 `expm1` 還原美元，再計算 MAE、RMSE、R²

這個選擇不是因為它在單一指標排名第一，而是綜合資料結構、模型行為與 validation 結果。

## 為什麼選 Elastic Net

### 1. 資料有明確共線性，OLS 不適合作為最終模型

完成 one-hot 後，每折約有 207–213 個模型輸入；含截距的設計矩陣平均缺少 22.6 個秩。面積、房間、地下室與車庫變數也存在高度相關。OLS 因此只能作無正則化參考；其係數解不唯一，數值預測曾出現不穩定，不能作主要模型或逐係數獨立解釋。

### 2. Ridge 符合共線性需求，但不做特徵縮減

Ridge 的 L2 懲罰會同時縮小相關特徵、保留全部欄位，跨折係數結構穩定；但平均保留 209.8 個非零係數，沒有處理大量 one-hot 與弱特徵造成的模型複雜度。其 H1 組 MAE 為 13,450.27 ± 805.40 USD。

### 3. Lasso 最低 MAE，但單靠最低分數不足以選它

Lasso 的 H1 組 MAE 最低，為 13,360.81 ± 763.16 USD；但只比 Elastic Net 少 5.25 USD（0.039%），遠小於約 763–809 USD 的折間波動。Lasso 在高度相關的特徵群中可能任意保留其中一個，使選擇與係數對抽樣較敏感。

### 4. Elastic Net 同時符合相關特徵與弱特徵的資料特性

Elastic Net 結合 L1 與 L2。CV 選出的 `l1_ratio=0.1` 表示以 L2 為主，保留相關特徵群的資訊，同時用少量 L1 移除部分弱特徵。它平均保留 113.4/209.8 個非零係數；跨折標準化係數的平均 cosine similarity 為 0.960，略高於 Lasso 的 0.954。

Elastic Net 的 MAE為 13,366.06 ± 809.27 USD，與 Lasso 實質相同；RMSE為 19,925.10 USD，略低於 Lasso 的 19,945.95 USD；R²也略高。因此它在不犧牲實際預測表現的情況下，更符合本資料的共線性與高維稀疏結構。

## 模型比較證據

| 模型 | CV MAE USD ± SD | CV RMSE USD ± SD | R² | 平均非零係數 | 跨折係數 cosine |
|---|---:|---:|---:|---:|---:|
| Ridge | 13,450.27 ± 805.40 | 20,177.30 ± 2,298.49 | 0.9317 | 209.8 | 0.961 |
| Lasso | 13,360.81 ± 763.16 | 19,945.95 ± 2,265.00 | 0.9332 | 107.8 | 0.954 |
| **Elastic Net** | **13,366.06 ± 809.27** | **19,925.10 ± 2,274.15** | **0.9334** | **113.4** | **0.960** |

這些數字來自相同五折、相同 H1 feature set 與相同 target。SD 是折間標準差，不是信賴區間。模型、特徵與參數在查看 Final Test 前已固定，Final Test 不用來改選模型。

## 已完成的內容

- 三層 baseline：training mean、GrLivArea 單特徵 OLS、Random Forest。
- 線性候選：OLS、Ridge、Lasso、Elastic Net，以及 QualityArea interaction model。
- 原始與 log1p target 比較，所有誤差統一以美元計算。
- 固定五折 CV、相同 folds、fold-local preprocessing、hyperparameter search。
- Raw、MI Top-15/20、Pearson Top-20、Engineered 與 H1–H3 ablation。
- 每折結果、OOF 預測、調參表、特徵入選、編碼維度、切片分析與警告檢查。
- 完整 training 重訓、一次性 Final Test、模型差異檢定、係數 CI/p/VIF 與最大誤差案例。

## Final Test 結果

在查看 Final Test 前，將可接受 MAE 門檻固定為 15,000 USD。這個門檻由 training CV mean + 2 SD = 14,984.60 USD 向上取整而來。之後使用完整 training data 重訓，並對封存的 292 筆 Final Test 評估一次。

| 模型 | Test MAE USD | Test RMSE USD | Test R² | 通過 15,000 MAE 門檻 |
|---|---:|---:|---:|---:|
| Mean | 62,580.40 | 87,619.50 | -0.0009 | 否 |
| Single-feature OLS | 38,473.84 | 57,594.46 | 0.5675 | 否 |
| Random Forest | 16,383.85 | 27,017.93 | 0.9048 | 否 |
| **Elastic Net** | **14,422.74** | **22,340.04** | **0.9349** | **是** |

Elastic Net 相較 Random Forest 的每筆絕對誤差平均少 1,961.11 USD；paired bootstrap 的 95% CI 為 399.02 至 3,846.87 USD 的改善，paired permutation p=0.0170。這支持兩者的差距不是只由少數測試案例造成。

最大三筆絕對誤差為 Id 899（137,718.68 USD）、775（99,159.63 USD）與 1047（97,064.61 USD），三筆皆為高品質且價格較高的住宅。切片結果也顯示高品質組 MAE 為 27,635.58 USD，高於其他品質組，表示模型的主要剩餘風險集中在高價／高品質住宅。

係數表包含 214 個 encoded predictors 的係數、bootstrap 95% CI、近似 p-value 與 VIF。29 個係數的未校正 95% CI 不含 0；大量 VIF 為無限大，反映完整 one-hot levels 與相關房屋特徵造成的共線性。這些統計量用於模型診斷，不作因果解釋；Elastic Net 係數的 p-value 為固定 preprocessing、features 與 hyperparameters 下的 bootstrap 近似值。
