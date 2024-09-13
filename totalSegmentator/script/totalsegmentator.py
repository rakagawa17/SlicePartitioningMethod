from totalsegmentator.python_api import totalsegmentator
import nibabel as nib
import numpy as np
import os

#スライス分割のためthyroid_gland, whole_lung, kidneyの3つのマスクを作成する
def thyroid_gland_segmentation(input_file, output_folder):
    # 患者IDをファイル名から取得
    patient_id = os.path.basename(input_file)[:-7]  # '.nii.gz'を除外
    output_path = os.path.join(output_folder, patient_id)

    # 出力フォルダが存在しない場合は作成
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # 検出するマスク
    mask = ["thyroid_gland"]

    # マスクの作成を実行
    totalsegmentator(input_file, output_path, roi_subset=mask)

    # マスク画像の読み込み
    ref_img_path = os.path.join(output_path, "thyroid_gland.nii.gz")
    if not os.path.exists(ref_img_path):
        print(f"マスクファイルが見つかりません: {ref_img_path}")
        return

    ref_img = nib.load(ref_img_path)
    combined = np.zeros(ref_img.shape, dtype=np.uint8)

    # マスクデータを処理し、しきい値で二値化
    img = ref_img.get_fdata()
    combined[img > 0.5] = 1

    # 新しいマスクファイルを保存
    thyroid_img = nib.Nifti1Image(combined, ref_img.affine)
    thyroid_path = os.path.join(output_path, "thyroid_gland.nii")
    nib.save(thyroid_img, thyroid_path)

    # 圧縮したマスクファイルを保存
    thyroid_gz_path = os.path.join(output_path, f"thyroid_gland_{os.path.basename(input_file)[-19:]}")
    img = nib.load(thyroid_path)
    nib.save(img, thyroid_gz_path)

    # 一時ファイルを削除
    os.remove(thyroid_path)
    os.remove(ref_img_path)

# def whole_lung_segmentation(input_file, output_folder):

# def kidney_segmentation(input_file, output_folder):

def main():
    # 入力フォルダと出力フォルダのパスを指定
    input_folder = '/niftifolder'
    output_folder = 'organSeg/dataset'

    # 入力フォルダ内の全ての .nii.gz ファイルを処理
    for filename in os.listdir(input_folder):
        if filename.endswith('.nii.gz'):
            input_file = os.path.join(input_folder, filename)
            thyroid_gland_segmentation(input_file, output_folder)
            # whole_lung_segmentation(input_file, output_folder)
            # kidney_segmentation(input_file, output_folder)

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()

