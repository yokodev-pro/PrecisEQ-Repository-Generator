import os
import re
import json
import shutil
import subprocess
import sys
import hashlib
from pathlib import Path

def sanitize_id(name):
    return re.sub(r'[\W_]+', '', name).lower()

def parse_brand_model(name):
    parts = name.split()
    if len(parts) == 1:
        return parts[0], ""
        
    brand_suffixes = ["audio", "acoustics", "ears", "ear", "hifi", "acousticwerkes", "design"]
    brand_parts = [parts[0]]
    model_start_idx = 1
    
    if len(parts) >= 3 and parts[1].lower() in ["&", "x"]:
        brand_parts.extend(parts[1:3])
        model_start_idx = 3
        
    while model_start_idx < len(parts):
        word = parts[model_start_idx]
        clean_word = re.sub(r'[\W_]+', '', word).lower()
        if clean_word in brand_suffixes:
            brand_parts.append(word)
            model_start_idx += 1
        else:
            break
            
    brand = " ".join(brand_parts)
    model = " ".join(parts[model_start_idx:])
    return brand, model

def get_file_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def update_readme_url():
    # If run in GitHub Actions, update the README with the URL
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        return
        
    username, repo_name = repo.split('/')
    url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/RepositoryFiles/"
    
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        # Replace the URL between <!-- URL_START --> and <!-- URL_END -->
        def replace_url(match):
            block_content = match.group(1)
            updated_block = re.sub(r'https://[^\s`\'"]+', url, block_content)
            return "<!-- URL_START -->" + updated_block + "<!-- URL_END -->"
            
        new_content = re.sub(r"<!-- URL_START -->(.*?)<!-- URL_END -->", replace_url, content, flags=re.DOTALL)
        readme_path.write_text(new_content, encoding='utf-8')

