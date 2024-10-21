import os
import shutil
import nibabel as nib

def copy_slices_up_to_segmentation(nifti_dir, src_dir, dst_dir, organ_name, copy_all=False):
    """
    Parameters:
    nifti_dir (str): NIfTI形式の臓器セグメンテーションファイルが格納されているフォルダのパス
    src_dir (str): コピー元のフォルダのパス
    dst_dir (str): コピー先のフォルダのパス
    organ_name (str): 臓器名 ('thyroid_gland', 'whole_lung', 'kidney' など)
    copy_all (bool): Trueの場合、セグメンテーションスライスに到達するまでの全スライスをコピー
    """
    
    # コピー先のディレクトリが存在しない場合は作成
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # ケースフォルダごとに処理を実行
    for case_folder in os.listdir(nifti_dir):
        nifti_case_path = os.path.join(nifti_dir, case_folder)
        
        # NIfTIファイルのパスを生成
        file_path = os.path.join(nifti_case_path, f'{organ_name}_{case_folder}.nii.gz')
        if not os.path.exists(file_path):
            print(f"NIfTI file {file_path} does not exist")
            continue
        
        img = nib.load(file_path)
        data = img.get_fdata()

        # スライス番号を取得
        slices_with_segmentation = [1 if data[:, :, i].sum() > 0 else 'none' for i in range(data.shape[2])]

        # 対応するケースフォルダのコピー元とコピー先パスを指定
        src_case_path = os.path.join(src_dir, case_folder.replace('_CT2', ''))
        dst_case_path = os.path.join(dst_dir, case_folder.replace('_CT2', ''))

        if not os.path.exists(src_case_path):
            print(f"Source case folder {src_case_path} does not exist")
            continue

        # ケースフォルダをコピー先に作成
        if not os.path.exists(dst_case_path):
            os.makedirs(dst_case_path)

        # CTフォルダごとにコピーを実行
        for ct in os.listdir(src_case_path):
            ct_path = os.path.join(src_case_path, ct)
            if os.path.isdir(ct_path):
                ct_dst_path = os.path.join(dst_case_path, ct)
                if not os.path.exists(ct_dst_path):
                    os.makedirs(ct_dst_path)

                # スライス番号に基づいてファイルをコピー
                total_slices = len(slices_with_segmentation)
                for i, val in enumerate(slices_with_segmentation):
                    if val == 1:
                        reversed_index = total_slices - i
                        if copy_all:
                            # 00000001.DCM~セグメンテーションスライスまで全スライスをコピー
                            for j in range(1, reversed_index + 1):
                                dcm_filename = f"{j:08}.DCM"
                                src_dcm_path = os.path.join(ct_path, dcm_filename)
                                dst_dcm_path = os.path.join(ct_dst_path, dcm_filename)
                                if os.path.exists(src_dcm_path):
                                    shutil.copy(src_dcm_path, dst_dcm_path)
                                    print(f"Copied {src_dcm_path} to {dst_dcm_path}")
                                else:
                                    print(f"File {src_dcm_path} does not exist")
                            break
                        else:
                            # セグメンテーションスライスのみをコピー
                            dcm_filename = f"{reversed_index:08}.DCM"
                            src_dcm_path = os.path.join(ct_path, dcm_filename)
                            dst_dcm_path = os.path.join(ct_dst_path, dcm_filename)
                            if os.path.exists(src_dcm_path):
                                shutil.copy(src_dcm_path, dst_dcm_path)
                                print(f"Copied {src_dcm_path} to {dst_dcm_path}")
                            else:
                                print(f"File {src_dcm_path} does not exist")

    print("Dataset copy complete.")

