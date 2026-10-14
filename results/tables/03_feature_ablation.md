# Table 3：Feature Ablation

報告位置：7.2 Feature Ablation。以下兩組實驗設定不同，分開呈現。

## 最終模型的特徵組比較

使用 Elastic Net、log1p target、相同五折與搜尋範圍，各特徵組分別選參數。誤差皆還原為 USD。

| Feature set | CV MAE ± SD (USD) | CV RMSE ± SD (USD) | alpha | l1_ratio |
|---|---|---|---|---|
| A：Raw | 13,749.64 ± 826.79 | 21,376.42 ± 3,271.07 | 0.000316228 | 0.9 |
| B：MI Top-20 | 16,966.27 ± 1,268.78 | 25,285.75 ± 2,906.04 | 0.000316228 | 0.9 |
| C：Final Raw + QualityArea | 13,366.06 ± 809.27 | 19,925.10 ± 2,274.15 | 0.00316228 | 0.1 |

- MI Top-20 在各 training fold 內選取，不直接使用全 training 的 EDA 排名。
- Final 的平均誤差最低；只取 MI20 反而變差。這是平均表現比較，不等於已證明 Final 顯著優於 Raw。
- 此處 C 指最終特徵組，來源名稱是 `H1_QualityArea`；repo 的 `C_Engineered` 是 MI20 加三個工程特徵，兩者不同。

## H1–H3 假設驗證

使用固定 Ridge alpha=10、log1p target 與相同五折。ΔRMSE=變更後−原設定，負值代表改善。

| 比較 | Control RMSE (USD) | Treatment RMSE (USD) | ΔRMSE (USD) | 改善折數 |
|---|---|---|---|---|
| H1：Raw → 加入 QualityArea | 21,399.66 | 20,177.30 | -1,222.36 | 5/5 |
| H2：原始 LotArea → LogLotArea | 21,638.62 | 21,398.04 | -240.57 | 4/5 |
| H2：P1 Box-Cox → LogLotArea | 21,399.66 | 21,398.04 | -1.62 | 3/5 |
| H3：三個面積分項 → TotalSF | 21,399.66 | 21,164.57 | -235.10 | 3/5 |

- H1 改善最明顯，五折皆下降；保留品質與面積的原始欄位，再加入乘積。
- H2 相較未轉換的土地面積有改善，但相較 P1 已做的 Box-Cox 幾乎相同。
- H3 減少欄位且平均誤差沒有惡化；原實驗容忍規則為 RMSE 最多增加 2%，不是正式非劣性檢定。
- 三個新特徵都由既有欄位計算，不增加資料蒐集成本；最終僅採用 QualityArea，避免加入改善有限的轉換。
- 這些是探索性比較；改善折數不是顯著性檢定。Δ 值由原始精度計算後四捨五入。

來源：[Feature sets](../../model/results/tables/feature_ablation/ablation_results.csv)、[H1–H3](../../model/results/tables/feature_ablation/hypothesis_results.csv)。
