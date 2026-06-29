---
title: 'Jupyter kernelがHDF5ファイルを保持していた時のBlockingIOErrorとその対処'
date: 2026-06-03
permalink: /posts/2026/06/hdf5-blocking-io-err/
tags:
  - python
  - linux
description: ".h5ファイルをpythonで開こうとしてBlockingIOErrorが発生した。これに対処するためにいろいろ見て回った。"
---

# 概要
Python, h5pyでHDF5ファイルを開こうとしていたところ、次のようなエラーが出た、

```bash
BlockingIOError: [Errno 11] Resource temporarily unavailable
```

このエラーは、同時に複数箇所（プロセス）からファイルにアクセスしたことが原因で出ることがある。

今回の場合は、過去に起動して実行していたJupyter Kernelが.h5ファイルをつかんだまま残っており、
別のPythonプロセスから同じHDF5ファイルへアクセスしようとして競合が発生した可能性が高い。

最終的にプロセスを終了するコマンドを実行することで解決した。


# 状況
linux端末で複数の Python スクリプトを screen session 上で実行していた。
同時に、以前使っていた Jupyter Notebook / VSCode Notebook の kernel が残っていたらしく、lsof で調べると Python プロセスが対象の .h5 ファイルを REG として保持していた。

その結果、別プロセスから h5py で同じファイルを開く際に、
```
BlockingIOError: [Errno 11] Resource temporarily unavailable
```
が発生したと考えられる。

# 対処
## 情報収集
まず対象ファイル(以下、file.h5とする)がどこで開かれているか、目星を付ける。

```bash
lsof | grep "file.h5"
```
どこかでプロセスがファイルを保持していたりすると、情報が出てくるので確認する。

```
python <PID> USER xxxxxxx /path/to/file.h5
```
上記のような情報が出てくる（今回はpythonを使用していたので左端はpythonと出ていた）ので、PIDを確認する。

これを雑に
```bash 
kill -KILL <PID>
```
としてもいいが、原因の切り分けもできなくなるのでそれは最終手段。

## 対象PIDがどこ由来かを探す
```bash
ps -p <PID> -o pid,ppid,stat,cmd
```
等で、どのプロセス由来でファイルを保持しているプロセスが残っているのか確認する。

```bash
pstree -ps <PID> 
```
でプロセスツリーを確認してもいい。

screen上で実行しているような場合は
```
(screen) -> (bash) -> (python)
```
とかになるはず。

jupyter notebookのkernelが残っている場合は、cmdに
```
.../jupyter/runtime/kernel-xxxxxxxxxx.json
```
等のruntime JSONが見えることがある。この場合、Jupyter kernelがファイルを保持している可能性がある。

## ファイルを解放する
上記のようにnotebookがファイルをつかんでいると仮定して説明する。

### まずはnotebookを探す
file.h5を開いたノートブックに心当たりがある場合、そのノートブックを開き、該当箇所を探したり、kernelの初期化をすれば解決することがある。

今回対処したのはそれでは解決しなかったので次の手段を講じる

### `<PID>`を止める
まずは穏当に`SIGTERM`を送信する。

```bash 
kill -TERM <PID>
```

これで終了すれば解決。
プロセスが残っているかどうかは
```bash 
ps -p <PID> -o pid,stat,etime,cmd
```
だったり、
```bash 
lsof | grep file.h5
```
等で確かめればよい。

それでもプロセスが残っている場合、順に以下を試し、プロセスが終了したかどうか確認する。
```bash 
kill -INT <PID>
kill -TERM <PID> 
kill -KILL <PID>
```
但し、書き込み中であったりするとファイルが不完全に閉じられたり壊れたりする場合がある。
KILLで終わらせたときはその後のファイルの中身をチェックするのがよい。

## ファイルが読めるか確認する。

プロセスを止めたことで、ファイルをpython, h5pyなどで開けるようになる（はず）。
簡単に確認するためにPythonで以下を実行した

```python 
import h5py 
with h5py.File(path, "r") as f:
    print(list(f.keys())[:5])
```

これで開ければ、少なくともHDF5ファイルとして読める状態になっている。

# まとめる
ファイルが存在するのにアクセスできないようなエラーの時は、
別プロセスが対象ファイルを開いたまま保持していたり、HDF5 のファイルロックに引っかかっていたりすることが原因の場合がある。
ファイルを開いて保持している意図しないプロセスを特定して適当に終了させることで、ファイルへのアクセスを取り戻せる。

# そもそも.......
pythonでファイルを開くときは、
```python 
file = h5py.File(path, "r")
```
とするのではなく、
```python
with h5py.File(path, "r") as file:
```
を使用してアクセスする方がよい。

後者では、`with` ブロックを抜けた時点で `close()` 相当の処理が呼ばれるため、ファイルハンドルを不要に保持し続ける事故を減らせる。

特に、Jupyter notebookのような実行環境では、コードセルを実行した後でも変数としてファイルアクセスを残し続けるので、
`with ...`を主として使うよう注意する。

（fileIOを全て手動で管理でき、そっちの方がいいと感じる場合はそれでいいと思います。）

# よく使ったコマンドまとめ
- 対象ファイルを開いているプロセスを見る
```
lsof /path/to/problem.h5
```

- HDF5を開いているプロセスを探す
```
lsof | grep '\.h5'
```

- 対象PIDが開いているものを見る
```
lsof -p <PID>
```

- 通常ファイルだけ見る
```
lsof -p <PID> | grep REG
```

- Pythonプロセスを見る
```
ps -fu "$USER" | grep python
```

- PIDの状態を見る
```
ps -p <PID> -o pid,ppid,stat,etime,pcpu,pmem,cmd
```

- 親子関係を見る
```
pstree -ps <PID>
```

- 穏当に止める
```
kill -TERM <PID>
```

- まだ掴んでいるか確認
```
lsof /path/to/problem.h5
```

# リンクなど
- [IBMのドキュメント](https://www.ibm.com/docs/ja/aix/7.2.0?topic=management-process-termination)
- [Zennで見つけたSIGINT/SIGTERM/SIGKILLについての記事](
https://zenn.dev/waffledog/scraps/30107eecdfb90b)
- [Wikipedia/シグナル(Unix)](https://ja.wikipedia.org/wiki/
シグナル_(Unix)#個々のシグナル)