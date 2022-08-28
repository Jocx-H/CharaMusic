# musicpy的基本语法（八）

## 目录
- [eval_time函数新增返回时间数值的功能](#eval_time函数新增返回时间数值的功能)
- [reverse函数的重新设计](#reverse函数的重新设计)
- [音符和频率之间的转换](#音符和频率之间的转换)
- [乐曲类型新增的一些语法](#乐曲类型新增的一些语法)
- [音轨类型新增的一些语法](#音轨类型新增的一些语法)
- [新增读取其他种类的midi信息的功能](#新增读取其他种类的midi信息的功能)
- [改变和弦类型和乐曲类型的律制](#改变和弦类型和乐曲类型的律制)
- [统一和弦类型的音符的升降号](#统一和弦类型的音符的升降号)
- [和弦类型和乐曲类型的清除速度变化信息和弯音信息的函数的改进](#和弦类型和乐曲类型的清除速度变化信息和弯音信息的函数的改进)
- [清除乐曲类型的pan和volume信息](#清除乐曲类型的pan和volume信息)
- [筛选出和弦类型中满足指定条件的音符](#筛选出和弦类型中满足指定条件的音符)
- [筛选出和弦类型中指定音高范围内的音符](#筛选出和弦类型中指定音高范围内的音符)
- [音符类型新增按照音程关系生成和弦的功能](#音符类型新增按照音程关系生成和弦的功能)
- [按照音程关系生成和弦类型](#按照音程关系生成和弦类型)
- [音程名称的使用](#音程名称的使用)
- [查找一个和弦类型的某度音](#查找一个和弦类型的某度音)
- [确认一个音符是一个和弦的第几度音](#确认一个音符是一个和弦的第几度音)
- [按照和弦的度数来获得和弦声位(chord voicing)](#按照和弦的度数来获得和弦声位chord-voicing)
- [把当前的和弦类型的音符调整为距离另一个和弦的音比较近的地方](#把当前的和弦类型的音符调整为距离另一个和弦的音比较近的地方)

## eval_time函数新增返回时间数值的功能
`eval_time`的参数mode设置为`number`的时候，返回秒数的数值，数值类型为小数。  
另外，除了和弦类型，`eval_time`函数同样也适用于乐曲类型。
```python
>>> a.eval_time(80, mode='number') # 计算一个和弦类型的时间长度，返回一个数值
92.56
```

## reverse函数的重新设计
在2021年6月，`reverse`函数有了重新的设计，重新设计过后的`reverse`函数的算法得到的结果与音频文件的反向本质上是一致的 (除了声音的开始和结束的反向的听感)。 
如果你想使用以前的reverse函数的算法，可以使用`reverse_chord`函数。这个改变使用于和弦类型，乐曲类型和音轨类型。

## 音符和频率之间的转换
你可以使用`get_freq`函数来得到一个音符的频率，可以设置标准音高A4的频率以获得不同标准下的音符的频率。  
你可以使用`freq_to_note`函数来把一个频率转换为最接近这个频率的音符，可以设置标准音高A4的频率以获得不同标准下的最接近这个频率的音符。
```python
# get_freq函数的参数可以是表示音符的字符串或者音符类型
>>> get_freq('C5') # 获得音符C5的频率，默认的标准音高A4为440 hz
523.2511306011972

>>> get_freq('C5', standard=415) # 获得音符C5的频率，使用巴洛克标准音高415 hz
493.5209527261292

>>> freq_to_note(500) # 获得最接近500 hz的频率的音符，默认的标准音高A4为440 hz，返回的是音符类型
B4

>>> freq_to_note(500, to_str=True) # 设置to_str参数为True，返回表示音符的字符串
B4

>>> >>> freq_to_note(500, standard=415) # 获得最接近500 hz的频率的音符，使用巴洛克标准音高415 hz
C5
```

## 乐曲类型新增的一些语法

### 替换一个乐曲类型中的音轨
```python
a[i] = new_track # 把乐曲类型a的第i个音轨(从0开始)替换为new_track, 这里的new_track为音轨类型
```

### 删除一个乐曲类型中的音轨
```python
del a[i] # 删除乐曲类型a的第i个音轨(从0开始)
```

### 把一个乐曲类型的音轨静音
你可以使用`mute`函数把一个乐曲类型中的音轨静音，使用`unmute`函数取消静音。
```python
a.mute(i=None) # 如果不指定i，则将全部的音轨静音，如果指定i，则将第i个音轨静音(从0开始)
a.unmute(i=None) # 取消静音，参数的用法和mute函数一样
```

## 音轨类型新增的一些语法
和弦类型中的`a + i`, `a - i`, `a | i`, `a & i`, `a % i`的语法现在也已经添加到音轨类型中，用法可以参考和弦类型中的用法。

## 新增读取其他种类的midi信息的功能
现在除了musicpy中已经定义的midi信息的类型(包括`tempo`, `pitch_bend`, `pan`, `volume`)，在读取midi文件时，musicpy可以读取更多其他类型的midi信息，统一存放在`other_messages`这个属性里，`other_messages`是一个列表。`other_messages`一般来说只会读取到和弦类型与乐曲类型中。

在构建弦类型与乐曲类型的时候，也可以设定`other_messages`，把想要写入的其他的midi信息放在`other_messages`这个列表里，在使用`play`或者`write`函数时会默认写入其中存储的midi信息。

在使用`read`函数的时候，如果选择返回和弦类型，那么`other_messages`会添加到和弦类型的属性中,如果你不想要其他的midi信息，那么可以在读取之后把返回结果的和弦类型的`other_messages`使用列表的`clear`方法清空，比如`a.other_messages.clear()`。

如果选择返回乐曲类型，那么`other_messages`会添加到每一个音轨的和弦类型中，也会合并所有的音轨的其他的midi信息作为一个整体的`other_messages`添加到乐曲类型的属性中。在对于读取过后的乐曲类型提取某条音轨时，提取出来的音轨类型中的`content`(是一个和弦类型)也会有之前读取时添加的`other_messages`。

由于目前musicpy中已定义的其他的midi信息包括`program_change`，也就是改变乐器的信息，此时如果修改乐曲类型或者音轨类型的乐器，就很有可能因为`other_messages`中有着`program_change`的信息而导致在写入midi文件后乐器并没有发生变化，此时你可以把`play`函数和`write`函数中的`nomsg`参数设置为True，可以忽略`other_messages`(也就是不进行写入)，这样就可以让乐器发生变化。或者你也可以把`other_messages`的列表清空。如果你还想保留`other_messages`中的其他的midi信息，你可以把`other_messages`中的为'program_change'类型的midi信息去除，比如`a.other_messages = [i for i in a if type(i) != program_change]`

在使用`play`函数或者`write`函数的时候，当写入的和弦类型或者乐曲类型（或者其他的乐理类型）没有`other_messages`属性或者`other_messages`的列表为空/None的时候，你可以指定`msg`参数，会写入`msg`参数的列表中的midi信息。如果写入的乐理类型有`other_messages`的属性并且不为空/None时，则会写入乐理类型自带的`other_messages`，此时`play`函数或者`write`函数的`msg`参数会被忽略。

如果你不想写入任何`other_messages`，那么可以设置`nomsg`参数为True (默认值为False)，会忽略传入的乐理类型的`other_messages`以及指定的`msg`参数。

### 目前musicpy已经定义的其他midi信息的类型
其他的midi信息的类型以General MIDI为标准。

大部分的midi信息类型都有`track` (音轨编号，从0开始), `channel` (通道编号，从0开始), `time` (开始时间，从0开始，单位为小节)这3个参数，用法都是一样的，以下不作介绍。

1. 控制器事件  
   controller_event(track=0,
                 channel=0,
                 time=0,
                 controller_number=None,
                 parameter=None)
* controller_number: 控制器事件的数字
* parameter: 控制器事件的参数

2. 版权事件  
copyright_event(track=0, time=0, notice=None)
* notice: 版权声明的内容，字符串

3. 调号事件  
   key_signature(track=0,
              time=0,
              accidentals=None,
              accidental_type=None,
              mode=None)
* accidentals: 调号中的升降号的个数，整数
* accidental_type: 调号使用的升降号的类型，可以指定升号(SHARPS)或者降号(FLATS)
* mode: 调式，可以指定大调(MAJOR)或者小调(MINOR)

4. 系统专用数据事件  
sysex(track=0, time=0, manID=None, payload=None)
* manID: 制造商的ID
* payload: 实际数据(负载)，必须是以二进制打包的值

5. 文本事件  
text_event(track=0, time=0, text='')
* text: 写入的文本，字符串

6. 拍号事件  
   time_signature(track=0,
               time=0,
               numerator=None,
               denominator=None,
               clocks_per_tick=None,
               notes_per_quarter=8)
* numerator: 拍号的分子
* denominator: 拍号的分母
* clocks_per_tick: 每一次节拍器点击的ticks
* notes_per_quarter: 一个4分音符里的32分音符的数量

7. 普遍系统专用数据事件  
   universal_sysex(track=0,
                time=0,
                code=None,
                subcode=None,
                payload=None,
                sysExChannel=127,
                realTime=False)
* code: 事件的代码
* subcode: 事件的副代码
* payload: 实际数据(负载)，必须是以二进制打包的值
* sysExChannel: SysEx通道 (0 - 127)
* realTime: 设置实时的flag

8. 注册参数编号事件  
   rpn(track=0,
    channel=0,
    time=0,
    controller_msb=None,
    controller_lsb=None,
    data_msb=None,
    data_lsb=None,
    time_order=False,
    registered=True)
* controller_msb: 控制器的最高有效字节
* controller_lsb: 控制器的最低有效字节
* data_msb: 控制器的参数的最高有效字节
* data_lsb: 控制器的参数的最低有效字节
* time_order: 是否按照时间顺序排序控制事件
* registered: 如果为True，返回RPN (注册参数编号)，如果为False，返回NRPN (非注册参数编号)

9. 调节群组事件  
   tuning_bank(track=0,
            channel=0,
            time=0,
            bank=None,
            time_order=False)
* bank: 调节群组编号 (0 - 127)
* time_order: 是否按照时间顺序排序组件事件

10. 调节音色事件  
    tuning_program(track=0,
               channel=0,
               time=0,
               program=None,
               time_order=False)
* program: 调节音色编号 (0 - 127)
* time_order: 是否按照时间顺序排序组件事件

11. 通道压力事件  
channel_pressure(track=0, channel=0, time=0, pressure_value=None)
* pressure_value: 通道压力 (0 - 127)

12. 音色转换事件  
program_change(track=0, channel=0, time=0, program=0)
* program: 音色编号 (0 - 127)

13. 音轨名称事件  
track_name(track=0, time=0, name='')
* name: 分配给音轨的名称，字符串

### 可以使用event函数生成任意一种其他的midi信息
你可以使用`event`函数来得到任何一种其他的midi信息
```python
event(mode='controller', *args, **kwargs)
# mode: 表示你想要产生的MIDI事件的类型,可以是'controller', 'copyright', 'key signature', 'sysex',
# 'text', 'time signature', 'universal sysex', 'nrpn', 'rpn', 'tuning bank', 'tuning program',
# 'channel pressure', 'program change', 'track name'其中之一

# *args, **kwargs: 你选择的MIDI事件的参数

new_event = event('controller', track=1, channel=2, controller_number=12, parameter=30)
```

## 改变和弦类型和乐曲类型的律制
你可以使用`tuning`类型来作为一个音符插入到和弦类型和乐曲类型的音轨中改变律制(自定义每个音符对应的频率)， 
在写入和弦类型和乐曲类型到midi文件时，改变律制的midi信息也会一起写入到midi文件中。
```python
tuning(tuning_dict,
       track=0,
       sysExChannel=127,
       realTime=True,
       tuningProgam=0)

* tuning_dict: 表示律制的字典，表现形式为音符:频率，音符可以是字符串或者音符类型，比如: {'C5': 530, 'D5': 590}

* track: 轨道数

* sysExChannel: SysEx通道 (0 - 127)

* realTime: 设置实时的flag

* tuningProgram: 调节音色编号

part1 = C('C')
part1.append(tuning({'C5': 530, 'D5': 590}))
>>> part1
[C4, E4, G4, tuning: {'C5': 530, 'D5': 590}] with interval [0, 0, 0, 0]
```

## 统一和弦类型的音符的升降号
你可以使用和弦类型的`same_accidentals`函数来统一和弦类型的音符的升降号,
```python
a = chord('C5, D#5, F5, Ab5, E5, D5, C#5')
>>> a.same_accidentals('#')
[C5, D#5, F5, G#5, E5, D5, C#5] with interval [0, 0, 0, 0, 0, 0, 0]
>>> a.same_accidentals('b')
[C5, Eb5, F5, Ab5, E5, D5, Db5] with interval [0, 0, 0, 0, 0, 0, 0]
```

## 和弦类型和乐曲类型的清除速度变化信息和弯音信息的函数的改进
现在和弦类型和乐曲类型的`clear_tempo`函数和`clear_pitch_bend`函数增加了`cond`参数，你可以指定一个条件函数(推荐使用lambda函数) 
作为想要清除掉的速度变化信息和弯音信息的筛选器，条件函数里面描述的是你想要清除的信息需要满足的条件，如果让条件函数返回True,则会被清除。
```python
# 清除和弦类型的速度变化和弯音信息，使用cond参数，乐曲类型的可以类比
a.clear_tempo(cond=lambda s: s.start_time == 1 and s.bpm == 120)
a.clear_pitch_bend(cond=lambda s: s.start_time == 1 and s.value == 0)
```

## 清除乐曲类型的pan和volume信息
你可以使用乐曲类型的`clear_pan`函数来清除乐曲类型的pan信息(左右声道混音位置)，使用乐曲类型的`clear_volume`函数来清除乐曲类型的volume信息(音轨总体音量大小)。
```python
a.clear_pan()
a.clear_volume()
```

## 筛选出和弦类型中满足指定条件的音符
你可以使用和弦类型的`filter`函数，通过指定条件过滤掉和弦类型中不满足条件的音符,筛选出和弦类型中满足指定条件的音符。
比如筛选出音量在20到80之间的音符，音符长度在1/16小节到1小节之间的音符,音高在A0到C8之间的音符等等。你也可以指定一个函数对于筛选出来的音符进行操作。  
```python
filter(self, cond, action=None, mode=0, action_mode=0)

# cond: 筛选的条件函数，必须为一个参数为音符，返回值为布尔值的函数，推荐使用lambda函数

# action: 操作函数，如果不为None，则对于筛选出来的音符进行这个函数的操作，但是并不单独提取出筛选出来的音符，
# 返回的是经过修改的和弦类型，如果为None，则返回筛选出来的音符组成的和弦类型和第一个筛选出来的音符的开始时间

# mode: 如果为1，则返回筛选出来的音符的index列表

# action_mode: 如果为0，action函数作用音符的返回值会替换掉它作用的音符，如果为1，action函数会直接作用到音符上

a = chord('C, E, G, B') # 初始化一个和弦
a.setvolume([10, 20, 50, 90]) # 设置音符的音量
>>> a.filter(lambda s: 20 <= s.volume < 80) # 筛选出和弦类型里音量在20到80之间的音符
([E4, G4] with interval [0, 0], 0) # 返回筛选出来的音符组成的和弦类型以及第一个筛选出来的音符的开始时间

# 对于音量在20到80之间的音符，音量都设置为50
b = a.filter(lambda s: 20 <= s.volume < 80, action=lambda s: s.setvolume(50), action_mode=1)
>>> b
[C4, E4, G4, B4] with interval [0, 0, 0, 0] # 返回经过action函数修改音量的和弦类型
>>> b.get_volume() # 获得新的和弦类型的音量
[10, 50, 50, 90] # 之间音量在20到80之间的音符的音量现在都变成了50
```

## 筛选出和弦类型中指定音高范围内的音符
你可以使用和弦类型的`pitch_filter`函数筛选出和弦类型中指定音高范围内的音符。这个功能在很多场合下非常重要，比如当你读取了一个midi文件时，
需要把midi文件的音符对应到一个软件里的钢琴上进行显示，一般来说钢琴为88键，音高范围为A0 ~ C8，但是midi文件中是可以存储超过这个音高范围的音符的， 
可能低于A0，也可能高于C8，因此我们需要把读取的midi文件的音符的音高限制在A0到C8之间，不属于这个区间的音符需要去掉。这个功能就可以做到这件事情，
并且会重新计算筛选过后的所有音符的间隔，因此并不会影响到再次输出为midi文件时音符的位置。有着更普遍用途的`filter`函数也会重新计算所有音符的间隔。
```python
pitch_filter(self, x='A0', y='C8')

# x: 音高范围的最低音，默认值为A0

# y: 音高范围的最高音，默认值为C8

a = chord('Ab0, C5, E5, G5, B5, G10') # this is a chord with 2 notes that the pitches do not belongs to A0 ~ C8
>>> a.pitch_filter() # 使用默认音高范围A0到C8对和弦类型进行音符的筛选
([C5, E5, G5, B5] with interval [0, 0, 0, 0], 0)
# 返回筛选出来的在指定音高范围内的音符组成的和弦类型，和第一个筛选出来的音符的开始时间

b = chord('Ab0, C5, E5, G5, A5, C7, G10')
>>> b.pitch_filter('C5', 'C6') # 筛选出音高在C5到C6之间的音符
([C5, E5, G5, A5] with interval [0, 0, 0, 0], 0)
# 返回筛选出来的在指定音高范围内的音符组成的和弦类型，和第一个筛选出来的音符的开始时间
```

## 音符类型新增按照音程关系生成和弦的功能
你可以使用音符类型的`with_interval`函数，指定一个音程来形成一个含有两个音的和弦类型，两个音分别是当前的音符类型和与这个音符类型形成指定的音程关系的音符类型。
```python
a = N('C5')
>>> a.with_interval(major_seventh) # 形成一个表示C5的大七度的音程的和弦
[C5, B5] with interval [0, 0]
```

## 按照音程关系生成和弦类型
你可以使用`getchord_by_interval`函数通过音程关系的列表生成和弦类型，可以选择与根音的音程关系或者相每两个相邻的音之间的音程关系。 
音符类型也可以使用这个函数，使用的时候音符类型本身会作为起始音。
```python
getchord_by_interval(start,
                     interval1,
                     duration=0.25,
                     interval=0,
                     cummulative=True)

# start: 和弦类型的起始音，可以是表示音符的字符串或者音符类型
# interval1: 表示音程关系的列表，元素为整数
# duration: 生成的和弦类型的音符长度
# interval: 生成的和弦类型的音符间隔
# cummulative: 如果为True，音程关系为与起始音的音程关系，如果为False，音程关系为每两个相邻的音之间的音程关系，默认值为True

>>> getchord_by_interval('C5', [major_third, perfect_fifth, major_seventh])
# 获得起始音为C5，与C5依次形成大三度，完全五度和大七度的音组成的和弦类型
[C5, E5, G5, B5] with interval [0, 0, 0, 0] # 获得C大七和弦

>>> getchord_by_interval('C5', [major_third, minor_third, major_third], cummulative=False)
# 获得起始音为C5，相邻音程依次为大三度，小三度，大三度的音组成的和弦类型
[C5, E5, G5, B5] with interval [0, 0, 0, 0] # 获得C大七和弦

a = N('C5')
a.getchord_by_interval([major_third, perfect_fifth, major_seventh]) #音符类型调用这个函数
[C5, E5, G5, B5] with interval [0, 0, 0, 0]
```

## 音程名称的使用
在musicpy里有着完整的音程名称的全局定义，可以直接使用，比如`major_third`(大三度)的值为4 (半音数), `perfect_eleventh`(完全十一度)的值为17 (半音数)。 
此外，最近也加入了音程名称的简写的全局定义，比如你可以使用`M3`来代替`major_third`(大三度), `m3`来代替`minor_third`(小三度),
`M7`来代替`major_seventh`(大七度)等等。在这里我会展示出musicpy里完整的音程名称的全局定义，在这里的所有的音程名称都可以作为全局的常量使用。
```python
perfect_unison = diminished_second = P1 = d2 = 0
minor_second = augmented_unison = m2 = A1 = 1
major_second = diminished_third = M2 = d3 = 2
minor_third = augmented_second = m3 = A2 = 3
major_third = diminished_fourth = M3 = d4 = 4
perfect_fourth = augmented_third = P4 = A3 = 5
diminished_fifth = augmented_fourth = tritone = d5 = A4 = 6
perfect_fifth = diminished_sixth = P5 = d6 = 7
minor_sixth = augmented_fifth = m6 = A5 = 8
major_sixth = diminished_seventh = M6 = d7 = 9
minor_seventh = augmented_sixth = m7 = A6 = 10
major_seventh = diminished_octave = M7 = d8 = 11
perfect_octave = octave = augmented_seventh = diminished_ninth = P8 = A7 = d9 = 12
minor_ninth = augmented_octave = m9 = A8 = 13
major_ninth = diminished_tenth = M9 = d10 = 14
minor_tenth = augmented_ninth = m10 = A9 = 15
major_tenth = diminished_eleventh = M10 = d11 = 16
perfect_eleventh = augmented_tenth = P11 = A10 = 17
diminished_twelfth = augmented_eleventh = d12 = A11 = 18
perfect_twelfth = tritave = diminished_thirteenth = P12 = d13 = 19
minor_thirteenth = augmented_twelfth = m13 = A12 = 20
major_thirteenth = diminished_fourteenth = M13 = d14 = 21
minor_fourteenth = augmented_thirteenth = m14 = A13 = 22
major_fourteenth = diminished_fifteenth = M14 = d15 = 23
perfect_fifteenth = double_octave = augmented_fourteenth = P15 = A14 = 24
minor_sixteenth = augmented_fifteenth = m16 = A15 = 25
major_sixteenth = diminished_seventeenth = M16 = d17 = 26
minor_seventeenth = augmented_sixteenth = m17 = A16 = 27
major_seventeenth = M17 = 28
```

## 查找一个和弦类型的某度音
现在比如你有一个C小十一和弦，你想得到它的3度音和9度音，这时候可以使用和弦类型的`interval_note`函数，输入一个度数进行查找。 
如果当前的和弦类型并不包含指定度数的音符，那么会返回`None`。支持查找的度数包括从1度(根音)一直到13度，也包括变化音的情况，比如`#5`, `b9`。
```python
interval_note(self, interval, mode=0)

# interval: 想要查找的度数，可以是整数或者表示度数的字符串

# mode: 为0的时候，如果查找不到指定度数的音，返回None，为1的时候，会返回和弦类型的起始音加上指定度数的音符类型

>>> C('Cm11') # C小十一和弦
[C4, D#4, G4, A#4, D5, F5] with interval [0, 0, 0, 0, 0, 0]

>>> C('Cm11').interval_note(3) # 查找C小十一和弦的3度音
D#4 # 返回C小十一和弦的3度音，这里更加乐理上严谨一些的话应该是Eb4，
# 之所以这里是D#4是因为musicpy默认的音符表示方式是以#号为优先

>>> C('Cm11').interval_note(9) # 查找C小十一和弦的9度音
D5 # 返回C小十一和弦的9度音

>>> C('Cm11').interval_note(d5, mode=1) # 返回C小十一和弦的起始音的降5度音，
# 注意这里的度数不能为字符串，因为音符类型加上字符串会解释为组成一个和弦类型
F#4 # 返回C小十一和弦的起始音的降5度音 (这里严谨来说应该是Gb4，也是和之前同样的原因)
```

## 确认一个音符是一个和弦的第几度音
这里做的是和`查找一个和弦类型的某度音`反过来的事情，你可以使用和弦类型的`note_interval`函数，确认一个音符是一个和弦类型的第几度音。
如果指定的音符并不在和弦类型中，也会返回和弦类型的起始音与这个音符的度数关系。
```python
note_interval(self, current_note, mode=0)

# current_note: 想要确认度数的音符，可以是表示音符的字符串或者音符类型

# mode: 为0的时候，会返回以升降号和数字表示的度数，为1的时候，会返回纯英文的音程表示

>>> C('Cm11') # C小十一和弦
[C4, D#4, G4, A#4, D5, F5] with interval [0, 0, 0, 0, 0, 0]

>>> C('Cm11').note_interval('Eb4') # 确认音符Eb4是以C4为起始音的C小十一和弦原位的几度音
'b3' # 返回的结果是3度音(b3表示小3度，或者也可以说降3度，因为没有降的3度是大3度)

>>> C('Cm11').note_interval('D5') # 确认音符D5是以C4为起始音的C小十一和弦原位的几度音
'9' # 返回的结果是9度音 (大9度音)

>>> C('Cm11').note_interval('Db5') # 确认音符Db5是以C4为起始音的C小十一和弦原位的几度音
'b9' # C小十一和弦并没有包含Db这个音，但是这个函数也会返回和弦的起始音C4与Db5形成的音程关系，也就是b9 (降九度或者小九度)

>>> C('Cm11').note_interval('D5', mode=1) # 确认音符D5是以C4为起始音的C小十一和弦原位的几度音，返回纯英文的表示
'major ninth'
```

## 按照和弦的度数来获得和弦声位(chord voicing)
一个和弦的音有很多种排列组合的方式，每一种独特的组合都是一种voicing，通过对于和弦的音按照不同的顺序和八度数的摆放，一个和弦可以有各种各样的voicings，
每一种voicing都有着独特的听感，无论是柱式和弦，分解和弦还是琶音都可以听出不同的味道。比如一个Cm11和弦，你可以按照原位1, 3, 5, 7, 9, 11度音的顺序来弹，
也可以按照1, 5, 9, 3, 7, 11度音的顺序来营造一种更加梦幻唯美的听感。因此我们需要一个方便的函数可以通过和弦的音的度数来获得一个和弦的voicing，包括和弦的音的顺序，省略音，重复音在更高的八度的情况都需要考虑到。我最近设计出来的和弦类型的`get_voicing`函数可以做到这些。
```python
get_voicing(self, voicing)

# voicing: 和弦声位的列表，也就是表示和弦的度数的顺序的列表，元素可以是整数或者表示度数的字符串

# 需要注意的是，和弦声位列表中必须都是当前和弦类型有的度数

>>> C('Cm11').get_voicing([1,5,9,3,11,7]) # C小十一和弦按照根音，5度音，9度音，3度音，11度音，7度音的顺序摆放，
# 并且重新按照后面的音比前面的音更高的规则重新分配所有音符的八度数
[C4, G4, D5, D#5, F5, A#5] with interval [0, 0, 0, 0, 0, 0]
# 返回按照指定的和弦声位列表进行声部排列的C小十一和弦的voicing的和弦类型

play(C('Cm11').get_voicing([1,5,9,3,11,7]) % (1, 1/8), 150) # 以快速琶音进行演奏
```

## 把当前的和弦类型的音符调整为距离另一个和弦的音比较近的地方
在考虑和弦声部排列的时候，后一个和弦与前一个和弦之间如果想要更加平滑地连接，那么其中一个办法就是把后一个和弦的音放在距离前一个和弦的音比较近的地方，
这样和弦进行中不同声部的连接就会比较顺畅，因为声部的移动比较小。比如Am和弦的原位接到F和弦的原位，也就是A C E接到F A C，如果想要比较平滑地连接这两个和弦，
可以调整F和弦的音的顺序，让F和弦的每个音都距离Am和弦的原位的每个音尽量近，比如调整为A C F，这样F和弦的前两个音都与Am和弦的原位的前两个音是相同的，
第三个音F也只比Am和弦的原位的第三个音高一个半音，因此这两个和弦连接起来就会听着比较平滑流畅。

你可以使用和弦类型的`near_voicing`函数，把当前的和弦类型的音调整为另一个和弦类型的音在音高上比较相近的顺序，如果本身两个和弦的音高差就比较大，
那么也会把当前的和弦类型的音移动到另一个和弦类型的音高范围内。你也可以让当前和弦类型的最低音固定住，不进行最近音高距离的调整，因为有些时候最低音的变化
得到的和弦转位并不是我们想要的。
```python
near_voicing(self, other, keep_root=True, root_lower=False)

# other: 作为调整当前和弦类型的音的标准的和弦类型

# keep_root: 为True的时候，保持当前的和弦类型的最低音在调整过后还是最低音

# root_lower: 在你选择保持当前的和弦类型的最低音的情况下，为True的时候，
# 当前和弦类型的最低音会在标准的和弦类型的最低音的下方，为False的时候在上方。

>>> C('F').near_voicing(C('Am'), keep_root=False) # 得到F和弦原位关于Am和弦原位的最近距离的voicing，不保持最低音
[A4, C5, F5] with interval [0, 0, 0]

# 写一段C大调的2516和弦进行的平滑声部连接
chord1 = C('Dm7', 3).get_voicing([1, 7, 3]) % (1,[1/4,1/4,1/2])
chord2 = C('G7, omit5', 4).near_voicing(chord1, keep_root=True, root_lower=True) % (1,[1/4,1/4,1/2])
chord3 = C('Cmaj7, omit5', 4).near_voicing(chord1, keep_root=True) % (1,[1/4,1/4,1/2])
chord4 = C('Am7, omit5', 4).near_voicing(chord1, keep_root=True) % (1,[1/4,1/4,1/2])
play(chord1 | chord2 | chord3 | chord4, 165)
```

## 下一章 [musicpy的基本语法（九）](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy的基本语法（九）)

