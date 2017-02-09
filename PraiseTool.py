import re
import datetime


class PraiseTool:
    def __init__(self):
        self.__like_user_list = []
        self.__clip_user_list = []
        self.params = {'oldest': '昨天00:00', 'account': '', 'password': '', 'timetick': ''}
        mfile = open('config.ini', encoding='utf-8')
        for line in mfile.readlines():
            line = line.replace('\n', '').strip()
            name = line[6:]
            if line.startswith('[Both]'):
                self.__like_user_list.append(name)
                self.__clip_user_list.append(name)
            elif line.startswith('[Like]'):
                self.__like_user_list.append(name)
            elif line.startswith('[Clip]'):
                self.__clip_user_list.append(name)
            elif re.match('^.+=.+$', line):
                kv_set = line.split('=')
                key = kv_set[0]
                val = kv_set[1]
                if self.params.get(key, None) is not None:
                    self.params[key] = val
        ctime = datetime.datetime.now().strftime('%H:%M')
        if not compare_time(ctime, self.params['oldest']) and not self.params['oldest'].startswith('昨天'):
            self.params['oldest'] = '昨天' + self.params['oldest']
        mfile.close()

    def is_auto_like(self, user):
        if user in self.__like_user_list:
            return True
        else:
            return False

    def is_auto_clip(self, user):
        if user in self.__clip_user_list:
            return True
        else:
            return False

    def save_params(self):
        mfile = open('config.ini', 'w', encoding='utf-8')
        for _like in self.__like_user_list:
            if _like not in self.__clip_user_list:
                mfile.write('[Like]' + _like + '\n')
            else:
                mfile.write('[Both]' + _like + '\n')
        for _like in self.__clip_user_list:
            if _like not in self.__like_user_list:
                mfile.write('[Clip]' + _like + '\n')
        for key in self.params:
            mfile.write(key + '=' + self.params[key] + '\n')


# 返回参数一是否大于参数二
def compare_time(time_str1, time_str2):
    grade1, grade2 = 0, 0
    pattern = re.compile('^(昨天)?\d{1,2}:\d{1,2}$')
    if pattern.match(time_str1) and pattern.match(time_str2):
        if time_str1.startswith('昨天'):
            grade1 -= 1440
            time_str1 = time_str1[2:]
        if time_str2.startswith('昨天'):
            grade2 -= 1440
            time_str2 = time_str2[2:]
        time1 = time_str1.split(':')
        time2 = time_str2.split(':')
        grade1 += 60 * int(time1[0]) + int(time1[1])
        grade2 += 60 * int(time2[0]) + int(time2[1])
        return grade1 > grade2
