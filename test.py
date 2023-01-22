from typing import *
from ast import List
from tree_project import ObsVar, Observable, TreeCtrl, TreeNode
import wx
class TestTreeNode(TreeNode):
    def __init__(self, label: str, children: List[TreeNode]):
        self.tree_label = ObsVar(label)
        self._children = children
        self.tree_children_change = Observable()

    def is_tree_leaf(self) -> bool:
        return not bool(self._children)

    def get_tree_children(self) -> Iterable[TreeNode]:
        return self._children

class TestApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, title='Tree Example')
        tree_node_1 = TestTreeNode('Node 1', [])
        tree_node_2 = TestTreeNode('Node 2', [])
        tree_node_3 = TestTreeNode('Node 3', [tree_node_1, tree_node_2])
        tree_ctrl = TreeCtrl(tree_node_3, frame)
        frame.Show()
        return True

if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
