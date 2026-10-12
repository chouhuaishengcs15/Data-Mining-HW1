# -*- coding: utf-8 -*-
"""Reproduce P2 EDA: six figures and eight generated CSV tables.

Run from the repository: python EDA/codes/run_eda.py
Only P1 training is read. Hypotheses remain proposed; no CV/model fitting.
The manually maintained hypothesis_table.csv is not overwritten.
"""
from pathlib import Path
import ast
import hashlib
import json
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "p2-eda-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1]

def plot_feature_ranking():
    EXCLUDED=['編號','CV折號','總價美元','log總價','成交年份','成交月份','交易類型','交易條件']
    source=REPO/'data/outputs/p1/train_readable.csv'
    df=pd.read_csv(source,encoding='utf-8-sig')
    assert len(df)==1166 and df['編號'].is_unique
    assert not df['編號'].isin([524,1299]).any()
    assert np.allclose(df['log總價'],np.log1p(df['總價美元']))
    X=df.drop(columns=EXCLUDED)
    assert X.shape[1]==73 and not X.isna().any().any()
    numeric=X.select_dtypes(include=np.number)
    assert numeric.shape[1]==32
    y=df['log總價']
    pearson=numeric.corrwith(y,method='pearson')
    spearman=numeric.corrwith(y,method='spearman')
    continuous={'臨街長度英尺','地塊面積平方英尺','其他設施價值美元'}
    continuous.update(c for c in X if '面積平方英尺' in c)
    encoded=X.copy();discrete=[]
    for col in encoded:
        is_discrete=col not in continuous
        discrete.append(is_discrete)
        if is_discrete:encoded[col]=pd.factorize(encoded[col].astype(str),sort=True)[0]
    mi=mutual_info_regression(encoded,y,discrete_features=discrete,n_neighbors=3,random_state=42)
    result=pd.DataFrame({'feature':X.columns,'source_dtype':[str(X[c].dtype) for c in X],
        'mi_feature_type':['discrete' if d else 'continuous' for d in discrete],
        'n_observations':len(X),'n_unique':[X[c].nunique() for c in X],
        'target':'log總價','pearson_r':pearson.reindex(X.columns).values,
        'spearman_rho':spearman.reindex(X.columns).values,'mutual_information_nats':mi})
    result['pearson_abs_r']=result.pearson_r.abs()
    result['spearman_abs_rho']=result.spearman_rho.abs()
    # Ranking scope differs: 32 numeric features for correlations, all 73 for MI.
    result['pearson_rank']=result.pearson_abs_r.rank(ascending=False,method='min').astype('Int64')
    result['spearman_rank']=result.spearman_abs_rho.rank(ascending=False,method='min').astype('Int64')
    result['mi_rank']=result.mutual_information_nats.rank(ascending=False,method='min').astype('Int64')
    result['correlation_status']=np.where(result.feature.isin(numeric.columns),'computed_on_original_numeric','not_applicable_text_category')
    result['pearson_rank_scope']=32;result['spearman_rank_scope']=32;result['mi_rank_scope']=73
    result['mi_n_neighbors']=3;result['mi_random_state']=42
    result['input_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    result=result.sort_values(['mi_rank','feature'],kind='stable').reset_index(drop=True)
    (OUT/'tables').mkdir(parents=True,exist_ok=True)
    result.to_csv(OUT/'tables/feature_ranking.csv',index=False,encoding='utf-8-sig')
    assert len(result)==73 and result.feature.is_unique
    assert result.pearson_r.notna().sum()==32 and result.spearman_rho.notna().sum()==32
    assert result.mutual_information_nats.notna().all()
    for p in [os.environ.get('EDA_FONT',''),'/System/Library/Fonts/STHeiti Light.ttc',
              '/System/Library/Fonts/PingFang.ttc','C:/Windows/Fonts/msjh.ttc',
              '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']:
        if p and Path(p).is_file():
            font_manager.fontManager.addfont(p)
            plt.rcParams['font.family']=[font_manager.FontProperties(fname=p).get_name(),'DejaVu Sans'];break
    else:raise RuntimeError('請設定 EDA_FONT 為中文字型檔案路徑。')
    plt.rcParams['axes.unicode_minus']=False
    top=result.head(15).iloc[::-1]
    fig,ax=plt.subplots(figsize=(11,8))
    bars=ax.barh(top.feature,top.mutual_information_nats,color='#315e91',height=.7)
    ax.bar_label(bars,fmt='%.3f',padding=5,fontsize=10)
    ax.set(xlabel='Mutual Information (nats)',title='Feature Ranking — MI Top-15\nTarget：log 房屋總價')
    ax.set_xlim(0,top.mutual_information_nats.max()*1.15)
    ax.spines[['top','right']].set_visible(False)
    ax.set_axisbelow(True);ax.grid(axis='x',alpha=.18)
    fig.tight_layout()
    (OUT/'figures').mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/'figures/01_feature_ranking.png',dpi=180)
    plt.close(fig)
    print('Generated MI Top-15 and full 73-feature ranking CSV.')


