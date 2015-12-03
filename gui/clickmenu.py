#-*- coding:utf-8 -*-
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, ObjectProperty

from hoverbehavior import HoverBehavior

from Tools import *

from kivy.lang import Builder
Builder.load_file('clickmenu.kv')


#kv�ļ��и���transparent���ÿɼ���
#selected����ʵ����select��ѡ�����ͣ����ɼ��ȵ�ת��
#select����
#0δѡ�У�1��껬����2ѡ��
class BackGround:
	select = 0
	space_color = ListProperty([0, .6, 1, 0])
	frame_color = ListProperty([0, .6, 1, 0])

	def selected(self, select):
		self.select = select
		if select == 0:
			self.space_color[3] = 0
			self.frame_color[3] = 0
		elif select == 1:
			self.space_color[3] = .1
			self.frame_color[3] = .4
		elif select == 2:
			self.space_color[3] = .3
			self.frame_color[3] = .6

class AttributeMenu(Label):
	pass

class OptionMenu(BackGround, GridLayout, HoverBehavior):
	click_menu = None #��һ���˵�

	def insert(self, **kwargs):
		text = kwargs.get('text')
		#���Լ�����չ
		if isinstance(text, tuple) or isinstance(text, list):
			self.click_menu = ClickMenu()
			self.click_menu.parent_menu = self.parent #���ø��˵�
			kwargs['text'] = text[1:]
			self.click_menu.insert(**kwargs)
			kwargs['text'] = text[0]
		label = AttributeMenu(**kwargs)
		self.add_widget(label)
		#insert_args(self, **kwargs)

	def on_touch_down(self, touch):
		if self.collide_point(touch.x, touch.y):
			return True
		super(OptionMenu, self).on_touch_down(touch)

	def click(self):
		if self.click_menu:
			self.click_menu.open(self.pos, open_type='enter', size=self.size)

	def on_enter(self, *args):
		#���븸�ؼ�ʱ���ӿؼ���
		if self.parent.child_menu:
			if self.parent.child_menu.collide_point(self.border_point[0], self.border_point[1]):
				return
			self.parent.child_menu.close()
			
		#���ͬ���˵�selectֵ
		for child in self.parent.children:
			if child.select == 1:
				child.selected(0)
		if self.select == 0:
			self.selected(1)
		self.click()

	def on_leave(self, *args):
		#�ӿؼ��ڵ��л�
		if self.parent.collide_point(self.border_point[0], self.border_point[1]):
			return

		#�뿪�ӿؼ�ʱ�ڸ��ؼ���
		if self.parent.parent_menu:
			if self.parent.parent_menu.collide_point(self.border_point[0], self.border_point[1]): #�ڸ��ؼ���
				self.parent.close()
				#���ͬ���˵�selectֵ
				for child in self.parent.parent_menu.children:
					if child.select == 1:
						child.selected(0)
				#��ȡ���ڿؼ�
				for child in self.parent.parent_menu.children:
					if child.collide_point(self.border_point[0], self.border_point[1]):
						if child.select == 0:
							child.selected(1)
						child.click()
						break


class ClickMenu(GridLayout, HoverBehavior):
	@apply_insert(OptionMenu)
	def insert(self, **kwargs):
		pass

	attach_to = ObjectProperty(None)
	_window = ObjectProperty(None, allownone=True)
	status = False #�Ƿ��
	child_menu = None #�򿪵��Ӳ˵�
	parent_menu = None #���˵�

	def __init__(self, **kwargs):
		self._parent = None
		super(ClickMenu, self).__init__(**kwargs)

	def _search_window(self):
		# get window to attach to
		window = None
		if self.attach_to is not None:
			window = self.attach_to.get_parent_window()
			if not window:
				window = self.attach_to.get_root_window()
		if not window:
			from kivy.core.window import Window
			window = Window
		return window

	def open(self, pos, open_type='click', size=(0, 0)):
		if self.status: return

		if self._window is not None:
			Logger.warning('ModalView: you can only open once.')
			return self
		# search window
		self._window = self._search_window()
		if not self._window:
			Logger.warning('ModalView: cannot open view, no window found.')
			return self

		x, y = pos
		if open_type == 'click':
			if self.width + x > self._window.width:
				x = self._window.width - self.width

			if y > self.height:
				y -= self.height

		elif open_type == 'enter':
			width, height = size
			if self.width + x + width > self._window.width:
				x -= width - 3
			else:
				x += width - 3

			if y > self.height:
				y = y - self.height + height

		self.pos = (x, y)
		#Logger.info(str(self.pos))
		self._window.add_widget(self)

		self.status = True
		if self.parent_menu:
			self.parent_menu.child_menu = self
		return self

	def close(self):
		#�ݹ�ر����нڵ�
		for child in self.children:
			if child.select == 1:
					child.selected(0)
			if child.click_menu:
				child.click_menu.close()

		if self._window is None:
			return self
		self._window.remove_widget(self)
		self._window = None
		self.status = False
		#�ر�ʱ���ؼ���child_menu�ÿ�
		if self.parent_menu:
			self.parent_menu.child_menu = None
		return self
