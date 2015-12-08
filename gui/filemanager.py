#-*- coding:utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from kivy.core.window import Window
from kivy.animation import Animation

from clickmenu import BackGround, ClickMenu
from hoverbehavior import HoverBehavior
import time

from kivy.logger import Logger
from Tools import *

from kivy.lang import Builder
Builder.load_file('filemanager.kv')

class AttributeLabel(Label):
	def insert(self, **kwargs):
		insert_args(self, **kwargs)

	def delete(self, **kwargs):
		delete_args(self, **kwargs)

	def update(self, **kwargs):
		insert_args(self, **kwargs)


class FileLabel(BackGround, GridLayout, HoverBehavior):
	@apply_insert(AttributeLabel)
	def insert(self, **kwargs):
		pass

	@apply_delete
	def delete(self, **kwargs):
		pass

	@apply_update
	def update(self, **kwargs):
		pass

	def on_touch_down(self, touch):
		#���ѡ����ֱ�Ӵ�ѡ����
		#���δѡ�����������ѡ�ѡ����Ȼ���ѡ����
		if self.collide_point(touch.x, touch.y):
			if touch.button == 'left':
				if self.select == 0 or self.select == 1:
					self.selected(2)
				elif self.select == 2:
					self.selected(0)
			elif touch.button == 'right':
				if self.select == 0 or self.select == 1:
					for child in self.parent.children:
						if child.select:
							child.selected(0)
					self.selected(2)

	def on_enter(self, *args):
		#��������Ҽ��˵�����ѡ��
		try:
			if not self.parent.enable:
				return
			#ListLabel��click_menu
			if self.parent.click_menu.status:
				return
		except: pass
		#ѡ��ǰ��������ѡ�е����
		for child in self.parent.children:
			if child.select == 1:
				child.selected(0)
		if self.select == 0:
			self.selected(1)

	def on_leave(self, *args):
		if self.select == 1:
			self.selected(0)