def plot_feature_correlation():
    OUTPUT = Path(__file__).resolve().parents[1] / "figures/02_feature_correlation.png"
    NOT_FEATURE = ["編號", "CV折號", "總價美元", "log總價", "成交年份", "成交月份", "交易類型", "交易條件"]
    ENGLISH_NAMES = {'編號': 'Id',
     '住宅類型': 'MSSubClass',
     '土地分區': 'MSZoning',
     '臨街長度英尺': 'LotFrontage',
     '地塊面積平方英尺': 'LotArea',
     '道路鋪面': 'Street',
     '巷道': 'Alley',
     '地塊形狀': 'LotShape',
     '地形': 'LandContour',
     '公用設施': 'Utilities',
     '地塊位置': 'LotConfig',
     '坡度': 'LandSlope',
     '社區': 'Neighborhood',
     '鄰近條件1': 'Condition1',
     '鄰近條件2': 'Condition2',
     '建物型態': 'BldgType',
     '樓層樣式': 'HouseStyle',
     '整體品質1到10分': 'OverallQual',
     '整體狀況1到10分': 'OverallCond',
     '建造年份': 'YearBuilt',
     '改建年份': 'YearRemodAdd',
     '屋頂樣式': 'RoofStyle',
     '屋頂材料': 'RoofMatl',
     '外牆材料1': 'Exterior1st',
     '外牆材料2': 'Exterior2nd',
     '砌面類型': 'MasVnrType',
     '砌面面積平方英尺': 'MasVnrArea',
     '外牆品質': 'ExterQual',
     '外牆狀況': 'ExterCond',
     '地基類型': 'Foundation',
     '地下室高度品質': 'BsmtQual',
     '地下室狀況': 'BsmtCond',
     '地下室採光': 'BsmtExposure',
     '地下室完工區1品質': 'BsmtFinType1',
     '地下室完工區1面積平方英尺': 'BsmtFinSF1',
     '地下室完工區2品質': 'BsmtFinType2',
     '地下室完工區2面積平方英尺': 'BsmtFinSF2',
     '地下室未完工面積平方英尺': 'BsmtUnfSF',
     '地下室總面積平方英尺': 'TotalBsmtSF',
     '暖氣類型': 'Heating',
     '暖氣品質': 'HeatingQC',
     '中央空調': 'CentralAir',
     '電力系統': 'Electrical',
     '一樓面積平方英尺': '1stFlrSF',
     '二樓面積平方英尺': '2ndFlrSF',
     '低品質完工面積平方英尺': 'LowQualFinSF',
     '地上居住面積平方英尺': 'GrLivArea',
     '地下室全套衛浴數': 'BsmtFullBath',
     '地下室半套衛浴數': 'BsmtHalfBath',
     '地上全套衛浴數': 'FullBath',
     '地上半套衛浴數': 'HalfBath',
     '地上臥室數': 'BedroomAbvGr',
     '地上廚房數': 'KitchenAbvGr',
     '廚房品質': 'KitchenQual',
     '地上房間總數': 'TotRmsAbvGrd',
     '居家功能性': 'Functional',
     '壁爐數': 'Fireplaces',
     '壁爐品質': 'FireplaceQu',
     '車庫類型': 'GarageType',
     '車庫建造年份': 'GarageYrBlt',
     '車庫內裝': 'GarageFinish',
     '車庫車位數': 'GarageCars',
     '車庫面積平方英尺': 'GarageArea',
     '車庫品質': 'GarageQual',
     '車庫狀況': 'GarageCond',
     '車道鋪面': 'PavedDrive',
     '木平台面積平方英尺': 'WoodDeckSF',
     '開放門廊面積平方英尺': 'OpenPorchSF',
     '封閉門廊面積平方英尺': 'EnclosedPorch',
     '三季門廊面積平方英尺': '3SsnPorch',
     '紗窗門廊面積平方英尺': 'ScreenPorch',
     '泳池面積平方英尺': 'PoolArea',
     '泳池品質': 'PoolQC',
     '圍籬': 'Fence',
     '其他設施': 'MiscFeature',
     '其他設施價值美元': 'MiscVal',
     '成交月份': 'MoSold',
     '成交年份': 'YrSold',
     '交易類型': 'SaleType',
     '交易條件': 'SaleCondition',
     '總價美元': 'SalePrice'}
    # 中文字型：優先使用環境變數 EDA_FONT，再嘗試常見系統字型。
    candidates = [os.environ.get("EDA_FONT", ""), "/System/Library/Fonts/STHeiti Light.ttc",
                  "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msjh.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for path in candidates:
        if path and Path(path).is_file():
            font_manager.fontManager.addfont(path)
            plt.rcParams["font.family"] = [font_manager.FontProperties(fname=path).get_name(), "DejaVu Sans"]
            break
    else:
        raise RuntimeError("請用 EDA_FONT 環境變數指定中文字型檔。")
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11,
                        "axes.spines.top": False, "axes.spines.right": False,
                        "figure.facecolor": "white", "savefig.facecolor": "white"})
    df = pd.read_csv(REPO / "data/outputs/p1/train_readable.csv", encoding="utf-8-sig")
    assert len(df) == 1166 and df["編號"].is_unique
    assert not df["編號"].isin([524, 1299]).any()
    assert df["CV折號"].value_counts().sort_index().tolist() == [233, 234, 234, 232, 233]
    assert np.allclose(np.log1p(df["總價美元"]), df["log總價"])
    features = df.drop(columns=NOT_FEATURE)
    assert not features.isna().any().any()
    numeric = features.select_dtypes(include=np.number)
    # 名目類別不任意編號後計算 Pearson 或 Spearman。
    corr = numeric.corr(method="pearson")
    assert corr.shape == (32, 32)
    assert np.allclose(corr, corr.T, equal_nan=True)
    assert not corr.isna().any().any()
    assert np.allclose(np.diag(corr), 1.0)
    tables = Path(__file__).resolve().parents[1] / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    corr.to_csv(tables / "feature_feature_pearson_matrix.csv", encoding="utf-8-sig", index_label="feature")
    # Strict exploratory threshold; exclude diagonal and symmetric duplicates.
    rows = []
    for i, a in enumerate(corr.columns):
        for b in corr.columns[i+1:]:
            value = corr.loc[a, b]
            if abs(value) > 0.8:
                rows.append({"feature_1": a, "feature_1_english": ENGLISH_NAMES[a],
                             "feature_2": b, "feature_2_english": ENGLISH_NAMES[b],
                             "pearson_r": value, "abs_r": abs(value),
                             "n_observations": len(numeric), "threshold": "abs(r) > 0.8",
                             "status": "exploratory_candidate_for_ablation"})
    pairs = pd.DataFrame(rows, columns=["feature_1", "feature_1_english", "feature_2", "feature_2_english", "pearson_r", "abs_r", "n_observations", "threshold", "status"])
    pairs = pairs.sort_values("abs_r", ascending=False).reset_index(drop=True)
    pairs.to_csv(tables / "high_correlation_feature_pairs.csv", index=False, encoding="utf-8-sig")
    print(pairs.to_string(index=False))
    fig, ax = plt.subplots(figsize=(20, 18))
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#d5d9de")
    im = ax.imshow(np.ma.masked_invalid(corr.values), cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=90, fontsize=9)
    ax.set_yticks(range(len(corr)), corr.index, fontsize=9)
    for i in range(len(corr)):
        for j in range(len(corr)):
            value = corr.iloc[i, j]
            ax.text(j, i, "—" if pd.isna(value) else f"{value:.2f}", ha="center", va="center", fontsize=6,
                    color="white" if pd.notna(value) and abs(value) > .65 else "#182838")
    ax.set_title("Feature–Feature Pearson Correlation（32 numeric features）", fontsize=18, pad=20)
    fig.colorbar(im, ax=ax, fraction=.035, pad=.02, label="Pearson r")
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


