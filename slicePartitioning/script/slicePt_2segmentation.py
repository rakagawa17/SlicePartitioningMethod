import os
import shutil
import nibabel as nib
import pydicom

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

# ※ 注意：seg1_start < seg2_startとなるようにしてください
def split_dicom_files(dataset_folder, seg1_nifti, seg2_nifti, output_upper, output_middle, output_lower):
    # NIfTI ファイルからを最初のスライス番号のindex取得
    seg1_start = get_nifti_slice_range(seg1_nifti)
    seg2_start = get_nifti_slice_range(seg2_nifti)
    print(f"segmentation1の初めのスライス番号：{seg1_start}\nsegmentation2の初めのスライス番号：{seg2_start}")

    if seg1_start is None or seg2_start is None:
        print("セグメンテーションデータに有効なスライスが見つかりません。")
        return

    # DICOMファイルを分割するためのフォルダを作成
    os.makedirs(output_upper, exist_ok=True)
    os.makedirs(output_middle, exist_ok=True)
    os.makedirs(output_lower, exist_ok=True)

    # DICOMファイルを取得し、スライス番号を逆順に処理して対応するフォルダにコピー
    dicom_files = sorted([f for f in os.listdir(dataset_folder) if f.endswith(".DCM")], reverse=True)

    for file_name in dicom_files:
        slice_num_str = file_name.split('.')[0]  # ファイル名の番号部分 (例: 00000001)

        try:
            # 8桁の番号を整数に変換してスライス番号として扱う
            slice_num = int(slice_num_str)

        except ValueError:
            print(f"ファイル名 {file_name} からスライス番号を取得できませんでした。")
            continue

        # DICOMファイルを読み込み、エラーチェック
        dicom_file_path = os.path.join(dataset_folder, file_name)
        dicom_data = validate_dicom_file(dicom_file_path)

        if dicom_data is None: 
            # DICOMファイルが正しく読み込めない場合はスキップ
            continue

        # 逆順のスライス番号に基づいて DICOM ファイルを対応するフォルダにコピー
        if slice_num <= seg1_start:
            shutil.copy(dicom_file_path, os.path.join(output_upper, file_name))
        elif seg1_start < slice_num <= seg2_start:
            shutil.copy(dicom_file_path, os.path.join(output_middle, file_name))
        else:
            shutil.copy(dicom_file_path, os.path.join(output_lower, file_name))

    print("DICOMファイルが正常に分割されました．")

# 入力フォルダと出力フォルダのパス
dataset_folder = '/Users/akagawa/Downloads/demo/sample/case0001/CT1'
seg1_nifti = '/Users/akagawa/Downloads/demo/sample/organ/case0001_CT2/aorta_case0001_CT2.nii.gz'
seg2_nifti = '/Users/akagawa/Downloads/demo/sample/organ/case0001_CT2/liver_case0001_CT2.nii.gz'

output_path = '/Users/akagawa/Downloads/demo/sample/case0001'
output_upper = output_path + '_upper'
output_middle = output_path + '_middle'
output_lower = output_path + '_lower'
# DICOMファイルを分割して保存
split_dicom_files(dataset_folder, seg1_nifti, seg2_nifti, output_upper, output_middle, output_lower)
