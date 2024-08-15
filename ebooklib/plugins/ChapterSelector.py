# @Time    : 2024/8/15 14:35
# @Author  : TwoOnefour
# @blog    : https://www.pursuecode.cn
# @Email   : twoonefour@pursuecode.cn
# @File    : ChapterSelector.py
import sys
from functools import wraps
from bs4 import BeautifulSoup



chapterArray = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]  # 用于映射中文
Start_Chapter_index = 0
End_Chapter_index = 0  # 用于多章节下载时指定书名
def chapterselector(flag, chapter_str, loggerFunc, chapter_index):
    '''
    装饰器。改变下载章节方法的行为。
    :param flag: 判断是否生效的标志
    :param chapter_str: 需要下载的章节
    :param loggerFunc: 传入日志方法用于格式化标准输出
    :return: 被修饰的新方法
    '''
    def wrapper(func):
        @wraps(func)
        def changetargets(*args, **kwargs):
            start_index: int = 0
            findFlag: bool = False
            end_index: int = chapter_index
            for index, tag in enumerate(args[0]):
                if tag.has_key("colspan"):  # 如果是章节名字
                    if findFlag:
                        end_index += 1

                    if chapter_str in tag.text:  # 到了要找的章节
                        start_index = index
                        findFlag = True

            if not findFlag:
                # findFlag来判断没有找到章节
                loggerFunc("没有找到该章节，将下载全部内容")
                return func(*args, **kwargs)
            global End_Chapter_index
            End_Chapter_index = end_index
            return func((args[0][start_index:]))
        return changetargets if flag else func
    return wrapper


def changeToChapterBookName(flag, remove_special_symbols, raw_book_name, title, author, chapter_index, index):
    '''
    装饰器。改变epub保存的名称
    :param flag: 判断是否生效的标志
    :param remove_special_symbols: 本地方法
    :param raw_book_name:
    :param title:
    :param author:
    :param chapter_index:
    :param index:
    :return:
    '''
    def wrapper(func):
        @wraps(func)
        def changeName(*args, **kwargs):
            if End_Chapter_index == chapter_index:
                # noinspection PyStringFormat
                name = '%s %s - %s%s.epub' % (
                    *[remove_special_symbols(s) if not raw_book_name else s for s in [title, str(chapter_index), author]],
                    '' if index is None else f'({args[0]})')
            else:
                # noinspection PyStringFormat
                name = '%s %s-%s - %s%s.epub' % (
                    *[remove_special_symbols(s) if not raw_book_name else s for s in
                      [title, str(chapter_index), str(End_Chapter_index), author]],
                    '' if index is None else f'({args[0]})')
            return name
        return changeName if flag else func
    return wrapper


def Paramhandler(val) -> tuple[str, int]:
    '''
    获得参数指定的章节
    :param val: -c输入的参数
    :return: _chapter, _chapter_index
    '''
    _chapter: str = None
    _chapter_index: int = -1
    val = int(val)
    if val <= 10:
        _chapter = chapterArray[val - 1]
        _chapter_index = val
    elif val >= 100:
        print("目前只支持1-99章的单章下载")
        sys.exit(1)
    else:
        '''
        生成超过10章节的对应中文的数组
        '''
        tmp = chapterArray[:]
        pointer = 0
        for _ in range(10, val):
            if pointer == 9:
                pointer = 0

            tenPosStr = tmp[(_ + 1) // 10 - 1]
            if (_ + 1) // 10 - 1 == 0:
                tenPosStr = "十"
            tmpstr = tenPosStr
            if ((_ + 1) % 10) == 0 and (_ + 1) // 10 - 1:
                chapterArray.append(tmpstr + "十")
                continue
            if _ + 1 > 20:
                tmpstr += "十"
            tmpstr += tmp[pointer]
            chapterArray.append(tmpstr)
            pointer += 1

        _chapter = chapterArray[val - 1]
        _chapter_index = val
    return _chapter, _chapter_index