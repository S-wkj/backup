#-*- coding:utf-8 -*-

class Base:
	@classmethod
	def walk(self, target_path):
		target_dir, target_file = self.show(target_path)
		yield (target_path, target_dir, target_file)
		for path in target_dir:
			for g in self.walk('%s/%s' % (target_path, path)):
				yield g
				
	def restore_walk(self, target_path):
		target_dir, target_file = self.show(target_path)
		backup_dir = []
		backup_file = []
		for path in target_dir:
			#��Ŀ¼��ȫ��Ϊ�ļ�������Ӧ���ݵ��ļ�����Ŀ¼������
			if len(self.show('%s/%s' % (target_path, path))[0]):
				backup_dir.append(path)
			else:
				backup_file.append(path)
		target_dir, target_file = backup_dir, backup_file
		yield (target_path, target_dir, target_file)
		for path in target_dir:
			for g in self.restore_walk('%s/%s' % (target_path, path)):
				yield g