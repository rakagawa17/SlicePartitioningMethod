import os
import pydicom
import numpy as np
import shutil  

# 入力フォルダのパス
folders = [
    '/Users/akagawa/Research/Pix2Pix/result/upper/test_NCCT_upper',
    '/Users/akagawa/Research/Pix2Pix/result/middle/test_NCCT_middle',
    '/Users/akagawa/Research/Pix2Pix/result/lower/test_NCCT_lower'
]
folder_path = folders[0]
cases = []  

cases = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

# 加重平均用の重みリスト（必要に応じて変更）
weights = {
    'upper': 0.5,  # 上部の重み
    'middle': 0.5,  # 中部の重み
    'lower': 0.5   # 下部の重み
}

# DICOMファイルの処理
for case in cases:
    # 各ケースごとに出力フォルダを作成
    output_folder = f'/Users/akagawa/Research/Pix2Pix/result/unity/test_NCCT/{case}'
    os.makedirs(output_folder, exist_ok=True)

    # 各フォルダのdicomファイルのパスを取得
    dicom_files = {}
    all_files = set()  # 全てのファイルを保存するセット
    for folder in folders:
        dicom_folder = os.path.join(folder, case, 'dicom')
        if os.path.exists(dicom_folder):
            for file in os.listdir(dicom_folder):
                if file.endswith('.DCM'):
                    all_files.add(file)  # 全てのファイルをセットに追加
                    if file not in dicom_files:
                        dicom_files[file] = []
                    dicom_files[file].append(os.path.join(dicom_folder, file))

    # 全てのファイルを処理
    for file_name in all_files:
        if file_name in dicom_files and len(dicom_files[file_name]) > 1:  # 重複するDCMファイルが存在する場合
            print(f"重複するファイル名: {file_name} -> {dicom_files[file_name]}")

            # すべてのDCMファイルを読み込む
            dcm_images = [pydicom.dcmread(path) for path in dicom_files[file_name]]

            # フォルダに基づいて適切な重みを取得
            folder_names = []
            for path in dicom_files[file_name]:
                # フォルダ構造から 'upper', 'middle', 'lower' を特定する
                split_path = path.split(os.sep)  # パスを分割
                for part in split_path:
                    if part in weights:
                        folder_names.append(part)
                        break  # 見つけたら次のファイルへ

            # 加重平均用の重みを取得
            weights_for_files = np.array([weights[folder] for folder in folder_names])

            # ピクセルデータを加重平均化
            pixel_arrays = [dcm.pixel_array.astype(np.float32) for dcm in dcm_images]
            weighted_pixel_arrays = np.array([pixel_array * weight for pixel_array, weight in zip(pixel_arrays, weights_for_files)])
            averaged_pixels = np.sum(weighted_pixel_arrays, axis=0) / np.sum(weights_for_files)

            # 平均化したデータを最初のDCMファイルに書き戻し
            averaged_dcm = dcm_images[0]
            averaged_pixels = averaged_pixels.astype(np.uint16)  # データ型を元に戻す
            averaged_dcm.PixelData = averaged_pixels.tobytes()

            # 新しいファイル名と出力パスを定義
            output_path = os.path.join(output_folder, f'{case}_{file_name}')
            averaged_dcm.save_as(output_path)
            print(f'Weighted Averaged DICOM file saved: {output_path}')

        else:
            # 重複しないファイルはそのままコピー
            source_file_path = dicom_files[file_name][0]
            output_path = os.path.join(output_folder, f'{case}_{file_name}')
            shutil.copy(source_file_path, output_path)
            print(f'Copied DICOM file: {output_path}')