def plot_quality_area():
    OUTPUT = Path(__file__).resolve().parents[1] / "figures/03_quality_area.png"
    NOT_FEATURE = ["編號", "CV折號", "總價美元", "log總價", "成交年份", "成交月份", "交易類型", "交易條件"]
    # 中文字型：優先使用環境變數 EDA_FONT，再嘗試常見系統字型。
    candidates = [os.environ.get("EDA_FONT", ""), "/System/Library/Fonts/STHeiti Light.ttc",
                  "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msjh.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for path in candidates:
        if path and Path(path).is_file():
            font_manager.fontManager.addfont(path)
            plt.rcParams["font.family"] = [font_manager.FontProperties(fname=path).get_name(), "DejaVu Sans"]
            break
    else:
        raise RuntimeError("請用 EDA_FONT 環境變數指定中文字型檔。")
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11,
                        "axes.spines.top": False, "axes.spines.right": False,
                        "figure.facecolor": "white", "savefig.facecolor": "white"})

    df = pd.read_csv(REPO / "data/outputs/p1/train_readable.csv")
    assert len(df)==1166 and df["編號"].is_unique
    x, y = df["整體品質1到10分"] * df["地上居住面積平方英尺"], df["log總價"]
    assert np.isfinite(x).all() and np.isfinite(y).all()
    pearson = x.corr(y, method="pearson")
    spearman = x.corr(y, method="spearman")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x, y, color="#315e91", s=23, alpha=.45, edgecolors="none")
    ax.set(xlabel="QualityArea（rating point × sq ft）", ylabel="log 房屋總價",
           title=f"QualityArea 與 log 房屋總價\nPearson r = {pearson:.3f}  |  Spearman ρ = {spearman:.3f}")
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


