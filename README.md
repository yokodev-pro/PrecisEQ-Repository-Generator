# PrecisEQ Repository Generator

[English](#english) | [中文](#中文)

---

<a id="english"></a>

Simply upload the frequency response measurement data (CSV) of your headphones to automatically generate a dedicated online headphone calibration repository for PrecisEQ. Calibration files are generated using AutoEq.

### Repository Address

After you upload the CSV files for the first time and successfully generate the headphone calibration files, the following URL will be automatically replaced with your own repository address. Enter it in **Headphone Calibration -> Headphone model -> Repo -> Import**:
<!-- URL_START -->
```
https://raw.githubusercontent.com/yokodev-pro/PrecisEQ-Repository-Generator/main/RepositoryFiles/
```
<!-- URL_END -->

### How to Use

#### Step 1: Fork and customize repository info
1. Click **Use this template** at the top right to create your own **Public** repository.
2. Modify the repository information in [RepositoryFiles/repo_info.json](RepositoryFiles/repo_info.json).

#### Step 2: Upload measurement data
1. Collect your headphone frequency response measurement files (`.csv` format), and name them according to the rule: `Brand Model.csv`, for example `Sony IER-Z1R.csv`, `Sennheiser IE 900.csv`.
2. Enter the corresponding folder in the repository based on the headphone type:
   - In-Ear: [measurements/0_in-ear/](measurements/0_in-ear/)
   - Over-Ear (Open-Back): [measurements/1_open-back/](measurements/1_open-back/)
   - Over-Ear (Closed-Back): [measurements/2_closed-back/](measurements/2_closed-back/)
3. Click **Add file -> Upload files**, drag and drop the `.csv`, and submit (Commit changes).
4. If you want to **update** measurement data for a headphone, just upload a new CSV file with the same name to overwrite the old file.

#### Step 3: Wait for processing
- After submitting the files, GitHub will process them automatically. You can click the **Actions** tab at the top of the repository to check progress.
- After processing is complete (usually takes a few minutes), the generated IRs will be stored in the [RepositoryFiles](RepositoryFiles) folder, which PrecisEQ will download for headphone calibration. The [images](images) folder will be used to store the generated frequency response graphs; these images are for manual inspection only and PrecisEQ will not download them.
- Restart PrecisEQ to sync the repository content.

#### Optional Steps
- **Chinese Localization**: If you want to add Chinese localization for brand and model names, add the Chinese name to the second item in the list in [RepositoryFiles/headphone_list.json](RepositoryFiles/headphone_list.json):
  ```json
  "brandName": ["Brand", "品牌名"],
  "modelName": ["Model Name", "型号名"]
  ```
- **Subjective Volume Correction**: If there is a significant difference in subjective volume perception before and after calibrating a headphone, modifying the `noDspOffsetDb` field in [RepositoryFiles/headphone_list.json](RepositoryFiles/headphone_list.json) can increase/decrease the volume before calibration, in dB.

### Directory Description
* [measurements/](measurements/) - Stores headphone frequency response measurement data (CSV).
* [RepositoryFiles/](RepositoryFiles/) - Automatically generated PrecisEQ repository folder, containing repository description JSON and IR files.
* [images/](images/) - Automatically generated headphone and calibration frequency response graphs.
* [scripts/](scripts/) - Python backend operational scripts for automated processing.

---

<a id="中文"></a>

只需要简单地上传耳机的频率响应测量数据（CSV），就能自动化生成 PrecisEQ 专用的在线耳机校准仓库。校准文件使用 AutoEq 生成。

### 仓库地址

首次上传 CSV 文件并成功生成耳机校准文件后，以下链接会自动替换为你的仓库地址。在 **耳机校准 -> 耳机型号 -> 仓库 -> 导入** 填入：
<!-- URL_START -->
```
https://raw.githubusercontent.com/yokodev-pro/PrecisEQ-Repository-Generator/main/RepositoryFiles/
```
<!-- URL_END -->

### 如何使用

#### 第一步：获取和自订仓库信息
1. 点击右上角的 **Use this template** 创建一个你自己的 **公开（Public）** 仓库。
2. 修改 [RepositoryFiles/repo_info.json](RepositoryFiles/repo_info.json) 中的仓库信息。

#### 第二步：上传测量数据
1. 收集你的耳机频响测量文件（`.csv` 格式），并按以下规则命名：`品牌 型号.csv`，例如 `Sony IER-Z1R.csv`、`Sennheiser IE 900.csv`。
2. 根据耳机的类型，进入仓库里的对应文件夹：
   - 入耳式：[measurements/0_in-ear/](measurements/0_in-ear/)
   - 头戴式（开放）：[measurements/1_open-back/](measurements/1_open-back/)
   - 头戴式（封闭）：[measurements/2_closed-back/](measurements/2_closed-back/)
3. 点击 **Add file -> Upload files**，把 `.csv` 拖入并提交（Commit changes）。
4. 如果你要**更新**某款耳机的测量数据，上传同名的新 CSV 文件覆盖旧文件即可。

#### 第三步：等待处理
- 提交文件后，GitHub 会自动处理。你可以点击仓库顶部的 **Actions** 标签查看进度。
- 处理完成后（通常需要几分钟），生成的 IR 会存放在 [RepositoryFiles](RepositoryFiles) 文件夹，PrecisEQ 将下载这些文件用于耳机校准；[images](images) 文件夹用于存放生成的频响曲线图，这些图片仅用于人工核查，PrecisEQ 不会下载这些图片。
- 重新启动 PrecisEQ 即可同步仓库内容。

#### 可选步骤
- **中文本地化**：如果你想为品牌名、型号名添加中文本地化，在 [RepositoryFiles/headphone_list.json](RepositoryFiles/headphone_list.json) 把中文添加到列表第二项：
  ```json
  "brandName": ["Brand", "品牌名"],
  "modelName": ["Model Name", "型号名"]
  ```
- **主观音量校正**：如果某个耳机校准前后的主观音量感受有明显差异，修改 [RepositoryFiles/headphone_list.json](RepositoryFiles/headphone_list.json) 中的 `noDspOffsetDb` 字段可以增大/减小校准前的音量，单位为dB。

### 目录说明
* [measurements/](measurements/) - 存放耳机频率响应测量数据（CSV）。
* [RepositoryFiles/](RepositoryFiles/) - 自动生成的 PrecisEQ 仓库文件夹，包含仓库描述 JSON 和 IR 文件。
* [images/](images/) - 自动生成的耳机和校准频响图。
* [scripts/](scripts/) - 后台运行的 Python 自动化处理脚本。
