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
			#DisplayScreen��click_menu
			if self.parent.parent.parent.click_menu.status:
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
	move_num = 0
	#��һ����
	move_pos = None

	def get_type(self):
		children = self.children[::-1]
		for child in children:
			split_line = child.x + child.width
			split_width = 10
			if split_line - split_width < Window.mouse_pos[0] < split_line + split_width:
				return 1
		return 2

	def get_num(self):
		children = self.children[::-1]
		for num, child in enumerate(children):
			if child.x < Window.mouse_pos[0] <= child.x + child.width:
				return num
		return -1

	def on_mouse_pos(self, *args):
		#self.get_type()
		pass

	#���ڿ���¼���move_type = 1
	#�ƶ�λ���¼���move_type = 2
	def on_touch_down(self, touch):
		#�ж����λ�ã������ұ߽������ڿ��״̬������λ�ý����ƶ�λ��״̬
		super(TitleLabel, self).on_touch_down(touch)
		self.move_type = self.get_type()
		self.move_pos = int(round(touch.x)), int(round(touch.y))
		self.move_num = self.get_num()

	def on_touch_move(self, touch):
		super(TitleLabel, self).on_touch_move(touch)
		pos = int(round(touch.x)), int(round(touch.y))
		if self.move_type == 1:
			self.stretch(self.move_num, pos[0] - self.move_pos[0])
		elif self.move_type == 2:
			num = self.get_num()
		self.move_pos = pos

	def on_touch_up(self, touch):
		super(TitleLabel, self).on_touch_up(touch)
		num = self.get_num()
		if self.move_type == 2:
			if self.move_num == num:
				return
			else:
				self.change(self.move_num, num)


class ListLabel(GridLayout):
	@apply_insert(FileLabel)
	def insert(self, **kwargs):
		pass

	@apply_delete
	def delete(self, **kwargs):
		pass

	@apply_update
	def update(self, **kwargs):
		pass


class DisplayScreen(GridLayout):
	def build(self):
		f = ListLabel()
		f.insert(a=[range(4)] * 32)
		t = []
		for i in range(len(f.children)):
			t.append(['a%s' % i, 'b', 'c', 'd', 'ab'])
		f.update(text=t)
		f.update(width=[[120, 80, 160, 40]] * len(f.children))
		#f.delete(text=[[('a', 'b'), ('a', 'c'), 'd', 'e']] * len(f.children))
		#f.draw()
		f.bind(minimum_height=f.setter('height'), minimum_width=f.setter('width'))

		s = ScrollView()
		s.add_widget(f)

		t = TitleLabel()
		t.mapping(f)
		t.insert(text=['title-0', 'title-1', 'title-2', 'title-3'])
		t.update(width=[120, 80, 160, 40])
		self.add_widget(t)
		self.add_widget(s)
		t.stretch(0, -20)
		t.stretch(1, 20)
		t.stretch(2, -20)
		t.change(2, 3)
		#Logger.info(str(t.size))

		self.click_menu = ClickMenu()
		self.click_menu.insert(text=['a', ['b', 'b1', 'b2', 'b3', 'b4', 'b5', ['ee', 'ee1', 'ee2', ['f', 'f1', ['g', ['h', 'h1']]]]], ['c', 'c1', 'c2'], 'd'])

	click_menu = None

	def on_touch_down(self, touch):
		#δ�򿪲˵�����
		if not self.click_menu.status or touch.button not in ['scrollup', 'scrolldown', 'middle']:
			super(DisplayScreen, self).on_touch_down(touch) #�ȵ����ӽڵ���¼�����selectֵ
		#Logger.info(str(touch.button))
		if touch.button not in ['scrollup', 'scrolldown', 'middle']:
			self.click_menu.close()
		if self.collide_point(touch.x, touch.y):
			if touch.button == 'right':
				self.click_menu.open(touch.pos)


class FileListApp(App):
	def build(self):
		ds = DisplayScreen()
		ds.build()
		return ds

if __name__ == '__main__':
	FileListApp().run()