def plot_log_lot_area():
    OUTPUT = Path(__file__).resolve().parents[1] / "figures/04_log_lot_area.png"
    NOT_FEATURE = ["編號", "CV折號", "總價美元", "log總價", "成交年份", "成交月份", "交易類型", "交易條件"]
    # 中文字型：優先使用環境變數 EDA_FONT，再嘗試常見系統字型。
    candidates = [os.environ.get("EDA_FONT", ""), "/System/Library/Fonts/STHeiti Light.ttc",
                  "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msjh.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for path in candidates:
        if path and Path(path).is_file():
            font_manager.fontManager.addfont(path)
            plt.rcParams["font.family"] = [font_manager.FontProperties(fname=path).get_name(), "DejaVu Sans"]
            break
    else:
        raise RuntimeError("請用 EDA_FONT 環境變數指定中文字型檔。")
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11,
                        "axes.spines.top": False, "axes.spines.right": False,
                        "figure.facecolor": "white", "savefig.facecolor": "white"})

    df = pd.read_csv(REPO / "data/outputs/p1/train_readable.csv")
    assert len(df)==1166 and df["編號"].is_unique
    y=df['log總價'];raw=df['地塊面積平方英尺']
    fig,axes=plt.subplots(1,2,figsize=(13,6),sharey=True)
    for ax,x,label in zip(axes,[raw,np.log1p(raw)],['LotArea (sq ft)','LogLotArea']):
        ax.scatter(x,y,color='#315e91',s=22,alpha=.45,edgecolors='none')
        ax.set(xlabel=label,title=f"Pearson r = {x.corr(y):.3f}  |  Spearman ρ = {x.corr(y,method='spearman'):.3f}")
    axes[0].set_ylabel('log 房屋總價')
    fig.suptitle('LotArea / LogLotArea 與 log 房屋總價',fontsize=16)
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


