import os
import shutil
import nibabel as nib
import pydicom

'''
２つのセグメンテーションデータから３領域に分割するスクリプト

Parameters:
dataset_folder (str): 分割したデータセットのフォルダパス
seg1_nifti_base (str): セグメンテーションデータが保存されているフォルダのパス
seg2_nifti_base (str): セグメンテーションデータが保存されているフォルダのパス
'''

def get_nifti_slice_range(nifti_file):
    # NIfTIファイルを読み込む
    img = nib.load(nifti_file)
    data = img.get_fdata()

    # セグメンテーションデータが存在するかを確認
    slices_with_segmentation = [1 if data[:, :, i].sum() > 0 else 'none' for i in range(data.shape[2])]

    # 逆順でスライス番号を取得
    total_slices = len(slices_with_segmentation)
    seg_start = None

    # 最初に1（セグメンテーションデータ）が出現するスライスをseg_startとする
    for i, val in enumerate(slices_with_segmentation[::-1]):
        if val == 1:
            if seg_start is None:
                seg_start = i   # 逆順にしているので調整

    # 最初のスライス番号のindexを返す
    return seg_start

def validate_dicom_file(file_path):
    try:
        # DICOMファイルを読み込む
        dicom_data = pydicom.dcmread(file_path)
        return dicom_data
    except Exception as e:
        print(f"Error reading DICOM file {file_path}: {e}")
        return None

# セグメンテーションのスライス範囲に基づいてDICOMファイルを分割
def split_dicom_files(dataset_folder, case_folder, seg1_nifti, seg2_nifti, output_upper, output_middle, output_lower):
    # NIfTI ファイルが存在するかチェック
    if not os.path.exists(seg1_nifti) or not os.path.exists(seg2_nifti):
        print(f"{case_folder} のセグメンテーションファイルが見つかりません。スキップします。")
        return

    # NIfTI ファイルから最初のスライス番号のindexを取得
    try:
        seg1_start = get_nifti_slice_range(seg1_nifti)
        seg2_start = get_nifti_slice_range(seg2_nifti)
    except FileNotFoundError as e:
        print(f"セグメンテーションファイルの読み込みに失敗しました: {e}")
        return

    print(f"segmentation1の初めのスライス番号：{seg1_start}\nsegmentation2の初めのスライス番号：{seg2_start}")

    if seg1_start > seg2_start :
        print("seg1_start < seg2_startとなるようにしてください")
        return  

    if seg1_start is None or seg2_start is None:
        print("セグメンテーションデータに有効なスライスが見つかりません。")
        return

    # 出力フォルダ (upper, middle, lower) を作成
    os.makedirs(output_upper, exist_ok=True)
    os.makedirs(output_middle, exist_ok=True)
    os.makedirs(output_lower, exist_ok=True)

    ct_folders = [os.path.join(case_folder, sub_folder) for sub_folder in os.listdir(case_folder)
                  if os.path.isdir(os.path.join(case_folder, sub_folder)) and sub_folder.startswith("CT")]

    for ct_folder in ct_folders:
        ct_name = os.path.basename(ct_folder)  # CT1とCT2のフォルダ名を取得

        # 出力フォルダ内にCT1, CT2フォルダを作成
        output_upper_ct = os.path.join(output_upper, ct_name)
        output_middle_ct = os.path.join(output_middle, ct_name)
        output_lower_ct = os.path.join(output_lower, ct_name)

        os.makedirs(output_upper_ct, exist_ok=True)
        os.makedirs(output_middle_ct, exist_ok=True)
        os.makedirs(output_lower_ct, exist_ok=True)

        dicom_files = sorted([f for f in os.listdir(ct_folder) if f.endswith(".DCM")], reverse=True)

        for file_name in dicom_files:
            slice_num_str = file_name.split('.')[0]  # ファイル名の番号部分 (例: 00000001)

            try:
                # 8桁の番号を整数に変換してスライス番号として扱う
                slice_num = int(slice_num_str)

            except ValueError:
                print(f"ファイル名 {file_name} からスライス番号を取得できませんでした。")
                continue

            # DICOMファイルを読み込み、エラーチェック
            dicom_file_path = os.path.join(ct_folder, file_name)
            dicom_data = validate_dicom_file(dicom_file_path)

            if dicom_data is None: 
                # DICOMファイルが正しく読み込めない場合はスキップ
                continue

            # 上部：上端スライスから大動脈の上端までの範囲を指定
            if slice_num <= seg1_start:
                shutil.copy(dicom_file_path, os.path.join(output_upper_ct, file_name))
            # 中部：大動脈の上端から肝臓の上端までの範囲
            elif seg1_start < slice_num <= seg2_start:
                shutil.copy(dicom_file_path, os.path.join(output_middle_ct, file_name))
            # 下部：肝臓の上端から末端スライスまでの範囲
            else:
                shutil.copy(dicom_file_path, os.path.join(output_lower_ct, file_name))

    print(f"{case_folder} のDICOMファイルが正常に分割されました。")

def process_all_cases(dataset_folder, seg1_nifti_base, seg2_nifti_base, output_base):
    case_folders = [os.path.join(dataset_folder, case) for case in os.listdir(dataset_folder)
                    if os.path.isdir(os.path.join(dataset_folder, case))]

    for case_folder in case_folders:
        case_name = os.path.basename(case_folder)

        # 対応するセグメンテーションデータのパスを生成
        seg1_nifti = os.path.join(seg1_nifti_base, f"{case_name}_CT2", f"aorta_{case_name}_CT2.nii.gz")
        seg2_nifti = os.path.join(seg2_nifti_base, f"{case_name}_CT2", f"liver_{case_name}_CT2.nii.gz")

        # 出力フォルダ名を設定
        output_upper = os.path.join(output_base + "_upper", f"{case_name}")
        output_middle = os.path.join(output_base + "_middle", f"{case_name}")
        output_lower = os.path.join(output_base + "_lower", f"{case_name}")

        # 各ケースを処理
        split_dicom_files(dataset_folder, case_folder, seg1_nifti, seg2_nifti, output_upper, output_middle, output_lower)

# 入力フォルダと出力フォルダのパス
dataset_folder = '~/dataset'
seg1_nifti_base = '~/totalSegmentator/organSeg/dataset_aorta'
seg2_nifti_base = '~/totalSegmentator/organSeg/dataset_liver'
output_base = dataset_folder

# 全てのケースを処理
process_all_cases(dataset_folder, seg1_nifti_base, seg2_nifti_base, output_base)
  