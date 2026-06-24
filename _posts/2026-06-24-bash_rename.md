---
title: 'bashで条件一致した文字列を処理する'
date: 2026-06-02
permalink: /posts/2026/06/bash_rename/
tags:
  - bash
description: "bash上でパターンマッチして文字列を取得する"
---

# やりたいこと
あるディレクトリ下の特定の表現を含む複数のファイルを一括で操作したい。

[以前のpost](/posts/2026/06/bash/)でbashでfor文を回す方法について書いていたが、それから派生して文字列取得していろいろ処理をしたかった。

特に、あるディレクトリの ` prefix_DATA??_suffix.ext `のような名前表現のファイルを取得して、
対応する` /DATA??/prefix_DATA??_suffix.ext `に移動するなどを実現したかった。


# 設定等
```
main_dir/
    - prefix_dataAA_suffix01.h5
    - prefix_dataAA_suffix02.h5
    - prefix_dataAA_suffix03.h5
    - prefix_dataAA_suffix04.h5
    - prefix_dataBB_suffix01.h5
    - prefix_dataBB_suffix02.h5
    - prefix_dataBB_suffix03.h5
    - prefix_dataBB_suffix04.h5
    - analyzed_data_01.bin
    - analyzed_data_02.bin
    - analyzed_data_03.bin
sub_dir/
condig/
/dataAA/
/dataBB/
```

# 具体的な方法

## prefix, suffixの除去

main_dirのdataAA, dataBBが入っているファイルを、/dataAA/, /dataBB/の対応するそれぞれのディレクトリに移動する
```bash
for f in main_dir/prefix_data*.ext; do
    base=$(basename "$f")
    name="${base#prefix_}"
    name="${name%_suffix*.ext}"
    mv -- "$f" "/$name/"
done
```

もう少し堅牢に正規表現を用いる場合は、
```bash 
for f in main_dir/prefix_*_suffix*.h5; do
    base=$(basename "$f")

    if [[ $base =~ ^prefix_(.*)_suffix[0-9]+\.h5$ ]]; then
        name="${BASH_REMATCH[1]}"
        mv -- "$f" "$name/"
    fi
done
```
のようになる。

## if~fiの中身について
```
    if [[ $base =~ ^prefix_(.*)_suffix[0-9]+\.h5$ ]]; then
        name="${BASH_REMATCH[1]}"
        mv -- "$f" "$name/"
```
これは、
```
if <条件> ; then
    条件が真の時に実行する処理
fi
```
という構造になっている。

## [[$base=~ 正規表現]]
bashの正規表現マッチで、
```
[[文字列=~正規表現]]
```
を意味しており、boolが返ってくる。

今回では
`$base`が`prefix_(.*)_suffix[0-9]+\.h5`にマッチするか？を見ている。

## 正規表現　
詳しくはネットの海に無数に存在する「正規表現まとめ」みたいなサイトを見るとして（一つくらいは末尾にリンクを載せておく）、
今回使っているものに限り簡単に説明する

### `(.*)`
何らかの文字の連続。文字が当てはまればよく、何ならなくてもよい。
今回では`dataAA`及び`dataBB`を拾う。

### `[0-9]+`
二文字以上連続した数字。少なくとも一文字は必要だが、一文字以上一致すれば文字数不問。
今回は01~04のように、数字が連続している表現を拾う。

### `\.h5$`
正規表現で`.`は特別なはたらきをする。それと区別するための記法。
`$`は行末を示す。
ここでは`.h5`で終わる文字列を拾う。

## BASH_REMATCHについて
`[[ ... =~ ...]]`でパターンに位置すると、bashは結果を`BASE_REMATCH`に格納する。
```bash
BASH_REMATCH[0] : 正規表現全体に一致した部分
BASH_REMATCH[1] : 1個目の（...）グループに一致した部分
BASH_REMATCH[2] : 2個目の（...）グループに一致した部分
BASH_REMATCH[k] : k個目の（...）グループに一致した部分
```
ここでの`(...)`とは、例えば今回の例では`(.*)`で条件としたメタ文字のグループ。
今回でいうと`BASH_REMATCH[0]`はファイル名全体、`BASH_REMATCH[1]`は`dataAA, dataBB`を拾う。

# おしまい
私はこれでデータファイルを整理したり、複製したりしました。

これくらいのパターンだったら正規表現を使う必要はあんまりないかもしれません。

# リンクなど
正規表現についてわかりやすくまとめられていたサイト [サルにもわかる正規表現入門](https://userweb.mnet.ne.jp/nakama/)