def plot_total_sf():
    OUTPUT = Path(__file__).resolve().parents[1] / "figures/05_total_sf.png"
    NOT_FEATURE = ["編號", "CV折號", "總價美元", "log總價", "成交年份", "成交月份", "交易類型", "交易條件"]
    # 中文字型：優先使用環境變數 EDA_FONT，再嘗試常見系統字型。
    candidates = [os.environ.get("EDA_FONT", ""), "/System/Library/Fonts/STHeiti Light.ttc",
                  "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msjh.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for path in candidates:
        if path and Path(path).is_file():
            font_manager.fontManager.addfont(path)
            plt.rcParams["font.family"] = [font_manager.FontProperties(fname=path).get_name(), "DejaVu Sans"]
            break
    else:
        raise RuntimeError("請用 EDA_FONT 環境變數指定中文字型檔。")
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11,
                        "axes.spines.top": False, "axes.spines.right": False,
                        "figure.facecolor": "white", "savefig.facecolor": "white"})

    df = pd.read_csv(REPO / "data/outputs/p1/train_readable.csv")
    assert len(df)==1166 and df["編號"].is_unique
    x, y = df["地下室總面積平方英尺"] + df["一樓面積平方英尺"] + df["二樓面積平方英尺"], df["log總價"]
    assert np.isfinite(x).all() and np.isfinite(y).all()
    pearson = x.corr(y, method="pearson")
    spearman = x.corr(y, method="spearman")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x, y, color="#315e91", s=23, alpha=.45, edgecolors="none")
    ax.set(xlabel="TotalSF（sq ft）", ylabel="log 房屋總價",
           title=f"TotalSF 與 log 房屋總價\nPearson r = {pearson:.3f}  |  Spearman ρ = {spearman:.3f}")
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


def plot_house_age():
    OUTPUT = Path(__file__).resolve().parents[1] / "figures/supplementary/house_age.png"
    NOT_FEATURE = ["編號", "CV折號", "總價美元", "log總價", "成交年份", "成交月份", "交易類型", "交易條件"]
    # 中文字型：優先使用環境變數 EDA_FONT，再嘗試常見系統字型。
    candidates = [os.environ.get("EDA_FONT", ""), "/System/Library/Fonts/STHeiti Light.ttc",
                  "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msjh.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for path in candidates:
        if path and Path(path).is_file():
            font_manager.fontManager.addfont(path)
            plt.rcParams["font.family"] = [font_manager.FontProperties(fname=path).get_name(), "DejaVu Sans"]
            break
    else:
        raise RuntimeError("請用 EDA_FONT 環境變數指定中文字型檔。")
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11,
                        "axes.spines.top": False, "axes.spines.right": False,
                        "figure.facecolor": "white", "savefig.facecolor": "white"})

    df = pd.read_csv(REPO / "data/outputs/p1/train_readable.csv")
    assert len(df)==1166 and df["編號"].is_unique
    x, y = df["成交年份"] - df["建造年份"], df["log總價"]
    assert np.isfinite(x).all() and np.isfinite(y).all()
    pearson = x.corr(y, method="pearson")
    spearman = x.corr(y, method="spearman")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x, y, color="#315e91", s=23, alpha=.45, edgecolors="none")
    ax.set(xlabel="HouseAge（years）", ylabel="log 房屋總價",
           title=f"HouseAge 與 log 房屋總價（Exploratory only）\nPearson r = {pearson:.3f}  |  Spearman ρ = {spearman:.3f}")
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print(OUTPUT)