def find_and_copy_missing_files(folder1, folder2, alldata_folder):
    """
    フォルダに重複がある場合何もせず．
    フォルダに重複がない場合は, alldataフォルダから重複していない領域をコピーする関数

    ※注意
    folder1, folder2, alldata_folder全てに同じフォルダ(caseフォルダ)が含まれている必要があります．
    """
    # folder1とfolder2の中に含まれるcaseフォルダを取得
    case_folders = os.listdir(folder1)
    
    for case_folder in case_folders:
        folder1_case = os.path.join(folder1, case_folder)
        folder2_case = os.path.join(folder2, case_folder)
        alldata_case = os.path.join(alldata_folder, case_folder)
        
        if not (os.path.exists(folder1_case) and os.path.exists(folder2_case) and os.path.exists(alldata_case)):
            print(f"{case_folder} がどちらかのフォルダに存在しません")
            continue

        # CT1とCT2フォルダを取得
        ct_folders = ['CT1', 'CT2']
        
        # # testの場合はCT1, CT2, CT3となります
        # ct_folders = ['CT1', 'CT2', 'CT3']

        for ct_folder in ct_folders:
            folder1_ct = os.path.join(folder1_case, ct_folder)
            folder2_ct = os.path.join(folder2_case, ct_folder)
            alldata_ct = os.path.join(alldata_case, ct_folder)
            
            if not (os.path.exists(folder1_ct) and os.path.exists(folder2_ct) and os.path.exists(alldata_ct)):
                print(f"{ct_folder} が {case_folder} のいずれかに存在しません")
                continue
            
            # folder1_ct, folder2_ctに含まれるファイルリストを取得
            folder1_files = set(os.listdir(folder1_ct))
            folder2_files = set(os.listdir(folder2_ct))
            
            # DCMファイルだけを対象にする
            folder1_files = {file for file in folder1_files if file.endswith('.DCM')}
            folder2_files = {file for file in folder2_files if file.endswith('.DCM')}
            
            # 重複しているファイルを確認
            common_files = folder1_files & folder2_files
            if common_files:
                # 重複ファイルがあれば何もしない
                print(f"{ct_folder} in {case_folder}: 重複ファイルが見つかりました: {common_files}")
                continue
            else:
                # 重複していないファイルを探す
                all_files = sorted(folder1_files | folder2_files)
                
                # all_files の間にある連番を探す
                missing_files = []
                for i in range(int(all_files[0].split('.')[0]), int(all_files[-1].split('.')[0])):
                    file_name = f"{i:08d}.DCM"
                    if file_name not in all_files:
                        missing_files.append(file_name)

                # missing_files を alldata_folder からコピーする
                for file_name in missing_files:
                    src_path = os.path.join(alldata_ct, file_name)
                    if os.path.exists(src_path):
                        shutil.copy(src_path, folder1_ct)  # folder1のCTフォルダにコピー
                        shutil.copy(src_path, folder2_ct)  # folder2のCTフォルダにもコピー
                        print(f"{file_name} を {folder1_ct} と {folder2_ct} にコピーしました")
                    else:
                        print(f"{file_name} が {alldata_ct} に存在しません")

#入力フォルダ: dataset01 or dataset02 or test
src_dir = '~/dataset'

# 呼び出し例

# 上部datsetの作成
copy_slices_up_to_segmentation(
    nifti_dir='~/totalSegmentator/organSeg/dataset_thyroidgland',
    src_dir = src_dir,
    dst_dir='~/dataset_upper',
    organ_name='thyroid_gland',
    copy_all=True
)

# 中部datasetの作成
copy_slices_up_to_segmentation(
    nifti_dir='~/totalSegmentator/organSeg/dataset_wholelung',
    src_dir = src_dir,
    dst_dir='~/dataset_middle',
    organ_name='whole_lung',
    copy_all=False
)

# 下部datasetの作成
copy_slices_up_to_segmentation(
    nifti_dir='~/totalSegmentator/organSeg/dataset_kidney',
    src_dir = src_dir,
    dst_dir='~/dataset_lower',
    organ_name='kidney',
    copy_all=False  
)

# 上部データセットと中部データセットに対して重複領域の有無を確認
find_and_copy_missing_files(
    folder1 = '~/dataset_upper', 
    folder2 = '~/dataset_middle', 
    alldata_folder = '~/dataset_all' # 3領域分割前のデータセット
)

# 中部データセットと下部データセットに対して重複領域の有無を確認
find_and_copy_missing_files(
    folder1 = '~/dataset_lower', 
    folder2 = '~/dataset_middle', 
    alldata_folder = '~/dataset_all' 
)