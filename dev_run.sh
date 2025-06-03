#/bin/bash
base_path="${HOME}/items/clash_sub_optimize"
cd ${base_path}
git pull
./venv/bin/python3 ./main.py debug
time=$(date "+%Y%m%d-%H%M%S")
git checkout .
git status
