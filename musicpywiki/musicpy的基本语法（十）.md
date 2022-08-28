# musicpy的基本语法（十）

## 目录
- [对乐曲类型整体进行转调](#对乐曲类型整体进行转调)
- [对乐曲类型整体应用函数](#对乐曲类型整体应用函数)
- [重新设置MIDI通道编号和音轨编号](#重新设置MIDI通道编号和音轨编号)
- [和弦类型从index列表中提取音符组成新的和弦类型](#和弦类型从index列表中提取音符组成新的和弦类型)
- [修改乐理类型的属性的同时返回新的乐理类型](#修改乐理类型的属性的同时返回新的乐理类型)
- [得到一个乐曲实例中的音符总数](#得到一个乐曲实例中的音符总数)

## 对乐曲类型整体进行转调
使用乐曲类型的`modulation`函数可以对于乐曲类型整体进行转调，返回的是转调之后的新的乐曲类型。
```python
modulation(old_scale, new_scale, mode=1, inds='all')

# old_scale: 之前的音阶类型
# new_scale: 之后的音阶类型
# mode: 当mode为1时，通道编号为9的轨道(鼓轨)不会进行转调
# inds: 当inds为'all'时，转换所有的音轨，也可以为一个index的列表，转换列表中的index对应的音轨
```

## 对乐曲类型整体应用函数
使用乐曲类型的`apply`函数可以对于乐曲类型的每个音轨都应用一个函数。
```python
apply(func, inds='all', mode=0, new=True)

# func: 应用到每个音轨上的函数

# inds: 当inds为'all'时，应用函数到所有的音轨上，也可以为一个index或者index的列表

# mode: 当mode为0时，应用函数的音轨会被应用的结果所替代，当mode为1时，只进行应用函数到音轨的步骤

# new: 当new为True时，返回全新的乐曲类型，当new为False时，直接在原来的乐曲类型上修改
```

## 重新设置MIDI通道编号和音轨编号
和弦类型和乐曲类型有`reset_channel`和`reset_track`函数，可以重新设置所有音符，弯音信息，其他MIDI信息的MIDI通道编号和MIDI音轨编号。这两个函数都是直接在原来的对象上直接修改。
```python
# 和弦类型
reset_channel(channel,
              reset_msg=True,
              reset_pitch_bend=True,
              reset_note=True)

# channel: MIDI通道编号
# reset_msg: 是否重新设置所有其他MIDI信息的MIDI通道编号
# reset_pitch_bend: 是否重新设置所有弯音信息的MIDI通道编号
# reset_note: 是否重新设置所有音符的MIDI通道编号

reset_track(track, reset_msg=True, reset_pitch_bend=True)

# track: MIDI音轨编号
# reset_msg: 是否重新设置所有其他MIDI信息的MIDI音轨编号
# reset_pitch_bend: 是否重新设置所有弯音信息的MIDI音轨编号


# 乐曲类型
reset_channel(channels,
              reset_msg=True,
              reset_pitch_bend=True,
              reset_pan_volume=True,
              reset_note=True)

# channels: MIDI通道编号的列表，也可以为一个整数，将每个音轨的MIDI通道编号都设置为这个整数
# reset_msg: 是否重新设置所有其他MIDI信息的MIDI通道编号
# reset_pitch_bend: 是否重新设置所有弯音信息的MIDI通道编号
# reset_pan_volume: 是否重新设置所有声相和音轨音量的MIDI通道编号
# reset_note: 是否重新设置所有音符的MIDI通道编号

reset_track(tracks,
            reset_msg=True,
            reset_pitch_bend=True,
            reset_pan_volume=True)

# tracks: MIDI音轨编号的列表，也可以为一个整数，将每个音轨的MIDI音轨编号都设置为这个整数
# reset_msg: 是否重新设置所有其他MIDI信息的MIDI音轨编号
# reset_pitch_bend: 是否重新设置所有弯音信息的MIDI音轨编号
# reset_pan_volume: 是否重新设置所有声相和音轨音量的MIDI音轨编号
```

## 和弦类型从index列表中提取音符组成新的和弦类型
当你通过index从和弦类型中挑选了一些音符，想把它们取出来，但是还想保留原来的音符之间的距离关系，那么可以使用和弦类型的`pick`函数，返回的是提取出来的音符组成的新的和弦类型。
```python
pick(indlist)

# indlist: 音符的index的列表
```

## 修改乐理类型的属性的同时返回新的乐理类型
常见的乐理类型都可以使用`reset`函数，重新设置任意多个属性，并且返回全新的乐理类型，这个函数只接受关键字参数。
```python
reset(**kwargs)

a = C('C')
>>> a
[C4, E4, G4] with interval [0, 0, 0]
>>> a.reset(interval=[1,1,1])
[C4, E4, G4] with interval [1, 1, 1]
```

## 得到一个乐曲实例中的音符总数
你可以使用乐曲类型的`total`函数来获得乐曲实例中的音符总数。当你想计算一个MIDI文件中的音符总数时，这很有用，你可以把MIDI文件读取到一个乐曲实例中，然后使用这个函数。这个函数将计算出乐曲实例中所有音轨的音符数之和。
```python
total(mode='all')

# mode: 如果是'all'，那么返回总的音符数，包括乐曲实例中的弯音和速度变化信息。
# 如果是'notes'，那么只返回音符的总数。默认是'all'。

>>> a = P([C('C'), C('Cmaj7')])
>> a.total()
7
```
