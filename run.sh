#!/bin/bash
base_path="${HOME}/clash_sub"
cd ${base_path}
git pull
source "venv/bin/activate"
python main.py
deactivate
git checkout kernel/config.yaml
time=$(date "+%Y%m%d-%H%M%S")
git commit -a -m "${time}更新"
git push
echo "配置回溯"
origin_config=/etc/mihomo/config.yaml
rm ${origin_config}
cp ${origin_config}.bak ${origin_config}
curl -v -X PUT -H "Content-Type: application/json" -d '{"path": "'"${origin_config}"'"}' -L 'http://127.0.0.1:33451/configs?force=true'
systemctl restart mihomo
