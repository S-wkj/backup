#-*- coding:utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

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
		#如果选中则直接打开选项栏
		#如果未选中则清空其它选项并选择该项，然后打开选项栏
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
		#如果打开了右键菜单，则不选中
		try:
			#DisplayScreen的click_menu
			if self.parent.parent.parent.click_menu.status:
				return
		except: pass
		#选中前，将其它选中的清空
		for child in self.parent.children:
			if child.select == 1:
				child.selected(0)
		if self.select == 0:	
			self.selected(1)

	def on_leave(self, *args):
		if self.select == 1:
			self.selected(0)


#调节宽度，改变排列顺序等功能
class TitleLabel(GridLayout):
	filelist = None

	#将标题栏和文件列表关联起来
	def mapping(self, filelist):
		self.filelist = filelist

	@apply_insert(AttributeLabel)
	def insert(self, **kwargs):
		pass

	@apply_update
	def update(self, **kwargs):
		pass

	#第num个标题后的分隔线向右移动distance个单位
	def stretch(self, num, distance):
		width_min = 40 #最小宽度
		if distance == 0: #移动0距离时直接返回
			return
		children = self.children[::-1]
		if num < 0 or num > len(children):  #超出范围
			return
		children[num].width += distance
		if children[num].width < width_min:
			children[num].width = width_min

		#调节子标题后重新设置宽度
		self.width = sum([child.width for child in self.children])

		if self.filelist:
			for filelabel in self.filelist.children:
				children = filelabel.children[::-1]
				children[num].width += distance
				if children[num].width < width_min:
					children[num].width = width_min
				filelabel.width = sum([child.width for child in filelabel.children])

	#将第num个标题插入到position之后
	def change(self, num, position):
		children = self.children[::-1]
		if num < 0 or num > len(children):  #超出范围
			return
		if position < 0 or position > len(children):  #超出范围
			return

		if num == position: #相同位置，无须移动
			return
		move_label = children.pop(num)
		children = children[:position] + [move_label] + children[position:]
		self.children = children[::-1]
		
		if self.filelist:
			for filelabel in self.filelist.children:
				children = filelabel.children[::-1]
				if num == position: #相同位置，无须移动
					return
				move_label = children.pop(num)
				children = children[:position] + [move_label] + children[position:]
				filelabel.children = children[::-1]

	#事件类型
	move_type = 0
	#上一个点
	last_pos = None
	#操作编号
	num = 0

	#调节宽度事件
	#移动位置事件
	def on_touch_down(self, touch):
		#判断鼠标位置，靠近右边界进入调节宽度状态，其它位置进入移动位置状态
		super(TitleLabel, self).on_touch_down(touch)
		self.move_type = 1
		self.last_pos = int(round(touch.x)), int(round(touch.y))
		for num, child in enumerate(self.children[::-1]):
			if child.collide_point(touch.x, touch.y):
				self.num = num

	def on_touch_move(self, touch):
		super(TitleLabel, self).on_touch_move(touch)
		pos = int(round(touch.x)), int(round(touch.y))
		if self.move_type == 1:
			self.stretch(self.num, pos[0] - self.last_pos[0])
		self.last_pos = pos

	def on_touch_up(self, touch):
		super(TitleLabel, self).on_touch_up(touch)


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
		#未打开菜单或不是
		if not self.click_menu.status or touch.button not in ['scrollup', 'scrolldown', 'middle']:
			super(DisplayScreen, self).on_touch_down(touch) #先调用子节点的事件更新select值
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