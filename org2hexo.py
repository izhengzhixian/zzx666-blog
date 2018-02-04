#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sys
import json
import shutil


# config
config_json = {
    "org_blog_path": ".",
    "hexo_path": "~/blog",
    "npm": "npm"
}
org_blog_path = os.path.dirname(os.path.realpath(__file__))
hexo_path = os.path.expanduser("~/blog")
config_path = os.path.expanduser("~/.org2hexo.config")
npm = "npm"


def load_config():
    global org_blog_path
    global hexo_path
    global config_json
    global config_path
    global npm
    if not os.path.exists(config_path):
        with open(config_path, "w") as con:
            con.write(json.dumps(config_json, ensure_ascii=False, indent=4))
        return False
    with open(config_path) as con:
        config = json.loads(con.read())

        config_org_hexo_path = config.get("org_hexo_path")
        if config_org_hexo_path:
            config_org_hexo_path = os.path.expanduser(config_org_hexo_path)
            org_blog_path = os.path.join(org_blog_path, config_org_hexo_path)

        config_hexo_path = config.get("hexo_path")
        if config_hexo_path:
            config_hexo_path = os.path.expanduser(config_hexo_path)
            hexo_path = os.path.join(hexo_path, config_hexo_path)

        config_npm = config.get("npm")
        if config_npm:
            npm = config_npm
    return True


def copy_tree(src, dest):
    if not os.path.exists(src):
        return False
    if not os.path.exists(dest):
        os.makedirs(dest)
    for fi in os.listdir(src):
        if fi == "." or fi == "..":
            continue
        if os.path.isdir(os.path.join(src, fi)):
            copy_tree(os.path.join(src, fi), os.path.join(dest, fi))
        else:
            shutil.copyfile(os.path.join(src, fi), os.path.join(dest, fi))
    return True


def hexo_init(init_path=[]):
    if len(init_path) != 0:
        os.system("hexo init " + init_path[0])
    else:
        hexo_split = os.path.split(hexo_path)
        os.chdir(hexo_split[0])
        os.system("hexo init " + hexo_split[1])
    return True


def hexo_init_after(init_path=[]):
    if len(init_path) != 0:
        os.chdir(init_path[0])
    else:
        os.chdir(hexo_path)
        # 删除_posts文件夹下的文件
    _posts_path = os.path.join(hexo_path, "source/_posts")
    shutil.rmtree(_posts_path)
    os.makedirs(_posts_path)
    _drafts_path = os.path.join(hexo_path, "source/_drafts")
    os.makedirs(_drafts_path)
    # 安装主题
    os.system("git clone https://github.com/litten/hexo-theme-yilia.git"
              + " themes/yilia")
    # 显示该主题所有文章的模块
    os.system(npm + " i hexo-generator-json-content --save")
    # orgmode 渲染器 hexo-renderer-org
    os.system(npm + " install https://"
              + "github.com/CodeFalling/hexo-renderer-org#emacs --save")
    # hexo部署
    os.system(npm + " install hexo-deployer-git --save")
    os.system(npm + " install hexo-deployer-rsync --save")
    return True


def copy_save_hexo_config(argv):
    save_hexo_config = os.path.join(org_blog_path, "hexo")
    copy_tree(save_hexo_config, hexo_path)
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def modify_file(src, dest):
    with open(src) as fi_open:
        fi_content = fi_open.read()
        # 对于有相对链接的org文件进行某些修改
        # fi_content.replace("[[file:" + fi_name + "/", "[[file:")
        # fi_content.replace("[[" + fi_name + "/", "[[file:")
    with open(dest, "w") as fi_open:
        fi_open.write(fi_content)
    return True


