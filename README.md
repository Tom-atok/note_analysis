# note_analysis

# 前準備
## 仮想環境の準備
参考：[https://packaging.python.org/ja/latest/guides/installing-using-pip-and-virtual-environments/](https://packaging.python.org/ja/latest/guides/installing-using-pip-and-virtual-environments/)

仮想環境の作成
```sh
python3 -m venv .venv
```

仮想環境の活性化
```sh
source .venv/bin/activate
```

仮想環境でpythonを使用する
```sh
.venv/bin/python
```

仮想環境を終了する
```sh
deactivate
```

##  パッケージのインストールする

### MeCabを使用する
そもそもPCにMeCabを入れる必要がある
`brew install mecab`
辞書のインストール
`brew install mecab-ipadic`

#### Neologdをインストール
ref: https://qiita.com/taroc/items/b9afd914432da08dafc8
```sh
brew install git curl xz
git clone --depth 1 git@github.com:neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd
./bin/install-mecab-ipadic-neologd -n
```

Neologdを指定するパスを見つけるには
```sh
echo `mecab-config --dicdir`"/mecab-ipadic-neologd"
```

#### デフォルトをNeolgdにする方法
ref: https://qiita.com/shimajiroxyz/items/e488e9b28a56e908e7cb
現在使用している辞書を確認する
```sh
mecab -D
```

mecabrcを探して書き換える
```sh
mecab-config --sysconfdir
```

```mecabrc
#書き換え前
dicdir =  /usr/local/lib/mecab/dic/ipadic

#書き換え後
;dicdir =  /usr/local/lib/mecab/dic/ipadic
dicdir =  /usr/local/lib/mecab/dic/mecab-ipadic-neologd
```
