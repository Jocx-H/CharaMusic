# musicpy的基本语法（五）

## 这一部分我会讲一些2021年初新加入的一些功能（现在打字的日期：2021/2/2）
## 目录
- [往一首曲子插入实时速度变化](#往一首曲子插入实时速度变化)
- [往一首曲子插入实时的弯音,滑音,颤音变化](#往一首曲子插入实时的弯音滑音颤音变化)
- [设定一个和弦类型的音量的另一种方法](#设定一个和弦类型的音量的另一种方法)
- [读取midi文件现在也会读取速度变化信息和弯音信息](#读取midi文件现在也会读取速度变化信息和弯音信息)
- [去除一个和弦类型的所有除了音符类型以外的类型](#去除一个和弦类型的所有除了音符类型以外的类型)
- [按照吉他的品格数和吉他定弦标准来得到和弦类型](#按照吉他的品格数和吉他定弦标准来得到和弦类型)
- [piece类型的编辑操作一览](#piece类型的编辑操作一览)
- [按照指定的BPM计算一个和弦类型的实际演奏时间](#按照指定的BPM计算一个和弦类型的实际演奏时间)
- [按照小节数的范围进行和弦类型的切片](#按照小节数的范围进行和弦类型的切片)
- [计算一个和弦类型的总小节数](#计算一个和弦类型的总小节数)
- [按照现实演奏时间的范围进行和弦类型的切片](#按照现实演奏时间的范围进行和弦类型的切片)
- [提取一个和弦类型前n个小节的部分](#提取一个和弦类型前n个小节的部分)
- [提取一个和弦类型某一个小节的部分](#提取一个和弦类型某一个小节的部分)
- [提取一个和弦类型的每一个小节的内容](#提取一个和弦类型的每一个小节的内容)
- [对一个和弦类型内某个音名的出现次数进行计数](#对一个和弦类型内某个音名的出现次数进行计数)
- [得到一个和弦类型出现次数最多的音](#得到一个和弦类型出现次数最多的音)

## 往一首曲子插入实时速度变化
你可以使用tempo类型（速度类型）插入到一个和弦类型中，可以设定tempo类型插入的具体位置，  
也可以直接按照插入的位置作为速度变化的位置。插入实时速度变化可以让你的曲子的速度进行动态的变化。

### tempo类型的构成
```python
tempo(bpm, start_time=None, channel=None, track=None)
```
- bpm: 想要变化到的曲速
- start_time: 想要在什么时间改变位置，单位为小节，可以是整数，小数或者分数，可以不设置，默认值为None。如果start_time没有设置，则会按照tempo插入到和弦类型中的具体位置作为start_time
- channel: MIDI通道编号
- track: MIDI音轨编号

### tempo类型插入到和弦类型中
只需要把tempo类型当做一个音符类型插入到和弦类型中就行了。
```python
a = chord(['C5', 'D5', 'E5', tempo(150), 'F5', 'G5', 'A5', 'B5', 'C6']) % (1/8,1/8)
play(a, 80)
# 和弦类型a从开始到E5会以80BPM的速度演奏，之后会以150BPM的速度演奏
```

### 设定start_time可以选择在哪里开始变化速度
```python
a = chord(['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', tempo(150, 0.5)]) % (1/8,1/8)
play(a, 80)
# 和弦类型a从开始到第0.5小节会以80BPM的速度演奏，之后会以150BPM的速度演奏(以第0小节作为开头)
```

### 写在一个字符串里的tempo类型构建的语法
```python
a = chord('C5, D5, E5, tempo;150, F5, G5, A5, B5, C6') % (1/8,1/8)
a = chord('C5, D5, E5, F5, G5, A5, B5, C6, tempo;150;1.5') % (1/8,1/8)
# 请注意，因为tempo类型本身不是音符类型，只是一个通知改变速度的信息，因此在写在一个字符串里的语法中
# 没有使用括号设定音符类型的长度，间隔等的语法，比如tempo;150(.8;.)这样是不行的。
```

## 往一首曲子插入实时的弯音,滑音,颤音变化
你可以使用pitch_bend类型（弯音类型）插入到一个和弦类型中，可以实时改变某一个片段的音符的音高，可以很细微地变化音高。
构建pitch_bend类型时，使用mode参数可以选择三种不同的单位:
* 半音 (-2到2之间的任意整数，小数或者分数，不包括-2和2本身)
* 音分 (1个半音 = 100音分，-200到200之间的任意整数，小数或者分数，不包括-200和200本身，音分是默认单位)
* midi弯音值 (-8192到8192之间的任意整数，不包括-8192和8192本身)

### pitch_bend类型的构成
```python
pitch_bend(value, start_time=None, mode='cents', channel=None, track=None)
```
- value: 音符的音高变化的量
- start_time: 音符的音高变化的位置，单位为小节，如果不设置，则以pitch_bend类型插入和弦类型的具体位置为准
- mode: mode == 'cents' 选择音分作为单位，为默认值，mode如果不设置就选择音分作为单位; mode == 'semitones' 选择半音作为单位; mode == 'values' 选择midi弯音值作为单位
- channel: MIDI通道编号
- track: MIDI音轨编号

### pitch_bend类型插入到和弦类型中
只需要把pitch_bend类型当做一个音符类型插入到和弦类型中就行了。
```python
a = chord(['C5', 'D5', 'E5', pitch_bend(30), 'F5', 'G5', 'A5', 'B5', 'C6']) % (1/8,1/8)
play(a, 80)
# 和弦类型a从开始到E5会以正常的音高演奏，之后的音符会调高30音分进行演奏（也就是0.3个半音）
```

### 设定start_time可以选择在哪里开始变化音符的音高
```python
a = chord(['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', pitch_bend(30, 0.5)]) % (1/8,1/8)
play(a, 80)
# 和弦类型a从开始到第0.5小节会以正常的音高演奏，之后的音符会调高30音分进行演奏（也就是0.3个半音）(以第0小节作为开头)
```

### 写在一个字符串里的pitch_bend类型构建的语法
```python
a = chord('C5, D5, E5, pitch;30, F5, G5, A5, B5, C6') % (1/8,1/8)
a = chord('C5, D5, E5, F5, G5, A5, B5, C6, pitch;30;1.5') % (1/8,1/8)
a = chord('C5, D5, E5, F5, G5, A5, B5, C6, pitch;1.37;1.5;semitones') % (1/8,1/8)
# 请注意，因为pitch_bend类型本身不是音符类型，只是一个通知改变音符的音高的信息，因此在写在一个字符串里的语法中
# 没有使用括号设定音符类型的长度，间隔等的语法，比如pitch_bend;30(.8;.)这样是不行的。
# 在写在一个字符串里的语法中，mode参数是第三个参数，在value和start_time之后，后面的两个参数分别是channel和track
```

## 设定一个和弦类型的音量的另一种方法
```python
# 可以使用setvolume方法设置一个和弦类型的音量
a = C('Emaj7')
a.setvolume(80)
# 也可以使用set函数或者进阶写法%来设定音量，作为第音符长度和间隔之后的第三个参数
a = a.set(1/8,1/8,80)
a = a % (1/8,1/8,80)
```

## 读取midi文件现在也会读取速度变化信息和弯音信息
现在的musicpy的版本中使用`read`函数读取一个midi文件时，也会读取这个midi文件的实时速度变化信息和弯音信息，  
并且转换为tempo类型和pitch_bend类型，并且会存储发生的时间的参数到信息中，因此当再次使用`play`函数播放  
读取midi文件后转换的和弦类型时，会完全重现原来的midi文件的实时速度变化和弯音。

## 去除一个和弦类型的所有除了音符类型以外的类型
如果想要只保留一个和弦类型中的音符类型，去除所有其他的类型（比如tempo类型，pitch_bend类型等等），  
那么可以使用`only_notes`这个内置函数。
```python
bpm, a, start_time = read('example.mid').merge()
a = a.only_notes()
```

## 按照吉他的品格数和吉他定弦标准来得到和弦类型
你可以使用`guitar_chord`函数，通过吉他的6根弦的品格数和吉他定弦标准(可以不设置，默认为6弦吉他标准定弦)来得到和弦类型
```python
guitar_chord(frets,
             return_chord=False,
             tuning=['E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
             duration=0.25,
             interval=0,
             **detect_args)
# frets: 你按吉他的6根弦从最低音的弦到最高音的弦的品格数的列表，品格数为一个整数，如果是空弦就写0，如果是不弹的弦就写None
# return_chord: 是否返回和弦类型，为False的时候会判断你按的品格数弹出来是什么和弦，返回的具体的和弦名称，默认值为False。
# tuning: 吉他的定弦，默认值为6弦吉他的标准定弦，你也可以自己定制想要的吉他定弦
# duration: 返回的和弦类型的音符长度的列表
# interval: 返回的和弦类型的音符间隔的列表
# detect_args: 判断和弦的具体类型的参数，也就是detect函数的参数，以关键字参数设置

# 比如吉他的C大三和弦在前三品的一个标准按法是5弦3品，4弦2品，3弦空弦，2弦1品，1弦空弦，那么就可以写
>>> guitar_chord([None, 3, 2, 0, 1, 0], True)
[C3, E3, G3, C4, E4] with interval [0, 0, 0, 0, 0]
>>> guitar_chord([None, 3, 2, 0, 1, 0])
'Cmajor'
```

## piece类型的编辑操作一览
piece类型(乐曲类型)可以存储一整首多个不同乐器和不同midi通道的曲子的信息，  
你除了可以对一个乐曲类型里的任何一个midi通道进行和弦类型的编辑以外，  
在整个乐曲类型层面上也有很多可以编辑的操作。
```python
# 首先构建一个乐曲类型，A1, B1, C1, D1都是已经写好的和弦类型
a = piece(tracks=[A1, B1, C1, D1],
          instruments_list=[1, 35, 1, 49],
          bpm=150,
          start_times=[0, 8, 8, 16],
          channels=[0,1,9,2],
          track_names=['piano', 'electric bass', 'drums', 'strings'])

# 如果想要完全重复这个乐曲类型n遍，那么可以写
b = a | n

# 如果想要对这个乐器类型的所有midi通道进行复制粘贴n遍的操作，那么可以写
b = a * n
b = a % n
# 分别对应不同的add模式，可以参考和弦类型的对应的符号化写法的运作逻辑

# 可以使用index值查看一个乐曲类型的某一个音轨的信息，以0作为第1个音轨
# 使用a[n]的语法可以得到第n个音轨类型
>>> a[0]
[track] 
BPM: 150
channel 0 piano | instrument: Acoustic Grand Piano | start time: 0 | [C4, E4, G4, B4] with interval [0, 0, 0, 0]

# 使用a(n)的语法可以得到一个列表，元素依次为第n个midi通道的和弦类型，乐器类型，BPM，开始时间，
# 通道编号，音轨名称，通道声相，通道音量
>>> a(0)
[[C4, E4, G4, B4] with interval [0, 0, 0, 0], 'Acoustic Grand Piano', 150, 0, 0, 'piano', [], []]

# 升高/降低整首曲子n个半音，同样也是与音符类型，和弦类型相同的语法，可以使用up/down函数或者+/-的进阶语法
b = a.up()
b = +a
b = a + 2
b = a.down()
b = -a
b = a - 2

# 可以往指定的位置添加实时的速度变化
a.add_tempo_change(bpm=100, start_time=None, ind=None, track_ind=None)
# bpm: 想要变化到的速度，单位为BPM
# start_time: 速度变化发生的时间，单位为小节，如果不设置则以ind为准
# ind: 速度变化信息插入的位置，需要和track_ind配合使用
# track_ind: 可以选择在第几个midi通道插入速度的信息，以0作为第1个midi通道，ind是选择的midi通道里放在第几个位置
# 如果ind和track_ind没有设置，那么就默认往第一个midi通道的最后添加速度变化的信息

# 可以往指定的位置添加实时的弯音（pitch bend可以模拟出音符的弯音，滑音，颤音等效果）
a.add_pitch_bend(value, start_time=0, channel='all', track=0, mode='cents', ind=None)
# value: 音符的音高变化的量
# start_time: 音符的音高变化发生的时间，单位为小节
# channel: 选择往第几个通道插入pitch bend信息，以0作为第1个midi通道，如果为'all'则往所有的midi通道插入相同的pitch bend信息
# track: midi轨道，一般情况下不用设置
# mode: 弯音信息的单位，之前有详细的说明
# ind: 弯音信息插入的位置，如果start_time有设置则以start_time的位置为准

# 查看乐曲类型个midi通道数量
>>> len(a)
4

# 添加新的音轨
a.append(new_track)
# new_track: 新添加的音轨，必须为音轨类型

# 可以使用build函数通过多个音轨类型构建乐曲类型
new_piece = build(track(A1, instrument=1, start_time=0, channel=0, track_name='piano'),
                  track(B1, instrument=35, start_time=1, channel=1, track_name='electric bass'),
                  track(C1, instrument=1, start_time=8, channel=9, track_name='drums'),
                  track(D1, instrument=49, start_time=16, channel=2, track_name='strings'),
                  bpm=150)
# 请注意，用build函数传入音轨类型来构建乐曲类型时，得到的乐曲类型的BPM只取决于build函数的bpm这个参数，
# 与传入的音轨类型自带的BPM无关
```

## 按照指定的BPM计算一个和弦类型的实际演奏时间
可以使用`eval_time`这个内置函数，指定一个BPM，计算出一个和弦类型的实际演奏时间
```python
a = C('Cmaj7') | C('Dm7') | C('E9sus') | C('Amaj9', 3)
>>> a.eval_time(80)
'3.0s'

eval_time(bpm, ind1=None, ind2=None, mode='seconds', start_time=0)
# bpm: 指定的速度BPM
# ind1, ind2: 选择小节的区间，以0作为第1个小节，如果不设置则默认以整首曲子为准
# mode: 可以选择'seconds'返回格式为秒数的时间，或者'hms'返回格式为小时,分钟，秒的时间
```

## 按照小节数的范围进行和弦类型的切片
如果我们想要提取一个和弦类型的第6个小节到第8个小节的片段，可以使用`cut`这个内置函数
```python
cut(ind1=0, ind2=None, start_time=0)
# ind1, ind2: 提取的小节数的范围，ind2如果不设置，则提取到最后，ind1默认值为0，也就是从开头第0个小节开始提取。
# start_time: 在读取一个midi文件时，一个midi通道的音符会有自己的开始时间，在这里可以作为和弦类型延后演奏的设置，这里的单位为小节
# cut函数返回的是一个新的和弦类型，内容为指定的小节数的范围内的切片
a.cut(6, 8)
# 提取和弦类型a的从第6个小节到第8个小节的部分（从第6个小节的开头到第8个小节的开头）
```

## 计算一个和弦类型的总小节数
使用内置函数`bars`就可以得到一个和弦类型的总小节数
```python
a = C('Cmaj7') | C('Dm7') | C('E9sus') | C('Amaj9', 3)
>>> a.bars()
1.0
```

## 按照现实演奏时间的范围进行和弦类型的切片
使用内置函数`cut_time`，指定一个BPM，就可以选择一个时间范围进行和弦类型的切片，  
比如和弦类型a在速度为100BPM的时候，提取第10秒到第20秒的部分，可以写
```python
a.cut_time(100, 10, 20)
# 如果范围的右侧不设置，那么就默认提取到最后，左侧默认为从最开始提取
```

## 提取一个和弦类型前n个小节的部分
```python
a.firstnbars(n)
```

## 提取一个和弦类型某一个小节的部分
```python
a.get_bar(n)
```

## 提取一个和弦类型的每一个小节的内容
```python
a.split_bars()
# 可以得到和弦类型a的每一个小节的部分的和弦类型组成的列表
```

## 对一个和弦类型内某个音名的出现次数进行计数
```python
# 如果想得到和弦类型a里音名为F#的音出现了多少次，可以写
a.count('F#')
# 也可以指定八度数，只对音名和八度数都相同的音进行计数
a.count('F#5')
```

## 得到一个和弦类型出现次数最多的音
```python
a.most_appear()
# choices参数可以设置要从哪些音里面选，如果不设置则默认为全部的12音
```
## 下一章 [musicpy的基本语法（六）](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy的基本语法（六）)

