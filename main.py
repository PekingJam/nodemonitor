import traceback
import subprocess
import uuid

import core.sub as core
from push.tg_bot import push_message
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        core.get_sub()
        try:
            # 使用 subprocess.run 执行 git restore .
            # subprocess.run("git restore .", shell=True, check=True)
            print("Git restore command executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing git restore command: {e}")
        sys.exit(0)
    try:
        # core.get_sub()
        dirs = [f'proxies/proxies.yaml',
                f'release/release.yaml',
                f'proxies/one_proxies.yaml',
                f'release/one_release.yaml',
                f'proxies/pc_proxies.yaml',
                f'release/pc_release.yaml',
                f'release/mob_release.yaml',
                f'release/tcl_release.yaml',
                f"proxies/tcl.txt",
                f"release/tcl_release.txt",
                ]
        # core.Utl.dav(dirs, "/clash")
        core.Utl.upload_to_upyun(dirs, "/d/sub/clash")
        core.Utl.upload_to_myoss(dirs, "clash/subs")
        # core.mail.SendEmail.send_email(f"clash订阅更新", f'🟢更新成功\n🔎{time.strftime("%m-%d %H:%M", time.localtime())}')
    except Exception as e:
        traceback.print_exc()
        # 推送错误日志
        push_message("clash_sub程序main处错误", f"uuid: {uuid.uuid1()} \n 错误日志：{str(e)}")
