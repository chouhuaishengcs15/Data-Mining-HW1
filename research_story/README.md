# I1：Research Story

本資料夾整理專題的研究故事：Target User、Research Question、Decision Threshold、Contributions，以及從 EDA 假設到最終結果的對應關係。

所有數字取自 P1、P2、P3 已提交的結果檔，括號內註明出處。若與 Results Master Sheet 有出入，以 Master Sheet 為準並回報 I1。

主要出處：

- [`model/results/tables/final_test/final_test_results.csv`](../model/results/tables/final_test/final_test_results.csv)
- [`model/results/tables/final_test/freeze_settings.json`](../model/results/tables/final_test/freeze_settings.json)
- [`model/results/tables/final_test/model_significance.csv`](../model/results/tables/final_test/model_significance.csv)
- [`model/results/tables/feature_ablation/hypothesis_results.csv`](../model/results/tables/feature_ablation/hypothesis_results.csv)
- [`model/results/tables/final_test/coefficients_ci_pvalue_vif.csv`](../model/results/tables/final_test/coefficients_ci_pvalue_vif.csv)
- [`model/results/tables/final_test/slice_metrics.csv`](../model/results/tables/final_test/slice_metrics.csv)

---

## 1. Target User / Decision

| 項目 | 內容 |
|---|---|
| Target User | 主要：準備開價的賣方與房仲；次要：評估開價是否合理的買方 |
| 預測時間點 | 物件準備上架、尚未成交；只使用房屋本身條件 |
| 不使用的資訊 | 成交年月、交易類型、交易條件；也因此不使用需以成交年份（YrSold）計算的屋齡 |
| 支援的 Decision | 賣方／房仲：設定開價的參考依據；買方：判斷開價是否偏離模型估價、是否需要議價或進一步查證 |
| 預測輸出 | 成交價 SalePrice，單位 USD |

---

## 2. Research Question

**主 RQ**

> 在成交前、只使用房屋本身條件的情況下，正則化線性迴歸模型能否將 Ames 住宅成交價的預測誤差控制在事先設定的門檻（MAE ≤ 15,000 USD）內，且表現不輸非線性的 Random Forest？

**子問題**

| 子 RQ | 結果 | 出處 |
|---|---|---|
| RQ1：準確度與 baseline 比較 | Elastic Net Test MAE 14,423 USD，通過 15,000 USD 門檻；Mean 62,580、Single-feature OLS 38,474、Random Forest 16,384。相較 Random Forest 每筆平均少 1,961 USD（p = 0.017） | `final_test_results.csv`、`model_significance.csv` |
| RQ2：特徵工程是否有幫助 | H1（QualityArea）改善最明顯：RMSE 降低 5.7%–6.8%，5 份訓練資料全部改善；H2、H3 僅約 1% 改善；只取 Top-20 特徵反而變差 | `hypothesis_results.csv` |
| RQ3：哪些房屋條件與價格關聯最大 | 標準化係數較大者：QualityArea、GrLivArea、YearBuilt、OverallCond、LotArea、OverallQual、TotalBsmtSF，即品質、面積與建造年份 | `coefficients_ci_pvalue_vif.csv` |

---

## 3. Decision Threshold

**本研究以 Final Test MAE ≤ 15,000 USD 作為模型可用門檻。** 此門檻在執行 Final Test 前已固定（`freeze_settings.json` 中 `decision_MAE_USD = 15000`），之後未再修改。

### 選擇 15,000 USD 的理由

1. **由 Training CV 推導，不依賴 Test Set。**
   最終模型在 5-fold CV（訓練資料分成 5 份輪流驗證）的 MAE 為 13,366 ± 809 USD。取 mean + 2 SD = 14,984.60 USD，向上取整為 15,000 USD。5 份訓練資料之間的誤差波動反映模型在不同資料上的正常變化範圍；若 Final Test MAE 超過 mean + 2 SD，表示模型在新資料上的表現明顯差於訓練階段的預期，可能有 overfitting 或資料分布不一致的問題。因此，這個門檻同時檢驗「準確度」與「泛化穩定性」。

2. **對使用者有實際意義。**
   15,000 USD 約為 Training Data 房價中位數 165,000 USD 的 9.1%、平均房價 181,457 USD 的 8.3%，也就是平均誤差控制在房價的一成以內。對於準備開價的賣方、房仲或評估開價的買方而言，這個誤差範圍足以作為初步估價與議價的參考；但它不能取代正式鑑價。

3. **門檻有鑑別力，不是輕易就能通過。**
   在相同的 CV 設定下，各 baseline 的 MAE 為：Mean 56,392 USD、Single-feature OLS 37,160 USD、Random Forest 16,554 USD，三者都高於 15,000 USD。也就是說，只有表現優於強 nonlinear baseline 的模型才可能通過，門檻不會因為過於寬鬆而失去意義。

4. **單位與 Target 一致，容易溝通。**
   門檻以美元表示，與使用者實際面對的價格單位相同。模型雖以 log1p(SalePrice) 訓練，但預測值皆以 expm1 還原為美元後才計算 MAE，因此門檻可直接解讀為「平均每筆估價誤差不超過 15,000 美元」。

