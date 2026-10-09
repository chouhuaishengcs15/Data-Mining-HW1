# Data

這個資料夾放資料集與 P1 的前處理結果。

## Dataset

- Dataset name: House Prices - Advanced Regression Techniques（Ames Housing，美國愛荷華州 Ames 市房屋成交資料）
- Source: Kaggle 競賽資料；原始資料來自 De Cock, D. (2011). *Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project*. Journal of Statistics Education, 19(3)。資料由 Ames 市估價辦公室（Ames City Assessor's Office）提供，涵蓋 2006–2010 年的成交紀錄
- Download URL: https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques （下載日期 2026/10/9）
- License / usage restrictions: MIT License，允許再散布，使用時保留授權聲明並註明來源

## Data Policy

上傳前已確認：

1. 授權允許再散布：MIT License ✅
2. 不含個人或敏感資料：只有房屋屬性與成交價，沒有屋主姓名、地址等個資 ✅
3. 檔案大小適合 GitHub：最大的檔案約 1 MB ✅

## 資料夾結構

```
data/
├── P1_Preprocessing_v4.ipynb      P1 前處理 notebook（在 data/ 底下執行）
├── raw_data_FromKaggle/           Kaggle 原始檔，不要修改
│   ├── train.csv                  1,460 筆 × 81 欄（含 SalePrice）
│   ├── test.csv                   Kaggle 的測試集（沒有 SalePrice，本作業不使用）
│   ├── data_description.txt       官方欄位說明
│   └── sample_submission.csv
└── outputs/p1/                    P1 產出，交給 P2、P3
    ├── train.csv
    ├── test.csv
    ├── data_split.csv
    ├── train_readable.csv
    └── test_readable.csv
```

## Processed Data（P1 產出）

所有 CSV 都是 UTF-8 with BOM（`utf-8-sig`），Excel 直接打開中文不會亂碼。用 pandas 讀取：

```python
import pandas as pd
train = pd.read_csv("data/outputs/p1/train.csv", encoding="utf-8-sig")
```

| 檔案 | 筆數 × 欄數 | 內容 | 給誰 |
|---|---|---|---|
| `train.csv` | 1,166 × 221 | 前處理完成的 trainset（213 個特徵），可直接建模 | P2、P3 |
| `test.csv` | 292 × 221 | 前處理完成的 testset，**封存**，只在最後評分用一次 | P3 |
| `data_split.csv` | 1,460 × 3 | 每筆 `Id` 屬於 train 或 test，以及 trainset 的 5 折編號 `cv_fold` | P2、P3 |
| `train_readable.csv` | 1,166 × 81 | 中文、已補缺值、**未編碼未縮放**，畫 EDA 圖用 | P2 |
| `test_readable.csv` | 292 × 80 | 同上，testset 版本 | 對照用 |

### 切分方式

- 原始 1,460 筆依 `Id` 排序後，用 `train_test_split(test_size=292, shuffle=True, random_state=42)` 切成 trainset 1,168 筆、testset 292 筆
- trainset 再用 `KFold(n_splits=5, shuffle=True, random_state=42)` 分成 5 折（`cv_fold` = 0–4）
- `data_split.csv` 裡 testset 的 `cv_fold` 是空白，因為 testset 不參與 CV

### 前處理摘要（細節與理由見 notebook）

| 步驟 | 做法 |
|---|---|
| Outliers | 刪除 trainset 中 2 筆「地上居住面積 > 4000 平方英尺且總價 < 300,000 美元」的資料（Id 524、1299） |
| Target | 保留原始 `總價美元`，另加 `log總價` = log1p(總價)，偏態從 1.74 降到 0.12 |
| Missing | 「沒有該設施」的 NA 補「無」或 0；臨街長度用 trainset 同社區中位數；其餘少量缺值用 trainset 眾數 |
| 刪除欄位 | Utilities（幾乎全部相同）、GarageYrBlt（缺值都是沒有車庫的房子，補 0 會變成極端值，補其他年份也不合理） |
| Encoding | 22 個有順序的類別欄 → 手動對照成數字；19 個名目類別欄 → One-hot |
| 偏態轉換 | 35 個偏態絕對值 > 0.75 的數值欄做 Box-Cox（λ = 0.15） |
| Scaling | 54 個數值欄用 RobustScaler；One-hot 欄不縮放 |

所有從資料算出來的數字（眾數、中位數、要做 Box-Cox 的欄位、RobustScaler 參數）**只用 trainset 計算**，再套用到 testset。

## 給 P2、P3 的使用說明

### 欄位怎麼分

| 欄位 | 用途 |
|---|---|
| `總價美元` | y（原始價格） |
| `log總價` | y（log1p 後） |
| `編號`、`CV折號` | 識別用，**不是特徵** |
| `成交年份`、`成交月份`、`交易類型`、`交易條件` | 成交後才知道的資訊，**不是特徵**（預測時間點是「還沒成交時估價」） |
| 其餘 213 欄 | 特徵 X |

```python
NOT_FEATURE = ["編號", "CV折號", "總價美元", "log總價", "成交年份", "成交月份", "交易類型", "交易條件"]
X = train.drop(columns=NOT_FEATURE)
y = train["log總價"]   # 或 train["總價美元"]
```

### P2（EDA）

- 畫圖建議用 `train_readable.csv`：欄名和類別都是中文、數值是原始單位，比較好解讀
- 只用 trainset 做 EDA，不要看 testset

### P3（建模與評估）

1. **y 二選一**：`總價美元` 或 `log總價`，選了一個，另一個就不能放進 X。用 `log總價` 訓練的話，預測值要用 `np.expm1()` 轉回美元再算誤差
2. **CV 用 `CV折號`**：trainset 刪了 2 筆異常值，所以 5 折筆數是 233 / 234 / 234 / 232 / 233，不是完全平均
3. **testset 封存**：`test.csv` 只在模型全部定案後評分一次，不能拿來調參數
4. **已知限制**：前處理的統計值是用整個 trainset 算的，做 CV 時 validation 折的資訊會稍微混進這些數字，影響很小，報告中可註明
5. `test.csv` 的 `CV折號` 欄沒有意義（全部是 0），請忽略

## 重跑前處理

在 `data/` 資料夾底下執行 `P1_Preprocessing_v4.ipynb`，會讀 `raw_data_FromKaggle/train.csv`，輸出覆寫到 `outputs/p1/`。切分和處理都固定了亂數種子，重跑結果相同。

需要的套件：pandas、numpy、scipy、scikit-learn、matplotlib、seaborn。
