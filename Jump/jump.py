from PySide import QtCore, QtGui
import sys
import os 
import ui
import studio

#-----------------------------------------------------------------------------#
# TEST VALUES TO DEBUG

ACTIONS= (
	"Open Shell",
	"List Artists",
	"Recent Activity",
	"Maya",
	"Houdini",
	"Browse Dailies"
	)

ASSETS = (
	"Modeling",
	"Animation",
	"Lighting",
	"Effects",
	"Compositing"
	)

PARMS = os.listdir("/Users/koen/Google/Dev/Jump")

#-----------------------------------------------------------------------------#

class Shot:
	"""general description of an item in the shotmenu"""

	def __init__(self, sspec):
		
		# store teh shot spec
		self._sspec = sspec
	
		#---------------------------------------#
		# TEST - fill the list with the test data
		actions = []
		for a in ACTIONS:
			actions.append(Action(a))
		#---------------------------------------#

		# keep a list of all the actions that are possible in this shot
		self._actionList = JumpList(actions)
	
	def actions(self):
		return self._actionList

	def sspec(self):
		return self._sspec

	def __repr__(self):
		# let the shot spec return the description
		return self._sspec.description()

#-----------------------------------------------------------------------------#

class Action:
	"""description of an action"""

	def __init__(self, label):
		
		self._label = label
		
		#---------------------------------------#
		# TEST - fill the list with the test data
		assets = []
		for a in ASSETS:
			assets.append(Asset(a))
		#---------------------------------------#
		
		self._assetList = JumpList(assets)
	
	def assets(self):
		return self._assetList

	def __repr__(self):
		return "%s" % self._label

#-----------------------------------------------------------------------------#

class Asset:
	"""description of an item in the shotmenu"""

	def __init__(self, label):
		self._label = label
	
		#---------------------------------------#
		# TEST - fill the list with the test data
		parms = []
		for p in PARMS:
			parms.append(Parm(p))
		#---------------------------------------#

		self._parmList = JumpList(parms)

	def parms(self):
		return self._parmList

	def __repr__(self):
		return "%s" % self._label

#-----------------------------------------------------------------------------#

class Parm:
	"""description of an parm"""

	def __init__(self, label):
		self._label = label
	
	def __repr__(self):
		return "%s" % self._label

#-----------------------------------------------------------------------------#

class JumpList:
	"""list of items"""
	
	def __init__(self, items= None):
		
		self._set  = set()
		if items:
			for item in items:
				self._set.add(item)
		
		# maintain a cache
		self._cache = sorted(list(self._set))
		
		# maintain a model of the list
		self._model = JumpListModel(self)

	def item(self, index):
		return self._cache[index]

	def list(self):
		return self._cache

	def model(self):
		return self._model

	def count(self):
		return len(self._cache)

	def add(self, item):
		self._set.add(item)
		# update the cache
		self._cache = sorted(list(self._set))
		
#-----------------------------------------------------------------------------#

class JumpListModel(QtCore.QAbstractListModel):

    def __init__(self, list):
        super(JumpListModel, self).__init__()
        self._list = list

    def rowCount(self,parent):
        return self._list.count()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

      	if role == QtCore.Qt.DisplayRole:
      		item = self._list.item(index.row())
      		return str(item)
            
#        elif role == QtCore.Qt.DecorationRole:
#            return QtGui.QIcon(icon_path)

#        elif role == QtCore.Qt.BackgroundColorRole:
#        	return QtGui.QBrush(QtGui.QColor("#d4d4d4"))

        return None

#-----------------------------------------------------------------------------#


# the main window
class mainWindow(QtGui.QMainWindow):
	
	def __init__(self, parent=None):
		
		super(mainWindow, self).__init__(parent)
		self.ui = ui.Ui_MainWindow()
		self.ui.setupUi(self)

		# init the shot list
		#self._shotList = shots.ShotList()
		#self._shotList.load()
		self._shotList = JumpList()
		self.load()

		#model = shots.ShotListModel(self._shotList)
		model = self._shotList.model()
		self.ui.shot.setModel(model)

		# connect up the shot list
		self.ui.shot.clicked.connect(self._shotSelected)

		# connect up the shot list
		self.ui.shot.doubleClicked.connect(self._shotDoubleClicked)
		
		# hook up the asset list
		self.ui.asset.clicked.connect(self._assetSelected)
		
		# hook up the action list
		self.ui.action.clicked.connect(self._actionSelected)
		
		# keep track of what is selected
		self.currentShot 	= None
		self.currentAsset 	= None
		self.currentAction 	= None

		#DEBUG,store shots in config
		self.save()
	
	# store a shotlist in a file
	def save(self):
		
		# get the filename from the configuration
		filename = studio.getUserSettingsFile('koen')

		with open (filename, 'w') as file: 
			for shot in self._shotList.list():
				file.write(shot.sspec().id())
				file.write('\n')
	
	# load the shotlist from a file 			
	def load(self):
		# get the filename from the configuration
		filename = studio.getUserSettingsFile('koen')

		with open (filename, 'r') as file: 
			for line in file: 
				# build a shotspec from the string, one spec per line.
				sspec = studio.ShotSpec(line)
				# add a new shots that is build from the shotspec
				self._shotList.add(Shot(sspec))

	def resetUI(self, level = 0):

		# reset everything above level, 0=shot, 1=asset, 2=action, 3=parm
		if level < 1:
			self.currentShot = None
			self.ui.shot.setModel(None)
		
		if level < 2:
			self.currentAction = None
			self.ui.action.setModel(None)

		if level < 3:
			self.currentAsset = None
			self.ui.asset.setModel(None)
		
		if level < 4:
			self.currentParm = None
			self.ui.parm.setModel(None)

	# UI callbacks

	def _shotDoubleClicked(self, index):
		if index.isValid():
			
			# get the shot belonging to this index
			shot = self._shotList.item(index.row())
			
			# run a terminal in this shot
			studio.runInShotEnv(shot.sspec(),'ls','-l')

	def _shotSelected(self, index):
		if index.isValid():
			
			# get the shot belonging to this index
			shot = self._shotList.item(index.row())
			
			# populate the next column in the UI 
			self.ui.action.setModel(shot.actions().model())
		
			# store the shot so we can get back to it later
			self.currentShot = shot
			
			# when we select a new shot, reset the rest 
			self.resetUI(2)

	def _actionSelected(self, index):
		if index.isValid():
			if self.currentShot:

				# find the right action by asking the shot
				action = self.currentShot.actions().item(index.row())

				# and populate the next column in the ui with the proper assets
				self.ui.asset.setModel(action.assets().model())

				# store the current action for later reference
				self.currentAction = action

				# reset the dependant ui
				self.resetUI(3)

	def _assetSelected(self, index):
		if index.isValid():
			if self.currentAction:
				
				# find the asset belonging to this index, since the shot owns the 
				# asset list, we need to go through the shot to get the asset 
				asset = self.currentAction.assets().item(index.row())
				
				# and populate the next column in the ui with the proper assets
				self.ui.parm.setModel(asset.parms().model())
			
				# store the current asset 
				self.currentAsset = asset

				# and reset the actions and parms
				self.resetUI(4)
	
	


# launch the application

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = mainWindow()
	window.show()
	sys.exit(app.exec_())