#���ڿ�ȣ��ı�����˳��ȹ���
class TitleLabel(GridLayout):
	def __init__(self, **kwargs):
		Window.bind(mouse_pos=self.on_mouse_pos)
		super(TitleLabel, self).__init__(**kwargs)

	filelist = None

	#�����������ļ��б��������
	def mapping(self, filelist):
		self.filelist = filelist

	@apply_insert(AttributeLabel)
	def insert(self, **kwargs):
		pass

	@apply_update
	def update(self, **kwargs):
		pass

	#��num�������ķָ��������ƶ�distance����λ
	def stretch(self, num, distance):
		width_min = 40 #��С���
		if distance == 0: #�ƶ�0����ʱֱ�ӷ���
			return
		children = self.children[::-1]
		if num < 0 or num > len(children):  #������Χ
			return
		children[num].width += distance
		if children[num].width < width_min:
			children[num].width = width_min

		#�����ӱ�����������ÿ��
		self.width = sum([child.width for child in self.children])

		if self.filelist:
			for filelabel in self.filelist.children:
				children = filelabel.children[::-1]
				children[num].width += distance
				if children[num].width < width_min:
					children[num].width = width_min
				filelabel.width = sum([child.width for child in filelabel.children])

	#����num��������뵽position֮��
	def change(self, num, position):
		children = self.children[::-1]
		if num < 0 or num > len(children):  #������Χ
			return
		if position < 0 or position > len(children):  #������Χ
			return

		if num == position: #��ͬλ�ã������ƶ�
			return
		move_label = children.pop(num)
		children = children[:position] + [move_label] + children[position:]
		self.children = children[::-1]

		if self.filelist:
			for filelabel in self.filelist.children:
				children = filelabel.children[::-1]
				if num == position: #��ͬλ�ã������ƶ�
					return
				move_label = children.pop(num)
				children = children[:position] + [move_label] + children[position:]
				filelabel.children = children[::-1]

	#�¼�����
	move_type = 0
	#�������
	move_num = -1
	move_position = -1
	#��һ����
	move_pos = None
	#��ʼλ��
	move_base = None

	#�ж����
	split_width = 10

	def get_type(self):
		pos = Window.mouse_pos[0]
		children = self.children[::-1]
		for child in children:
			split_line = child.x + child.width
			if split_line - self.split_width < pos < split_line + self.split_width:
				return 1
		return 2

	def get_num(self):
		pos = Window.mouse_pos[0]
		children = self.children[::-1]
		for num, child in enumerate(children):
			if num == self.move_num:
				continue
			if child.x < pos <= child.x + child.width:
				split_left = child.x + self.split_width
				split_right = child.x + child.width - self.split_width
				if child.x < pos <= split_left:
					side = -1
				elif split_right < pos <= child.x + child.width:
					side = 1
				else:
					side = 0
				return (num, side)
		return (self.move_num, 0)

	def on_mouse_pos(self, *args):
		try:
			import win32api
			import win32con
			if self.move_type == 1 or (self.get_type() == 1 and self.y < Window.mouse_pos[1] < self.y + self.height):
				win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_SIZEWE))
			#else:
			#	win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_ARROW))
		except:
			pass

	#���ڿ���¼���move_type = 1
	#�ƶ�λ���¼���move_type = 2
	def on_touch_down(self, touch):
		#�ж����λ�ã������ұ߽������ڿ��״̬������λ�ý����ƶ�λ��״̬
		super(TitleLabel, self).on_touch_down(touch)
		if not self.collide_point(touch.x, touch.y):
			return
		if touch.button != 'left':
			return
		self.move_type = self.get_type()
		self.move_num, side = self.get_num()
		if side == -1: #�����ʱ������һ��
			self.move_num -= 1
		self.move_pos = int(round(touch.x)), int(round(touch.y))
		self.move_base = list(self.children[::-1][self.move_num].pos)
		self.filelist.enable = False
		self.on_mouse_pos()

	def on_touch_move(self, touch):
		super(TitleLabel, self).on_touch_move(touch)
		#�ƶ�ʱ�������Ƴ���Χ
		if touch.button != 'left':
			return
		pos = int(round(touch.x)), int(round(touch.y))
		if self.move_type == 1:
			self.stretch(self.move_num, pos[0] - self.move_pos[0])
		elif self.move_type == 2:
			num, side = self.get_num()
			child = self.children[::-1][self.move_num]
			child.x += pos[0] - self.move_pos[0]
			if side:
				self.move_position = num
		self.move_pos = pos
		self.on_mouse_pos()

	def on_touch_up(self, touch):
		super(TitleLabel, self).on_touch_up(touch)
		if touch.button != 'left':
			return
		num, side = self.get_num()
		child = self.children[::-1][self.move_num]
		if self.move_num == num:
			if self.move_type == 2:
				child.pos = self.move_base
		else:
			if self.move_type == 2:
				self.change(self.move_num, self.move_position)
		self.move_type = 0
		self.move_num = -1
		self.move_position = -1
		self.move_pos = None
		self.move_base = None
		self.filelist.enable = True
		self.on_mouse_pos()


class ListLabel(GridLayout):
	enable = True

	@apply_insert(FileLabel)
	def insert(self, **kwargs):
		pass

	@apply_delete
	def delete(self, **kwargs):
		pass

	@apply_update
	def update(self, **kwargs):
		pass

	click_menu = None

	def on_touch_down(self, touch):
		if not self.click_menu:
			return
		#δ�򿪲˵�����
		if not self.click_menu.status or touch.button not in ['scrollup', 'scrolldown', 'middle']:
			super(ListLabel, self).on_touch_down(touch) #�ȵ����ӽڵ���¼�����selectֵ
		#Logger.info(str(touch.button))
		if touch.button not in ['scrollup', 'scrolldown', 'middle']:
			self.click_menu.close()
		if self.collide_point(touch.x, touch.y):
			if touch.button == 'right':
				self.click_menu.open(Window.mouse_pos) #touch������Ϊ�������

class FileManager(GridLayout):
	def __init__(self, **kwargs):
		super(FileManager, self).__init__(**kwargs)
		#�ļ��б�
		self.filelist = ListLabel()
		self.filelist.click_menu = ClickMenu()
		self.filelist.bind(minimum_height=self.filelist.setter('height'), minimum_width=self.filelist.setter('width'))

		#������
		self.titlelabel = TitleLabel()
		self.titlelabel.mapping(self.filelist)

		#������
		self.scrollview = ScrollView()
		self.scrollview.add_widget(self.filelist)

		self.add_widget(self.titlelabel)
		self.add_widget(self.scrollview)
