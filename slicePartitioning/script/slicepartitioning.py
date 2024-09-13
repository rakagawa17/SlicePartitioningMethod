import os
import shutil
import nibabel as nib

def copy_slices_up_to_segmentation(nifti_dir, src_dir, dst_dir, organ_name, copy_all=False):
    """
    NIfTIファイルからスライスを調べて、該当するスライスまでDCMファイルをコピーする関数。
    copy_all=Trueの場合、セグメンテーションスライスに到達するまでの全スライスをコピーする。

    Parameters:
    nifti_dir (str): NIfTIファイルが格納されているフォルダのパス
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

#入力：dataset01 or dataset02
src_dir = 'dataset'

# 呼び出し例
copy_slices_up_to_segmentation(
    nifti_dir='totalSegmentator/organSeg/thyloid_gland_segmentation',
    src_dir = src_dir,
    dst_dir='dataset_upper',
    organ_name='thyroid_gland',
    copy_all=True
)

copy_slices_up_to_segmentation(
    nifti_dir='totalSegmentator/organSeg/lung_segmentation,
    src_dir = src_dir,
    dst_dir='dataset_middle',
    organ_name='whole_lung',
    copy_all=False
)

copy_slices_up_to_segmentation(
    nifti_dir='totalSegmentator/organSeg/kidney_segmentation',
    src_dir = src_dir,
    dst_dir='dataset_lower',
    organ_name='kidney',
    copy_all=False  
)