### 結果

| 模型 | Test MAE (USD) | 是否通過 15,000 USD |
|---|---:|---|
| Mean | 62,580 | 否 |
| Single-feature OLS | 38,474 | 否 |
| Random Forest | 16,384 | 否 |
| Elastic Net | 14,423 | 是 |

### 使用限制

MAE 是平均值，個別房屋的誤差可能遠大於 15,000 USD。Final Test 中最大誤差為 137,719 USD（Id 899）；整體品質 ≥ 8 的房屋 MAE 為 27,636 USD（n = 45），大面積房屋 MAE 為 23,372 USD（n = 84）。因此，對高品質或大坪數住宅，模型估價應更保守地使用。

---

## 4. Contributions

1. **無 data leakage 的成交前估價設定。** 明確排除成交後才能取得的資訊（成交年月、交易類型與交易條件，以及依賴成交年份的屋齡），使模型只使用實際估價時間點可取得的房屋條件。

2. **以 Ablation 驗證 EDA 提出的特徵假設。** 品質 × 面積交互作用（QualityArea）使 Ridge 的 5-fold CV RMSE 由 21,400 USD 降至 20,177 USD（−5.7%，5 份訓練資料皆改善）；log 土地面積與合併總面積僅帶來約 1% 的改善；只取 Top-20 相關特徵則明顯變差（RMSE 25,352 USD）。

3. **可解釋且優於 nonlinear baseline 的線性模型。** Elastic Net 在 292 筆封存測試資料上 MAE 為 14,423 USD（R² = 0.935），通過事先設定的 15,000 USD 門檻，且比 Random Forest 每筆平均少 1,961 USD（95% CI：399–3,847 USD，paired permutation p = 0.017）。

---

## 5. Storyline 對照表

下表連結 EDA 假設、設計的特徵、驗證實驗與結論。實驗模型為 Ridge（固定 alpha = 10），以 5-fold CV RMSE（USD）比較。

5-fold CV 的做法：P1 將 1,166 筆訓練資料固定分成 5 份（233 / 234 / 234 / 232 / 233 筆）。每次用其中 4 份訓練模型、剩下 1 份計算誤差，輪流 5 次，讓每一份都當過一次驗證資料。表中「5 份訓練資料皆改善」表示這 5 次驗證中，加入新特徵後的 RMSE 每一次都比原本低，代表改善是穩定的，不是只在某一份資料上剛好變好。

| 假設 | Feature | 比較 | 結果 | 結論 |
|---|---|---|---|---|
| H1：品質 × 面積交互作用可改善預測 | QualityArea = OverallQual × GrLivArea | A_Raw vs A_Raw + QualityArea | RMSE 21,400 → 20,177（−5.7%），5 份訓練資料皆改善；MAE −368 | 支持；成為最終模型的特徵 |
| H2：土地面積取 log 可改善預測 | LogLotArea = log1p(LotArea) | 原始 LotArea vs LogLotArea | RMSE −1.1%，5 份訓練資料中 4 份改善；但與 P1 已做的 Box-Cox 版本相比幾乎沒有差別（−1.6） | 支持非線性轉換有幫助，但 P1 的 Box-Cox 已涵蓋此效果，最終未加入 |
| H3：合併總面積可減少特徵並維持準確率 | TotalSF = TotalBsmtSF + 1stFlrSF + 2ndFlrSF | A_Raw vs 以 TotalSF 取代三個面積分項 | 維度減少，RMSE −1.1%（在 2% tolerance 內）；MAE 幾乎不變 | 支持；但改善幅度小，最終未採用 |
| Feature set 比較 | C_Engineered = B_MI20 + 三個新特徵 | C vs B_MI20；C vs A_Raw | 比 B_MI20 好 11%，但比 A_Raw 差 5% | Top-k 篩選丟失過多資訊；最終採用 A_Raw + QualityArea |

最終模型：Elastic Net（alpha = 0.00316、l1_ratio = 0.1），特徵為 73 個原始特徵 + QualityArea（one-hot 後約 214 個輸入欄位），Target 為 log1p(SalePrice)。

---

## 6. Claims 與證據

供 Paper 與 Slides 撰寫時對照。每一個結論性敘述都應能對應到下表的證據。

| 可以寫的 claim | 證據 |
|---|---|
| Elastic Net 通過事先設定的 15,000 USD 門檻 | Test MAE 14,423 USD |
| 線性模型在本研究中優於 Random Forest | MAE 差 −1,961 USD，95% CI 不含 0，p = 0.017 |
| QualityArea 改善預測 | RMSE −5.7%，5 份訓練資料皆改善 |
| 品質、面積、建造年份是與房價關聯最大的因素 | 標準化係數排名；214 個係數中 29 個的 95% CI 不含 0 |
| 模型對高品質、大坪數房屋誤差較大 | 品質 ≥ 8：MAE 27,636 USD；大面積：MAE 23,372 USD |
| CV 與 Test 結果一致 | CV MAE 13,366 ± 809 USD；Test MAE 14,423 USD |