def build_candidate_features():
    DEFINITIONS=[
        {'feature':'HouseAge','formula':'YrSold - YearBuilt','formula_readable':'成交年份 - 建造年份',
         'rationale':'表示房屋在成交年份的年齡，探索屋齡與價格的關係。','unit':'years',
         'source_features':'YrSold;YearBuilt','source_columns':'成交年份;建造年份',
         'status':'exploratory_only_not_model_eligible',
         'limitation':'依 P1，YrSold 為預測時不可用的成交資訊；此公式不得直接用於正式模型。若需屋齡，必須先明確提供估價當時可取得的年份，不能以成交年替代。'},
        {'feature':'TotalSF','formula':'TotalBsmtSF + 1stFlrSF + 2ndFlrSF',
         'formula_readable':'地下室總面積平方英尺 + 一樓面積平方英尺 + 二樓面積平方英尺',
         'rationale':'整合地下室、一樓與二樓面積，探索整體空間規模的價格關聯。','unit':'sq ft',
         'source_features':'TotalBsmtSF;1stFlrSF;2ndFlrSF','source_columns':'地下室總面積平方英尺;一樓面積平方英尺;二樓面積平方英尺',
         'status':'candidate_pending_step4','limitation':'不同空間不一定具有相同價值。與全部三個分項同時入模會產生 exact linear dependence；Step 4 應比較替換或保留方案。'},
        {'feature':'QualityArea','formula':'OverallQual * GrLivArea','formula_readable':'整體品質1到10分 * 地上居住面積平方英尺',
         'rationale':'品質與面積的 Interaction，探索不同品質下的面積價格關係。','unit':'rating point * sq ft',
         'source_features':'OverallQual;GrLivArea','source_columns':'整體品質1到10分;地上居住面積平方英尺',
         'status':'candidate_pending_step4','limitation':'品質分數使用現有 1–10 編碼。若驗證 Interaction，原始 main effects 原則上同時保留；本特徵是原始面積乘品質，不是之前的 log 面積乘品質。'},
        {'feature':'LogLotArea','formula':'log1p(LotArea)','formula_readable':'ln(1 + 地塊面積平方英尺)',
         'rationale':'測試地塊面積的 nonlinear relationship，壓縮大面積的相對差距。','unit':'log-transformed sq-ft numeric value',
         'source_features':'LotArea','source_columns':'地塊面積平方英尺',
         'status':'candidate_pending_step4','limitation':'直接對 readable 原始單位計算；不可再對 P1 已 Box-Cox 或縮放的欄位套用相同公式。'}]
    source=REPO/'data/outputs/p1/train_readable.csv'
    df=pd.read_csv(source,encoding='utf-8-sig')
    assert len(df)==1166 and df['編號'].is_unique
    assert not df['編號'].isin([524,1299]).any()
    assert df['CV折號'].value_counts().sort_index().tolist()==[233,234,234,232,233]
    assert np.allclose(np.log1p(df['總價美元']),df['log總價'])
    values=pd.DataFrame({'Id':df['編號'],'CV_fold':df['CV折號'],'SalePrice':df['總價美元'],'log_SalePrice':df['log總價']})
    values['HouseAge']=df['成交年份']-df['建造年份']
    values['TotalSF']=df['地下室總面積平方英尺']+df['一樓面積平方英尺']+df['二樓面積平方英尺']
    values['QualityArea']=df['整體品質1到10分']*df['地上居住面積平方英尺']
    values['LogLotArea']=np.log1p(df['地塊面積平方英尺'])
    assert (values.HouseAge>=0).all() and np.isfinite(values.to_numpy()).all()
    for folder in ['tables']: (OUT/folder).mkdir(parents=True,exist_ok=True)
    pd.DataFrame(DEFINITIONS).to_csv(OUT/'tables/feature_definition.csv',index=False,encoding='utf-8-sig')
    # Baselines shown alongside candidates; target and identifiers never enter X.
    references={'YearBuilt':'建造年份','TotalBsmtSF':'地下室總面積平方英尺','1stFlrSF':'一樓面積平方英尺',
                '2ndFlrSF':'二樓面積平方英尺','OverallQual':'整體品質1到10分','GrLivArea':'地上居住面積平方英尺','LotArea':'地塊面積平方英尺'}
    rows=[]
    for name in list(values.columns[4:])+list(references):
        candidate=name in values.columns
        x=values[name] if candidate else df[references[name]]
        rows.append({'feature':name,'role':'candidate' if candidate else 'original_reference',
            'target':'log_SalePrice','n':len(x),'Pearson_r':x.corr(values.log_SalePrice),
            'Spearman_rho':x.corr(values.log_SalePrice,method='spearman'),
            'abs_Pearson_r':abs(x.corr(values.log_SalePrice)),
            'status':next(d['status'] for d in DEFINITIONS if d['feature']==name) if candidate else 'original_reference'})
    corr=pd.DataFrame(rows)
    corr.to_csv(OUT/'tables/candidate_feature_correlations.csv',index=False,encoding='utf-8-sig')
    links={'HouseAge':['YearBuilt'],'TotalSF':['TotalBsmtSF','1stFlrSF','2ndFlrSF','GrLivArea'],
           'QualityArea':['OverallQual','GrLivArea'],'LogLotArea':['LotArea']}
    ci=corr.set_index('feature');comparisons=[]
    for candidate,refs in links.items():
        for ref in refs:
            comparisons.append({'candidate':candidate,'reference':ref,
                'candidate_Pearson_r':ci.loc[candidate,'Pearson_r'],'reference_Pearson_r':ci.loc[ref,'Pearson_r'],
                'delta_abs_Pearson_r':ci.loc[candidate,'abs_Pearson_r']-ci.loc[ref,'abs_Pearson_r'],
                'candidate_Spearman_rho':ci.loc[candidate,'Spearman_rho'],'reference_Spearman_rho':ci.loc[ref,'Spearman_rho']})
    pd.DataFrame(comparisons).to_csv(OUT/'tables/candidate_vs_original.csv',index=False,encoding='utf-8-sig')
    print(corr.to_string(index=False))


