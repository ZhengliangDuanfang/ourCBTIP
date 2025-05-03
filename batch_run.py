import subprocess

conda_python = "/home/dell/anaconda3/envs/torch17_biomip/bin/python"

# 定义训练脚本和参数列表
training_scripts = [
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0", "--constant", "0", "-lr", "0.001", "--max_epoch", "1"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0", "--constant", "0", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "1", "--constant", "0.5", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "1", "--constant", "0.1", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "1", "--constant", "0", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0.01", "--constant", "0.5", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0.01", "--constant", "0.1", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0.01", "--constant", "0", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0.0001", "--constant", "0.5", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0.0001", "--constant", "0.1", "-lr", "0.001", "--max_epoch", "500"]},
    {"script": "train_main.py", "args": ["-d", "CB-DB", "-sp", "811-1", "--gpu", "2", "--alpha_loss", "1", "--beta_loss", "0.3", "--gamma_loss", "0.001", "--delta_loss", "0.0001", "--constant", "0", "-lr", "0.001", "--max_epoch", "500"]},
]

# 依次运行每个训练脚本
for task in training_scripts:
    script = task["script"]
    args = task["args"]
    print(f"Running {script} with args: {args}")
    result = subprocess.run([conda_python, script] + args, capture_output=True, text=True)
    
    # 检查是否有错误
    if result.returncode != 0:
        print(f"Error occurred while running {script}:")
        print(result.stderr)
        break
    else:
        print(f"{script} completed successfully.\n")