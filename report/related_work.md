# Related Work 整理（W1）

最後更新：2026/10/11

- 書目資料（作者、年份、期刊、卷期頁碼、DOI）：全部已用 Crossref 核對
- 「查核程度」欄說明每篇的 Reported Error 是從哪裡讀來的
- BibTeX 在 [`paper/references.bib`](paper/references.bib)，key 對應下表第一欄

## 1. 比較表

| Key | Task | Dataset | Features | Model | Reported Error | 查核程度 |
|---|---|---|---|---|---|---|
| `sharma2024optimal` | 房價迴歸 | **Ames, Iowa**，2,930 筆、82 個變數（Kaggle 版本） | Ames 原始房屋屬性，用 RF 做 feature selection | Linear Regression、MLP、RF、SVR、XGBoost；GridSearchCV 調參 | 調參後 test：**XGBoost** R² 0.930、RMSE 0.116、MAE 0.084；**Linear Regression** R² 0.910、RMSE 0.130、MAE **0.075**（MAE 最低）；RF R² 0.890、RMSE 0.145 | ✅ 原文全文（Table 3、4） |
| `ho2021predicting` | 房價迴歸 | 香港將軍澳 14 個私人屋苑二手成交，1996/06–2014/08，約 39,5xx 筆 | log 樓面面積、log 屋齡、樓層、log 到中環時間（朝向 dummy 因相關性近 0 被排除） | SVM、RF、GBM；80/20 split + 5-fold CV | Test（y = log 實質價格）：**GBM** R² 0.904、RMSE 0.0890、MAPE 0.323%；RF R² 0.903、RMSE 0.0892；SVM R² 0.827、RMSE 0.119 | ✅ 原文全文（Table 4） |
| `limsombunchai2004house` | 房價迴歸 | 紐西蘭 Christchurch，200 筆（2003 年 Harcourts 網站**刊登價**） | 土地面積、屋齡、有無花園、房數、衛浴數、車庫數、周邊設施、6 區位 dummy | Hedonic（semi-log、WLS） vs. ANN；160 / 40 split | Out-of-sample（Model 1，全樣本）：**Hedonic** R² 0.619、RMSE 876,216；**ANN** R² 0.900、RMSE 449,111 | ✅ 原文全文（Table 4） |
| `truong2020housing` | 房價迴歸（y = **每平方米均價**，不是總價） | 北京（Kaggle 鏈家資料），2009–2018 成交，原始 30 萬筆以上，清理後 231,962 筆 | 19 個特徵（one-hot 後 58 個）：經緯度、區、到市中心距離、屋齡、面積、社區均價、成交時間、樓層、建築類型、電梯、近地鐵等 | RF、XGBoost、LightGBM、Hybrid（三者等權平均）、Stacked（RF + LightGBM → XGBoost）；4:1 split | Test RMSLE：**Stacked 0.16350**、Hybrid 0.16372、RF 0.16568、XGBoost 0.16603、LightGBM 0.16944 | ✅ 原文全文（Table 2） |
| `park2015using` | 房價**分類**（成交價高於或低於刊登價） | 美國 Virginia 州 Fairfax County，5,359 筆 townhouse | 經 t-test、logistic regression 篩選的屬性 | C4.5、RIPPER、Naïve Bayes、AdaBoost | 文獻普遍引用 RIPPER 表現最好；精確 accuracy 未核對 | ⚠️ 只核對了書目；是分類任務，建議只在背景段落引用，**不放進比較表** |

### 背景與方法文獻（不需要 Reported Error）

| Key | 用途 |
|---|---|
| `decock2011ames` | 資料集原始出處（Ames City Assessor's Office 的 2006–2010 成交紀錄，2,930 筆）。Kaggle 版本是其中的 1,460 筆訓練集 |
| `kaggle2016house` | Kaggle 競賽頁面（我們的資料下載來源） |
| `rosen1974hedonic` | Hedonic pricing 理論：房價 = 各項屬性的隱含價格加總，是「用線性模型預測房價」的理論基礎 |
| `hoerl1970ridge`、`tibshirani1996lasso`、`zou2005elastic` | Ridge、Lasso、Elastic Net 原始論文，Method 章節（W2）也會用到 |

## 2. 寫作時要注意

1. **各篇的誤差不能直接比較大小**：Sharma 和 Ho 的 RMSE 是在 log 或縮放後的尺度（Sharma 的原文沒有明確說明 y 的尺度），Limsombunchai 是紐幣原始價格，Truong 用的是 RMSLE。寫的時候要註明尺度，不能寫成「我們的 RMSE 比 XX 低」，除非尺度相同
2. **Sharma 2024 跟我們最接近**，但資料不同：他們用的是完整 2,930 筆，我們用 Kaggle 的 1,460 筆子集。他們的 Linear Regression 跟 XGBoost 只差 0.02 R²，MAE 甚至還比較低。這可以拿來支持「線性模型在 Ames 上有競爭力」這個研究動機
3. **Ho 2021 的筆數**：原文正文寫 39,554，但 Table 2 是 39,544，論文本身前後不一致。引用時寫「約 40,000 筆」就好
4. **Truong 2020 的細節**：
   - 特徵包含「社區均價」和「成交時間」，跟我們排除成交後資訊的設定不同，可以拿來對比
   - 原文 Table 1 寫 tradeTime 是 2002–2018，但正文寫 2009–2018，論文本身前後不一致
   - 原文說用 `RandomForestClassifier`，但做的是迴歸，應該是筆誤。這些都不用寫進報告
5. **重要線索：Lu et al. 2017**（Truong 2020 的引用 [5]）用的就是**我們的 Kaggle House Prices 資料**。根據 Truong 的轉述，Kaggle test RMSLE 是 Lasso 0.11449、XGBoost 0.11843、65% Lasso + 35% XGBoost 混合 0.11260。也就是說，**Lasso 比 XGBoost 好**，這對我們「線性模型有競爭力」的論點非常有用。書目已對過 Crossref（IEEE IEEM 2017, pp. 319–323），但數字目前只是二手轉述，要找到原文確認後才能引用
6. **Limsombunchai 2004 用的是刊登價，不是成交價**，作者自己也在 Limitations 承認這點。可以拿來對比：我們用的是真實成交價

## 3. 本研究與既有工作的差異（草稿，等 P3 結果出來再定稿）

下面列的是目前可以主張的方向，最後要以實際結果為準：

1. **預測時間點明確**：P1 已經把成交年月、交易類型、交易條件這些成交後才知道的欄位排除在特徵外，模擬「成交前估價」的情境。上面幾篇都沒有特別討論這一點
2. **評估流程嚴謹**：固定的 5-fold CV（報告 mean ± sd），加上封存的 test set 只評分一次，並與 strong nonlinear baseline 做差異檢定。Sharma 2024 只報單次 split 的結果
3. **可解釋性**：正則化線性模型可以提供 coefficient、95% CI 和 VIF，這呼應 hedonic pricing 的「屬性隱含價格」概念（Rosen 1974）。這是 tree ensemble 比較難做到的

## 4. 還沒完成

- [x] 核對 Truong 2020 原文（2026/10/11 完成）
- [ ] 找 Lu et al. 2017 原文（https://doi.org/10.1109/IEEM.2017.8289904），確認 Lasso / XGBoost 的數字（可能需要學校 IEEE Xplore 權限）
- [ ] 決定 Park & Bae 2015 要不要引用
- [ ] 和 I1 確認 Research Question 之後，把第 3 節改寫成英文 Related Work 段落
