# Table 5：錯誤案例

報告位置：8.2 Error Analysis。選用 P3 Final Test 絕對誤差最大的三筆；Error=Actual−Predicted，正值代表低估。

| Id | Actual (USD) | Predicted (USD) | Error (USD) | 房屋背景 |
|---|---|---|---|---|
| 899 | 611,657.00 | 473,938.32 | 137,718.68 | OverallQual=9；GrLivArea=2,364 sq ft；NridgHt |
| 775 | 395,000.00 | 295,840.37 | 99,159.63 | OverallQual=8；GrLivArea=1,973 sq ft；NridgHt |
| 1047 | 556,581.00 | 459,516.39 | 97,064.61 | OverallQual=9；GrLivArea=2,868 sq ft；StoneBr |

## 案例解讀

- Id 899：2009 年建成，地下室 2,330 sq ft，品質高且低估最多。可能涉及社區、高品質新屋的價格差異，不能只由面積解釋。
- Id 775：和 Id 899 同屬 NridgHt，但居住面積較小，仍低估約 9.9 萬美元，顯示「只是大坪數」不足以解釋共同現象。
- Id 1047：品質高、居住面積大；可能有品質與面積的交互關係未被充分表示。

三筆都是高品質住宅且被低估。P3 的切片結果也顯示，高品質組（OverallQual≥8，n=45）的 EN MAE 為 27,635.58 USD；大面積組（n=84）為 23,372.14 USD，高於整體平均。

以上原因是可能解釋，不是已驗證的因果。第一個改進方向是檢查 training 中相同社區、品質與面積的資料覆蓋，再判斷是否需要調整特徵。模型切片比較不能直接當成 QualityArea 的改善幅度。

來源：[P3 錯誤案例](../../model/results/tables/final_test/large_error_cases.csv)、[切片結果](../../model/results/tables/final_test/slice_metrics.csv)。