def main():
    # 改为基于当前脚本所在位置寻找项目根目录，避免因为执行时的路径不同导致找错文件夹
    base_dir = Path(__file__).resolve().parent.parent
    measurements_dir = base_dir / "measurements"
    repo_files_dir = base_dir / "RepositoryFiles"
    images_dir = base_dir / "images"
    sync_state_file = base_dir / "sync_state.json"
    
    repo_files_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Load sync state
    sync_state = {}
    if sync_state_file.exists():
        try:
            with open(sync_state_file, 'r', encoding='utf-8') as f:
                sync_state = json.load(f)
        except Exception as e:
            print(f"Error loading sync_state.json: {e}")

    # Scan measurements
    current_scan = {}
    type_dirs = {
        "0_in-ear": 0,
        "1_open-back": 1,
        "2_closed-back": 2
    }
    
    for type_dir_name, hp_type in type_dirs.items():
        type_dir = measurements_dir / type_dir_name
        if not type_dir.exists():
            type_dir.mkdir(parents=True, exist_ok=True)
            continue
            
        for csv_file in type_dir.glob("*.csv"):
            original_name = csv_file.stem
            hp_id = sanitize_id(original_name)
            md5_hash = get_file_md5(csv_file)
            
            # If multiple csvs resolve to the same hp_id, we just overwrite (last one wins)
            current_scan[hp_id] = {
                "original_name": original_name,
                "type": hp_type,
                "csv_path": csv_file,
                "hash": md5_hash
            }

    # Compare state and find changes
    to_process = []
    deleted = []
    
    for hp_id, state in list(sync_state.items()):
        if hp_id not in current_scan:
            deleted.append(hp_id)
            
    for hp_id, current in current_scan.items():
        if hp_id not in sync_state:
            current["version"] = 1
            to_process.append(hp_id)
        elif sync_state[hp_id]["hash"] != current["hash"]:
            current["version"] = sync_state[hp_id]["version"] + 1
            to_process.append(hp_id)
        else:
            current["version"] = sync_state[hp_id]["version"]
            
    # Handle deleted
    for hp_id in deleted:
        print(f"Deleting removed headphone: {hp_id}")
        for wav_file in repo_files_dir.glob(f"{hp_id}_*.wav"):
            wav_file.unlink()
        png_file = images_dir / f"{hp_id}.png"
        if png_file.exists():
            png_file.unlink()
        del sync_state[hp_id]

    if not to_process and not deleted:
        print("No changes detected. Exiting.")
        update_readme_url()
        return

    if to_process:
        print(f"Found {len(to_process)} headphones to process.")
        
        type_targets = {
            0: base_dir / "targets" / "0_zero.csv",
            1: base_dir / "targets" / "1_zero.csv",
            2: base_dir / "targets" / "2_zero.csv"
        }
        
        by_type = {}
        for hp_id in to_process:
            t = current_scan[hp_id]["type"]
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(hp_id)
            
        for hp_type, ids in by_type.items():
            print(f"Processing type {hp_type} with {len(ids)} headphones...")
            temp_in = base_dir / "temp_in"
            temp_out = base_dir / "temp_out"
            temp_in.mkdir(parents=True, exist_ok=True)
            temp_out.mkdir(parents=True, exist_ok=True)
            
            target_path = type_targets.get(hp_type, base_dir / "targets")
            
            for hp_id in ids:
                csv_path = current_scan[hp_id]["csv_path"]
                (temp_in / csv_path.parent.name).mkdir(parents=True, exist_ok=True)
                shutil.copy2(csv_path, temp_in / csv_path.parent.name / csv_path.name)
                
                for old_wav in repo_files_dir.glob(f"{hp_id}_*.wav"):
                    old_wav.unlink()
                
            cmd = [
                sys.executable, "-m", "autoeq",
                "--input-dir", str(temp_in),
                "--output-dir", str(temp_out),
                "--target", str(target_path),
                "--fs", "44100,48000,96000,192000",
                "--convolution-eq",
                "--phase", "minimum",
                "--bit-depth", "32",
                "--preamp", "-11.8"
            ]
        
            try:
                print("Running AutoEq...")
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"AutoEq warning/error: {e}")
                # Even if there is an error, some might have been generated, we proceed to harvest
                
            # Process AutoEq output
            successful_hp_ids = set()
            wav_files = list(temp_out.rglob("*.wav"))
            for wav_file in wav_files:
                filename = wav_file.name
                match = re.search(r'^(.*?)\s+minimum\s+phase\s+(\d+)\s*Hz\.wav$', filename, re.IGNORECASE)
                if not match:
                    continue
                    
                orig_name_out = match.group(1).strip()
                fs_str = match.group(2)
                
                fs_map = {'44100': '44', '48000': '48', '96000': '96', '192000': '192'}
                mapped_fs = fs_map.get(fs_str)
                if not mapped_fs:
                    continue
                    
                out_hp_id = sanitize_id(orig_name_out)
                if out_hp_id not in ids:
                    continue
                    
                successful_hp_ids.add(out_hp_id)
                version = current_scan[out_hp_id]["version"]
                new_wav_name = f"{out_hp_id}_{version}_{mapped_fs}.wav"
                
                dest_wav_path = repo_files_dir / new_wav_name
                shutil.copy2(wav_file, dest_wav_path)
                
            for hp_id in ids:
                if hp_id not in successful_hp_ids:
                    print(f"Warning: Failed to generate or copy files for {hp_id}. Skipping state update.")
                    continue
                    
                orig_name = current_scan[hp_id]["original_name"]
                parent_dir_name = current_scan[hp_id]["csv_path"].parent.name
                
                # 兼容不同 AutoEq 输出结构的图片寻址
                img_file = temp_out / parent_dir_name / orig_name / f"{orig_name}.png"
                if not img_file.exists():
                    img_file = temp_out / parent_dir_name / f"{orig_name}.png"
                if not img_file.exists():
                    img_file = temp_out / orig_name / f"{orig_name}.png"
                if not img_file.exists():
                    img_file = temp_out / f"{orig_name}.png"
                
                if img_file.exists():
                    dest_img_path = images_dir / f"{hp_id}.png"
                    shutil.copy2(img_file, dest_img_path)
                    
                sync_state[hp_id] = {
                    "hash": current_scan[hp_id]["hash"],
                    "version": current_scan[hp_id]["version"],
                    "type": current_scan[hp_id]["type"],
                    "original_name": current_scan[hp_id]["original_name"]
                }
                
            # Cleanup
            shutil.rmtree(temp_in, ignore_errors=True)
            shutil.rmtree(temp_out, ignore_errors=True)

    # Rebuild headphone_list.json
    headphone_list = []
    # Sort for consistent output
    for hp_id in sorted(sync_state.keys()):
        state = sync_state[hp_id]
        brand, model = parse_brand_model(state["original_name"])
        headphone_info = {
            "id": hp_id,
            "type": state["type"],
            "brandName": [brand] if brand else [],
            "modelName": [model] if model else [],
            "version": state["version"],
            "noDspOffsetDb": 0.0
        }
        headphone_list.append(headphone_info)
        
    json_path = repo_files_dir / "headphone_list.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(headphone_list, f, indent=2, ensure_ascii=False)
        
    with open(sync_state_file, 'w', encoding='utf-8') as f:
        json.dump(sync_state, f, indent=2, ensure_ascii=False)

    print("Finished processing and saved metadata.")
    update_readme_url()

if __name__ == "__main__":
    main()
