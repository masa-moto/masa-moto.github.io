#tips #pathlib #python 

# BLUF
`pathlib.Path`を使って親ディレクトリのパス情報を取得し、`sys.path.append`を使ってimport パスに追加する。

# 中身　
以下のディレクトリ構成だったと仮定する。
```
project_root/
├─ other_module_dir/
│  └─ some_module.py
└─ src/
   └─ main.py 
```

src/main.pyで以下を記載することで、上記ディレクトリのsome_module.pyを呼び出すことができる。
```
from pathlib import Path 
import sys 

current_file = Path(__file__).resolve()

base_dir = current_file.parents[1]

target_dir = base_dir / "other_module_dir"

sys.path.append(str(target_dir))

import some_module
```

### 中身（詳しく）

###### パッケージのインポート
```
from pathlib import Path
import sys
```
pathlibとsysを使用する。
pathlibはプログラムファイルからディレクトリ情報を取得するために使用する。今回の肝。
sysは追加した親ディレクトリの情報をもとに別ディレクトリのファイルを参照するために使用する。

###### 現在地の取得
```
current_file = Path(__file__).resolve()
```
実行ファイルの情報を取得する。

###### 親ディレクトリを取得
```
base_dir = currentfile.parents[1]
```
`parents`で親ディレクトリの情報を取得する。`.parent`でも同じような操作ができ、その場合は`.parents[0]`と同じ。
必要な階層の数だけ`parents[n]`の`n`を指定する。

###### 階層を遡った後で、必要なフォルダを指定する
```
target_dir = base_dir / "target_module_dir"
```

###### pythonが参照できるように追加する。
```
sys.path.append(str(target_dir))
```
これをしないと、離れたディレクトリの情報を文字で取得しただけになってしまう。


# ドキュメントなど。
https://docs.python.org/3/library/pathlib.html
https://docs.python.org/3/tutorial/modules.html#the-module-search-path
## ところで。（１）
`__file__`が使えない場合もある。
1. 対話実行環境REPLでは使えない
2. Jupyter notebookとかのコードセルのような環境では使えない
## ところで。（２）

```
sys.path.append(str(target_dir))
```
で目的の別ディレクトリにある目的のモジュールを参照できる。が、

```
sys.path.insert(0, str(target_dir))
```
でも同様のことができる。

両者は既存パスに対して、`target_dir`を追記する場所が異なる。
- `append`は既存パスに追記する
- `insert(o, dir)`は頭に挿入する
これでモデュールを探す優先順位をある程度コントロールでき、同名のモジュールがあるときに衝突を回避できたりする（かもしれない。そもそも同名にしない方がいいという話もあるが。）