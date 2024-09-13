import os
import dicom2nifti
import shutil

def convert_dicom_to_nifti(dicom_folder, nifti_output_folder):
    # DICOMファイルが格納されているディレクトリ（case0001, case0002, case0003...）
    # 変換後のNIfTIファイルを保存するディレクトリ

    # 各ケースディレクトリを走査
    for case in os.listdir(dicom_folder):
        case_path = os.path.join(dicom_folder, case)
        if os.path.isdir(case_path):
            # CT1フォルダを探す
            ct1_path = os.path.join(case_path, 'CT1')
            # ct1_path = os.path.join(case_path, 'CT2')
            if os.path.isdir(ct1_path):
                # 一時出力先ディレクトリを指定
                temp_output_folder = os.path.join(nifti_output_folder, "temp")
                os.makedirs(temp_output_folder, exist_ok=True)
                
                # DICOMをNIfTIに変換
                try:
                    dicom2nifti.convert_directory(ct1_path, temp_output_folder, compression=True, reorient=True)
                    
                    # 変換されたファイルを見つけてリネーム
                    for file_name in os.listdir(temp_output_folder):
                        if file_name.endswith('.nii.gz'):
                            source_file = os.path.join(temp_output_folder, file_name)
                            target_file = os.path.join(nifti_output_folder, f"{case}_CT1.nii.gz")
                            # target_file = os.path.join(nifti_output_folder, f"{case}_CT2.nii.gz")
                            shutil.move(source_file, target_file)
                            print(f"Successfully converted {ct1_path} to {target_file}")
                except Exception as e:
                    print(f"Failed to convert {ct1_path}: {str(e)}")
                finally:
                    # 一時出力先ディレクトリをクリーンアップ
                    shutil.rmtree(temp_output_folder)

# 使用例
dicom_folder = ''  # DICOMファイルの親フォルダへのパス
nifti_output_folder = ''  # NIfTIファイルを保存するフォルダへのパス

convert_dicom_to_nifti(dicom_folder, nifti_output_folder)

