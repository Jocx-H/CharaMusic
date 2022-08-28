# 如何使用musicpy

### 在这一部分，我将会讲解如何使用musicpy这门语言来做一些音乐上比较实际的应用。

## 目录
  - [读取midi文件，转换成和弦类型，以便于进行各种乐理上的操作](#读取midi文件转换成和弦类型以便于进行各种乐理上的操作)
  - [把和弦类型写入midi文件，以方便DAW中查看和编辑](#把和弦类型写入midi文件以方便DAW中查看和编辑)
  - [我专门为musicpy这个项目写了一个高效的IDE供大家使用](#我专门为musicpy这个项目写了一个高效的IDE供大家使用)
  - [将musicpy的数据结构存储为单独的数据文件](#将musicpy的数据结构存储为单独的数据文件)

## 读取midi文件，转换成和弦类型，以便于进行各种乐理上的操作
使用read函数可以读取一个midi文件，将midi文件的内容转换成和弦类型。
```python
read(name,
     is_file=False,
     get_off_drums=False,
     split_channels=False,
     clear_empty_notes=False,
     clear_other_channel_msg=False)
```

* name: midi文件名（包括.mid文件扩展名）

* is_file: 是用来处理当第一个参数name传入的是一个midi文件流的情况。第一个参数name如果是midi文件流，is_file需要设置为True以进行正常的读取。默认值为False，第一个参数为midi文件名的时候用不到这个参数。

* get_off_drums: 设置为True的时候，过滤掉鼓轨。get_off_drums的默认值为False。

* split_channels: 当读取的midi文件是把所有不同的乐器的音符全部放在一个midi通道里，设置这个参数为True以转换为正确的乐曲类型。

* clear_empty_notes: 设置为True时，在转换每个音轨为和弦类型时将所有duration <= 0的音符类型去除。

* clear_other_channel_msg: 设置为True时，会清除返回的每一个音轨中不属于当前音轨的通道编号的midi信息。

### read函数使用示例：
比如现在有一个midi文件`Clair de Lune.mid`，这个midi文件只有一个有音符的轨道，里面存储着整首曲子的所有音符的信息，这个midi文件放在musicpy的文件夹里，现在使用read函数读取
```python
current_piece = read('Clair de Lune.mid')
A = current_piece.tracks[0]
```

现在我们可以对和弦类型A进行各种乐理上的操作了。和弦类型A里面存储的是整首曲子的信息，包括所有的音符，音符的间隔。可以使用基础语法部分里面讲到的很多语法来对曲子A进行乐理上的玩转，比如转调，升调，降调，切片，倒序等等。

我目前正在开发的一首曲子的调性判断算法也可以直接用在这里，不过目前还在开发阶段，还有很多地方需要改进，详情可以看detect_scale函数。

## 把和弦类型写入midi文件，以方便DAW中查看和编辑
使用write函数可以把一个音符类型，和弦类型，乐曲类型等乐理类型写入midi文件。

实际上play函数里面就有使用到write函数，然后调用pygame播放生成的midi文件。

```python
write(current_chord,
      bpm=120,
      channel=0,
      start_time=None,
      name='temp.mid',
      instrument=None,
      i=None,
      save_as_file=True,
      msg=None,
      nomsg=False,
      deinterleave=False,
      remove_duplicates=False,
      **midi_args)
```

* current_chord: 想要写入的乐理类型，可以为音符类型，和弦类型，乐曲类型，音轨类型，鼓点类型，也可以是一个和弦类型的列表。

* bpm: 想要写入的曲子的BPM（曲速）。

* channel: 想要写入的频道编号，需要注意的是9对应的是鼓的轨道。

* start_time: 想要写入的曲子的起始时间（单位为小节），如果为None，则使用和弦类型自带的start_time。

* name: 想要的midi文件名，生成的midi文件的名字。

* instrument: 想要写入的轨道的乐器类型，对应的是General Midi的乐器，编号从0~127,可以输入乐器名（General Midi的乐器列表里的乐器名），也可以直接输入数字（0-127之间的任何一个整数）。

* i: 与instrument参数一样

* save_as_file: 设置为True的时候，在本地写入或者生成midi文件，不返回任何值。设置为False的时候，返回一个midi文件流。默认值为True。

* msg: 你想要写入midi文件的其他的midi信息，可支持的类型请看基础语法(八)

* nomsg: 可以设置是否写入其他的midi信息,为True的时候将不会写入

* other_args: 其他的midi文件写入的一些配置参数，包括：  
deinterleave=False,  
remove_duplicates=False,  
**midi_args  
(这些参数具体请参考midiutil的文档)

## 我专门为musicpy这个项目写了一个高效的IDE供大家使用
[musicpy_editor](https://github.com/Rainbow-Dreamer/musicpy_editor)是我专门为musicpy语言开发的一个IDE。

这个编辑器里面有很多方便快速写musicpy代码的功能，并且可以实时听到对应的音乐。

接下来详细介绍一下这个编辑器。

首先，在上面的框输入musicpy代码，在下方的框显示结果，实时运行，不使用print和自动补全都是默认打开的，不用的时候也可以到对应的打钩框关闭。自动补全让你在写代码时可以只打一两个字符就给出一个包含这几个字符的函数方法的列表，让你快速选择，鼠标点击和方向盘上下键加上回车选择都可以。自动补全在一个对象的"."之后也会开启，此时的自动补全列表是这个对象所拥有的类方法和属性。小括号和中括号自动配对补全（打出左边的括号，会自动填上右边的括号），并且输入的光标自动放在两个括号之间。文件栏里面有打开musicpy代码文件（只要是文本文件格式都可以），保存当前写的musicpy代码为文件，以及设置。这个编辑器也支持语法高亮，同时大家也可以在设置里自己定制语法高亮的内容和对应的颜色。

我还给这个编辑器加入了输入以及输出界面的开灯/关灯功能，让大家可以在白底黑字主题和黑底白字主题来回切换，以适应不同程序员的的口味。同时，大家可以自己选择字体类型和字体大小，以及自己定制编辑器的部件的背景颜色，字体颜色以及鼠标光标移到部件上显示的颜色。设置文件config.py里的所有参数都可以修改，而且不需要打开config.py修改，只需要打开编辑器，然后点击左上角的文件——设置，在弹出的设置窗口里修改参数，然后点击保存按钮就可以了。某些参数修改后需要重启编辑器才会看到修改后的效果，我接下来在介绍设置里的参数的部分会说。

在设置里的参数的说明：
* bakground_image: 可以选择背景图片的文件路径，点击“更改”按钮就可以打开一个文件浏览框，选择自己想要设置的背景图片的文件路径，也可以手动输入文件路径。修改之后点击保存就会重新加载背景图片。

* background_places: 背景图片的位置，第一项为x（横向）的坐标，第二项为y（纵向）的坐标，以编辑器的左上角为0, 0（原点），x从左往右加大，y从上往下加大。修改之后点击保存就会重新加载背景图片的位置。

* eachline_character: 自动换行每一行的最大字数。

* pairing_symbols: 自动补全符号的列表，大家可以自己定制想要自动补全的符号，比如打一个`(`会自动补全`)`。

* wraplines_number： 自动换行的时候每两行之间的空行数。

* font_type: 输入和输出窗口的字体类型。

* font_size: 输入和输出窗口的字体大小。

* background_mode: 开灯/关灯模式的参数，`white`表示开灯模式，`black`表示关灯模式，在编辑器的主界面会有一个按钮可以切换开灯和关灯。

* grammar_highlight: 语法高亮的字典，键为颜色名称，值为需要语法高亮为这种颜色的单词的列表。

* background_color: 编辑器里的部件的背景颜色。（需要重启编辑器才能看到修改后的效果）

* foreground_color: 编辑器里的部件的字体颜色。（需要重启编辑器才能看到修改后的效果）

* active_background_color: 鼠标光标移到编辑器里的部件上显示的颜色。（需要重启编辑器才能看到修改后的效果）

* day_and_night_colors: 开灯/关灯模式分别对应的输入窗口和输出窗口的背景颜色名称。（需要重启编辑器才能看到修改后的效果）

* search_highlight_color: 搜索关键词时的匹配片段的高亮的颜色，依次为一般高亮颜色，选中高亮颜色

不使用print如果打勾，在输入一行代码时，在每一行，如果有可以显示出来的东西，下面的框就会显示，等价于自动加上了print。实时运行如果打勾，编辑器会在你写的代码发生改变时实时运行你写的代码，并且在下方的框里显示出结果（如果不使用print打勾的话）。在这个musicpy编辑器里，除了实时运行，自动补全，不使用print的几个打勾框和文件栏之外，还有保存的按钮，保存当下写的代码为文件；运行的按钮，运行当下写的代码，如果当前的代码运行会出现错误，则显示出错误信息在下方的框里，并且不会影响到编辑器的正常工作。在实时运行的时候，如果当前的代码运行会出现错误，则在下方的框不会显示任何东西，此时点击运行的按钮可以看到错误信息；自动换行的按钮，可以让下面的框显示的运行结果自动换行。

这个musicpy编辑器有几个非常好用的功能，接下来一一介绍。

1.在一行musicpy代码之前加上`/`,就会直接播放这段代码代表的音乐，并且是内部播放，并不会打开任何电脑上的播放器。与此同时也会在musicpy文件夹里生成当前的musicpy代码对应的midi文件。这个语法等价于在这行代码放在play函数里面，play函数的参数设置可以用英文的逗号跟在代码的后面，比如bpm（曲速），instrument(乐器)等等的选择。建议实时运行同时打开（默认是打开的），就可以musicpy代码写到哪，加上`/`就可以马上听到。比如在编辑器里写
```python
/C('Dmaj7') % 4 | C('Em7') % 4, 150
```
就可以直接听到这段musicpy语言对应的音乐了。

2.在一行musicpy代码前（特别是表示一个和弦的代码）加上`?`可以得到这个和弦按照乐理逻辑判断出来的和弦类型名称，比如
```python
?chord(['C','E','G','B'])
```
会得到`Cmaj7`。

这个语法等价于表示一个和弦的musicpy代码放在detect函数里面，detect函数的参数配置也可以用英文的逗号跟在代码的后面。

3.点击鼠标右键可以弹出IDE的菜单，可以选择播放选中的musicpy语句，也可以选择可视化播放选中的musicpy语句，可视化的窗口是我写的另一个音乐相关的项目，智能钢琴[Ideal Piano](https://github.com/Rainbow-Dreamer/Ideal-Piano)的主体。

4.在鼠标右键菜单中，可以选择导入midi文件，（在文件栏里也有）选择一个midi文件之后会自动生成一个默认参数的read函数的代码，并且赋值给一个变量new_midi_file，
变量名可以自行修改。停止播放是用来在播放musicpy代码时，如果只想听一段，不想听完整首曲子，那么可以马上停止播放。使用搜索功能可以搜索关键词。

5.这个编辑器里有内置很多电脑键盘的快捷键的组合，分别对应多种不同的功能。

ctrl + f 弹出搜索框  

ctrl + e 停止播放  

ctrl + d 导入midi文件  

ctrl + w 打开文件(文本文件)  

ctrl + s 保存当前的代码为文本文件  

ctrl + q 关闭编辑器  

ctrl + r 运行当前的代码  

ctrl + g 开灯/关灯  

ctrl + b 打开设置  

ctrl + t 打开可视化钢琴的设置  

ctrl + c, ctrl + a, ctrl + v, ctrl + x, ctrl + z, ctrl + y这些快捷键组合与大部分的文本编辑器的功能相同，分别为复制，全选，粘贴，剪切，撤销，恢复

ctrl + 鼠标滚轮可以调节字体大小，往上滚字体变大，往下滚字体变小，并且会自动保存改变后的字体大小的设置。

右下角的Line Col显示的是当前输入光标所在的行数和列数，以方便在代码出错的时候查看对应的位置。

alt + z 播放选中的musicpy代码  

alt + x 可视化播放选中的musicpy代码

这个musicpy编辑器我之后还会多加完善，希望大家用的开心~

## 将musicpy的数据结构存储为单独的数据文件
你可以使用`write_data`函数将任何的musicpy的数据结构存储为一个单独的二进制数据文件，建议的文件后缀名为`mpb` (musicpy binary), 比如
```python
write_data(C('C'), name='C major chord.mpb')
```
这行代码会在当前的文件目录下创建一个名为`C major chord.mpb`的musicpy的数据结构的二进制数据文件。

你可以使用`load_data`函数加载任何的mpb文件为musicpy的数据结构，比如
```python
result = load_data('C major chord.mpb')

>>> result
[C4, E4, G4] with interval [0, 0, 0]
```
在有些时候，当你不想存储musicpy代码或者其生成的MIDI文件时，存储为二进制数据文件是一个不错的选择。
