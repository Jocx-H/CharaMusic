# musicpy的基本语法（九）

## 目录
- [快速制作和弦琶音](#快速制作和弦琶音)
- [重新设定和弦类型的整体八度数](#重新设定和弦类型的整体八度数)
- [与其他midi信息一起构建和弦类型](#与其他midi信息一起构建和弦类型)
- [清除音色改变的midi信息](#清除音色改变的midi信息)
- [清除其他的midi信息](#清除其他的midi信息)
- [快速改变乐曲类型的音轨的乐器](#快速改变乐曲类型的音轨的乐器)
- [按照多声部来写和弦类型](#按照多声部来写和弦类型)
- [把一个列表中的和弦类型进行合并](#把一个列表中的和弦类型进行合并)
- [把多个音符按照长度比例平均分配到指定的小节长度内](#把多个音符按照长度比例平均分配到指定的小节长度内)
- [附点音符的使用](#附点音符的使用)
- [音阶类型按照使用罗马数字表示的和弦级数提取和弦](#音阶类型按照使用罗马数字表示的和弦级数提取和弦)
- [使用音阶类型产生和弦进行](#使用音阶类型产生和弦进行)
- [使用translate函数来按照鼓点语法写和弦类型](#使用translate函数来按照鼓点语法写和弦类型)
- [停止目前所有正在播放的声音](#停止目前所有正在播放的声音)
- [按照小节长度移动乐曲类型的音轨的位置](#按照小节长度移动乐曲类型的音轨的位置)
- [重新设定和弦类型的整体音高](#重新设定和弦类型的整体音高)
- [筛选和弦类型和乐曲类型中的某一种MIDI信息](#筛选和弦类型和乐曲类型中的某一种MIDI信息)

## 快速制作和弦琶音
2021年8月新增了快速制作和弦琶音的函数`arpeggio`, 你可以指定和弦类型，和弦琶音的八度范围，音符长度和音符间隔，也可以选择播放上行琶音或者下行琶音，或者两者都生成。你也可以使用`arp`作为简写。
```python
arpeggio(chord_type,
          start=3,
          stop=7,
          durations=1 / 4,
          intervals=1 / 32,
          first_half=True,
          second_half=False)

# chord_type: 表示和弦类型的字符串，可以使用C函数支持的语法，也可以是和弦类型

# start: 和弦琶音开始的八度数

# stop: 和弦琶音结束的八度数

# durations: 和弦琶音的音符长度

# intervals: 和弦琶音的音符间隔

# first_half: 生成上行的和弦琶音

# second_half: 生成下行的和弦琶音

Cmaj7_arpeggio = arpeggio('Cmaj7')

>>> Cmaj7_arpeggio
[C3, E3, G3, B3, C4, E4, G4, B4, C5, E5, G5, B5, C6, E6, G6, B6] with interval [0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125]

Cmaj7_arpeggio = arp('Cmaj7', 3, 6)

>>> Cmaj7_arpeggio
[C3, E3, G3, B3, C4, E4, G4, B4, C5, E5, G5, B5] with interval [0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125, 0.03125]
```

## 重新设定和弦类型的整体八度数
你可以使用`reset_octave`函数来把一个和弦类型的整体八度数进行设定，以和弦类型的第1个音的八度数为标准，把和弦类型整体移动到你设定的八度数，返回的是一个新的和弦类型。这个方法在你不知道本来的和弦的整体八度数的情况下很有用。
```python
a = C('Cmaj7', 5)

>>> a
[C5, E5, G5, B5] with interval [0, 0, 0, 0]

b = a.reset_octave(3)

>>> b
[C3, E3, G3, B3] with interval [0, 0, 0, 0]
```

## 与其他midi信息一起构建和弦类型
一般来说，你可以在构建和弦类型时传入`other_messages`的属性来添加其他的midi信息，但是如果你想在和弦类型构建之后再添加其他的midi信息，你可以直接设定和弦类型的`other_messages`属性，也可以使用和弦类型的`with_other_messages`函数来获得新的有着其他的midi信息的和弦类型。请注意`other_messages`是一个其他的midi信息的列表。
```python
a = C('Cmaj7')

b = a.with_other_messages([controller_event(controller_number=1, parameter=50)])

>>> b.other_messages

[<musicpy.structures.controller_event object at 0x000001AA05730188>]
```

## 清除音色改变的midi信息
当你读取一个midi文件时，经常会有其他的midi信息被读取到`other_messages`中，作为转换为的musicpy数据结构的属性，如果其中有`program_change`信息，就会在再次写入时也一样写入到midi文件中，让音轨的乐器强制改变，这会在你重新设定写入midi文件的乐器时造成困扰。你可以在写入midi文件的`write`函数中把`nomsg`的值设定为`True`,这样就不会写入其他的midi信息，但是有的时候你又想保留其他的不是改变乐器的midi信息，那么怎么办呢？为了解决这个问题，你可以使用`clear_program_change`函数来单独清除一个和弦类型或者乐曲类型的`program_change`信息，这样当再次写入midi文件时，midi文件的每个音轨就会按照你设定的乐器来进行播放了。
```python
a = read('test.mid') # 读取一个midi文件，转换为乐曲类型

a.clear_program_change() # 清除乐曲类型的program_change信息

# 乐曲类型的clear_program_change函数有一个参数apply_tracks, 如果为True,
# 会清除乐曲类型本身的program_change信息以及每一个音轨的program_change信息,
# 如果为False, 则只会清除乐曲类型本身的program_change信息, 默认值为True

a.clear_program_change(apply_tracks=False)

b = a.tracks[0] # 提取乐曲类型a的第一个音轨，是一个和弦类型
b.clear_program_change() # 清除和弦类型的program_change信息
```

## 清除其他的midi信息
你可以使用`clear_other_messages`函数清除一个和弦类型或者乐曲类型的所有的其他的midi信息，或者按照midi信息类型来进行筛选清除。  
如果你只是想要完全清除一个和弦类型或者乐曲类型的其他的midi信息，你只需要把它们的`other_messages`属性的列表清空即可，或者重新赋值为一个空列表。
```python
# 这两个方法都可以完全清空一个和弦类型或者乐曲类型的其他的midi信息
a.other_messages.clear()
a.other_messages = []

a.clear_other_messages() # 清除所有的其他的midi信息
a.clear_other_messages(program_change) # 清除其他的midi信息中的program_change类型的信息

# 当a是一个乐曲类型时，与clear_program_change函数类似，也有一个apply_tracks的参数，
# 用法也类似，默认值为True
```

## 快速改变乐曲类型的音轨的乐器
你可以使用乐曲类型的`change_instruments`函数来快速改变乐曲类型整体的每个音轨的乐器或者单个音轨的乐器，而不需要通过修改`instruments_list`和`instruments_numbers`属性来进行音轨的乐器的修改。你可以传入乐器名或者乐器的midi编号，可以进行整体的所有音轨的乐器的替换，或者指定某条音轨的乐器的替换。注意：如果你想通过修改属性来进行乐曲类型的音轨的乐器的修改，必须要修改`instruments_numbers`里的midi编号，因为它们才是在写入midi文件时真正有效的信息，`instruments_list`的修改只会影响乐曲类型显示时的乐器名。
```python
change_instruments(instruments_list, ind=None)

# instruments_list: 乐器的列表(所有音轨的乐器替换)或者单个乐器，可以为乐器名或者midi编号。
# General MIDI的乐器名和midi编号的对应关系可以打印变量'instruments'或者'reverse_instruments'来查看

# ind: 如果为None，则进行乐曲类型的音轨的乐器的整体替换，此时instruments_list必须为一个list或者tuple，
# 如果为一个整数，则把对应的index的音轨的乐器进行替换，index从0开始

piece1 = P([C('C'), C('D')], [1, 49])
>>> piece1
[piece] 
BPM: 120
track 1 | instrument: Acoustic Grand Piano | start time: 0 | [C4, E4, G4] with interval [0, 0, 0]
track 2 | instrument: String Ensemble 1 | start time: 0 | [D4, F#4, A4] with interval [0, 0, 0]

piece1.change_instruments([2, 47]) # 改变整体的音轨的乐器
>>> piece1
[piece] 
BPM: 120
track 1 | instrument: Bright Acoustic Piano | start time: 0 | [C4, E4, G4] with interval [0, 0, 0]
track 2 | instrument: Orchestral Harp | start time: 0 | [D4, F#4, A4] with interval [0, 0, 0]

# 或者也可以写
piece1.change_instruments(['Bright Acoustic Piano', 'Orchestral Harp'])

piece1.change_instruments(5, 0) # 把第1条音轨的乐器改变为midi编号为5的乐器
>>> piece1
[piece] 
BPM: 120
track 1 | instrument: Electric Piano 1 | start time: 0 | [C4, E4, G4] with interval [0, 0, 0]
track 2 | instrument: Orchestral Harp | start time: 0 | [D4, F#4, A4] with interval [0, 0, 0]

# 或者也可以写
piece1.change_instruments('Electric Piano 1', 0)
```

## 按照多声部来写和弦类型
你可以使用`multi_voice`函数来将多个和弦类型作为多个声部进行合并，返回的是多个声部合并后的新的和弦类型。这个方法在写同一种乐器的多声部旋律与和声的时候很有用，比如写A cappella和复杂的鼓点的时候。
```python
multi_voice(*current_chord, method=chord, start_times=None)

# *current_chord: 你可以传入任意多个和弦类型作为声部

# method: 如果传入的是表示和弦的字符串，可以在这边选择和弦解析的语法，你可以选择chord, translate和drum

# start_times: 第一个和弦类型之后的和弦类型的开始时间的列表，
# 如果你想设定第一个和弦类型之后的其他的声部相对第一个和弦类型的开始时间，可以设置这个参数，单位为小节

a = multi_voice(chord('C2') % (1, 1) % 2,
                C('G') % (1/8, 1/8) % 4)

>>> a
[C2, G4, B4, D5, G4, B4, D5, G4, B4, C2, D5, G4, B4, D5] with interval [0, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.125, 0.125, 0.125, 0.125]
```

## 把一个列表中的和弦类型进行合并
你可以使用`concat`函数，通过指定一种合并方式把一个列表中的所有的和弦类型进行合并，得到的是一个新的合并过后的和弦类型，可以指定的合并方式有`tail`, `head`, 'after', 分别以`+`, `&`, `|`来指定。
```python
concat(chordlist, mode='+', extra=None, start=None)

# chordlist: 要进行合并的和弦类型的列表

# mode: 合并方式，可以接收的值有'+', '&', '|'，分别对应'tail', 'head', 'after'，默认值为'+'

# extra: 每两个相邻的和弦类型进行合并时需要额外添加的间隔，单位为小节

# start: 合并的起始值，如果为None，则使用列表的第一个元素为起始值

chord_list = [C('C'), C('D'), C('E')]
>>> chord_list
[[C4, E4, G4] with interval [0, 0, 0], [D4, F#4, A4] with interval [0, 0, 0], [E4, G#4, B4] with interval [0, 0, 0]]

combined_chord = concat(chord_list, '|')

>>> combined_chord
[C4, E4, G4, D4, F#4, A4, E4, G#4, B4] with interval [0, 0, 0.25, 0, 0, 0.25, 0, 0, 0]
```

## 把多个音符按照长度比例平均分配到指定的小节长度内
你可以使用`distribute`函数来把多个音符按照长度比例平均分配到指定的小节长度内。这在写一些特殊的节奏型以及多连音的时候很有用。
```python
distribute(current_chord,
           length=1 / 4,
           start=0,
           stop=None,
           method=translate,
           mode=0)

# current_chord: 表示和弦的字符串或者音符的列表

# length: 用来分配的总长度，单位为小节

# start: 和弦中开始进行分配的音符的index，从0开始，默认从第1个音开始

# stop: 和弦中结束进行分配的音符的index，从0开始，如果为None，则到最后1个音，默认值为None

# method: 传入的是表示和弦的字符串时，用来解析的方法，默认值为translate，可以选择chord, translate

# mode: 为0的时候，音符的长度和间隔都按照各自的值按比例平均分配到指定的小节长度内，
# 为1的时候，音符间隔会取与音符长度一样的值。

# 把Cmaj9和弦的5个音平均分配到1/2个小节的长度，分配之前5个音的音符长度与间隔相同
a = distribute(C('Cmaj9') % (1/8, 1/8), 1/2)

>>> a
[C4, E4, G4, B4, D5] with interval [0.1, 0.1, 0.1, 0.1, 0.1]

>>> a.get_duration()
[0.1, 0.1, 0.1, 0.1, 0.1]

# 把音符长度分别为2分音符，4分音符的2个音符(重复2次)平均分配到1/2个小节的长度
b = distribute('C[.2;.], D[.4;.], {2}', 1/2)

>>> b
[C4, D4, C4, D4] with interval [0.16666666666666666, 0.08333333333333333, 0.16666666666666666, 0.08333333333333333]

>>> b.get_duration()
[0.16666666666666666, 0.08333333333333333, 0.16666666666666666, 0.08333333333333333]
```

## 附点音符的使用
你有多种方法可以使用附点音符。首先，音符类型可以使用`dotted`函数来将音符的长度变为附点音符的长度，可以自定义附点的个数。和弦类型也可以使用`dotted`函数来将和弦类型中的某个音符，某些音符或者全部音符都变为附点音符，也可以自定义附点的个数，默认情况下和弦类型的音符变为附点音符时只改变音符长度，你也可以设置音符间隔也跟着一起变成附点音符。

除此之外，在使用高级语法和translate函数来构建和弦类型和鼓点类型的时候，也可以使用附点音符，语法为在音符长度或者间隔的后面加上`.`，可以加上任意多个附点，音符的长度和间隔都会根据你加上的附点的个数进行计算。
```python
a = N('C5')

>>> a.duration
0.25

b = a.dotted() # 获得音符类型a的附点音符(单附点)

>>> b.duration
0.375

c = a.dotted(2) # 获得音符类型a的附点音符(双附点)

>>> c.duration
0.4375

# 和弦类型的dotted函数
dotted(ind=-1, num=1, duration=True, interval=False)

# ind: 变成附点音符的音符的index，可以为一个整数的index，从0开始，
# 或者'all'，表示全部的音符都变成附点音符，或者一个index的列表，从0开始，默认值为-1

# num: 附点的个数，默认值为1

# duration: 是否改变音符长度为附点音符的长度，默认值为True

# interval: 是否改变音符间隔为附点音符的长度，默认值为False

a = C('C')

>>> a.get_duration()
[0.25, 0.25, 0.25]

b = a.dotted() # 把和弦类型a的最后一个音符变为附点音符(单附点)

>>> b.get_duration()
[0.25, 0.25, 0.375]

c = a.dotted([0, 2]) # 把和弦类型a的第1个音符和第3个音符变为附点音符(单附点)

>>> c.get_duration()
[0.375, 0.25, 0.375]

a = chord('C5[.8.;.], D5[.8;.], E5[.8.;.], F5[.8;.]')
# 第1个音符和第3个音符为8分音符的附点音符，第2个音符和第4个音符为正常的8分音符

a = translate('C5[.8.;.], D5[.8;.], E5[.8.;.], F5[.8;.]') # 和上面的一样，使用translate函数

a = drum('0[.8.;.], 1, 2[.8.;.], 1') # 和上面的一样，鼓点类型
```

## 音阶类型按照使用罗马数字表示的和弦级数提取和弦
你可以使用音阶类型的`get_chord`函数按照使用罗马数字表示的和弦级数提取和弦。
```python
get_chord(degree, chord_type=None, natural=False)

# degree: 使用罗马数字表示的和弦级数的字符串，比如: 'IM7', 'ii7', 'IIm7', 'V7'，
# 可以是被调用的音阶类型里非自然出现的和弦。也可以是用数字与和弦名称的组合，比如: '1M7', '2m7'

# chord_type: 你可以分开写级数与和弦类型，此时degree为表示级数的字符串，可以是罗马数字，比如: 'I', 'II',
# 也可以是数字，比如: '1', '2'，chord_type为和弦类型，比如: 'M7', 'm7'

# natural: 是否按照音阶类型内自然出现的和弦为准，如果为True，
# 则会在得到的和弦不是音阶类型可以自然出现的和弦的情况下，
# 按照和弦的音符个数和级数在音阶类型内重新提取自然和弦，比如C大调音阶的'Im7'经过natural的转换之后会变成'IM7'，
# 默认值为False

Cmajor_scale = S('C major')

>>> Cmajor_scale.get_chord('IM7')
[C4, E4, G4, B4] with interval [0, 0, 0, 0]

>>> Cmajor_scale.get_chord('ii', '7')
[D4, F4, A4, C5] with interval [0, 0, 0, 0]
```

## 使用音阶类型产生和弦进行

```python
chord_progression(chords,
                  durations=1 / 4,
                  intervals=0,
                  volumes=None,
                  chords_interval=None,
                  merge=True)

# chords: 表示和弦级数的字符串的列表，可以是罗马数字或者数字与和弦名称的组合，
# 或者一个list或者tuple，里面有2个值，分别为罗马数字/数字, 和弦名称。

# durations: 每个和弦类型的音符长度

# intervals: 每个和弦类型的音符间隔

# volumes: 每个和弦类型的音符的音量大小

# chords_interval: 相邻的和弦类型之间的间隔，单位为小节

# merge: 是否合并为一个新的和弦类型，为True的时候返回合并过后的和弦类型，为False的时候，返回一个和弦类型的列表，默认值为True

Cmajor_scale = S('C major')

>>> Cmajor_scale.chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])
[C4, E4, G4, B4, G4, C5, D5, A4, C5, E5, G5, F4, A4, C5, E5] with interval [0, 0, 0, 0.25, 0, 0, 0.25, 0, 0, 0, 0.25, 0, 0, 0, 0]

>>> Cmajor_scale.chord_progression([('I', 'M7'), ('V', 'sus'), ('vi', '7'), 'IV'], intervals=[1/8, [1/8,1/8,1/4], 1/8, 1/8])
[C4, E4, G4, B4, G4, C5, D5, A4, C5, E5, G5, F4, A4, C5] with interval [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.25, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]

>>> Cmajor_scale.chord_progression(['1M7', '5sus', '6m7', '4M7'])
[C4, E4, G4, B4, G4, C5, D5, A4, C5, E5, G5, F4, A4, C5, E5] with interval [0, 0, 0, 0.25, 0, 0, 0.25, 0, 0, 0, 0.25, 0, 0, 0, 0]
```

## 使用translate函数来按照鼓点语法写和弦类型
在之前的鼓点语法的章节有提到过，你可以使用`translate`函数，来将鼓点的语法应用到音符中，实现用鼓点的语法写和弦类型。这里有更加详细的说明。`translate`函数和鼓点类型构建时的一个区别是，`translate`函数默认的音符间隔是0，而鼓点类型默认的音符间隔是1/8, `translate`函数和鼓点类型默认的音符长度都是1/8。这里我会给几个使用`translate`函数来写和弦类型的例子。
```python
a = translate('A2[1](2),[1],D3[1](2)')

>>> a
[A2, A2, D3, D3] with interval [1, 1, 1, 0]

b = translate('C5[.8;.](3), D5[.16;.](2), E5[.8;.], {2}')

>>> b
[C5, C5, C5, D5, D5, E5, C5, C5, C5, D5, D5, E5] with interval [0.125, 0.125, 0.125, 0.0625, 0.0625, 0.125, 0.125, 0.125, 0.125, 0.0625, 0.0625, 0.125]

c = translate('C5, E5, G5')

>>> c
[C5, E5, G5] with interval [0, 0, 0]
```


## 停止目前所有正在播放的声音
你可以使用`stopall`函数来停止目前所有正在播放的声音，具体来说是由`play`函数播放出来的声音。
```python
play(C('C') % 8)
stopall() # 停止目前正在播放的声音
```

## 按照小节长度移动乐曲类型的音轨的位置
你可以使用乐曲类型的`move`函数，来将乐曲类型的整体的音轨或者指定的音轨进行往右或者往左的位置的指定小节长度的移动。返回值是一个新的乐曲类型。
```python
move(time=0, ind='all')

# time: 移动的长度，单位为小节，为正表示向右方向移动，为负表示向左方向移动

ind: 进行移动的音轨的index，如果为'all'，则移动所有的音轨，如果为整数，则移动对应的index的音轨，从0开始

>>> a.start_times
[0, 2, 3]

b = a.move(2) # 乐曲类型a整体向右移动2个小节的长度

>>> b.start_times
[2, 4, 5]

c = a.move(2, 1) # 乐曲类型a的第1个音轨向右移动2个小节的长度

>>> c.start_times
[2, 2, 3]
```

## 重新设定和弦类型的整体音高
你可以使用和弦类型的`reset_pitch`函数，以和弦类型的第1个音为标准，将和弦类型整体的音高移动到另一个音高，返回的是一个新的和弦类型。参数可以是一个表示音符的字符串或者音符类型。比如一个Cmaj7和弦，你想移动到Emaj7和弦，但是你又不想使用`up`或者`+`来进行移调，因为这需要计算C到E的半音数，那么你可以使用这个方法。
```python
a = C('Cmaj7')

>>> a
[C4, E4, G4, B4] with interval [0, 0, 0, 0]

>>> a.reset_pitch('E')
[E4, G#4, B4, D#5] with interval [0, 0, 0, 0]

>>> a.reset_pitch('E3')
[E3, G#3, B3, D#4] with interval [0, 0, 0, 0]
```

## 筛选和弦类型和乐曲类型中的某一种MIDI信息
你可以使用`get_msg`函数来筛选和弦类型中的某一种MIDI信息，返回一个MIDI信息的列表，比如
```python
a.get_msg(program_change) # 筛选和弦类型a中的program_change信息
```
乐曲类型也有`get_msg`函数，你可以通过指定`ind`参数来提取某一个音轨的某一种MIDI信息，如果不指定，则从所有音轨中查找。
```python
a.get_msg(program_change, ind=0) # 筛选第1条音轨中的program_change信息
```

## 下一章 [musicpy的基本语法（十）](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy的基本语法（十）)