def define_feature_sets():
    EXCLUDED=['編號','CV折號','總價美元','log總價','成交年份','成交月份','交易類型','交易條件']
    CANDIDATES={
     'QualityArea':('OverallQual * GrLivArea',['整體品質1到10分','地上居住面積平方英尺']),
     'LogLotArea':('log1p(LotArea)',['地塊面積平方英尺']),
     'TotalSF':('TotalBsmtSF + 1stFlrSF + 2ndFlrSF',['地下室總面積平方英尺','一樓面積平方英尺','二樓面積平方英尺']),
     'HouseAge':('YrSold - YearBuilt',['成交年份','建造年份'])}
    AREAS=['地下室總面積平方英尺','一樓面積平方英尺','二樓面積平方英尺']
    SPECS=[
     dict(id='A_Raw',family='A',purpose='Baseline；H1/H2/H3 共同 Control',add=[],remove=[],method='none',k=None,count=73),
     dict(id='B_MI20',family='B',purpose='主要 Top-k 比較：全部 73 原始 features 的 fold-local MI Top 20',add=[],remove=[],method='mutual_information',k=20,count=20),
     dict(id='B_Pearson20',family='B',purpose='補充 Top-k 比較：32 個原始 numeric features 的 fold-local |Pearson| Top 20',add=[],remove=[],method='absolute_pearson',k=20,count=20),
     dict(id='C_Engineered',family='C',purpose='B_MI20 + QualityArea + LogLotArea + TotalSF；以同折 B_MI20 為 Control，檢查額外增益',add=['QualityArea','LogLotArea','TotalSF'],remove=[],method='mutual_information',k=20,count=23),
     dict(id='H1_QualityArea',family='H1',purpose='H1 Treatment：只新增原始面積 × 品質，保留 main effects',add=['QualityArea'],remove=[],method='none',k=None,count=74),
     dict(id='H2_LogLotArea',family='H2',purpose='H2 Treatment：只以 LogLotArea 替換 LotArea',add=['LogLotArea'],remove=['地塊面積平方英尺'],method='none',k=None,count=73),
     dict(id='H3_TotalSF',family='H3',purpose='H3 Treatment：移除三個分項，只加入 TotalSF',add=['TotalSF'],remove=AREAS,method='none',k=None,count=71),
    ]
    df=pd.read_csv(REPO/'data/outputs/p1/train_readable.csv',encoding='utf-8-sig')
    raw=df.drop(columns=EXCLUDED)
    numeric=set(raw.select_dtypes(include=np.number).columns)
    assert len(raw.columns)==73 and len(numeric)==32
    # Read only static column names from P1; never execute the notebook.
    notebook=json.loads((REPO/'data/P1_Preprocessing_v4.ipynb').read_text())
    names={}
    for cell in notebook['cells']:
        if cell['cell_type']!='code':continue
        for node in ast.parse(''.join(cell['source'])).body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rename_dict' for t in node.targets):
                names={v:k for k,v in ast.literal_eval(node.value).items()}
    names.update({'CV折號':'CV_fold','log總價':'SalePrice_log'})
    rows=[];summaries=[]
    for spec in SPECS:
        scope=list(raw.columns) if spec['method']=='mutual_information' else [c for c in raw if c in numeric] if spec['method']=='absolute_pearson' else []
        retain=[]
        for col in df.columns:
            if col in EXCLUDED:
                action='exclude_non_feature';reason='識別／CV／target 或 P1 規範排除的成交資訊，不得進入 X。'
            elif col in spec['remove']:
                action='remove_replaced';reason='由指定 engineered feature 替換；計算衍生值前保留來源資料，但不作為模型欄位。'
            elif spec['method']!='none':
                if col in scope:
                    action='select_within_fold';reason=('直接沿用同折 B_MI20 已選出的原始欄位清單；不重新納入 engineered features 排名。' if spec['id']=='C_Engineered' else '僅為候選，不代表已入選；每折 training 內重新計算分數，取 Top 20。')
                else:
                    action='exclude_selection_scope';reason='文字類別不任意編號計算 Pearson；本組僅選原始 numeric features。'
            else:
                action='retain';reason='保留 Raw 原始 feature 與其原始表示；後續套用共同 fold-local encoding/scaling。';retain.append(col)
            rows.append({'set_id':spec['id'],'family':spec['family'],'purpose':spec['purpose'],
                'feature':names[col],'source_column':col,'action':action,'formula':'','formula_inputs':'','reason':reason,
                'selection_method':spec['method'],'k':spec['k'],'ranking_candidate_count':len(scope) if scope else None,
                'expected_source_feature_count':spec['count'],'membership_final':spec['method']=='none',
                'target':'log總價 = log1p(SalePrice)','status':'defined_not_evaluated'})
        for name,(formula,inputs) in CANDIDATES.items():
            action='add_engineered' if name in spec['add'] else 'exclude_unavailable' if name=='HouseAge' else 'not_in_set'
            reason='指定候選加入，效果尚待 Ablation 驗證。' if action=='add_engineered' else 'YrSold 不符合目前 P1 prediction-time availability；禁止作為任何正式組的輸入。' if name=='HouseAge' else '此組不包含該候選，保持控制比較。'
            rows.append({'set_id':spec['id'],'family':spec['family'],'purpose':spec['purpose'],'feature':name,
                'source_column':'','action':action,'formula':formula,'formula_inputs':';'.join(inputs),'reason':reason,
                'selection_method':spec['method'],'k':spec['k'],'ranking_candidate_count':len(scope) if scope else None,
                'expected_source_feature_count':spec['count'],'membership_final':spec['method']=='none',
                'target':'log總價 = log1p(SalePrice)','status':'defined_not_evaluated'})
        if spec['id']=='C_Engineered':
            assert not spec['remove'] and spec['count']==spec['k']+len(spec['add'])
        if spec['method']=='none':assert len(retain)+len(spec['add'])==spec['count']
        summaries.append({'set_id':spec['id'],'purpose':spec['purpose'],'control':'B_MI20' if spec['id']=='C_Engineered' else 'A_Raw' if spec['id']!='A_Raw' else '',
            'expected_source_feature_count':spec['count'],'ranking_method':spec['method'],'k':spec['k'],
            'retained_source_columns':';'.join(retain) if retain else 'DYNAMIC: reuse exactly the same fold-specific B_MI20 selection' if spec['id']=='C_Engineered' else 'DYNAMIC: selected independently inside each training fold',
            'removed_source_columns':';'.join(spec['remove']), 'added_features':';'.join(spec['add']),
            'ranking_candidate_columns':';'.join(scope),'model_encoded_dimension':'record actual per-fold encoder output; not fixed here',
            'primary_metric':'pending P3 agreement: RMSE_USD or RMSE_log',
            'h3_tolerance':'pending pre-experiment agreement' if spec['family']=='H3' else '',
            'cv_protocol':'fixed P1 CV folds 0-4; no refitting selector on validation',
            'status':'defined_not_evaluated'})
    result=pd.DataFrame(rows)
    assert not result.duplicated(['set_id','feature']).any()
    assert not result.loc[result.feature=='HouseAge','action'].isin(['retain','add_engineered','select_within_fold']).any()
    out=OUT/'tables';out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/'feature_sets.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(summaries).to_csv(out/'feature_sets_summary.csv',index=False,encoding='utf-8-sig')
    print(pd.DataFrame(summaries)[['set_id','expected_source_feature_count','ranking_method','status']].to_string(index=False))
    print('Specification rows:',len(result),'; no ranking, model fitting, CV or test access executed.')


def main():
    # Each plot retains its original Matplotlib defaults. Styling must not
    # leak between figures now that they share a single Python process.
    steps = [
        plot_feature_ranking,
        plot_feature_correlation,
        plot_quality_area,
        plot_log_lot_area,
        plot_total_sf,
        plot_house_age,
        build_candidate_features,
        define_feature_sets,
    ]
    for step in steps:
        print(f"Running {step.__name__}...", flush=True)
        with plt.rc_context():
            plt.rcdefaults()
            step()
    print("Completed: 6 figures and 8 generated CSVs; hypothesis table unchanged.")


if __name__ == "__main__":
    main()