def copy_save_blog(argv):
    _posts_path = os.path.join(hexo_path, "source/_posts")
    src_path = os.path.join(org_blog_path, "src")

    if not os.path.isdir(_posts_path):
        print("没有" + _posts_path + "这个目录")
        exit(1)
    if not os.path.isdir(src_path):
        print("没有" + src_path + "这个目录")
        exit(1)

    for (root, dirs, files) in os.walk(src_path):
        _posts_path_root = os.path.join(_posts_path,
                                        os.path.relpath(root, src_path))
        if not os.path.exists(_posts_path_root):
            os.makedirs(_posts_path_root)
        for fi in files:
            fi_name, fi_ext = os.path.splitext(fi)
            # 对于符合条件的文件进行修改
            # if and fi_ext == ".org" and fi_name in dirs:
            if False:
                modify_file(os.path.join(root, fi),
                            os.path.join(_posts_path_root, fi))
            else:
                shutil.copyfile(os.path.join(root, fi),
                                os.path.join(_posts_path_root, fi))
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def hexo_generate(argv):
    os.chdir(hexo_path)
    os.system("hexo g")
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def hexo_server(argv):
    os.chdir(hexo_path)
    os.system("hexo s")
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def hexo_deploy(argv):
    os.chdir(hexo_path)
    os.system("hexo d")
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def hexo_clean(argv):
    os.chdir(hexo_path)
    os.system("hexo clean")
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def hexo_delete(argv):
    _posts_path = os.path.join(hexo_path, "source/_posts")
    shutil.rmtree(_posts_path)
    os.makedirs(_posts_path)
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def hexo_delete_copy(argv):
    argv.insert(0, "copy-blog")
    argv.insert(0, "delete")
    if len(argv) == 0:
        return True
    return get_function(argv[0])(argv[1:])


def one_key(argv):
    if len(argv) != 0:
        global hexo_path
        hexo_path = argv[0]
    hexo_init([])
    hexo_init_after([])
    copy_save_blog([])
    copy_save_hexo_config([])
    hexo_generate([])
    return True


def help_info(argv):
    print("org2hexo.py config             配置目录")
    print("org2hexo.py help               显示帮助信息")
    print("org2hexo.py s                  运行hexo项目http服务器")
    print("org2hexo.py server             运行hexo项目http服务器")
    print("org2hexo.py g                  生成hexo项目")
    print("org2hexo.py generate           生成hexo项目")
    print("org2hexo.py d                  部署到服务器")
    print("org2hexo.py deploy             部署到服务器")
    print("org2hexo.py g d                生成后部署")
    print("org2hexo.py g s                生成后运行")
    print("org2hexo.py delete             清空hexo项目下_posts文件夹")
    print("org2hexo.py init [path]        初始化hexo项目，不指定路径则使用默认值")
    print("org2hexo.py init-after [path]  简单配置，不指定路径则使用默认值")
    print("org2hexo.py copy-hexo          复制保存的hexo配置")
    print("org2hexo.py copy-blog          复制org-blog到hexo目录中")
    print("org2hexo.py delete-copy        等同delete copy-blog")
    print("org2hexo.py one-key [path]     初始化并配置并恢复保存并生成，不指定路径则使用默认值")
    print("org2hexo.py clean              清除缓存文件 (db.json) 和已生成的静态文件 (public)")


def config(argv):
    org_blog_path = input("输入org_blog_path: ")
    hexo_path = input("输入hexo_path: ")
    npm = input("输入npm: ")
    with open(config_path, "w") as con:
        if org_blog_path.strip() != "":
            config_json["org_blog_path"] = org_blog_path.strip()
        if hexo_path.strip() != "":
            config_json["hexo_path"] = hexo_path.strip()
        if npm.strip() != "":
            config_json["npm"] = npm
            con.write(json.dumps(config_json, ensure_ascii=False, indent=4))
    return True


def finish(argv):
    return True


def get_function(command_name):
    function = {
        "g": hexo_generate,
        "generate": hexo_generate,
        "s": hexo_server,
        "server": hexo_server,
        "d": hexo_deploy,
        "deploy": hexo_deploy,
        "delete": hexo_delete,
        "delete-copy": hexo_delete_copy,
        "clean": hexo_clean,
        "init": hexo_init,
        "copy-blog": copy_save_blog,
        "copy-hexo": copy_save_hexo_config,
        "config": config,
        "init-after": hexo_init_after,
        "one-key": one_key,
        "help": help_info,
    }
    func = function.get(command_name)
    if func:
        return func
    return finish


def main():
    load_config()
    print("npm:", npm)
    print("hexo_path:", hexo_path)
    print("org_blog_path:", org_blog_path)
    print()
    if len(sys.argv) == 1:
        return get_function("help")([])
    func = get_function(sys.argv[1])
    if func == finish:
        print("输入错误参数")
        return get_function("help")([])
    func = get_function(sys.argv[1])
    return func(sys.argv[2:])


if __name__ == "__main__":
    main()
