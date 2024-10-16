from totalsegmentator.python_api import totalsegmentator
import nibabel as nib
import numpy as np
import os

def process_file(input_file, output_folder, masks, combined_filename):
    patient_id = os.path.basename(input_file)[:-7]  # '.nii.gz'を除外
    output_path = os.path.join(output_folder, patient_id)

    # 出力フォルダ作成
    os.makedirs(output_path, exist_ok=True)

    # マスクの作成
    totalsegmentator(input_file, output_path, roi_subset=masks)

    # 結合マスクの初期化
    combined = None

    # 各マスクのデータを処理して結合
    for mask in masks:
        ref_img_path = os.path.join(output_path, f"{mask}.nii.gz")
        if not os.path.exists(ref_img_path):
            print(f"マスクファイルが見つかりません: {ref_img_path}")
            continue

        ref_img = nib.load(ref_img_path)
        img = ref_img.get_fdata()

        if combined is None:
            combined = np.zeros(ref_img.shape, dtype=np.uint8)

        combined[img > 0.5] = 1

    # 結合したマスクを保存
    if combined is not None:
        combined_img = nib.Nifti1Image(combined, ref_img.affine)
        combined_path = os.path.join(output_path, f"{combined_filename}.nii")
        nib.save(combined_img, combined_path)

        # 圧縮保存と一時ファイル削除
        combined_gz_path = os.path.join(output_path, f"{combined_filename}_{os.path.basename(input_file)[-19:]}")
        nib.save(nib.load(combined_path), combined_gz_path)
        os.remove(combined_path)

    # 個別のマスクファイルを削除
    for mask in masks:
        ref_img_path = os.path.join(output_path, f"{mask}.nii.gz")
        if os.path.exists(ref_img_path):
            os.remove(ref_img_path)

def main():
    
    inputfol = '/home/akagawa/Desktop/wd_black/test_nifti/CT2'
    # 入力と出力フォルダのリスト
    input_output_mask_data = [
        (inputfol, '/home/akagawa/totalsegmentator/organs/test_NCCT_kidney', ['kidney_right', 'kidney_left'], 'kidney'),
        (inputfol, '/home/akagawa/totalsegmentator/organs/test_NCCT_wholelung', ['lung_upper_lobe_right', 'lung_middle_lobe_right', 'lung_lower_lobe_right', 'lung_upper_lobe_left', 'lung_lower_lobe_left'], 'wholelung'),
        (inputfol, '/home/akagawa/totalsegmentator/organs/test_NCCT_thyroid', ['thyroid_gland'], 'thyroid_gland')
    ]

    # 各フォルダの処理
    for input_folder, output_folder, masks, combined_filename in input_output_mask_data:
        for filename in os.listdir(input_folder):
            if filename.endswith('.nii.gz'):
                process_file(os.path.join(input_folder, filename), output_folder, masks, combined_filename)

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()