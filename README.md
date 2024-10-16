# SlicePartitioningMethod

## 環境

## スクリプトの実行

step1．DCMファイルからniftiファイルに変換
```python
cd ~/SlicePartitioningMethod/totalSegmentator/script
python dcm2nifti.py 
```
<br>

step2．3領域に分割するための元となる（甲状腺，肺，腎臓）のセグメンテーションを作成
```python
pyhton totalseg.py
```

<br>

step3．作成したセグメンテーションをもとにデータセットを3領域に分割（dataset:upper, middle, lowerの作成）
```python
cd 
cd ~/SlicePartitioningMethod/slicePartitioning/script
python slicepartitioning.py
```

<br>

> ⚠️ **以下はPix2Pixでの処理** 
#### 作成した３つのデータセットをPix2Pixで学習

#### テストデータも同様にして, ３領域に分割してテストセットを作成

#### 各領域ごとの学習済みモデルを用いてテストセットに対しinference.ipynbを実行
↓
#### ここで３つのテストセットの生成画像が得られる　　<br><br>
  
step4．3つのモデルから得られた各テストセットの生成画像を平均化
```python
python unity_dcmfolder.py
```
<br>
<br>
<br>
<br>
<br>
<img src="https://img.shields.io/badge/-Python-F9DC3E.svg?logo=python&style=flat">