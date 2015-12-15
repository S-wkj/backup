#-*- coding:utf-8 -*-
#import os
#os.chdir('..') #切换回根目录
import sys
sys.path.append('.') #添加到搜索路径

import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.logger import Logger

from gui.filemanager import FileManager
from right_click import text, event

import os
def show(target_path):
	target_list = os.walk(target_path).next()
	target_dir = map(lambda x: '%s/%s' % (target_list[0], x), target_list[1][::-1])
	target_file = map(lambda x: '%s/%s' % (target_list[0], x), target_list[2][::-1])
	return target_dir, target_file

def get_filelist(target_path):
	t = []
	target_dir, target_file = show(target_path)
	for f in target_dir + target_file:
		f_stat= os.stat(f)
		t.append(map(str, [f.encode('utf-8'), f_stat.st_mtime, f_stat.st_dev, f_stat.st_size]))
	return t

def get_titlelabel():
	return ['名称', '修改日期', '设备', '大小']


class DisplayScreen(FileManager):
	w = [180, 180, 60, 40]
	def build(self):
		self.filelist.insert(text=get_filelist(u'C:/Users/Administrator/Desktop'))
		self.filelist.update(width=[self.w] * len(self.filelist.children))

		self.titlelabel.insert(text=get_titlelabel())
		self.titlelabel.update(width=self.w)
		self.titlelabel.auto_sort()

		self.filelist.click_menu.insert(text=text, event=event)


class mainApp(App):
	def build(self):
		ds = DisplayScreen()
		ds.build()
		return ds

if __name__ == '__main__':
	mainApp().run()
